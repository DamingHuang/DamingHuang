# DNS Not Working Over WireGuard VPN?
**Case Study: WireGuard DNS Configuration Preventing Domain Controller Access**

---

## 📋 Executive Summary

**Issue:**  
Local PC unable to access AWS Domain Controller DNS service via WireGuard VPN, preventing domain join functionality.

 

**Root Cause:**  
Incorrect DNS server configuration in WireGuard client (`DNS = 8.8.8.8, 1.1.1.1`), redirecting all DNS queries to public DNS instead of domain controller.

**Solution:**  
Modified WireGuard configuration to use domain controller IP (`10.0.1.12`) as DNS server.

**Critical Mistake:**  
Started troubleshooting from the server side instead of the client side, wasting significant time on server configurations that were not the issue.

---

## 🏗️ Environment Architecture

### Network Topology

```
Local PC (10.5.1.2)
    ↓ WireGuard Tunnel
Ubuntu VPN Server (10.0.1.4)
    ↓ AWS VPC Internal Network
AWS Domain Controller (10.0.1.12)
```

### Component Information

| Component | Details |
|-----------|---------|
| **AWS Domain Controller** | Windows Server 2022, IP: `10.0.1.12` |
| **Ubuntu VPN Server** | Ubuntu 22.04, IP: `10.0.1.4`, Instance ID: `i-080bb37f0130c9523` |
| **Local PC** | Windows 10/11, WireGuard IP: `10.5.1.2` |
| **VPC ID** | `vpc-0517d5e295a732156` |
| **Security Group ID** | `sg-078968af2967efd66` |
| **Route Table ID** | `rtb-08e60668585fd2dd0` |

---

## 🔍 Problem Diagnosis Process

### Phase 1: Initial Symptoms & Critical Errors

#### Command 1: Basic DNS Query Test

```powershell
PS C:\Users\Administrator> nslookup mingtea.com 10.0.1.12
```

**Error Result:**
```
❌ DNS request timed out.
    timeout was 2 seconds.
Server:  UnKnown
Address:  10.0.1.12

DNS request timed out.
    timeout was 2 seconds.
DNS request timed out.
    timeout was 2 seconds.
DNS request timed out.
    timeout was 2 seconds.
DNS request timed out.
    timeout was 2 seconds.
*** Request to UnKnown timed-out
```

---

#### Command 2: Detailed Port Connectivity Test

```powershell
PS C:\Windows\system32> Test-NetConnection -ComputerName 10.0.1.12 -Port 53 -InformationLevel Detailed
```

**Error Result:**
```
❌ WARNING: TCP connect to (10.0.1.12 : 53) failed

ComputerName            : 10.0.1.12
RemoteAddress           : 10.0.1.12
RemotePort              : 53
NameResolutionResults   : 10.0.1.12
InterfaceAlias          : VPnUbuntu
SourceAddress           : 10.5.1.2
NetRoute (NextHop)      : 0.0.0.0
PingSucceeded           : True
PingReplyDetails (RTT)  : 14 ms
TcpTestSucceeded        : False    ← CRITICAL FAILURE
```

**Observation:**  
Network ping successful (14ms RTT), but TCP port 53 connection failed.

---

### Phase 2: Server-Side Investigation (Initial Misdiagnosis)

#### Command 3: Check DNS Service Status

```powershell
PS C:\Users\Administrator> netstat -an | findstr ":53"
```

**Result:**
```
✅ TCP    10.0.1.12:53           0.0.0.0:0              LISTENING
✅ TCP    127.0.0.1:53           0.0.0.0:0              LISTENING
✅ UDP    10.0.1.12:53           *:*
✅ UDP    127.0.0.1:53           *:*
```

**Status:** DNS service is listening on the correct IP and port.

---

#### Command 4: Comprehensive DNS Diagnostics

```powershell
PS C:\Users\Administrator> dcdiag /test:dns /v
```

**Critical Findings:**
```
❌ Warning IP address is dynamic (can be a misconfiguration)
❌ Warning: Adapter 12:8A:E4:D1:23:ED has dynamic IP address (can be a misconfiguration)
✅ DNS service is running
✅ DC is a DNS server
✅ The A host record(s) for this DC was found
✅ All tests passed on this DNS server
```

**Interpretation:** DNS service is functioning correctly on the server side.

---

#### Command 5: Set DNS to Listen on All Interfaces

```powershell
PS C:\Users\Administrator> Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\DNS\Parameters" `
    -Name "ListenAddress" `
    -Value @("0.0.0.0") `
    -Type MultiString

