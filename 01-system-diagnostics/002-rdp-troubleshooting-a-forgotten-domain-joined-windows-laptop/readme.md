# Unable to RDP?  
**Case Study: Domain Group Policy Preventing RDP Listener**

---

## 📌 Overview

**Goal:**  
Connect a PC (Leon) to a laptop (LAPTOPADMIN) using Microsoft Remote Desktop (RDP) over a local network.

**Issue:**  
RDP connection failed even though:
- Firewall rules were enabled
- RDP was turned ON in settings
- Remote Desktop Services showed as *Running*

**Root Cause Identified:**  
A **Domain Group Policy** prevented the RDP service from listening on port **3389**.  
Once the laptop was **removed from the domain and placed into a workgroup**, RDP immediately began listening and connections succeeded.

---

## ✅ Method 1: Windows Defender Firewall (wf.msc)

**Inbound Rules Status (Advanced Security):**

- **Remote Desktop – User Mode (TCP-In)**  
  - Status: Enabled ✔  
  - Profile: All (Domain / Private / Public)  
  - Action: Allow  

- **Remote Desktop – User Mode (UDP-In)**  
  - Status: Enabled ✔  
  - Profile: All  
  - Action: Allow  

**Outcome:**  
✔ All critical RDP firewall rules were correctly enabled and set to Allow.

---

## ✅ Method 2: Control Panel – Allowed Apps

**Remote Desktop App Status:**
- App Allowed: ✔ Checked  
- Domain: ✔  
- Private: ✔  
- Public: ✔  

**Outcome:**  
✔ RDP fully authorized to communicate through the firewall across all network types.

---

## ✅ Method 3: PowerShell Firewall Validation

```powershell
Get-NetFirewallRule -DisplayGroup "Remote Desktop" |
Where-Object {$_.Enabled -eq "True"} |
Select DisplayName, Profile
```

**Output:**
```
DisplayName                         Profile
-----------                         -------
Remote Desktop - User Mode (TCP-In)     Any
Remote Desktop - User Mode (UDP-In)     Any
Remote Desktop - Shadow (TCP-In)        Any
```

**Analysis:**
- **Remote Desktop - User Mode (TCP-In):** Primary RDP rule, active on all network profiles (Any)
- **Remote Desktop - User Mode (UDP-In):** Enables smoother performance for video/graphics via UDP
- **Remote Desktop - Shadow (TCP-In):** Allows admin shadowing (view/control active sessions)

---

## 🖧 Network Configuration

### PC (Leon) - IPv4 Address: `192.168.1.153`

```powershell
ipconfig /all
```

**Key Details:**
```
Host Name . . . . . . . . . . . . : Leon
Primary Dns Suffix  . . . . . . . :
Node Type . . . . . . . . . . . . : Hybrid
DNS Suffix Search List. . . . . . : mynetworksettings.com

Wireless LAN adapter Wi-Fi:
   IPv4 Address. . . . . . . . . . : 192.168.1.153(Preferred)
   Subnet Mask . . . . . . . . . . : 255.255.255.0
   Default Gateway . . . . . . . . : 192.168.1.1
   DHCP Server . . . . . . . . . . : 192.168.1.1
   DNS Servers . . . . . . . . . . : 192.168.1.1
```

---

### Laptop (LAPTOPADMIN) - Before Domain Removal

**IPv4 Address: `192.168.1.38`**

```powershell
ipconfig /all
```

**Key Details:**
```
Host Name . . . . . . . . . . . . : lAPTOPADMIN
Primary Dns Suffix  . . . . . . . : CityNewYorkCollege.com
Node Type . . . . . . . . . . . . : Hybrid
DNS Suffix Search List. . . . . . : CityNewYorkCollege.com
                                    mynetworksettings.com

Wireless LAN adapter Wi-Fi:
   IPv4 Address. . . . . . . . . . : 192.168.1.38(Preferred)
   Subnet Mask . . . . . . . . . . : 255.255.255.0
   Default Gateway . . . . . . . . : 192.168.1.1
   DHCP Server . . . . . . . . . . : 192.168.1.1
   DNS Servers . . . . . . . . . . : 192.168.1.163
                                     8.8.8.8
```

