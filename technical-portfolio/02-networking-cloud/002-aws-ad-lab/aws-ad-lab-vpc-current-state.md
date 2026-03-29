# AWS AD Lab — VPC Current State Reference

> This document captures the **actual deployed state** of the VPC as queried from the AWS CLI.
> Use this as your source of truth when troubleshooting or continuing setup in later phases.

---

## VPC Overview

| Field | Value |
|---|---|
| **VPC ID** | `vpc-0517d5e295a732156` |
| **CIDR Block** | `10.0.0.0/16` |
| **Region** | `us-east-1` |
| **Owner ID** | `457451358907` |

---

## Route Tables

### Route Table 1 — Public (`AD-Pub-RT`)

| Field | Value |
|---|---|
| **Route Table ID** | `rtb-08e60668585fd2dd0` |
| **Name tag** | `AD-Pub-RT` |
| **Main (default)** | No |
| **Associated Subnet** | `subnet-0a2f8ae111d156552` |
| **Association ID** | `rtbassoc-02a69631f5ec2f982` |

**Routes:**

| Destination | Target | Origin | State | Notes |
|---|---|---|---|---|
| `10.5.1.0/24` | `eni-08b26a902cf73aa76` (instance `i-080bb37f0130c9523`) | CreateRoute | ⚠️ `blackhole` | Instance no longer exists or ENI is detached — **needs fixing** |
| `10.0.0.0/16` | `local` | CreateRouteTable | ✅ `active` | Local VPC traffic |
| `0.0.0.0/0` | `igw-056478d77867b53a6` | CreateRoute | ✅ `active` | Internet access via IGW |

> ⚠️ **Blackhole route action required:** The route for `10.5.1.0/24` (WireGuard VPN subnet) is in a `blackhole` state. This means the Ubuntu VPN instance it pointed to no longer exists at that ENI. Once the VPN server (VPnUbuntu) is running, re-create this route pointing to the new instance or ENI.

---

### Route Table 2 — Main / Private (Unnamed)

| Field | Value |
|---|---|
| **Route Table ID** | `rtb-0c500fce31e3bf721` |
| **Name tag** | *(none — consider adding `AD-Private-RT`)* |
| **Main (default)** | Yes — applies to any subnet not explicitly associated with another route table |
| **Associated Subnet** | *(implicit — main table)* |

**Routes:**

| Destination | Target | Origin | State | Notes |
|---|---|---|---|---|
| `10.0.0.0/16` | `local` | CreateRouteTable | ✅ `active` | Local VPC traffic only |

> 📝 **No internet or NAT route present.** This is correct for a private subnet — instances here cannot initiate outbound internet traffic unless a NAT Gateway route (`0.0.0.0/0 → nat-xxx`) is added.

---

## Subnets

### Subnet 1 — Public (VPN Server)

| Field | Value |
|---|---|
| **Subnet ID** | `subnet-0a2f8ae111d156552` |
| **Name tag** | `Public Subnet (for VPN server)` |
| **CIDR Block** | `10.0.1.0/28` |
| **Available IPs** | `7` of 11 usable |
| **Availability Zone** | `us-east-1a` (`use1-az2`) |
| **VPC ID** | `vpc-0517d5e295a732156` |
| **Auto-assign Public IP** | No (`MapPublicIpOnLaunch: false`) |
| **Associated Route Table** | `rtb-08e60668585fd2dd0` (`AD-Pub-RT`) |
| **Internet Gateway Blocking** | Off |

> ⚠️ **Tag conflict:** This subnet has two conflicting tags — `Name: "Public Subnet (for VPN server)"` and a tag key `"Private Subnet"` with an empty value. The `"Private Subnet"` tag should be deleted in the AWS Console to avoid confusion.

> 📝 **CIDR note:** This subnet is `/28` (16 IPs, 11 usable). The original Phase 1 plan used `/24` (256 IPs, 251 usable). For a lab environment with a small number of instances this is fine, but if you plan to add more resources to this subnet, consider whether `/28` is sufficient.

---

### Subnet 2 — Private (Windows Server / Domain Controller)

| Field | Value |
|---|---|
| **Subnet ID** | `subnet-048bc52084885ebae` |
| **Name tag** | `AD-Winsvr-Ubuntu` |
| **CIDR Block** | `10.0.2.0/28` |
| **Available IPs** | `10` of 11 usable |
| **Availability Zone** | `us-east-1a` (`use1-az2`) |
| **VPC ID** | `vpc-0517d5e295a732156` |
| **Auto-assign Public IP** | No (`MapPublicIpOnLaunch: false`) |
| **Associated Route Table** | `rtb-0c500fce31e3bf721` (main/default — no explicit association) |
| **Internet Gateway Blocking** | Off |

---

## Internet Gateway

| Field | Value |
|---|---|
| **Internet Gateway ID** | `igw-056478d77867b53a6` |
| **Name tag** | `AD-Winsvr-Ubuntu` |
| **Attachment State** | `available` |
| **Attached VPC** | `vpc-0517d5e295a732156` |
| **Owner ID** | `457451358907` |

> 📝 **Naming note:** The IGW is tagged `AD-Winsvr-Ubuntu` which matches a subnet name rather than the gateway itself. Consider renaming it to `AD-IGW` in the console for clarity.

---

## Security Groups

### Security Group 1 — Default

| Field | Value |
|---|---|
| **Group ID** | `sg-0ee29a518a5dbb9e1` |
| **Group Name** | `default` |
| **Description** | Default VPC security group |
| **VPC ID** | `vpc-0517d5e295a732156` |

