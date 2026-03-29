# Add XML profiles
$wifiProfiles= @(
    "C:\Users\User1\Desktop\script\PowerShell\GuestOpenNet.xml",
    "C:\Users\User1\Desktop\script\PowerShell\notwork.xml",
    "C:\Users\User1\Desktop\script\PowerShell\TestWiFi_A.xml",
    "C:\Users\User1\Desktop\script\PowerShell\Wi-Fi-home-1st.xml",
    "C:\Users\User1\Desktop\script\PowerShell\Wi-Fi-home.xml"
)

foreach ($wifiProfile in $wifiProfiles) {
    Write-Host "Adding Wi-Fi profile: $wifiProfile"
    netsh wlan add profile filename="$wifiProfile" | Out-Null
}

# Connect to Wi-Fi
$wifiList=@("GuestOpenNet","notwork","TestWiFi_A","home-1st","home")

foreach ($wifi in $wifiList) {
    Write-Host "Trying to connect to $wifi..."
    netsh wlan connect name="$wifi" | Out-Null

    Start-Sleep -Seconds 3  # Give it a few seconds to connect

    $rawSSID = (netsh wlan show interfaces) -match '^\s*SSID\s*:\s*(.+)$'

 
 if ($rawSSID) {
    $connectedSSID = ($Matches[1]).Trim()
    if ($connectedSSID -eq $wifi) {
        Write-Host "✅ Connected to $wifi"
        break
    }
    
}
else {
    Write-Host "⚠️ Not connected to any Wi-Fi"
}


}