PS C:\Users\Administrator> Restart-Service DNS -Force
```

**Verification After Fix:**
```powershell
PS C:\Users\Administrator> Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\DNS\Parameters" -Name "ListenAddress"
```

**Result:**
```
✅ ListenAddress : {0.0.0.0}
```

---

#### Re-Test After Server Configuration:

```powershell
PS C:\Users\Administrator> nslookup mingtea.com 10.0.1.12
```

**Result:**
```
❌ DNS request timed out.
    timeout was 2 seconds.
*** Request to UnKnown timed-out    ← STILL FAILING
```

**Conclusion:** Server configuration changes did NOT resolve the issue.

---

### Phase 3: Network Layer Investigation

#### Command 6: Check AWS Security Group Rules

```bash
~ $ aws ec2 describe-security-groups \
  --group-ids sg-078968af2967efd66 \
  --query "SecurityGroups[*].IpPermissions[*].{FromPort:FromPort, ToPort:ToPort, Protocol:IpProtocol, SourceCidr:IpRanges[*].CidrIp}" \
  --output table
```

**Result Showing Missing DNS Rules:**
```
------------------------------------
|      DescribeSecurityGroups      |
+----------+------------+----------+
| FromPort | Protocol   | ToPort   |
+----------+------------+----------+
|  65535   |  tcp       |  65535   |
+----------+------------+----------+
||           SourceCidr           ||
|+--------------------------------+|
||  10.5.1.0/24                   ||
|+--------------------------------+|
+----------+------------+----------+
|  None    |  -1        |  None    |
+----------+------------+----------+
||           SourceCidr           ||
|+--------------------------------+|
||  10.0.0.0/16                   ||
|+--------------------------------+|
```

**🚨 DISCOVERY:** No TCP/UDP port 53 rules for `10.5.1.0/24` subnet!

**Initial Conclusion:** This appeared to be a security group issue (later proved to be a red herring).

---

#### Command 7: Static Routing Attempt on Windows

```powershell
PS C:\Users\Administrator> route add 10.5.1.0 mask 255.255.255.0 10.0.1.4
```

**Result:**
```
✅ OK!
```

**Verify Connectivity:**
```powershell
PS C:\Users\Administrator> ping 10.5.1.2
```

**Error Result:**
```
❌ Pinging 10.5.1.2 with 32 bytes of data:
Request timed out.
Request timed out.
Request timed out.
Request timed out.

Ping statistics for 10.5.1.2:
    Packets: Sent = 4, Received = 0, Lost = 4 (100% loss),
```

**Conclusion:** Static routing did not resolve the connectivity issue.

---

### Phase 4: Client Configuration Investigation (BREAKTHROUGH)

#### Command 8: Check Windows DNS Client Configuration

```powershell
PS C:\Windows\system32> Get-DnsClientServerAddress -InterfaceAlias "VPnUbuntu"
```

**🚨 CRITICAL DISCOVERY:**
```
InterfaceAlias               Interface Address ServerAddresses
                             Index     Family
--------------               --------- ------- ---------------
VPnUbuntu                           10 IPv4    {8.8.8.8, 1.1.1.1}    ← PROBLEM FOUND!
```

**Analysis:**  
Windows is using Google's public DNS (`8.8.8.8`) and Cloudflare DNS (`1.1.1.1`) instead of the domain controller (`10.0.1.12`)!

---

#### Command 9: Examine WireGuard Configuration

```ini
[Interface]
PrivateKey = cPDEu/Rqdc/B7qTFD+35OTe1f2z3xvE9VHc8iIvl738=
Address = 10.5.1.2/24
DNS = 8.8.8.8, 1.1.1.1    ← ROOT CAUSE IDENTIFIED!

[Peer]
PublicKey = /Eeul6NXYIc1s5c7GjZTiGi+vyT0MSKOCQPRcoK7Qlg=
AllowedIPs = 0.0.0.0/0
Endpoint = 35.173.246.198:51820
PersistentKeepalive = 25
```

**🎯 ROOT CAUSE CONFIRMED:**  
WireGuard is configured to force all DNS queries through public DNS servers, completely bypassing the domain controller.

---

#### Command 10: Network Packet Capture Evidence

```bash
ubuntu@ip-10-0-1-4:~$ sudo tcpdump -i wg0 port 53 -vvv
```

**🔍 IRREFUTABLE EVIDENCE:**
```
20:27:13.883025 IP (tos 0x0, ttl 128, id 51436, offset 0, flags [none], proto UDP (17), length 68)
    ❌ 10.5.1.2.53645 > dns.google.domain: [udp sum ok] 35335+ PTR? 12.1.0.10.in-addr.arpa. (40)
    ↑ ↑ ↑ ↑ ↑
    Queries going to Google DNS (8.8.8.8), NOT to 10.0.1.12!

