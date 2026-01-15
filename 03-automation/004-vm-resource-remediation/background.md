# VM Performance Sentinel: Windows Update Remediation

![Status](https://img.shields.io/badge/Status-Complete-brightgreen)
![Environment](https://img.shields.io/badge/Environment-Virtualized%20VM-blue)
![Category](https://img.shields.io/badge/Category-System%20Optimization-orange)

## 📖 Background & Technical Context

### The Challenge: Unpredictable Resource Contention
In high-performance virtualized environments, resource stability is critical. This project originated from a recurring issue where a **Virtual Machine (VM)** experienced severe, intermittent sluggishness. 

**Initial Diagnostics:**
Utilizing Task Manager and Resource Monitor, I identified massive spikes in **CPU and Disk I/O**. These spikes were traced directly to:
* **Windows Update Ecosystem:** Continuous background scanning.
* **Windows Search Indexer:** High I/O overhead during indexing cycles.

---

## 🔍 The Discovery: Windows "Self-Healing"
During the **Root Cause Analysis (RCA)**, it was discovered that a standard "Stop and Disable" approach was insufficient. Modern Windows installations utilize a "self-healing" architecture that treats disabled maintenance services as a system failure.

### Critical Services Identified:
| Service Name | Display Name | Role |
| :--- | :--- | :--- |
| `WaaSMedicSvc` | Windows Update Medic Service | Automatically repairs/re-enables disabled update components. |
| `UsoSvc` | Update Orchestrator Service | Triggers update scans and downloads without user consent. |

This architecture created a "tug-of-war" between administrator performance requirements and internal OS maintenance policies.

---

## 🛠️ The Strategy: Multi-Layered Remediation
To reclaim control over the VM, I developed a defense-in-depth strategy that bypasses standard UI limitations:

1.  **System Hardening:** Modifying the Registry and utilizing `PsExec` to bypass `SYSTEM`-level permissions. This effectively "locks" the backdoors the OS uses to restart tasks.
2.  **Task Orchestration:** Manually identifying and disabling persistent update tasks within the **Task Scheduler** hierarchy.
3.  **The Watchdog Enforcement:** Implementation of a persistent script layer to monitor service states and revert unauthorized changes in real-time.

---

## 🚀 The Result: Deterministic Performance
The "Watchdog" script serves as the final enforcer. By running at a frequent interval (e.g., every 5 minutes), it ensures hardware cycles remain dedicated to the primary workload.

> [!NOTE]
> **Key Outcome:** By immediately detecting and terminating re-initialized update scans, this approach successfully eliminated resource contention and restored long-term VM stability.

---

## 💻 Technical Implementation Logic
The enforcement layer follows a persistent loop logic to maintain the system state:

```powershell
# Conceptual Watchdog Logic
while ($true) {
    $TargetServices = "WaaSMedicSvc", "UsoSvc"
    foreach ($service in $TargetServices) {
        $status = Get-Service -Name $service
        if ($status.Status -eq 'Running') {
            Stop-Service -Name $service -Force
            Write-Output "Terminated $service at $(Get-Date)"
        }
    }
    Start-Sleep -Seconds 300
}
