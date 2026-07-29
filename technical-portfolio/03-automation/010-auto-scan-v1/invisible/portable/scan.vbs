Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

CurrentDir = FSO.GetParentFolderName(WScript.ScriptFullName)
PsScript = CurrentDir & "\scan.ps1"

WshShell.Run "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File """ & PsScript & """", 0, False
