# File Scanner -- Portable Path Update

## Overview

This update improves how the PowerShell watcher locates `scan.py`.

Previously:

``` powershell
$ScannerScript = "C:\Users\DM27\Desktop\test\New folder (2)\scan.py"
```

The path was hard-coded and depended on the original folder location.

The updated version uses:

``` powershell
$ScannerScript = Join-Path $PSScriptRoot "scan.py"
```

`$PSScriptRoot` points to the directory containing the currently running
`.ps1` script, while `Join-Path` safely combines that directory with
`scan.py`.

------------------------------------------------------------------------

## Previous Version

``` text
C:\Users\user\Desktop\test\New folder (2)\
├── scan.ps1
└── scan.py
```

If the project was moved to another location, the path inside `scan.ps1`
had to be changed manually.

------------------------------------------------------------------------

## Current Version

``` powershell
$ScannerScript = Join-Path $PSScriptRoot "scan.py"
```

For example:

``` text
D:\SecurityScanner\
├── scan.ps1
└── scan.py
```

When `scan.ps1` runs:

``` text
$PSScriptRoot
      ↓
D:\SecurityScanner

Join-Path $PSScriptRoot "scan.py"
      ↓
D:\SecurityScanner\scan.py
```

The project can therefore be moved without changing the absolute path to
`scan.py`.

------------------------------------------------------------------------

## Before vs After

  Feature                             Previous Version   Current Version
  ----------------------------------- ------------------ -----------------
  Scanner path                        Hard-coded         Dynamic
  Full path required                  Yes                No
  Depends on username                 Yes                No
  Moving project requires path edit   Yes                No
  Uses `$PSScriptRoot`                No                 Yes
  Uses `Join-Path`                    No                 Yes
  Better for Git/GitHub               Limited            Yes

------------------------------------------------------------------------

## Portable Project Structure

``` text
SecurityScanner\
├── scan.ps1
├── scan.py
├── start.vbs
├── scan_history.json
└── scan_log.txt
```

The important relationship is:

``` text
scan.ps1
   │
   │ $PSScriptRoot
   ▼
Project Directory
   │
   │ Join-Path
   ▼
scan.py
```

As long as `scan.ps1` and `scan.py` keep the expected relative structure,
the parent project directory can be moved.

------------------------------------------------------------------------

## Why This Change Matters

Instead of telling PowerShell:

> `scan.py` exists at one specific machine-dependent location.

the script now effectively says:

> Find `scan.py` relative to the directory containing this PowerShell
> script.

Benefits include:

-   Easier project relocation
-   Easier deployment to another computer
-   No username-specific scanner path
-   Better Git/GitHub portability
-   Less configuration after copying the project

------------------------------------------------------------------------

## Relation to the Scanner

This update changes path handling, not the Python scanner's detection
logic.

The scanner continues to provide static analysis, archive inspection,
risk scoring, and scan-history handling. The newer scanner also uses
file paths and SHA-256 hashes to avoid rescanning unchanged files.

``` text
PowerShell Watcher
       │
       ▼
Locate scan.py dynamically
       │
       ▼
Python Scanner
       │
       ├── SHA-256 / scan history
       ├── Static analysis
       ├── Archive analysis
       └── Risk summary
```

------------------------------------------------------------------------

## Current Configuration

``` powershell
$WatchFolder = "C:\Users\DM27\Desktop\scan"
$ScannerScript = Join-Path $PSScriptRoot "scan.py"
```

Here, the Python scanner path is portable, while the watch-folder path
is still explicitly configured.

------------------------------------------------------------------------

## Possible Next Improvement

If the monitored folder is also stored inside the project:

``` text
SecurityScanner\
├── scan.ps1
├── scan.py
└── scan\
```

both paths could become relative:

``` powershell
$WatchFolder = Join-Path $PSScriptRoot "scan"
$ScannerScript = Join-Path $PSScriptRoot "scan.py"
```

This would make the project more fully portable.

------------------------------------------------------------------------

## Version Note

### Portable Path Update

Changed from:

``` powershell
$ScannerScript = "C:\Users\DM27\Desktop\test\New folder (2)\scan.py"
```

to:

``` powershell
$ScannerScript = Join-Path $PSScriptRoot "scan.py"
```

**Result:** The PowerShell watcher can locate `scan.py` based on its own
script directory instead of relying on a machine-specific absolute path.