20:27:13.883842 IP (tos 0x80, ttl 121, id 37685, offset 0, flags [none], proto UDP (17), length 68)
    dns.google.domain > 10.5.1.2.53645: [udp sum ok] 35335 NXDomain
```

**Proof:**  
Packet capture shows DNS queries being sent to `dns.google.domain` (8.8.8.8) instead of the domain controller (`10.0.1.12`).

---

## ✅ Phase 5: The Fix & Verification

### Step 1: Modify WireGuard Configuration

**Before (Incorrect):**
```ini
[Interface]
PrivateKey = cPDEu/Rqdc/B7qTFD+35OTe1f2z3xvE9VHc8iIvl738=
Address = 10.5.1.2/24
DNS = 8.8.8.8, 1.1.1.1    ← WRONG
```

**After (Corrected):**
```ini
[Interface]
PrivateKey = cPDEu/Rqdc/B7qTFD+35OTe1f2z3xvE9VHc8iIvl738=
Address = 10.5.1.2/24
DNS = 10.0.1.12    ← FIXED: Changed to domain controller IP
```

---

### Step 2: Apply Changes and Clear Cache

```powershell
PS C:\Windows\system32> ipconfig /flushdns
```

**Result:**
```
✅ Successfully flushed the DNS Resolver Cache.
```

---

### Step 3: Verify DNS Configuration Change

```powershell
PS C:\Windows\system32> Get-DnsClientServerAddress -InterfaceAlias "VPnUbuntu"
```

**✅ SUCCESSFUL CHANGE:**
```
InterfaceAlias               Interface Address ServerAddresses
                             Index     Family
--------------               --------- ------- ---------------
VPnUbuntu                           10 IPv4    {10.0.1.12}    ← NOW CORRECT!
VPnUbuntu                           10 IPv6    {}
```

---

### Step 4: Final DNS Test

```powershell
PS C:\Windows\system32> nslookup mingtea.com
```

**✅ SUCCESS RESULT:**
```
✅ Server:  UnKnown
Address:  10.0.1.12

Name:    mingtea.com
Address:  10.0.1.12    ← SUCCESSFULLY RESOLVED!
```

---

### Step 5: Final Port Connectivity Test

```powershell
PS C:\Windows\system32> Test-NetConnection -ComputerName 10.0.1.12 -Port 53
```

**✅ SUCCESS RESULT:**
```
✅ ComputerName     : 10.0.1.12
RemoteAddress    : 10.0.1.12
RemotePort       : 53
InterfaceAlias   : VPnUbuntu
SourceAddress    : 10.5.1.2
TcpTestSucceeded : True    ← PORT 53 NOW ACCESSIBLE!
```

---

## 🎯 Root Cause Analysis Timeline

### Error Sequence:

1. **Initial Symptom:** `nslookup` timeout errors
2. **First Misdiagnosis:** Assumed DNS server configuration issue
3. **Second Misdiagnosis:** Assumed network routing/security group issue
4. **Third Misdiagnosis:** Assumed Ubuntu forwarding/NAT configuration issue
5. **Final Discovery:** WireGuard DNS configuration overriding all settings

### Critical Evidence Chain:

| Evidence | Conclusion |
|----------|------------|
| Ping worked but DNS didn't | → Not a network layer issue |
| DNS service showed as listening | → Not a server service issue |
| Security groups missing port 53 rules | → Red herring (not the root cause) |
| `tcpdump` showed queries to `dns.google` | → Smoking gun evidence |
| WireGuard config showed `DNS = 8.8.8.8` | → Root cause confirmed |

---

## 💡 Key Technical Insights

### 1. WireGuard DNS Behavior

**Configuration Impact:**
```ini
# WireGuard FORCES DNS resolution through configured servers
DNS = 8.8.8.8, 1.1.1.1  # ← Overrides ALL system DNS settings
```

**Critical Understanding:**  
Even when specifying a DNS server explicitly (e.g., `nslookup domain 10.0.1.12`), WireGuard intercepts and redirects queries to the configured DNS servers.

---

### 2. Windows DNS Client Behavior

```powershell
Get-DnsClientServerAddress  # Shows WireGuard-enforced DNS, not system defaults
```

The DNS configuration shown by Windows reflects what WireGuard has set, not the operating system's default DNS settings.

---

### 3. Network Diagnosis Hierarchy

**✅ Correct Order:**
```
Client → Network Path → Server
```

**❌ Our Order (Wasted Time):**
```
Server → Network Path → Client
```

**Lesson Learned:**  
Always start troubleshooting from the client side in VPN scenarios, as client configuration often overrides server capabilities.

---

## 🛡️ Preventive Configuration Checklist

### 1. WireGuard Configuration

**✅ CORRECT:**
```ini
[Interface]
# For single domain controller:
DNS = 10.0.1.12

