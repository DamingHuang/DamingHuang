PowerShell-WiFi-AutoConnect
WiFi Auto Connect (PowerShell)

A PowerShell script that automatically imports multiple Wi-Fi XML profiles and attempts to connect to available networks in sequence.
Features

    Imports multiple saved Wi-Fi profiles (.xml format)
    Tries to connect to each network until a successful connection is made
    Displays connection status (✅ connected & ⚠️ not connected)

Usage
Place your Wi-Fi XML profiles in the same folder as the script.
Edit the script to include your profile paths and Wi-Fi names.
Run PowerShell as Administrator.
Execute:

.\WiFiAutoConnect.ps1

 

 

```powershell
Adding Wi-Fi profile: C:\Users\User1\Desktop\script\PowerShell\GuestOpenNet.xml
Adding Wi-Fi profile: C:\Users\User1\Desktop\script\PowerShell\notwork.xml
Adding Wi-Fi profile: C:\Users\User1\Desktop\script\PowerShell\TestWiFi_A.xml
Adding Wi-Fi profile: C:\Users\User1\Desktop\script\PowerShell\Wi-Fi-home-1st.xml
Adding Wi-Fi profile: C:\Users\User1\Desktop\script\PowerShell\Wi-Fi-home.xml
Trying to connect to GuestOpenNet...
⚠️ Not connected to any Wi-Fi
Trying to connect to notwork...
⚠️ Not connected to any Wi-Fi
Trying to connect to TestWiFi_A...
⚠️ Not connected to any Wi-Fi 
Cannot index into a null array.
At line:28 char:5
+     $connectedSSID = ($Matches[1]).Trim()
+     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : InvalidOperation: (:) [], RuntimeException
    + FullyQualifiedErrorId : NullArray
✅ Connected to home-1st
```
