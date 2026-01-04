@echo off

REM -------------------------------
REM Batch file to run AD User PowerShell script
REM -------------------------------
REM Instructions:
REM 1. Replace "your-path" with the folder where the script and logs will be stored.
REM 2. Replace "remove-user.ps1" with the name of your PowerShell script.

echo Script started at %date% %time% >> "your-path\log.txt"
powershell.exe -ExecutionPolicy Bypass -File "your-path\adusers.ps1" >> "your-path\errlog.txt" 2>&1

echo Script finished at  %date% %time% >> "your-path\log.txt"