**Note:** Device was joined to domain `CityNewYorkCollege.com`

---

### Laptop (LAPTOPADMIN) - After Domain Removal

**IPv4 Address: `192.168.1.38` (unchanged)**

```
Host Name . . . . . . . . . . . . : lAPTOPADMIN
Primary Dns Suffix  . . . . . . . : 
Node Type . . . . . . . . . . . . : Hybrid
DNS Suffix Search List. . . . . . : mynetworksettings.com
```

**Note:** Device now in workgroup (no domain suffix)

---

## 🔍 Diagnostic Steps Performed

### ✅ Step 1: Verify RDP is Enabled

**Method:** Registry check on target laptop

```powershell
reg query "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections
```

**Result:**
```
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Terminal Server
    fDenyTSConnections    REG_DWORD    0x0
```

**Interpretation:**
- `0x0` = RDP is **enabled** ✔
- `0x1` = RDP is **disabled** ❌

---

### ❌ Step 2: Check RDP Service Listening Status

**Method:** Check if RDP service is listening on port 3389

```powershell
netstat -ano | findstr :3389
```

#### **Result While Domain-Joined:**
```
PS C:\Windows\system32> netstat -ano | findstr :3389
PS C:\Windows\system32>
```

**Status:** ❌ **NO OUTPUT** - RDP service **NOT listening** despite being "enabled"

---

#### **Result After Leaving Domain:**
```powershell
netstat -ano | findstr :3389
```

**Output:**
```
TCP    0.0.0.0:3389           0.0.0.0:0              LISTENING       1592
TCP    [::]:3389              [::]:0                 LISTENING       1592
UDP    0.0.0.0:3389           *:*                                    1592
UDP    [::]:3389              *:*                                    1592
```

**Status:** ✅ **RDP service NOW listening** on all interfaces (IPv4 and IPv6)

**Process ID:** 1592 (Remote Desktop Services)

---

### ✅ Step 3: Service Status Verification

**Method:** Check via `services.msc`

**Finding:**  
Remote Desktop Services showed as **Running** even when port 3389 was not listening.

**Conclusion:**  
Service running ≠ Service actually listening on network port (due to Group Policy override)

---

### ❌ Step 4: Network Connectivity Test from PC

**Method:** Test network path from PC (192.168.1.153) to Laptop (192.168.1.38)

```powershell
Test-NetConnection 192.168.1.38 -Port 3389
```

**Result:**
```
WARNING: Ping to 192.168.1.38 failed with status: TimedOut

ComputerName           : 192.168.1.38
RemoteAddress          : 192.168.1.38
InterfaceAlias         : Wi-Fi
SourceAddress          : 192.168.1.153
PingSucceeded          : False
PingReplyDetails (RTT) : 0 ms
```

**Status:** ❌ Connection failed - TcpTestSucceeded: False

**Interpretation:**
- Network path exists
- Port 3389 not responding (service not listening)
- Not a firewall issue (rules were enabled)

---

### 🧪 Step 5: Local Loopback Test

**Method:** Test RDP locally on the laptop itself

```
mstsc
```

**Connect to:** `127.0.0.1`

**Error Message:**
```
Your computer could not connect to another console session on the remote computer
because you already have a console session in progress.
```

**Status:** ✔ RDP service functional locally  
**Conclusion:** Problem is with network listener binding, not RDP service itself

---

## 🎯 Root Cause Analysis

### The Problem: Domain Group Policy Override

**Evidence Summary:**

1. ✅ RDP enabled in registry (`fDenyTSConnections = 0x0`)
2. ✅ Firewall rules enabled (TCP/UDP for all profiles)
3. ✅ Remote Desktop Services running
4. ✅ Local loopback connection works
5. ❌ **Port 3389 NOT listening on network** (while domain-joined)
6. ✅ **Port 3389 IMMEDIATELY listening** (after leaving domain)

### The Culprit: Group Policy

When the laptop was domain-joined to `CityNewYorkCollege.com`, a **Group Policy Object (GPO)** prevented the RDP service from binding to the network interface, even though:
- The service showed as "Running"
- Registry settings indicated RDP was enabled
- Firewall rules allowed traffic

