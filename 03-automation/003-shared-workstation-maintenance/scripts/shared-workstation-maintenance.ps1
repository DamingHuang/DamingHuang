#for Public
$public = "C:\Users\Public"
$Publicfolders = @("Desktop", "Downloads", "Documents", "Pictures", "Videos")

foreach ($Publicfolder in $Publicfolders) {
    $Publicpath = Join-Path $PublicProfile $Publicfolder
    if (Test-Path $Publicpath) {
        Remove-Item "$Publicpath\*" -Recurse -Force -ErrorAction SilentlyContinue
    } else { 
	Add-Content $logFile "Path does not exist: $Publicpath"
    }
}

#add An end Log

Add-Content $logFile "Script finished at $(Get-Date)"
