# 🧱 Project Overview

You're building a hybrid network where:

- **Windows Server 2025 EC2** acts as a **Domain Controller (Active Directory Domain Services - AD DS)**.
- **Ubuntu EC2** acts as a **VPN gateway (WireGuard)** to allow secure access from your local Windows 10 VM into the private network.
- The whole environment is isolated inside a custom **AWS VPC** with:
  - A **Public Subnet** (for the VPN server)
  - A **Private Subnet** (for the Domain Controller)

---
## 🏗 Architecture Diagram

```
Your Local Windows 10 VM
        |
        |  WireGuard VPN
        v
Ubuntu EC2 (VPN Gateway) [Public IP]
        |
        |  AWS VPC Private Network
        v
Windows Server 2025 EC2 (Domain Controller) [Private IP]
```
