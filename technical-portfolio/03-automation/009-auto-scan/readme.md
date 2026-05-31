# auto-scan

A security scanning tool that analyzes files and archives for malware indicators before execution.

## Files

| File | Description |
|------|-------------|
| `scan.py` | Core scanner — analyzes folders and archives recursively |
| `start.ps1` | Auto-installs dependencies and runs the scan |
| `start.bat` | Double-click launcher for Windows |

## Usage

**Double-click** `start.bat` — it will:
1. Check if `pefile` and `py7zr` are installed, and install them if not
2. Automatically scan the current folder
3. Keep the window open so you can read the results

Or run manually:

```powershell
python scan.py <folder path>
python scan.py <archive.zip>
python scan.py .
```

## What It Scans

- **Archives** — ZIP, TAR, TAR.GZ, TAR.BZ2, TAR.XZ, 7Z (recursively, up to 5 levels deep)
- **PE files** — EXE, DLL, SYS (section entropy, import table, digital signature)
- **All files** — string scanning, embedded URLs, suspicious extensions

## Risk Levels

| Level | Meaning |
|-------|---------|
| ✅ Safe | No indicators found |
| 🟡 Low Risk | Minor indicators (suspicious extension or slightly high entropy) |
| 🟠 Medium Risk | Multiple indicators, review recommended |
| 🔴 High Risk | Strong malware indicators — do not execute |

## Detection Rules

- **Suspicious APIs** — network, registry, process injection, keylogging, anti-debugging
- **High entropy** (> 7.2) — data may be encrypted or packed
- **Suspicious extensions** — `.exe .dll .ps1 .bat .vbs .js .lnk` and more
- **PE analysis** — section entropy, import table, missing version info, no digital signature
- **Embedded URLs** — detects hardcoded network addresses

## Dependencies

```
pip install pefile py7zr
```

> Installed automatically by `start.bat` if not present.
