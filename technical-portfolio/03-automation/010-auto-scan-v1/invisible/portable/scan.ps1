$WatchFolder = "C:\Users\DM27\Desktop\scan"
$ScannerScript = Join-Path $PSScriptRoot "scan.py"
# ========================================
# UTF-8
# ========================================

chcp 65001 | Out-Null

$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"


# ========================================
# Check paths
# ========================================

if (!(Test-Path -LiteralPath $WatchFolder)) {
    Write-Host "[ERROR] Watch folder does not exist:"
    Write-Host $WatchFolder
    pause
    exit
}

if (!(Test-Path -LiteralPath $ScannerScript)) {
    Write-Host "[ERROR] scan.py does not exist:"
    Write-Host $ScannerScript
    pause
    exit
}


# ========================================
# FileSystemWatcher
# ========================================

$watcher = New-Object System.IO.FileSystemWatcher

$watcher.Path = $WatchFolder
$watcher.Filter = "*"

# 现在先只监听 scan 第一层
$watcher.IncludeSubdirectories = $false

$watcher.NotifyFilter = [System.IO.NotifyFilters]::FileName -bor `
                        [System.IO.NotifyFilters]::DirectoryName

$watcher.EnableRaisingEvents = $true


# ========================================
# Register Created Event
#
# 注意：
# 没有 -Action
# 所以不会创建后台 Action Job
# ========================================

$sourceId = "ScannerCreatedEvent"

# 清理之前残留的 subscriber
Unregister-Event -SourceIdentifier $sourceId -ErrorAction SilentlyContinue
Remove-Event -SourceIdentifier $sourceId -ErrorAction SilentlyContinue

Register-ObjectEvent `
    -InputObject $watcher `
    -EventName Created `
    -SourceIdentifier $sourceId | Out-Null


# ========================================
# Start
# ========================================

Write-Host ""
Write-Host "====================================="
Write-Host " File Scanner Watcher"
Write-Host "====================================="
Write-Host "Watching:"
Write-Host $WatchFolder
Write-Host ""
Write-Host "Waiting for new files..."
Write-Host "Press Ctrl+C to stop."
Write-Host ""

# ========================================
# Initial Scan
# ========================================

Write-Host "====================================="
Write-Host " Initial Scan"
Write-Host "====================================="
Write-Host "[*] Scanning existing files..."
Write-Host ""

& python $ScannerScript --folder "$WatchFolder"

Write-Host ""
Write-Host "[*] Initial scan finished."
Write-Host "[*] Python exit code: $LASTEXITCODE"
Write-Host ""

Write-Host "====================================="
Write-Host " Watching for new files..."
Write-Host "====================================="
Write-Host "Press Ctrl+C to stop."
Write-Host ""


# ========================================
# Main Event Loop
# ========================================

try {

    while ($true) {

        # 等待 Created 事件
        $event = Wait-Event -SourceIdentifier $sourceId

        if ($null -eq $event) {
            continue
        }

        $path = $event.SourceEventArgs.FullPath
        $name = $event.SourceEventArgs.Name

        # 把这个事件从 queue 删除
        Remove-Event -EventIdentifier $event.EventIdentifier -ErrorAction SilentlyContinue


        Write-Host ""
        Write-Host "====================================="
        Write-Host "[+] DETECTED"
        Write-Host "    $path"
        Write-Host "====================================="


        # 给 Windows 一点时间建立文件
        Start-Sleep -Milliseconds 300


        if (!(Test-Path -LiteralPath $path)) {

            Write-Host "[!] Path disappeared."
            continue

        }


        $item = Get-Item -LiteralPath $path


        # ========================================
        # Folder
        # ========================================

        if ($item.PSIsContainer) {

            Write-Host "[+] Folder detected:"
            Write-Host "    $name"

            Write-Host "[*] Waiting for folder copy..."
            Start-Sleep -Seconds 2

            Write-Host "[*] Starting Python folder scan..."
            Write-Host ""

            & python $ScannerScript --folder "$path"

            Write-Host ""
            Write-Host "[*] Python exit code: $LASTEXITCODE"

            continue
        }


        # ========================================
        # File
        # ========================================

        Write-Host "[+] File detected:"
        Write-Host "    $name"

        Write-Host "[*] Waiting for copy to finish..."


        $lastSize = -1
        $stableCount = 0


        while ($stableCount -lt 2) {

            if (!(Test-Path -LiteralPath $path)) {
                break
            }

            try {

                $size = (Get-Item -LiteralPath $path).Length

            }
            catch {

                Start-Sleep -Milliseconds 500
                continue

            }


            if ($size -eq $lastSize) {

                $stableCount++

            }
            else {

                $lastSize = $size
                $stableCount = 0

            }


            Start-Sleep -Milliseconds 500
        }


        if (!(Test-Path -LiteralPath $path)) {
            continue
        }


        Write-Host "[*] Copy finished."
        Write-Host "[*] Starting Python scanner..."
        Write-Host ""


        & python $ScannerScript --file "$path"


        Write-Host ""
        Write-Host "[*] Python exit code: $LASTEXITCODE"
        Write-Host "[*] Waiting for next file..."
        Write-Host ""

    }

}
finally {

    Write-Host ""
    Write-Host "[*] Stopping watcher..."

    Unregister-Event `
        -SourceIdentifier $sourceId `
        -ErrorAction SilentlyContinue

    Remove-Event `
        -SourceIdentifier $sourceId `
        -ErrorAction SilentlyContinue

    $watcher.Dispose()

}

