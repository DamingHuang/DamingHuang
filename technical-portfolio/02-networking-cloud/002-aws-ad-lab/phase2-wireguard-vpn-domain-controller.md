# AWS AD Lab — Phase 2: WireGuard VPN Server & Domain Controller Setup

> **How to read this guide:**
> - **Field** — the exact label or setting you are configuring.
> - **Value / Your Entry** — what to type or select. Suggested names are shown as examples (e.g., `AD-VPN-Server`). Fill in your own where indicated.
> - Scripts are shown on the line **below** the description, inside a code block.
> - Anywhere you see `"your-value-here"` inside a script — **replace it with your own value** before running.

---

## Part A: WireGuard VPN Server (Ubuntu EC2)

### A.1 Install WireGuard

| Field | Value / Your Entry |
|---|---|
| **Action** | Update packages and install WireGuard |

```bash
sudo apt update
sudo apt install wireguard -y
```

---

### A.2 Generate Server Keys

| Field | Value / Your Entry |
|---|---|
| **Server private key file** | `/etc/wireguard/server_private.key` *(or your own name, e.g. `mylab_server_private.key`)* |
| **Server public key file** | `/etc/wireguard/server_public.key` *(or your own name, e.g. `mylab_server_public.key`)* |
| **Server public key value** *(auto-generated — record this)* | `<server-public-key>` — **copy and save this output** |

```bash
# Generate server private key
wg genkey | sudo tee /etc/wireguard/server_private.key

# Generate server public key from the private key
sudo cat /etc/wireguard/server_private.key | wg pubkey | sudo tee /etc/wireguard/server_public.key
```

> 📝 The public key printed to the terminal is what you will paste into the **client config** later.

---

### A.3 Generate Client Key Pair (on the server)

| Field | Value / Your Entry |
|---|---|
| **Client private key file** | `/etc/wireguard/client1_private.key` *(e.g. `mylab_client1_private.key`)* |
| **Client public key file** | `/etc/wireguard/client1_public.key` *(e.g. `mylab_client1_public.key`)* |
| **Client public key value** *(auto-generated — record this)* | `<client-public-key>` — **copy and save this output** |
| **Client private key value** *(auto-generated — record this)* | `<client-private-key>` — **copy and save this output** |

```bash
# Generate client private key
wg genkey | sudo tee /etc/wireguard/client1_private.key

# Generate client public key from the private key
sudo cat /etc/wireguard/client1_private.key | wg pubkey | sudo tee /etc/wireguard/client1_public.key
```

> ⚠️ **Keep the client private key safe.** It goes into the client config on your local machine. Transfer it securely — never share it.

---

### A.4 Create Server Configuration File

| Field | Value / Your Entry |
|---|---|
| **Config file path** | `/etc/wireguard/wg0.conf` |
| **PrivateKey** | Paste the contents of `/etc/wireguard/server_private.key` |
| **Address** | `10.5.1.1/24` *(VPN server IP — change subnet if needed, e.g. `10.8.0.1/24`)* |
| **ListenPort** | `51820` *(default WireGuard port — change if needed)* |
| **Network interface** | `eth0` *(verify with `ip a` — may be `ens5` on some Ubuntu AMIs)* |
| **Client PublicKey** | Paste the contents of `/etc/wireguard/client1_public.key` |
| **Client AllowedIPs** | `10.5.1.2/32` *(IP address assigned to this client inside the VPN tunnel)* |

```ini
[Interface]
PrivateKey = <server-private-key>
Address = 10.5.1.1/24
ListenPort = 51820

PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

[Peer]
PublicKey = <client-public-key>
AllowedIPs = 10.5.1.2/32
```

> 💡 Replace `eth0` in PostUp/PostDown with your actual interface name if different (check with `ip a`).

---

### A.5 Enable IP Forwarding

| Field | Value / Your Entry |
|---|---|
| **Action** | Allow the server to forward packets between VPN clients and the VPC |

```bash
sudo sysctl -w net.ipv4.ip_forward=1
echo "net.ipv4.ip_forward = 1" | sudo tee -a /etc/sysctl.conf
```

---

### A.6 Start and Enable WireGuard

| Field | Value / Your Entry |
|---|---|
| **Service name** | `wg-quick@wg0` *(change `wg0` if you named your config file differently)* |

```bash
sudo systemctl enable wg-quick@wg0
sudo systemctl start wg-quick@wg0
sudo systemctl status wg-quick@wg0
```

