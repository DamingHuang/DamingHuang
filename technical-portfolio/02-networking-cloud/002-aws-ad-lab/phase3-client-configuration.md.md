# AWS AD Lab — Phase 3: Client Configuration (Local Windows 10)

> **How to read this guide:**
> - **Field** — the exact label or setting you are configuring.
> - **Value / Your Entry** — what to type or select. Suggested names are shown as examples. Fill in your own where indicated.
> - Scripts and config blocks are shown on the line **below** the description table.
> - Anywhere you see `"your-value-here"` inside a config — **replace it with your own value** before saving.

---

## 3.1 Install WireGuard Client

| Field | Value / Your Entry |
|---|---|
| **Download URL** | https://www.wireguard.com/install/ |
| **Platform** | Windows 10 (x64) |
| **Action** | Download the installer → run it → complete the installation wizard |

---

## 3.2 Create the Client Configuration File

| Field | Value / Your Entry |
|---|---|
| **Config file name** | `client.conf` *(e.g. `mylab-client.conf` — any `.conf` name works)* |
| **PrivateKey** | Paste your client's private key *(generated in Phase 2, Step A.3)* |
| **Address** | `10.5.1.2/32` *(your client's VPN IP — must match `AllowedIPs` on the server peer entry)* |
| **DNS (primary)** | `10.0.2.10` *(⚠️ your Domain Controller's private IP — required for `adlab.local` resolution)* |
| **DNS (fallback)** | `8.8.8.8, 1.1.1.1` *(public fallback — used if DC is unreachable)* |
| **PublicKey** | Paste your server's public key *(from `/etc/wireguard/server_public.key` on Ubuntu)* |
| **AllowedIPs** | `0.0.0.0/0` *(routes ALL traffic through the VPN tunnel)* |
| **Endpoint** | `<your-ubuntu-elastic-ip>:51820` *(public/Elastic IP of Ubuntu EC2 + WireGuard port)* |
| **PersistentKeepalive** | `25` *(sends a keepalive every 25 seconds — recommended behind NAT)* |

```ini
[Interface]
PrivateKey = <client-private-key>
Address = 10.5.1.2/32
DNS = 10.0.2.10, 8.8.8.8, 1.1.1.1

[Peer]
PublicKey = <server-public-key>
AllowedIPs = 0.0.0.0/0
Endpoint = <ubuntu-elastic-ip>:51820
PersistentKeepalive = 25
```

> ⚠️ Because `AllowedIPs = 0.0.0.0/0` routes **all** traffic through the VPN, your DNS setting is critical. If the DC IP is wrong here, all name resolution (including public sites) will break while the tunnel is active.

---

### Configuration Field Reference

| Field | What it does |
|---|---|
| `PrivateKey` | Identifies this client to the server — keep this secret |
| `Address` | The IP address assigned to this client inside the VPN tunnel |
| `DNS` | Name servers used while tunnel is active — primary must be your DC |
| `PublicKey` | The server's identity — used to verify you're connecting to the right server |
| `AllowedIPs` | Which traffic is sent through the tunnel — `0.0.0.0/0` means everything |
| `Endpoint` | The server's public IP and port to connect to |
| `PersistentKeepalive` | Keeps the tunnel open through NAT (sends a packet every N seconds) |

---

## 3.3 Import Configuration into WireGuard

| Step | Action |
|---|---|
| **1** | Open the **WireGuard** application on Windows 10 |
| **2** | Click **"Import tunnel(s) from file"** |
| **3** | Browse to and select your `client.conf` file |
| **4** | Click **"Activate"** to bring the tunnel up |

> ✅ The tunnel status should change to **Active**. You can verify DNS is correct by running in PowerShell:

```powershell
Get-DnsClientServerAddress -InterfaceAlias "client"
```

> The output should show `10.0.2.10` (your DC IP) as the IPv4 DNS server — not `8.8.8.8`.

---

## 3.4 Update the Ubuntu Server Config (`wg0.conf`)

Whenever you add a new client (peer), you must update `/etc/wireguard/wg0.conf` on the Ubuntu server and restart WireGuard.

### 3.4.1 Open the Config File for Editing

| Field | Value / Your Entry |
|---|---|
| **File path** | `/etc/wireguard/wg0.conf` |
| **Editor** | `nano` *(or `vim`, your preference)* |

```bash
sudo nano /etc/wireguard/wg0.conf
```

---

### 3.4.2 Full Server Config Reference

| Field | Value / Your Entry |
|---|---|
| **PrivateKey** | Server's private key *(contents of `/etc/wireguard/server_private.key`)* |
| **Address** | `10.5.1.1/24` *(server's IP inside the VPN tunnel)* |
| **ListenPort** | `51820` *(UDP port WireGuard listens on — must be open in your security group)* |
| **Network interface (PostUp/PostDown)** | `ens5` *(verify with `ip a` — may be `eth0` on older Ubuntu AMIs)* |
| **Client 1 PublicKey** | Paste Client 1's public key *(e.g. from `/etc/wireguard/client1_public.key`)* |
| **Client 1 AllowedIPs** | `10.5.1.2/32` *(must match the `Address` in Client 1's config)* |
| **Client 2 PublicKey** | Paste Client 2's public key *(e.g. from `/etc/wireguard/client2_public.key`)* |
| **Client 2 AllowedIPs** | `10.5.1.3/32` *(must match the `Address` in Client 2's config)* |

```ini
[Interface]
PrivateKey = <server-private-key>
Address = 10.5.1.1/24
ListenPort = 51820

# Enable IP forwarding (NAT and routing)
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -t nat -A POSTROUTING -o ens5 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -t nat -D POSTROUTING -o ens5 -j MASQUERADE

# DNS forwarding for clients (optional — uncomment if needed)
#PostUp = iptables -t nat -A PREROUTING -i wg0 -p udp --dport 53 -j DNAT --to-destination 10.5.1.1
#PostDown = iptables -t nat -D PREROUTING -i wg0 -p udp --dport 53 -j DNAT --to-destination 10.5.1.1

[Peer]
# Client 1
PublicKey = <client-1-public-key>
AllowedIPs = 10.5.1.2/32

[Peer]
# Client 2
PublicKey = <client-2-public-key>
AllowedIPs = 10.5.1.3/32
```

> 💡 **To add more clients:** Add another `[Peer]` block with that client's public key and a unique `AllowedIPs` address (e.g. `10.5.1.4/32`, `10.5.1.5/32`, and so on).

---

### 3.4.3 Save and Restart WireGuard

After editing and saving the file (`Ctrl+O` → `Enter` → `Ctrl+X` in nano):

| Field | Value / Your Entry |
|---|---|
| **Service name** | `wg-quick@wg0` *(change `wg0` if your config file has a different name)* |

```bash
sudo systemctl restart wg-quick@wg0
sudo systemctl status wg-quick@wg0
```

---

### 3.4.4 Verify All Peers Are Visible

```bash
sudo wg
```

> You should see one entry per `[Peer]` block in your config. Each peer shows its public key and its `allowed ips`.

---

## Phase 3 — Client & Peer Summary Table

Fill this in for every client you add:

| Client | Tunnel Name | VPN IP (Address) | Public Key | Config File | Status |
|---|---|---|---|---|---|
| Client 1 *(local PC)* | `client` | `10.5.1.2/32` | `<client-1-public-key>` | `client.conf` | |
| Client 2 | *(your name)* | `10.5.1.3/32` | `<client-2-public-key>` | *(your file)* | |
| Client 3 | *(your name)* | `10.5.1.4/32` | *(to be generated)* | *(your file)* | |

---

## Phase 3 — Master Resource Log

| Resource | Suggested Value | Your Value |
|---|---|---|
| WireGuard install URL | `https://www.wireguard.com/install/` | |
| Client config file name | `client.conf` | |
| Client 1 VPN IP | `10.5.1.2/32` | |
| Client 2 VPN IP | `10.5.1.3/32` | |
| DNS — primary (DC IP) | `10.0.2.10` | |
| DNS — fallback 1 | `8.8.8.8` | |
| DNS — fallback 2 | `1.1.1.1` | |
| Ubuntu server VPN IP | `10.5.1.1/24` | |
| Ubuntu network interface | `ens5` *(verify with `ip a`)* | |
| WireGuard listen port | `51820` | |
| Ubuntu Elastic IP (Endpoint) | `<elastic-ip>` | |
