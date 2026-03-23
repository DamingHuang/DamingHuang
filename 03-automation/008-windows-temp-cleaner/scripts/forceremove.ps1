# ============================================================
# Auto-Elevate to Administrator
# ============================================================
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process powershell -Verb RunAs -ArgumentList "-File `"$PSCommandPath`""
    exit
}

# ============================================================
# Global Log Setup
# ============================================================
# Auto-create log folder next to the script, fallback to Desktop
$global:ScriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { "$env:USERPROFILE\Desktop\scripts\alert\part1" }
if (-not (Test-Path $global:ScriptDir)) { New-Item -ItemType Directory -Path $global:ScriptDir -Force | Out-Null }
$global:LogFile = "$($global:ScriptDir)\cleanup_log_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"

function Write-Log {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logLine   = "$timestamp - $Message"
    Write-Host $logLine -ForegroundColor $Color
    Add-Content -Path $global:LogFile -Value $logLine
}

# ============================================================
# Download handle.exe
# ============================================================
function Get-HandleExe {
    $inPath = Get-Command "handle.exe" -ErrorAction SilentlyContinue
    if ($inPath) { return $inPath.Source }

    $local = Join-Path $global:ScriptDir "handle.exe"
    if (Test-Path $local) { return $local }

    Write-Log "📥 handle.exe not found, downloading..." "Yellow"
    try {
        $zipPath = Join-Path $env:TEMP "Handle.zip"
        Invoke-WebRequest -Uri "https://download.sysinternals.com/files/Handle.zip" `
                          -OutFile $zipPath -UseBasicParsing -TimeoutSec 30
        Expand-Archive -Path $zipPath -DestinationPath $global:ScriptDir -Force
        Remove-Item $zipPath -Force
        $handlePath = Join-Path $global:ScriptDir "handle.exe"
        & $handlePath -accepteula | Out-Null
        Write-Log "✅ handle.exe downloaded successfully" "Green"
        return $handlePath
    }
    catch {
        Write-Log "❌ Download failed: $($_.Exception.Message)" "Red"
        return $null
    }
}

# ============================================================
# Core Delete Function
# ============================================================
function Remove-WithForce {
    param([string[]]$Paths)

    $handleExe = Get-HandleExe

    foreach ($Path in $Paths) {
        Write-Log "🗂️  Processing: $Path" "Cyan"

        # First attempt - delete directly
        try {
            Remove-Item -Path $Path -Recurse -Force -ErrorAction Stop
            Write-Log "✅ Deleted successfully: $Path" "Green"
            continue
        }
        catch {
            $errorMsg = $_.Exception.Message
            Write-Log "❌ Delete failed: $errorMsg" "Red"
        }

        # Find the locked file
        if ($errorMsg -match "'(.+?)' because it is being used") {
            $lockedFile = $Matches[1]
            Write-Log "🔍 Locked file: $lockedFile" "Yellow"

            if ($handleExe) {
                $handleOutput = & $handleExe $lockedFile -accepteula 2>&1
                $foundAny = $false

                foreach ($line in $handleOutput) {
                    if ($line -match "^(.+?)\s+pid:\s+(\d+)") {
                        $foundAny = $true
                        $procName = $Matches[1].Trim()
                        $procPID  = [int]$Matches[2]

                        Write-Log "⚠️  Locking process: $procName (PID: $procPID)" "Yellow"

                        # Protect critical system processes
                        $protected = @("System","smss","csrss","wininit","winlogon","lsass","services")
                        if ($procName -in $protected) {
                            Write-Log "🛡️  System process, skipping: $procName" "Red"
                            continue
                        }

                        try {
                            Stop-Process -Id $procPID -Force -ErrorAction Stop
                            Write-Log "✅ Process terminated: $procName (PID: $procPID)" "Green"
                        }
                        catch {
                            Write-Log "❌ Cannot terminate: $procName" "Red"
                        }
                    }
                }

                if (-not $foundAny) {
                    Write-Log "⚠️  No locking process found" "Yellow"
                }
            }

            # Wait for process to fully exit
            Start-Sleep -Seconds 1

            # Second attempt
            try {
                Remove-Item -Path $Path -Recurse -Force -ErrorAction Stop
                Write-Log "✅ Second attempt succeeded: $Path" "Green"
            }
            catch {
                # Last resort: schedule delete on reboot
                Write-Log "❌ Still failing, scheduling delete on reboot..." "Red"
                $regPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager"
                $entry   = [string[]]@("\??\" + $lockedFile, "")
                $current = (Get-ItemProperty -Path $regPath -Name "PendingFileRenameOperations" `
                            -ErrorAction SilentlyContinue).PendingFileRenameOperations
                Set-ItemProperty -Path $regPath -Name "PendingFileRenameOperations" `
                                 -Value ($current + $entry)
                Write-Log "🔁 Scheduled for deletion on reboot: $lockedFile" "Yellow"
            }
        }
    }
}

# ============================================================
# ENTRY POINT - script starts here
# ============================================================
Write-Log "========================================" "White"
Write-Log "Cleanup script started" "White"
Write-Log "========================================" "White"

Remove-WithForce -Paths @(
    "C:\Windows\TEMP\*",
    "C:\Windows\Prefetch\*",
    "$env:LOCALAPPDATA\Temp\*"
)

Write-Log "========================================" "White"
Write-Log "Cleanup script finished" "White"
Write-Log "Log saved to: $global:LogFile" "White"
Write-Log "========================================" "White"

$runpython = you python file path"
python $runpython

