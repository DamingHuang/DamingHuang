# AWS AD Lab — Phase 4: Active Directory Group Policy Configuration (Offline Logoff Script)

> **How to read this guide:**
> - **Field** — the exact label or setting you are configuring.
> - **Value / Your Entry** — what to type or select. Suggested names shown as examples — fill in your own where indicated.
> - Scripts are shown on the line **below** the description table.
> - Anywhere you see `"your-value-here"` inside a script — **replace it with your own value** before running.

---

## 4.1 Create Required PowerShell Scripts on the Domain Controller

All scripts are stored in the SYSVOL share so they are automatically available to domain-joined machines.

---

### 4.1.1 Create `deploy-logoff-monitor.ps1` — Startup Script

> This script runs once per machine at startup. It creates local folders, copies the cleanup script from SYSVOL, copies the monitor template, and registers a scheduled task.

| Field | Value / Your Entry |
|---|---|
| **Script file name** | `deploy-logoff-monitor.ps1` *(keep this name — it is referenced in the GPO startup entry)* |
| **GPO name** | `PublicPolicy` *(e.g. `"MyLab-Policy"` — must match your GPO's actual name exactly)* |
| **GPO GUID** | Auto-resolved from GPO name *(no manual entry needed — script fetches it)* |
| **Domain name (SYSVOL paths)** | `yourdomainame.com` *(replace every occurrence with your actual domain, e.g. `adlab.local`)* |
| **Local script folder** | `C:\Scripts\Logoff` *(e.g. `C:\LabScripts\Logoff` — used on every client machine)* |
| **Scheduled task name** | `UserProfileLogoffMonitor` *(e.g. `"LabLogoffMonitor"` — must be consistent across all scripts)* |
| **Script save path** | `\\yourdomainame.com\SYSVOL\yourdomainame.com\Policies\{GPO-GUID}\Machine\Scripts\Startup\deploy-logoff-monitor.ps1` |

```powershell
# deploy-logoff-monitor.ps1
# GPO Computer Startup Script – runs at machine startup

$gpoName = "PublicPolicy"                          # Replace with your GPO name
$gpoGuid = (Get-GPO -Name $gpoName).Id
$localDir = "C:\Scripts\Logoff"                    # Replace with your preferred local folder path
$localScript = "$localDir\userprofile.ps1"
$monitorScript = "$localDir\logoff-monitor.ps1"
$monitorTemplate = "\\yourdomainame.com\SYSVOL\yourdomainame.com\Scripts\logoff-monitor.ps1"   # Replace yourdomainame.com
$taskName = "UserProfileLogoffMonitor"             # Replace with your preferred task name

Write-Host "=== Deploying Logoff Monitor ===" -ForegroundColor Cyan

# Step 1: Create local folder
if (!(Test-Path $localDir)) {
    New-Item -ItemType Directory -Path $localDir -Force | Out-Null
    Write-Host "✓ Created folder: $localDir"
}

# Step 2: Copy userprofile.ps1 from SYSVOL
$fullSysvolPath = "\\yourdomainame.com\SYSVOL\yourdomainame.com\Policies\{$gpoGuid}\User\Scripts\Logoff"   # Replace yourdomainame.com
if (Test-Path $fullSysvolPath) {
    $sourceFile = "$fullSysvolPath\userprofile.ps1"
    if (Test-Path $sourceFile) {
        Copy-Item $sourceFile -Destination $localScript -Force
        Write-Host "✓ userprofile.ps1 copied"
    } else {
        Write-Host "✗ userprofile.ps1 not found in SYSVOL"
        exit 1
    }
} else {
    Write-Host "✗ SYSVOL path not found: $fullSysvolPath"
    exit 1
}

# Step 3: Create monitor script from template
if (Test-Path $monitorTemplate) {
    $monitorContent = Get-Content -Path $monitorTemplate -Raw
    Set-Content -Path $monitorScript -Value $monitorContent -Force
    Write-Host "✓ logoff-monitor.ps1 created"
} else {
    Write-Host "✗ Monitor template not found: $monitorTemplate"
    exit 1
}

# Step 4: Create scheduled task (logon trigger – will be upgraded to event trigger in Phase 4.3)
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -NoProfile -File `"$monitorScript`""
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Hours 24)
$principal = New-ScheduledTaskPrincipal -GroupId "BUILTIN\Users" -RunLevel Limited

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null
Write-Host "✓ Scheduled task created (logon trigger) – upgrade to event trigger in Phase 4.3"