# For redundancy (multiple DCs):
DNS = 10.0.1.12, 10.0.1.13
```

**❌ WRONG:**
```ini
[Interface]
DNS = 8.8.8.8, 1.1.1.1    # Public DNS - breaks domain resolution
```

---

### 2. AWS Security Groups (Recommended Rules)

```bash
# Add DNS TCP rule for VPN clients
aws ec2 authorize-security-group-ingress \
    --group-id sg-078968af2967efd66 \
    --protocol tcp --port 53 \
    --cidr 10.5.1.0/24

# Add DNS UDP rule for VPN clients
aws ec2 authorize-security-group-ingress \
    --group-id sg-078968af2967efd66 \
    --protocol udp --port 53 \
    --cidr 10.5.1.0/24
```

**Note:** While not the root cause in this case, these rules should be present for proper security group configuration.

---

### 3. Ubuntu VPN Server Configuration

```bash
# Enable IP forwarding (essential for routing)
sudo sysctl -w net.ipv4.ip_forward=1
echo "net.ipv4.ip_forward = 1" | sudo tee -a /etc/sysctl.conf

# Configure NAT for WireGuard clients
sudo iptables -t nat -A POSTROUTING -s 10.5.1.0/24 -o eth0 -j MASQUERADE
sudo iptables -A FORWARD -i wg0 -j ACCEPT
sudo iptables -A FORWARD -o wg0 -j ACCEPT
```

---

## 📊 Troubleshooting Decision Tree for Future

```
DNS Resolution Fails Over VPN
    ↓
1. Check VPN Client DNS Configuration FIRST
    ↓
2. Run: Get-DnsClientServerAddress -InterfaceAlias "VPN-Interface"
    ↓
3. If shows public DNS (8.8.8.8, 1.1.1.1)
    → Fix VPN client config (WireGuard/OpenVPN)
    ↓
4. If shows correct DNS
    → Check network path
    ↓
5. Test: Test-NetConnection -ComputerName DC-IP -Port 53
    ↓
6. If fails
    → Check firewalls/security groups/routing
    ↓
7. If succeeds
    → Check DNS service on Domain Controller
```

---

## 🎓 Final Resolution Summary

| Aspect | Details |
|--------|---------|
| **Root Cause** | WireGuard configuration `DNS = 8.8.8.8, 1.1.1.1` |
| **Impact** | All DNS queries redirected to Google DNS, bypassing domain controller |
| **Fix** | Changed to `DNS = 10.0.1.12` in WireGuard configuration |
| **Verification** | DNS resolution and port 53 connectivity restored |
| **Critical Mistake** | Starting troubleshooting from server side instead of client side |
| **Key Learning** | In VPN scenarios, **client configuration overrides server capabilities** |

---

## 📝 Key Takeaways

### What We Learned:

1. **Client Configuration is King in VPNs**  
   VPN client settings (especially DNS) override all server-side configurations.

2. **Start Troubleshooting at the Client**  
   Always check client configuration first before diving into server/network issues.

3. **WireGuard DNS is Mandatory**  
   The `DNS` directive in WireGuard configuration is not optional—it forces DNS resolution through specified servers.

4. **Packet Capture Never Lies**  
   When in doubt, use `tcpdump` or Wireshark to see actual network traffic.

5. **Red Herrings are Common**  
   Missing security group rules looked like the problem but were not the root cause.

---

## 🔧 Quick Reference Commands

### Check DNS Configuration
```powershell
# Windows
Get-DnsClientServerAddress -InterfaceAlias "VPN-Interface-Name"
ipconfig /all
```

### Test DNS Connectivity
```powershell
# Windows
nslookup domain.com DNS-Server-IP
Test-NetConnection -ComputerName DNS-Server-IP -Port 53
```

### Capture DNS Traffic
```bash
# Linux
sudo tcpdump -i wg0 port 53 -vvv
```

### Flush DNS Cache
```powershell
# Windows
ipconfig /flushdns
```

---

 
**System Environment:** Windows 10/11 Client, Ubuntu 22.04 VPN Server, AWS Windows Server 2022 DC  
**Network:** WireGuard VPN (10.5.1.0/24) ↔ AWS VPC (10.0.0.0/16)
