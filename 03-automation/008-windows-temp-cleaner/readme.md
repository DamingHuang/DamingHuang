# Windows System Cleanup Tool

A powerful PowerShell script that automatically cleans temporary Windows files, forcibly removes locked files by terminating blocking processes, and sends real-time alerts via Discord.

## 🎯 Purpose

This tool solves a common Windows administration challenge: **stuck temporary files that cannot be deleted because they're in use by running processes.**

Instead of manually hunting down which process is locking a file, this script:
1. Automatically identifies the blocking process
2. Safely terminates non-critical processes
3. Retries the deletion
4. Falls back to scheduling deletion on reboot if needed

## ✨ Key Features

### 🔒 Force Delete Locked Files
- Detects files locked by running processes using Sysinternals Handle.exe
- Identifies and terminates the specific process holding the file lock
- Automatically retries deletion after process termination

### 🛡️ System Process Protection
- **Never terminates** critical Windows processes:
  - System, smss, csrss, wininit, winlogon, lsass, services
- Ensures system stability while still cleaning aggressively

### 📝 Comprehensive Logging
- Creates timestamped log files with detailed operation history
- Color-coded console output for easy monitoring
- Logs include: timestamps, operations performed, success/failure status

### 🔔 Discord Integration
- Sends real-time alerts to Discord via webhook
- Different alert types:
  - ✅ **Success** - Files cleaned successfully
  - ❌ **Error** - Cleanup failed for specific items
  - 🔁 **Reboot Required** - Files scheduled for next reboot

### 🔄 Multiple Deletion Strategies
The script uses a progressive approach:

| Attempt | Strategy | Success Rate |
|---------|----------|--------------|
| 1 | Direct deletion | Handles most files |
| 2 | Kill locking process + retry | Handles user-process locked files |
| 3 | Schedule on reboot (registry) | Handles system-locked files |

### 🚀 Self-Contained
- Automatically downloads Sysinternals Handle.exe if missing
- Auto-elevates to administrator privileges
- No manual dependencies to install

## 🧹 What It Cleans

| Path | What Gets Deleted |
|------|-------------------|
| `C:\Windows\TEMP\*` | System temporary files (setup logs, crash dumps, etc.) |
| `C:\Windows\Prefetch\*` | Windows prefetch cache (can grow to hundreds of MB) |
| `%LOCALAPPDATA%\Temp\*` | User application temporary files (browser caches, installer leftovers) |

## 🖥️ How It Works
Start
│
├─→ Elevate to Administrator
│
├─→ Download/Verify handle.exe
│
├─→ For each target folder:
│ │
│ ├─→ Try direct deletion
│ │ │
│ │ ├─→ Success → Log ✓
│ │ └─→ Fail (locked file) → Continue
│ │
│ ├─→ Identify locking process using handle.exe
│ │
│ ├─→ Is process system-critical?
│ │ │
│ │ ├─→ Yes → Skip (protected)
│ │ └─→ No → Terminate process
│ │
│ ├─→ Wait 1 second
│ │
│ ├─→ Retry deletion
│ │ │
│ │ ├─→ Success → Log ✓
│ │ └─→ Still fails → Schedule for reboot
│ │
│ └─→ Log result
│
└─→ Send Discord alert with summary