Write-Host "`n=== Deployment Complete ==="
```

---

### 4.1.2 Create `logoff-monitor.ps1` — Monitor Template

> This script runs in the background after user logon. It waits in a loop; when the process is killed at logoff, it triggers the cleanup script.

| Field | Value / Your Entry |
|---|---|
| **Script file name** | `logoff-monitor.ps1` *(keep this name — referenced by the deploy script)* |
| **Script save path** | `\\yourdomainame.com\SYSVOL\yourdomainame.com\Scripts\logoff-monitor.ps1` *(replace `yourdomainame.com` with your domain)* |
| **Cleanup script path** | `C:\Scripts\Logoff\userprofile.ps1` *(must match `$localScript` in the deploy script above)* |

```powershell
# logoff-monitor.ps1
# Background monitor – runs at user logon, triggers cleanup on PowerShell exit

param([switch]$RunCleanup)

if ($RunCleanup) {
    & "C:\Scripts\Logoff\userprofile.ps1"    # Replace path if you changed $localScript above
    exit
}

# Simple loop – killed by system at logoff, which triggers the cleanup
while ($true) {
    Start-Sleep -Seconds 300
}
```

---

### 4.1.3 Create `userprofile.ps1` — Cleanup Script

> This script performs the actual cleanup of the Public user's profile folders. It uses absolute paths so it works correctly when run as SYSTEM.

| Field | Value / Your Entry |
|---|---|
| **Script file name** | `userprofile.ps1` *(keep this name — referenced by both deploy and monitor scripts)* |
| **Script save path** | `\\yourdomainame.com\SYSVOL\yourdomainame.com\Policies\{GPO-GUID}\User\Scripts\Logoff\userprofile.ps1` *(replace `yourdomainame.com` and `{GPO-GUID}` with your values)* |
| **Public user profile path** | `C:\Users\yourprofile` *(replace `yourprofile` with your actual profile folder name, e.g. `C:\Users\public.adlab`)* |
| **Log file path** | `C:\Users\yourprofile\cleanup.log` *(replace to match profile path above)* |
| **Folders to clean** | `Desktop, Downloads, Documents, Pictures, Videos` *(add or remove folder names as needed)* |

```powershell
# userprofile.ps1
# Cleanup script – clears profile folders for the Public user on logoff

$public = "C:\Users\yourprofile"            # Replace yourprofile with your actual profile folder name
$logFile = "C:\Users\yourprofile\cleanup.log"   # Replace to match above
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

$logDir = Split-Path $logFile -Parent
if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

Add-Content $logFile "[$timestamp] Starting cleanup - User: Public"

$Publicfolders = @("Desktop", "Downloads", "Documents", "Pictures", "Videos")   # Edit list as needed
$cleanedCount = 0

foreach ($Publicfolder in $Publicfolders) {
    $Publicpath = Join-Path $public $Publicfolder
    if (Test-Path $Publicpath) {
        $files = Get-ChildItem "$Publicpath\*" -File -Recurse -ErrorAction SilentlyContinue
        $fileCount = ($files | Measure-Object).Count
        Remove-Item "$Publicpath\*" -Recurse -Force -ErrorAction SilentlyContinue
        Add-Content $logFile "    Cleaned $Publicfolder : $fileCount file(s)"
        $cleanedCount++
    } else {
        Add-Content $logFile "    Path does not exist: $Publicpath"
    }
}