---

### A.7 Verify WireGuard is Running

| Field | Value / Your Entry |
|---|---|
| **Expected output** | The `wg0` interface and your configured peer should be listed |

```bash
sudo wg
```

---

## Part B: WireGuard Client Configuration (Your Local PC)

> Create a new tunnel in the WireGuard client app on your local Windows (or other) machine.

### B.1 Create Client Tunnel Configuration

| Field | Value / Your Entry |
|---|---|
| **Tunnel name** | `AD-Lab-VPN` *(e.g. `MyLab-Tunnel`, any name you like in the WireGuard app)* |
| **PrivateKey** | Paste the contents of `client1_private.key` (generated in Step A.3) |
| **Address** | `10.5.1.2/24` *(client VPN IP — must match what you set in the server's `AllowedIPs`)* |
| **DNS** | `10.0.2.10` *(⚠️ MUST be your Domain Controller's private IP — **not** `8.8.8.8`)* |
| **Server PublicKey** | Paste the contents of `/etc/wireguard/server_public.key` (from Step A.2) |
| **AllowedIPs** | `10.0.0.0/16, 10.5.1.0/24` *(routes VPC and VPN subnet traffic through the tunnel)* |
| **Endpoint** | `<VPN-server-public-IP>:51820` *(public IP of your Ubuntu EC2 instance + port)* |
| **PersistentKeepalive** | `25` *(keeps the tunnel alive through NAT — recommended)* |

```ini
[Interface]
PrivateKey = <client-private-key>
Address = 10.5.1.2/24
DNS = 10.0.2.10

[Peer]
PublicKey = <server-public-key>
AllowedIPs = 10.0.0.0/16, 10.5.1.0/24
Endpoint = <VPN-server-public-IP>:51820
PersistentKeepalive = 25
```

> ⚠️ **DNS must point to your Domain Controller IP.** Using `8.8.8.8` here will cause domain name resolution (`MingTea.local`) to fail.

---

### B.2 Activate the Tunnel & Verify DNS

| Field | Value / Your Entry |
|---|---|
| **Action** | Activate the tunnel in the WireGuard app, then run the command below |
| **Interface alias** | `"AD-Lab-VPN"` *(use the exact tunnel name you gave it in the WireGuard app)* |
| **Expected IPv4 DNS output** | `{10.0.2.10}` *(your DC IP — confirms DNS is routed correctly)* |

```powershell
Get-DnsClientServerAddress -InterfaceAlias "AD-Lab-VPN"
```

---

## Part C: Windows Domain Controller Setup (AWS EC2)

### C.1 Launch the EC2 Instance

Navigate to: **EC2 → Instances → Launch instances**

| Field | Value / Your Entry |
|---|---|
| **Name** | `DC01` *(e.g. `MyLab-DC`, `AD-DomainController`)* |
| **AMI** | Windows Server 2022 Base *(or 2019)* |
| **Instance type** | `t3.medium` *(2 vCPU, 4 GB RAM — minimum for Active Directory)* |
| **Key pair** | Select or create your key pair *(e.g. `MyLab-WinKey`)* |
| **VPC** | `AD-VPC` (`vpc-xxxxxxxxxxxx`) |
| **Subnet** | `AD-Private-Subnet` (`10.0.2.0/24`) — **no public IP** |
| **Auto-assign Public IP** | **Disable** |
| **Security Group name** | `AD-DomainController-SG` *(e.g. `MyLab-DC-SG`)* |
| **Storage size** | `30 GiB` GP2 minimum |

**Security Group Inbound Rules for `AD-DomainController-SG`:**

| Type | Protocol | Port | Source | Purpose |
|---|---|---|---|---|
| RDP | TCP | 3389 | Your public IP | Initial setup only — remove after setup |
| DNS | TCP | 53 | `10.5.1.0/24` *(VPN subnet)* | DNS from VPN clients |
| DNS | UDP | 53 | `10.5.1.0/24` *(VPN subnet)* | DNS from VPN clients |
| All ICMP | ICMP | All | `10.0.0.0/16` *(VPC CIDR)* | Ping tests within VPC |
| All traffic *(optional)* | All | All | `10.0.0.0/16` *(VPC CIDR)* | Easier internal comms |

---

### C.2 Connect and Configure Windows Server

Connect via RDP (using a jump host, Session Manager, or temporary public IP). Run all commands below as **Administrator** in PowerShell.

---

### C.2.1 Set Static IP and DNS

| Field | Value / Your Entry |
|---|---|
| **Interface alias** | `"Ethernet"` *(verify with `Get-NetAdapter` — may differ on your instance)* |
| **Static IP address** | `10.0.2.10` *(choose a free IP in your private subnet, e.g. `10.0.2.10`)* |
| **Prefix length** | `24` *(matches your `/24` subnet)* |
| **Default gateway** | `10.0.2.1` *(your private subnet's gateway — first IP of the subnet)* |
| **DNS server** | `127.0.0.1` *(points to itself — will be updated after AD is promoted)* |

```powershell
New-NetIPAddress -InterfaceAlias "Ethernet" -IPAddress "10.0.2.10" -PrefixLength 24 -DefaultGateway "10.0.2.1"

Set-DnsClientServerAddress -InterfaceAlias "Ethernet" -ServerAddresses ("127.0.0.1")
```

---

### C.2.2 Rename the Computer

| Field | Value / Your Entry |
|---|---|
| **New computer name** | `DC01` *(e.g. `MyLab-DC01` — this becomes the DC hostname)* |

```powershell
Rename-Computer -NewName "DC01" -Restart
```

> ⏳ Reconnect via RDP after the reboot before continuing.

---

### C.2.3 Install Active Directory Domain Services

| Field | Value / Your Entry |
|---|---|
| **Windows Feature** | `AD-Domain-Services` *(includes management tools)* |

```powershell
Install-WindowsFeature AD-Domain-Services -IncludeManagementTools
```

---

### C.2.4 Promote to Domain Controller

| Field | Value / Your Entry |
|---|---|
| **Domain name** | `MingTea.local` *(e.g. `"yourcompany.local"` — choose your own internal domain)* |
| **NetBIOS name** | `MingTea` *(e.g. `"YOURLAB"` — short name used for `DOMAIN\username` login)* |
| **Safe Mode password** | `"YourStrongPassword123!"` — **replace with your own strong password** |

```powershell
$domainName = "MingTea.local"
$netbiosName = "MingTea"
$safeModePassword = ConvertTo-SecureString "YourStrongPassword123!" -AsPlainText -Force

Install-ADDSForest `
    -DomainName $domainName `
    -DomainNetbiosName $netbiosName `
    -SafeModeAdministratorPassword $safeModePassword `
    -InstallDns:$true `
    -NoRebootOnCompletion:$false `
    -Force:$true
```

> ⏳ The server will **reboot automatically**. Reconnect and log in as `MingTea\Administrator` (or `YOURLAB\Administrator` if you used a different NetBIOS name).

---

### C.3 Post-Installation Configuration

All commands below run as `MingTea\Administrator` after the reboot.

---

### C.3.1 Create Organizational Units and Users

| Field | Value / Your Entry |
|---|---|
| **Domain path** | `"DC=MingTea,DC=local"` *(replace with your domain, e.g. `"DC=yourcompany,DC=local"`)* |
| **OU names** | `Workstations`, `Users`, `Servers` *(rename to suit your lab)* |
| **Domain joiner account name** | `DomainJoiner` *(e.g. `"LabJoinAccount"`)* |
| **Domain joiner password** | `"JoinPass123!"` — **replace with your own strong password** |
| **Test user name** | `TestUser` *(e.g. `"LabUser01"`)* |
| **Test user password** | `"UserPass123!"` — **replace with your own strong password** |

```powershell
New-ADOrganizationalUnit -Name "Workstations" -Path "DC=MingTea,DC=local"
New-ADOrganizationalUnit -Name "Users" -Path "DC=MingTea,DC=local"
New-ADOrganizationalUnit -Name "Servers" -Path "DC=MingTea,DC=local"

# Create a domain join account
$joinerPassword = ConvertTo-SecureString "JoinPass123!" -AsPlainText -Force
New-ADUser -Name "DomainJoiner" -AccountPassword $joinerPassword -Enabled $true -Path "OU=Users,DC=MingTea,DC=local"
Add-ADGroupMember -Identity "Domain Admins" -Members "DomainJoiner"

# Create a regular test user
$userPassword = ConvertTo-SecureString "UserPass123!" -AsPlainText -Force
New-ADUser -Name "TestUser" -AccountPassword $userPassword -Enabled $true -Path "OU=Users,DC=MingTea,DC=local"
```

---

### C.3.2 Configure DNS Forwarders (for external name resolution)

| Field | Value / Your Entry |
|---|---|
| **Forwarder 1** | `8.8.8.8` *(Google DNS — change if your org requires different forwarders)* |
| **Forwarder 2** | `8.8.4.4` *(Google DNS secondary)* |

```powershell
Add-DnsServerForwarder -IPAddress "8.8.8.8" -PassThru
Add-DnsServerForwarder -IPAddress "8.8.4.4" -PassThru
```

---

### C.3.3 Ensure DNS Listens on All Interfaces

| Field | Value / Your Entry |
|---|---|
| **Listen address** | `"0.0.0.0"` *(listens on all interfaces — safe for a single-NIC DC)* |

```powershell
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\DNS\Parameters" -Name "ListenAddress" -Value @("0.0.0.0") -Type MultiString
Restart-Service DNS -Force
```

---

### C.3.4 Verify DNS is Working Locally

| Field | Value / Your Entry |
|---|---|
| **Domain name to query** | `MingTea.local` *(replace with your own domain name)* |
| **Expected result** | Returns the DC's local IP (`10.0.2.10`) |

```powershell
nslookup MingTea.local 127.0.0.1
```

---

## Part D: Verification from VPN Client

Ensure the WireGuard tunnel is **active** on your local machine before running these checks.

### D.1 Ping the Domain Controller

| Field | Value / Your Entry |
|---|---|
| **DC private IP** | `10.0.2.10` *(replace with your DC's actual private IP)* |
| **DC hostname** | `DC01.MingTea.local` *(replace with your DC name and domain)* |

```powershell
ping 10.0.2.10
ping DC01.MingTea.local
```

---

### D.2 Test DNS Resolution

| Field | Value / Your Entry |
|---|---|
| **Internal domain query** | `MingTea.local` *(replace with your domain — should return DC IP)* |
| **External domain query** | `google.com` *(or any public domain — tests that DC forwarders work)* |

```powershell
nslookup MingTea.local
nslookup google.com
```

---

### D.3 Test DNS Port Connectivity (TCP 53)

| Field | Value / Your Entry |
|---|---|
| **Target IP** | `10.0.2.10` *(your DC private IP)* |
| **Port** | `53` |
| **Expected result** | `TcpTestSucceeded : True` |

```powershell
Test-NetConnection -ComputerName 10.0.2.10 -Port 53
```

---

### D.4 Troubleshooting Checklist

If any of the above verifications fail, work through this checklist:

| Check | What to Verify |
|---|---|
| **WireGuard client DNS setting** | Must be DC's private IP (e.g. `10.0.2.10`) — not `8.8.8.8` |
| **Security group rules** | UDP/TCP port 53 must allow source `10.5.1.0/24` (VPN subnet) |
| **Windows Firewall on DC** | DNS ports should be open by default after DNS role install — verify if blocked |
| **DC static IP** | Confirm DC IP is `10.0.2.10` (or your chosen IP) and has not changed |
| **VPN AllowedIPs** | Must include your VPC CIDR (`10.0.0.0/16`) so DC traffic routes through the tunnel |
| **IP forwarding on Ubuntu** | Run `sysctl net.ipv4.ip_forward` — must return `1` |

---

## Phase 2 — Master Resource Log

Fill this in as you complete each section:

| Resource | Suggested Name | Your Custom Name | Value / ID *(fill in after creation)* |
|---|---|---|---|
| WireGuard server private key file | `server_private.key` | | *(file path on Ubuntu EC2)* |
| WireGuard server public key | *(auto-generated)* | | `<server-public-key>` |
| WireGuard client private key | *(auto-generated)* | | `<client-private-key>` |
| WireGuard client public key | *(auto-generated)* | | `<client-public-key>` |
| VPN server interface IP | `10.5.1.1/24` | | |
| VPN client tunnel IP | `10.5.1.2/24` | | |
| WireGuard listen port | `51820` | | |
| Ubuntu EC2 public IP *(Endpoint)* | *(Elastic IP)* | | `x.x.x.x` |
| DC computer name | `DC01` | | |
| DC private static IP | `10.0.2.10` | | |
| Active Directory domain name | `MingTea.local` | | |
| AD NetBIOS name | `MingTea` | | |
| Domain joiner account | `DomainJoiner` | | |
| Test user account | `TestUser` | | |
| DC Security Group | `AD-DomainController-SG` | | `sg-` |
