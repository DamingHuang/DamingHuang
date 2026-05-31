import os
import re
import sys
import math
import zipfile
import tarfile
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
        if cat == "Embedded URL":
            continue
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

    if is_archive(name, data):
        indent = "  " * depth
        print(f"{indent}  📦 Extracting archive: {name}")
        process_archive(name, data, depth, source_label or name)
    else:
        result = analyze(name, data, source_label)
        all_results.append(result)


# ──────────────────────────────────────────────
# Entry Point: Walk Folder
# ──────────────────────────────────────────────

def scan_folder(folder_path: str):
    print(f"\n{'═'*60}")
    print(f"  📁 Scanning folder: {folder_path}")
    print(f"{'═'*60}\n")

    for root, dirs, files in os.walk(folder_path):
        for fname in sorted(files):
            filepath = os.path.join(root, fname)
            try:
                size = os.path.getsize(filepath)
                if size > MAX_FILE_SIZE:
                    print(f"  ⏭️  Skipping (too large {size//1024//1024}MB): {filepath}")
                    continue
                with open(filepath, "rb") as f:
                    data = f.read()
                rel = os.path.relpath(filepath, folder_path)
                process_item(rel, data, depth=0, source_label="")
            except Exception as e:
                print(f"  ❌ Unable to read: {filepath} ({e})")

    _print_summary(folder_path)


# ──────────────────────────────────────────────
# Summary Output
# ──────────────────────────────────────────────

def _print_summary(label: str):
    # Only print files with risk (no need to show all safe files)
    risky = [r for r in all_results if risk_level(r) != "✅ Safe"]
    safe  = len(all_results) - len(risky)

    print(f"\n{'═'*60}")
    print(f"  📊 Scan complete: {label}")
    print(f"     Total {len(all_results)} files  |  At risk: {len(risky)}  |  Safe: {safe}")
    print(f"{'═'*60}")

    if risky:
        print("\n  ── Files Requiring Attention ──")
        for r in sorted(risky, key=lambda x: ["✅ Safe","🟡 Low Risk","🟠 Medium Risk","🔴 High Risk"].index(risk_level(x)), reverse=True):
            print_result(r)
    else:
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


# ──────────────────────────────────────────────
# main
# ──────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scan.py <folder path>")
        print("       python scan.py <archive.zip/.7z>")
        sys.exit(1)

    target = sys.argv[1]
    if not os.path.exists(target):
        print(f"❌ Path does not exist: {target}")
        sys.exit(1)

    if os.path.isdir(target):
        scan_folder(target)
    else:
        # Single archive file also supported
        with open(target, "rb") as f:
            data = f.read()
        process_item(os.path.basename(target), data, depth=0)
        _print_summary(target)