Add-Content $logFile "[$timestamp] Cleanup completed, processed $cleanedCount folders"
Write-Host "Cleanup completed. Log file: $logFile"
```

---

## 4.2 Configure Group Policy

### 4.2.1 Create or Edit the GPO

| Step | Field | Value / Your Entry |
|---|---|---|
| 1 | **Console** | Open **Group Policy Management Console** on the Domain Controller |
| 2 | **Navigate to** | Group Policy Objects |
| 3 | **Action** | Right-click → **New** (or right-click existing GPO → **Edit**) |
| 4 | **GPO name** | `PublicPolicy` *(e.g. `"MyLab-Policy"` — must match `$gpoName` in the deploy script)* |
| 5 | **Scope / Link** | Link to the OU containing target client computers, e.g. `OU=Computers,DC=yourdomainame,DC=com` *(replace with your OU and domain)* |

---

### 4.2.2 Add the Computer Startup Script

| Step | Field | Value / Your Entry |
|---|---|---|
| 1 | **Navigate to** | Computer Configuration → Policies → Windows Settings → Scripts → Startup |
| 2 | **Action** | Double-click **Startup** → click the **PowerShell Scripts** tab |
| 3 | **Click** | **Add** |
| 4 | **Script Name** | `powershell.exe` |
| 5 | **Script Parameters** | `-ExecutionPolicy Bypass -File \\yourdomainame.com\SYSVOL\yourdomainame.com\Policies\{GPO-GUID}\Machine\Scripts\Startup\deploy-logoff-monitor.ps1` *(replace `yourdomainame.com` and `{GPO-GUID}`)* |
| 6 | **Click** | **OK** twice to save |

---

### 4.2.3 Optional — Keep User Logoff Script as Online Fallback

| Field | Value / Your Entry |
|---|---|
| **Navigate to** | User Configuration → Policies → Windows Settings → Scripts → Logoff |
| **Purpose** | Optional online fallback — not required for offline operation |
| **Action** | Leave existing logoff script in place if present, or skip this section |

---

## 4.3 Upgrade Scheduled Task to Event Trigger (First Client Only)

> The deploy script (Step 4.1.1) creates a logon-triggered task. For true logoff triggering, replace it with an event-based task using the XML method below. Run this **once on your first client as Administrator**.

| Field | Value / Your Entry |
|---|---|
| **Run on** | First client machine *(e.g. `SURFTEA` — the first machine you are testing on)* |
| **Run as** | Local Administrator |
| **Old task name** | `UserProfileLogoffMonitor` *(must match `$taskName` in the deploy script)* |
| **Cleanup script path in XML** | `C:\Scripts\Logoff\userprofile.ps1` *(replace if you changed the local folder path)* |
| **Event trigger** | Windows Logon event ID `7002` from provider `Microsoft-Windows-Winlogon` *(do not change unless you know what you are doing)* |
| **Run as identity** | `S-1-5-18` = SYSTEM account *(runs with highest privilege — required for profile cleanup)* |
| **Execution time limit** | `PT10M` = 10 minutes *(increase if cleanup takes longer on large profiles)* |

```powershell
# Delete the old logon-triggered task created by the deploy script
Unregister-ScheduledTask -TaskName "UserProfileLogoffMonitor" -Confirm:$false -ErrorAction SilentlyContinue

# Create event-triggered task via XML
$xmlContent = @'
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>2026-02-17T00:00:00</Date>
    <Description>Clean up user profile on logoff</Description>
  </RegistrationInfo>
  <Triggers>
    <EventTrigger>
      <Enabled>true</Enabled>
      <Subscription>&lt;QueryList&gt;&lt;Query Id="0" Path="System"&gt;&lt;Select Path="System"&gt;*[System[Provider[@Name='Microsoft-Windows-Winlogon'] and (EventID=7002)]]&lt;/Select&gt;&lt;/Query&gt;&lt;/QueryList&gt;</Subscription>
    </EventTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-18</UserId>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <ExecutionTimeLimit>PT10M</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>powershell.exe</Command>
      <Arguments>-ExecutionPolicy Bypass -WindowStyle Hidden -NoProfile -File "C:\Scripts\Logoff\userprofile.ps1"</Arguments>
    </Exec>
  </Actions>
