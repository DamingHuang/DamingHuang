
# Shared Workstation Maintenance Script

## 🖥️ Project Overview

**Script Name:** `shared-workstation-maintenance.ps1`  
**Purpose:** Automatically clears temporary files from public user folders on shared workstations  
**Use Case:** Organizations with shared computers (libraries, labs, classrooms, reception areas)  
**Deployment:** Designed to run at user sign-off or via scheduled tasks  

## 🎯 Business Problem Solved

In shared workstation environments, users often leave personal files, downloads, and temporary data in public folders. This script ensures that each new user starts with a clean environment, improving:

- **Privacy** - Prevents accidental data exposure between users
- **Performance** - Reduces disk clutter and improves system speed
- **Security** - Removes potential malware vectors in temporary folders
- **Consistency** - Provides uniform starting state for all users

## 📁 Target Folders Cleaned

The script systematically cleans these public folders:

- `C:\Users\Public\Desktop`
- `C:\Users\Public\Downloads`
- `C:\Users\Public\Documents`
- `C:\Users\Public\Pictures`
- `C:\Users\Public\Videos`

## 🚀 Deployment Methods

### Option 1: Group Policy Logoff Script (Recommended)

```batch
@echo off
powershell.exe -ExecutionPolicy Bypass -File "\\server\scripts\shared-workstation-maintenance.ps1"
```

**GPO Configuration:**
- Computer/User Configuration → Windows Settings → Scripts → Logoff
- Add batch file calling PowerShell script
- Works reliably for domain-joined workstations

### Option 2: Scheduled Task (For Non-Domain)

```powershell
# Creates task that runs on user logoff
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File C:\Scripts\cleanup.ps1"
$trigger = New-ScheduledTaskTrigger -AtLogOff
Register-ScheduledTask -TaskName "CleanPublicFolders" -Action $action -Trigger $trigger -User "SYSTEM"
```

### Option 3: Manual Testing

```powershell
# Run with elevated privileges for testing
powershell.exe -ExecutionPolicy Bypass -File "shared-workstation-maintenance.ps1"
```

## 🔧 Technical Details

### Core Script

```powershell
# Clean Public user folders
$public = "C:\Users\Public"
$Publicfolders = @("Desktop", "Downloads", "Documents", "Pictures", "Videos")

foreach ($Publicfolder in $Publicfolders) {
    $Publicpath = Join-Path $public $Publicfolder
    if (Test-Path $Publicpath) {
        Remove-Item "$Publicpath\*" -Recurse -Force -ErrorAction SilentlyContinue
    } else { 
        Add-Content $logFile "Path does not exist: $Publicpath"
    }
}

# Log completion
Add-Content $logFile "Script finished at $(Get-Date)"
```

### Features

1. **Recursive Cleaning** - Removes all files and subfolders within target directories
2. **Error Handling** - Silently continues on permission or locked file errors
3. **Path Validation** - Checks if each folder exists before attempting cleanup
4. **Logging** - Records script execution and any missing paths
5. **Force Flag** - Overrides read-only and hidden file attributes

 

 
---
**Category:** Automation & Maintenance | **Tags:** #Windows #PowerShell #SharedWorkstation #Cleanup #ITAutomation