**Common GPO Settings that Block RDP:**
- `Computer Configuration > Administrative Templates > Windows Components > Remote Desktop Services > Remote Desktop Session Host > Connections`
  - "Deny logons to Remote Desktop Session Host server"
  - "Restrict Remote Desktop Services users to a single Remote Desktop Services session"
  - Network-level authentication requirements
  - Connection encryption settings

---

## ✅ Solution Implemented

### Action Taken: Remove from Domain

**Steps:**
1. Settings → System → About → Advanced system settings
2. Computer Name tab → Change
3. Select "Workgroup" instead of "Domain"
4. Restart computer

### Immediate Result:

**Before (Domain-joined):**
```powershell
netstat -ano | findstr :3389
# (No output - not listening)
```

**After (Workgroup):**
```powershell
netstat -ano | findstr :3389
TCP    0.0.0.0:3389           0.0.0.0:0              LISTENING       1592
TCP    [::]:3389              [::]:0                 LISTENING       1592
UDP    0.0.0.0:3389           *:*                                    1592
UDP    [::]:3389              *:*                                    1592
```

**Status:** ✅ **RDP immediately started listening**  
**Outcome:** ✅ **RDP connections from PC to Laptop now successful**

---

## 📝 Key Takeaways

### What We Learned:

1. **Service Status ≠ Service Listening**  
   A service can show as "Running" but not actually bind to network ports due to policy restrictions.

2. **Group Policy Overrides Local Settings**  
   Domain GPOs can silently override local RDP settings, even when everything appears configured correctly.

3. **Firewall Rules Were Not the Issue**  
   All firewall rules were properly configured; the problem was deeper in the system policy layer.

4. **`netstat` is the Definitive Test**  
   Checking if port 3389 is listening (`netstat -ano | findstr :3389`) is the most reliable diagnostic.

5. **Domain Policies Persist Until Rejoining**  
   Removing from domain immediately cleared the restrictive GPO.

---

## 🛠️ Alternative Solutions (If Domain Must Stay)

If the laptop **must remain domain-joined**, consider these alternatives:

### 1. Contact Domain Administrator
Request modification of the Group Policy to allow RDP for specific users/computers.

### 2. Use GPO Override (if you have admin rights)
```powershell
# Run as Administrator
gpupdate /force
# Then check local policy:
gpedit.msc
```
Navigate to:  
`Computer Configuration > Administrative Templates > Windows Components > Remote Desktop Services`

### 3. Use Alternative Remote Access Tools
- **TeamViewer**
- **AnyDesk**
- **Chrome Remote Desktop**
- **VNC** (TightVNC, RealVNC)

These tools bypass Group Policy RDP restrictions.

### 4. Configure RDP on Non-Standard Port
Change RDP to listen on a different port (e.g., 3390) that GPO may not restrict.

---

## 📊 Summary Table

| Component | Status (Domain-Joined) | Status (Workgroup) |
|-----------|------------------------|-------------------|
| RDP Registry Setting | ✅ Enabled (`0x0`) | ✅ Enabled (`0x0`) |
| Firewall Rules | ✅ Enabled (All profiles) | ✅ Enabled (All profiles) |
| RDP Service Running | ✅ Yes | ✅ Yes |
| Port 3389 Listening | ❌ **NO** | ✅ **YES** |
| Remote Connections | ❌ Failed | ✅ **Success** |
| Root Cause | 🔒 Domain GPO Block | N/A |

---

## 🎓 Conclusion

This case demonstrates the hidden complexity of enterprise network policies. While local troubleshooting showed all RDP components configured correctly, a domain-level Group Policy was silently preventing the service from accepting network connections.

**The fix:** Removing the laptop from the domain and placing it in a workgroup immediately resolved the issue, proving that Group Policy was the blocking factor.

**For future troubleshooting:**  
Always check `netstat -ano | findstr :3389` to verify the RDP service is actually listening on the network, not just "running" in Services.

---

**Report Generated:** February 1, 2026  
**System Environment:** Windows 10/11, Local Network (192.168.1.x/24)  
**Devices:** PC (Leon - 192.168.1.153), Laptop (LAPTOPADMIN - 192.168.1.38)