</Task>
'@

# Save as UTF-16 (required for schtasks /XML)
[System.IO.File]::WriteAllText("$env:TEMP\logoff-task.xml", $xmlContent, [System.Text.Encoding]::Unicode)

# Register the task
schtasks /Create /XML "$env:TEMP\logoff-task.xml" /TN "UserProfileLogoffMonitor" /F   # Replace task name if you changed it

# Clean up temp file
Remove-Item "$env:TEMP\logoff-task.xml" -ErrorAction SilentlyContinue

Write-Host "Event trigger task created successfully!" -ForegroundColor Green
```

> 📝 **Note:** This step is only needed on the first client if you have not yet updated the deploy script with the XML method. Once you update `deploy-logoff-monitor.ps1` (see Phase 4.5), all subsequent clients will receive the correct event-triggered task automatically via GPO.

---

## 4.4 Verification on First Client

| Step | What to Run | Expected Result |
|---|---|---|
| 1 | Run cleanup script manually | No errors, log file created |
| 2 | Read the log file | Shows cleaned folder names and file counts |
| 3 | Check scheduled task info | Task exists and `LastRunTime` is populated |
| 4 | Check task trigger type | Should show `EventTrigger` with the Winlogon subscription |
| 5 | Real logoff test | Log off, log back on, confirm log file is updated |

```powershell
# 1. Run cleanup script manually to confirm it works
powershell -ExecutionPolicy Bypass -File "C:\Scripts\Logoff\userprofile.ps1"

# 2. Read the log file
Get-Content "C:\Users\yourprofile\cleanup.log"    # Replace yourprofile with your actual profile folder name

# 3. Check scheduled task status
Get-ScheduledTask -TaskName "UserProfileLogoffMonitor" | Get-ScheduledTaskInfo    # Replace task name if changed

# 4. Confirm event trigger is set
$task = Get-ScheduledTask -TaskName "UserProfileLogoffMonitor"    # Replace task name if changed
$task.Triggers    # Should show EventTrigger with Subscription property
```

---

## 4.5 Automate Event Trigger for All Clients

> Replace **Step 4** inside `deploy-logoff-monitor.ps1` with the XML creation code below. After this update, the GPO will push the correct event-triggered task to every client automatically — no manual intervention needed.

| Field | Value / Your Entry |
|---|---|
| **Task name** | `UserProfileLogoffMonitor` *(must match `$taskName` variable at the top of the deploy script)* |
| **Cleanup script path in XML** | `C:\Scripts\Logoff\userprofile.ps1` *(replace if you changed the local folder path)* |
| **Execution time limit** | `PT10M` = 10 minutes *(adjust if needed)* |

```powershell
# Step 4 (updated): Create scheduled task with event trigger (logoff)
$taskName = "UserProfileLogoffMonitor"    # Replace with your task name if different
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

$xmlContent = @'
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>{0}</Date>
    <Description>Clean up user profile on logoff</Description>
  </RegistrationInfo>
  <Triggers>
    <EventTrigger>
      <Enabled>true</Enabled>
      <Subscription>&lt;QueryList&gt;&lt;Query Id="0" Path="System"&gt;&lt;Select Path="System"&gt;*[System[Provider[@Name='Microsoft-Windows-Winlogon'] and (EventID=7002)]]&lt;/Select&gt;&lt;/Query&gt;&lt;/QueryList&gt;</Subscription>
    </EventTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-18</UserId>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <ExecutionTimeLimit>PT10M</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>powershell.exe</Command>
      <Arguments>-ExecutionPolicy Bypass -WindowStyle Hidden -NoProfile -File "C:\Scripts\Logoff\userprofile.ps1"</Arguments>
    </Exec>
  </Actions>
</Task>
'@ -f (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")