**Inbound Rules:**

| Protocol | Port | Source | Notes |
|---|---|---|---|
| All traffic | All | `sg-0ee29a518a5dbb9e1` *(self)* | Allows all traffic only from within this same security group |

**Outbound Rules:**

| Protocol | Port | Destination | Notes |
|---|---|---|---|
| All traffic | All | `0.0.0.0/0` | Allows all outbound traffic |

> ⚠️ **Best practice:** The default security group should not be attached to any instances. Leave it unused — it exists as a VPC default only.

---

### Security Group 2 — AD-DC-SG

| Field | Value |
|---|---|
| **Group ID** | `sg-078968af2967efd66` |
| **Group Name** | `AD-DC-SG` |
| **Description** | `launch-wizard-5 created 2026-01-03T02:18:46.458Z` |
| **VPC ID** | `vpc-0517d5e295a732156` |

**Inbound Rules:**

| Protocol | Port(s) | Source | Service / Description |
|---|---|---|---|
| All traffic | All | `10.0.0.0/16` | All internal VPC traffic |
| TCP | 22 | `98.116.74.198/32` | SSH — your public IP |
| TCP | 3389 | `98.116.74.198/32` | RDP — your public IP |
| UDP | 51820 | `98.116.74.198/32` | WireGuard VPN — your public IP |
| TCP | 53 | `10.5.1.0/24` | DNS (TCP) from VPN subnet |
| UDP | 53 | `10.5.1.0/24` | DNS (UDP) from VPN subnet |
| TCP | 135 | `10.5.1.0/24` | RPC Endpoint Mapper |
| TCP | 389 | `10.5.1.0/24` | LDAP |
| TCP | 445 | `10.5.1.0/24` | SMB |
| TCP | 636 | `10.5.1.0/24` | LDAPS (Secure LDAP) |
| TCP | 65535 | `10.5.1.0/24` | RPC Dynamic Ports |
| UDP | 88 | `10.5.1.0/24` | Kerberos |
| UDP | 137 | `10.5.1.0/24` | NetBIOS Name Service |

**Outbound Rules:**

| Protocol | Port | Destination | Notes |
|---|---|---|---|
| All traffic | All | `0.0.0.0/0` | Allows all outbound traffic |

> ⚠️ **Dynamic IP warning:** `98.116.74.198/32` is your personal public IP hardcoded into three rules (SSH/22, RDP/3389, WireGuard/51820). If your ISP assigns a dynamic IP, these rules will stop working when your IP changes. Update them in the console whenever your public IP changes.

> 📝 **Description note:** The auto-generated description `launch-wizard-5 created 2026-01-03...` should be updated to something meaningful like `"AD Domain Controller and VPN Server security group"` for easier identification.

---

## Issues & Action Items (Updated)

| # | Severity | Issue | Action Required |
|---|---|---|---|
| 1 | ⚠️ High | Route `10.5.1.0/24` in `AD-Pub-RT` is `blackhole` | Re-create route once VPnUbuntu is running — point to new ENI or instance ID |
| 2 | ⚠️ Medium | `98.116.74.198/32` hardcoded in `AD-DC-SG` for SSH/RDP/WireGuard | Update these three rules whenever your public IP changes |
| 3 | 🔵 Low | `subnet-0a2f8ae111d156552` has conflicting tags (`"Private Subnet"` key with empty value) | Delete the `"Private Subnet"` tag in EC2 Console → Subnets → Tags tab |
| 4 | 🔵 Low | IGW named `AD-Winsvr-Ubuntu` — conflicts with subnet of same name | Rename to `AD-IGW` in EC2 Console → Internet Gateways |
| 5 | 🔵 Low | Private route table (`rtb-0c500fce31e3bf721`) has no name tag | Add name tag `AD-Private-RT` for clarity |
| 6 | 🔵 Low | `AD-DC-SG` description is auto-generated launch wizard text | Update to a meaningful description |
| 7 | 📝 Note | Both subnets are `/28` instead of `/24` planned in Phase 1 | No action needed unless you exceed 11 instances per subnet |

---

## CLI Commands Used

```bash
# Route tables
aws ec2 describe-route-tables --filters "Name=vpc-id,Values=vpc-0517d5e295a732156"

# Subnets
aws ec2 describe-subnets --filters "Name=vpc-id,Values=vpc-0517d5e295a732156"

# Internet Gateway
aws ec2 describe-internet-gateways --filters "Name=attachment.vpc-id,Values=vpc-0517d5e295a732156"

# Security Groups
aws ec2 describe-security-groups --filters "Name=vpc-id,Values=vpc-0517d5e295a732156"
```

---

## Fix: Repair the Blackhole Route (run after VPnUbuntu is back online)

| Field | Value / Your Entry |
|---|---|
| **Route table to update** | `rtb-08e60668585fd2dd0` (`AD-Pub-RT`) |
| **Destination to replace** | `10.5.1.0/24` |
| **New target — Instance ID** | `i-xxxxxxxxxxxx` *(new VPnUbuntu instance ID)* |

```bash
# Step 1 — Delete the blackhole route
aws ec2 delete-route \
  --route-table-id rtb-08e60668585fd2dd0 \
  --destination-cidr-block 10.5.1.0/24

# Step 2 — Re-create it pointing to the new VPN instance
aws ec2 create-route \
  --route-table-id rtb-08e60668585fd2dd0 \
  --destination-cidr-block 10.5.1.0/24 \
  --instance-id i-xxxxxxxxxxxx
# Replace i-xxxxxxxxxxxx with your new VPnUbuntu instance ID
```
