import os
import re
import sys
import math
import json
import hashlib
import zipfile
import tarfile
import datetime
import argparse
from pathlib import Path

try:
    import pefile
    HAS_PEFILE = True
except ImportError:
    HAS_PEFILE = False
    print("[Warning] pefile not installed: pip install pefile")

try:
    import py7zr
    HAS_7Z = True
except ImportError:
    HAS_7Z = False
    print("[Warning] py7zr not installed: pip install py7zr")


# ──────────────────────────────────────────────
# Rule Configuration
# ──────────────────────────────────────────────

SUSPICIOUS_APIS = {
    "Network Connection": [
        "socket", "WSASocket", "connect", "recv", "send",
        "WinInet", "InternetOpen", "InternetConnect",
        "HttpSendRequest", "URLDownloadToFile",
    ],
    "Registry Operation": [
        "RegCreateKey", "RegSetValue", "RegOpenKey",
        "RegDeleteKey", "RegQueryValue",
    ],
    "Process Injection": [
        "CreateRemoteThread", "NtCreateThreadEx",
        "WriteProcessMemory", "VirtualAllocEx",
        "OpenProcess", "SetThreadContext",
    ],
    "Keyboard/Screen Monitoring": [
        "SetWindowsHookEx", "GetAsyncKeyState",
        "GetForegroundWindow", "BitBlt",
    ],
    "High-Risk Execution": [
        "ShellExecute", "WinExec", "CreateProcess",
        "cmd.exe", "powershell", "mshta", "wscript",
    ],
    "Anti-Debugging": [
        "IsDebuggerPresent", "CheckRemoteDebuggerPresent",
        "NtQueryInformationProcess",
    ],
    "Remote Desktop (RDP)": [
        "mstsc", "TermService", "rdpwrap", "TermSrv",
        "RDPCLIP", "rdpclip", "RDPDR", "3389",
        "WTSEnumerateSessions", "WTSQuerySessionInformation",
    ],
    "SSH/Remote Terminal": [
        "sshd", "libssh", "plink", "putty.exe",
        "WinSCP", "OpenSSH", "ssh-rsa", "authorized_keys",
        ".ssh/", "22/tcp",
    ],
}

ARCHIVE_EXTENSIONS = {".zip", ".tar", ".gz", ".bz2", ".xz", ".7z"}

SUSPICIOUS_EXTENSIONS = {
    ".exe", ".dll", ".sys",
    ".bat", ".cmd", ".ps1",
    ".vbs", ".vbe", ".js", ".jse",
    ".wsf", ".wsh", ".hta", ".scr",
    ".pif", ".com", ".lnk",
}

HIGH_ENTROPY   = 7.2
MAX_FILE_SIZE  = 2000000000000  * 1024 * 1024  # 2.097 EB, skip if exceeded

# Global results collector
all_results = []


# ──────────────────────────────────────────────
# Scan history (hash-based dedupe) — avoid rescanning unchanged files
# ──────────────────────────────────────────────

HISTORY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scan_history.json")


def _load_history() -> dict:
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_history(history: dict):
    try:
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"  ⚠️  Could not save scan history: {e}")


def _sha256_of_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def already_scanned(abs_path: str, data: bytes, history: dict):
    """
    Returns (skip: bool, file_hash: str).
    skip=True means this exact path+content was already scanned before
    (same hash on record) -> safe to skip.
    """
    file_hash = _sha256_of_bytes(data)
    prev = history.get(abs_path)
    if prev and prev.get("hash") == file_hash:
        return True, file_hash
    return False, file_hash