$xmlContent | Out-File -FilePath "$env:TEMP\logoff-task.xml" -Encoding utf8
schtasks /Create /XML "$env:TEMP\logoff-task.xml" /TN $taskName /F
Remove-Item "$env:TEMP\logoff-task.xml" -Force
Write-Host "✓ Scheduled task (event trigger) created"
```

---

## 4.6 Final Validation Across Multiple Clients

| Step | Action | Expected Result |
|---|---|---|
| 1 | On each client, run: `gpupdate /force` | Policy update completes without errors |
| 2 | Reboot the client | Startup script runs, local files are deployed |
| 3 | Check that local files exist | `C:\Scripts\Logoff\userprofile.ps1` and `logoff-monitor.ps1` both present |
| 4 | Check scheduled task | `UserProfileLogoffMonitor` exists with event trigger |
| 5 | Offline test | Disconnect network → log off → log back on → check `cleanup.log` is updated |

```powershell
# Force Group Policy update on the client
gpupdate /force
```

---

## 4.7 Copy Validated Script to SYSVOL

> After confirming the cleanup script works correctly on the first client, copy it to SYSVOL so all other domain computers receive the validated version via Group Policy.
> Run these commands with **Domain Administrator credentials** — from the first client or any machine with network access to both the client and the Domain Controller.

| Field | Value / Your Entry |
|---|---|
| **Source machine name** | `SURFTEA` *(replace with your first client's actual computer name)* |
| **Source path** | `\\SURFTEA\C$\Scripts\Logoff\userprofile.ps1` *(replace `SURFTEA` and path if different)* |
| **Destination SYSVOL path** | `\\yourdomainame.com\SYSVOL\yourdomainame.com\Policies\{GPO-GUID}\User\Scripts\Logoff\userprofile.ps1` *(replace `yourdomainame.com` and `{GPO-GUID}`)* |
| **Expected output** | `✅ Script successfully copied to SYSVOL` |

```powershell
# 1. Copy the validated script from first client to SYSVOL
Copy-Item "\\SURFTEA\C$\Scripts\Logoff\userprofile.ps1" `
    -Destination "\\yourdomainame.com\SYSVOL\yourdomainame.com\Policies\{GPO-GUID}\User\Scripts\Logoff\userprofile.ps1" `
    -Force
# Replace: SURFTEA → your first client name
# Replace: yourdomainame.com → your actual domain name
# Replace: {GPO-GUID} → your GPO's actual GUID (find it in GPMC under Group Policy Objects)

# 2. Verify the file was copied successfully
$destPath = "\\yourdomainame.com\SYSVOL\yourdomainame.com\Policies\{GPO-GUID}\User\Scripts\Logoff\userprofile.ps1"
# Replace yourdomainame.com and {GPO-GUID} above before running
if (Test-Path $destPath) {
    Write-Host "✅ Script successfully copied to SYSVOL" -ForegroundColor Green
} else {
    Write-Host "❌ Copy failed – check network connectivity and permissions" -ForegroundColor Red
}
```

---

## Phase 4 — Master Resource Log

Fill this in as you complete each section:

| Resource | Suggested Name / Value | Your Custom Value |
|---|---|---|
| GPO name | `PublicPolicy` | |
| GPO GUID *(from GPMC)* | `{GPO-GUID}` | `{` `}` |
| Domain name *(used in all SYSVOL paths)* | `yourdomainame.com` | |
| Target OU path | `OU=Computers,DC=yourdomainame,DC=com` | |
| Local script folder on clients | `C:\Scripts\Logoff` | |
| Scheduled task name | `UserProfileLogoffMonitor` | |
| Public user profile path | `C:\Users\yourprofile` | |
| Cleanup log file path | `C:\Users\yourprofile\cleanup.log` | |
| First client computer name | `SURFTEA` | |
| Deploy script SYSVOL path | `\\domain\SYSVOL\domain\Policies\{GUID}\Machine\Scripts\Startup\` | |
| Cleanup script SYSVOL path | `\\domain\SYSVOL\domain\Policies\{GUID}\User\Scripts\Logoff\` | |
| Monitor template SYSVOL path | `\\domain\SYSVOL\domain\Scripts\logoff-monitor.ps1` | |
