@echo off
echo Script started at %date% %time% >> C:\Users\Public\Scripts\Public\log.txt
powershell.exe -ExecutionPolicy Bypass -File "C:\Users\Public\Scripts\Public\Public.ps1" >> C:\Users\Public\Scripts\Public\log.txt 2>&1
echo Script finished at  %date% %time% >> C:\Users\Public\Scripts\Public\log.txt