def mark_scanned(abs_path: str, file_hash: str, history: dict):
    history[abs_path] = {
        "hash": file_hash,
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


# ──────────────────────────────────────────────
# Optional: duplicate all console output into a .txt log file
# ──────────────────────────────────────────────

class _Tee:
    """Writes to multiple streams at once (e.g. real console + a log file)."""
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for s in self.streams:
            try:
                s.write(data)
            except Exception:
                pass

    def flush(self):
        for s in self.streams:
            try:
                s.flush()
            except Exception:
                pass


def enable_file_logging(log_path: str):
    """
    Call this once near the start of a run to make every print() go to BOTH
    the console (live, as before) AND append into a text log file.
    Does not change how anything is displayed on screen.
    """
    log_file = open(log_path, "a", encoding="utf-8")
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file.write(f"\n\n{'#'*70}\n# Scan run at {ts}\n{'#'*70}\n")
    sys.stdout = _Tee(sys.__stdout__, log_file)
    sys.stderr = _Tee(sys.__stderr__, log_file)


# ──────────────────────────────────────────────
# Utility Functions
# ──────────────────────────────────────────────

def calc_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    freq = [0] * 256
    for b in data:
        freq[b] += 1
    n = len(data)
    return -sum((f/n) * math.log2(f/n) for f in freq if f > 0)


def extract_strings(data: bytes, min_len=5) -> list:
    ascii_strs = re.findall(rb'[ -~]{%d,}' % min_len, data)
    uni_strs   = re.findall(rb'(?:[\x20-\x7e]\x00){%d,}' % min_len, data)
    result  = [s.decode('ascii',     errors='ignore') for s in ascii_strs]
    result += [s.decode('utf-16-le', errors='ignore') for s in uni_strs]
    return result


def scan_strings(strings: list) -> dict:
    hits = {}
    for s in strings:
        s_clean = s.strip()
        for category, apis in SUSPICIOUS_APIS.items():
            for api in apis:
                if api.lower() in s_clean.lower():
                    hits.setdefault(category, [])
                    entry = (api, s_clean[:70])
                    if entry not in hits[category]:
                        hits[category].append(entry)
    return hits


def is_archive(filename: str, data: bytes = None) -> bool:
    """Determine if a file is an archive (by extension + magic bytes)"""
    ext = Path(filename).suffix.lower()
    if ext in ARCHIVE_EXTENSIONS:
        return True
    # Additional magic byte check
    if data:
        if data[:2] == b'PK':  return True  # ZIP
        if data[:5] == b'7z\xbc\xaf\x27': return True  # 7z
        if data[:2] in (b'\x1f\x8b', b'BZ'): return True  # GZ / BZ2
    return False


# ──────────────────────────────────────────────
# Single File Analysis
# ──────────────────────────────────────────────

def analyze(display_name: str, data: bytes, source: str = "") -> dict:
    """Analyze the binary content of a file and return a structured result dict"""
    ext     = Path(display_name).suffix.lower()
    entropy = calc_entropy(data)
    is_pe   = data[:2] == b'MZ'

    result = {
        "name":      display_name,
        "source":    source,        # Which archive it came from (empty = direct file)
        "size":      len(data),
        "entropy":   entropy,
        "ext_bad":   ext in SUSPICIOUS_EXTENSIONS,
        "pe_issues": [],
        "str_hits":  {},
    }

    # PE deep analysis
    if is_pe and HAS_PEFILE:
        try:
            pe = pefile.PE(data=data)
            for sec in pe.sections:
                name = sec.Name.decode(errors='replace').strip('\x00')
                e = sec.get_entropy()
                if e > HIGH_ENTROPY:
                    result["pe_issues"].append(f"Section '{name}' entropy={e:.2f} → may contain encrypted payload")
            if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
                funcs = []
                for entry in pe.DIRECTORY_ENTRY_IMPORT:
                    for imp in entry.imports:
                        if imp.name:
                            funcs.append(imp.name.decode(errors='ignore'))
                for cat, hits in scan_strings(funcs).items():
                    for api, _ in hits:
                        result["pe_issues"].append(f"Imported API [{cat}]: {api}")
            if not getattr(pe, 'VS_VERSIONINFO', None):
                result["pe_issues"].append("No version info")
            try:
                sec_dir = pe.OPTIONAL_HEADER.DATA_DIRECTORY[
                    pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_SECURITY']
                ]
                if sec_dir.VirtualAddress == 0:
                    result["pe_issues"].append("No digital signature")
            except Exception:
                pass
            pe.close()
        except Exception as e:
            result["pe_issues"].append(f"PE parsing failed: {e}")

    # String scanning
    strings = extract_strings(data)
    result["str_hits"] = scan_strings(strings)

    # Embedded URLs
    urls = re.findall(r'https?://[^\s\x00"\'<>]{8,}', ' '.join(strings))
    for u in list(set(urls))[:5]:
        result["str_hits"].setdefault("Embedded URL", []).append((u, u))

    # Embedded IP addresses (potential C2 / remote-access targets)
    joined = ' '.join(strings)
    ip_candidates = re.findall(
        r'\b(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\b',
        joined
    )
    # Filter obvious noise: 0.0.0.0, 255.255.255.255, and things that are really version numbers (x.y.z.w where all parts < 20 and file has no other network indicators is still shown, just de-duped)
    junk = {"0.0.0.0", "255.255.255.255", "127.0.0.1"}
    ips = sorted(set(ip for ip in ip_candidates if ip not in junk))
    for ip in ips[:10]:
        result["str_hits"].setdefault("Embedded IP", []).append((ip, ip))

    return result


def risk_level(r: dict) -> str:
    score = 0
    if r["ext_bad"]:              score += 2
    if r["entropy"] > HIGH_ENTROPY: score += 2
    score += len(r["pe_issues"]) // 2
    for hits in r["str_hits"].values():
        score += len(hits)
    if score == 0:  return "✅ Safe"
    if score <= 2:  return "🟡 Low Risk"
    if score <= 6:  return "🟠 Medium Risk"
    return "🔴 High Risk"


def print_result(r: dict):
    risk = risk_level(r)
    kb   = r["size"] / 1024
    src  = f"  [{r['source']}]" if r["source"] else ""
    print(f"\n  {'─'*56}")
    print(f"  📄 {r['name']}{src}")
    print(f"     Size: {kb:.1f} KB  Entropy: {r['entropy']:.2f}  Risk: {risk}")
    if r["ext_bad"]:
        print(f"     ⚠️  Suspicious extension: {Path(r['name']).suffix}")
    if r["entropy"] > HIGH_ENTROPY:
        print(f"     ⚠️  High entropy → data may be encrypted/compressed")
    for issue in r["pe_issues"]:
        print(f"     🔬 {issue}")
    for cat, hits in r["str_hits"].items():
        if cat in ("Embedded URL", "Embedded IP"):
            icon = "🌐" if cat == "Embedded IP" else "🔗"
            for val, _ in hits[:5]:
                print(f"     {icon}  {cat}: {val}")
        else:
            for api, ctx in hits[:2]:
                print(f"     ⚠️  [{cat}] {api}  ← \"{ctx}\"")


# ──────────────────────────────────────────────
# Archive Extraction → Recursively Process Each File Inside
# ──────────────────────────────────────────────

def process_archive(path_or_name: str, data: bytes, depth: int, source_label: str):
    """Extract archive and recursively call process_item for each file inside"""
    ext = Path(path_or_name).suffix.lower()
    label = source_label or path_or_name

    # ZIP (including in-memory data)
    try:
        import io
        buf = io.BytesIO(data)
        if zipfile.is_zipfile(buf):
            buf.seek(0)
            with zipfile.ZipFile(buf, 'r') as zf:
                for info in zf.infolist():
                    if info.is_dir() or info.file_size > MAX_FILE_SIZE:
                        continue
                    inner_data = zf.read(info.filename)
                    process_item(info.filename, inner_data, depth + 1, label)
            return
    except Exception:
        pass

    # 7z
    if HAS_7Z and ext == '.7z':
        try:
            import io
            buf = io.BytesIO(data)
            with py7zr.SevenZipFile(buf, mode='r') as zf:
                file_infos = {f.filename: f for f in zf.list()}
                targets = [n for n, f in file_infos.items()
                           if f.uncompressed <= MAX_FILE_SIZE]
                if targets:
                    extracted = zf.read(targets)
                    for name, bio in extracted.items():
                        inner_data = bio.read() if hasattr(bio, 'read') else bio
                        process_item(name, inner_data, depth + 1, label)
            return
        except Exception:
            pass

    # TAR (requires temp file since tarfile doesn't support BytesIO for all formats)
    try:
        import io, tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(data)
            tmp_path = tmp.name
        with tarfile.open(tmp_path, 'r:*') as tf:
            for member in tf.getmembers():
                if not member.isfile() or member.size > MAX_FILE_SIZE:
                    continue
                f = tf.extractfile(member)
                if f:
                    process_item(member.name, f.read(), depth + 1, label)
        os.unlink(tmp_path)
        return
    except Exception:
        pass

    # If all fail, treat as a regular file
    result = analyze(path_or_name, data, source_label)
    all_results.append(result)


# ──────────────────────────────────────────────
# Core Router: Determine File Type and How to Handle It
# ──────────────────────────────────────────────

MAX_DEPTH = 5  # Maximum 5 levels of nested archive extraction to prevent infinite recursion

def process_item(name: str, data: bytes, depth: int = 0, source_label: str = ""):
    """
    Core routing function:
    - If archive → extract and recursively process each file inside
    - If regular file → analyze directly
    """
    if depth > MAX_DEPTH:
        print(f"  ⚠️  Nesting too deep, skipping: {name}")
        return

    indent = "  " * depth
    if is_archive(name, data):
        print(f"{indent}  📦 Extracting archive: {name}  ({len(data)/1024:.1f} KB)")
        process_archive(name, data, depth, source_label or name)
    else:
        print(f"{indent}  🔎 Analyzing: {name}")
        result = analyze(name, data, source_label)
        all_results.append(result)
        # heartbeat every 200 files so long scans don't look stuck
        if len(all_results) % 200 == 0:
            print(f"     ...{len(all_results)} files analyzed so far...")


# ──────────────────────────────────────────────
# Entry Point: Walk Folder
# ──────────────────────────────────────────────

def scan_folder(folder_path: str):
    all_results.clear()
    print(f"\n{'═'*60}")
    print(f"  📁 Scanning folder: {folder_path}")
    print(f"{'═'*60}\n")

    history = _load_history()

    # Collect all top-level files, then split into plain files vs archives
    all_paths = []
    for root, dirs, files in os.walk(folder_path):
        for fname in sorted(files):
            filepath = os.path.join(root, fname)
            if os.path.abspath(filepath) != os.path.abspath(__file__):
                all_paths.append(filepath)

    plain_items = []
    archive_items = []
    skipped_unchanged = 0
    for filepath in all_paths:
        try:
            size = os.path.getsize(filepath)
            if size > MAX_FILE_SIZE:
                print(f"  ⏭️  Skipping (too large {size//1024//1024}MB): {filepath}")
                continue
            rel = os.path.relpath(filepath, folder_path)
            with open(filepath, "rb") as f:
                data = f.read()

            abs_path = os.path.abspath(filepath)
            skip, file_hash = already_scanned(abs_path, data, history)
            if skip:
                skipped_unchanged += 1
                continue
            mark_scanned(abs_path, file_hash, history)

            if is_archive(rel, data):
                archive_items.append((rel, data))
            else:
                plain_items.append((rel, data))
        except Exception as e:
            print(f"  ❌ Unable to read: {filepath} ({e})")

    _save_history(history)

    if skipped_unchanged:
        print(f"  ⏭️  Skipped {skipped_unchanged} unchanged file(s) (same content as last scan)\n")
    print(f"  Found {len(plain_items)} plain file(s) and {len(archive_items)} archive(s) to scan\n")

    # Phase 1: plain / already-unzipped files first
    print(f"  ── Phase 1: Scanning unzipped/standalone files ({len(plain_items)}) ──")
    for idx, (rel, data) in enumerate(plain_items, start=1):
        print(f"  [{idx}/{len(plain_items)}] {rel}")
        process_item(rel, data, depth=0, source_label="")

    # Phase 2: archives
    print(f"\n  ── Phase 2: Scanning archive contents ({len(archive_items)}) ──")
    for idx, (rel, data) in enumerate(archive_items, start=1):
        print(f"  [{idx}/{len(archive_items)}] {rel}")
        process_item(rel, data, depth=0, source_label="")

    _print_summary(folder_path)


def scan_single_file(filepath: str):
    """Scan exactly one file (used by --file). Uses the same hash dedupe as scan_folder."""
    all_results.clear()
    history = _load_history()

    abs_path = os.path.abspath(filepath)
    with open(filepath, "rb") as f:
        data = f.read()

    skip, file_hash = already_scanned(abs_path, data, history)
    if skip:
        print(f"  ⏭️  Skipped (unchanged since last scan): {filepath}")
        return

    mark_scanned(abs_path, file_hash, history)
    _save_history(history)

    process_item(os.path.basename(filepath), data, depth=0)
    _print_summary(filepath)


# ──────────────────────────────────────────────
# Summary Output
# ──────────────────────────────────────────────

def _print_summary(label: str):
    unzipped = [r for r in all_results if not r["source"]]
    zipped   = [r for r in all_results if r["source"]]

    risky_unzipped = [r for r in unzipped if risk_level(r) != "✅ Safe"]
    risky_zipped   = [r for r in zipped   if risk_level(r) != "✅ Safe"]
    safe = len(all_results) - len(risky_unzipped) - len(risky_zipped)

    print(f"\n{'═'*60}")
    print(f"  📊 Scan complete: {label}")
    print(f"     Total {len(all_results)} files  |  Safe: {safe}")
    print(f"     📂 Unzipped/standalone scanned: {len(unzipped)}  (at risk: {len(risky_unzipped)})")
    print(f"     📦 Zip/archive contents scanned: {len(zipped)}  (at risk: {len(risky_zipped)})")
    print(f"{'═'*60}")

    order = ["✅ Safe", "🟡 Low Risk", "🟠 Medium Risk", "🔴 High Risk"]

    if risky_unzipped:
        print("\n  ── [Unzipped/Standalone] Files Requiring Attention ──")
        for r in sorted(risky_unzipped, key=lambda x: order.index(risk_level(x)), reverse=True):
            print_result(r)

    if risky_zipped:
        print("\n  ── [From Archives] Files Requiring Attention ──")
        for r in sorted(risky_zipped, key=lambda x: order.index(risk_level(x)), reverse=True):
            print_result(r)

    if not risky_unzipped and not risky_zipped:
        print("\n  ✅ No obvious threats detected")

    high   = sum(1 for r in all_results if risk_level(r) == "🔴 High Risk")
    medium = sum(1 for r in all_results if risk_level(r) == "🟠 Medium Risk")
    low    = sum(1 for r in all_results if risk_level(r) == "🟡 Low Risk")
    print(f"\n     🔴 High Risk: {high}  🟠 Medium Risk: {medium}  🟡 Low Risk: {low}  ✅ Safe: {safe}\n")

    if high > 0:
        print("  ⛔ High-risk files detected, do NOT execute!")
    elif medium > 0:
        print("  ⚠️  Medium-risk files detected, recommend further analysis in an isolated environment.")
    else:
        print("  ✅ No obvious threats detected. Recommend a second pass with antivirus software.")

    _print_network_summary()


def _print_network_summary():
    """Aggregate view of embedded IPs and RDP/SSH indicators across all scanned files."""
    ip_map = {}       # ip -> set of filenames it was found in
    rdp_ssh_hits = [] # (filename, category, api)

    for r in all_results:
        for cat, hits in r["str_hits"].items():
            if cat == "Embedded IP":
                for ip, _ in hits:
                    ip_map.setdefault(ip, set()).add(r["name"])
            elif cat in ("Remote Desktop (RDP)", "SSH/Remote Terminal"):
                for api, _ in hits:
                    rdp_ssh_hits.append((r["name"], cat, api))

    if not ip_map and not rdp_ssh_hits:
        return

    print(f"{'═'*60}")
    print("  🌐 Network / Remote-Access Indicators")
    print(f"{'═'*60}")

    if ip_map:
        print("\n  Embedded IP addresses found (verify manually — may include false positives):")
        for ip, files in sorted(ip_map.items()):
            names = ", ".join(list(files)[:3])
            more = f"  (+{len(files)-3} more files)" if len(files) > 3 else ""
            print(f"    • {ip}  ← {names}{more}")

    if rdp_ssh_hits:
        print("\n  RDP / SSH indicators found:")
        seen = set()
        for fname, cat, api in rdp_ssh_hits:
            key = (fname, cat, api)
            if key in seen:
                continue
            seen.add(key)
            print(f"    • [{cat}] {api}  ← {fname}")
    print()


# ──────────────────────────────────────────────
# main
# ──────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Archive/folder security scanner")
    parser.add_argument("--file", help="Scan a single file")
    parser.add_argument("--folder", help="Recursively scan a folder")
    parser.add_argument("target", nargs="?", help="(legacy) folder or file path, if --file/--folder not used")
    args = parser.parse_args()

    target = args.file or args.folder or args.target
    if not target:
        parser.print_help()
        sys.exit(1)

    # Duplicate all output into a text log next to this script (scan_log.txt)
    LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scan_log.txt")
    enable_file_logging(LOG_PATH)

    if not os.path.exists(target):
        print(f"❌ Path does not exist: {target}")
        sys.exit(1)

    if args.folder or (not args.file and os.path.isdir(target)):
        scan_folder(target)
    else:
        scan_single_file(target)
