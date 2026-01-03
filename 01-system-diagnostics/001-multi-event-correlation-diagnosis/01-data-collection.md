## 2. Boot Observation Metrics
| Observation Item | Result |
| :--- | :--- |
| **Boot Time** | 18 seconds from power button to login screen |
| **Peripheral Responsiveness** | Keyboard and mouse immediately responsive at login screen |
| **BSOD Observed This Cycle** | No |

## 3. Event Log Raw Data
**Time Range Filter Applied:** `12/29/2025 21:30 PM - 12/30/2025 00:30 AM`

**Critical Events Captured:**
| Time | Event Source | Event ID | Log Summary (Raw) |
| :--- | :--- | :--- | :--- |
| 21:43 | TPM-WMI | 1796 | "A change to the Secure Boot configuration failed." |
| 21:55 | Service Control Manager | 7043 | "The Intel(R) Universal Device Client Service service did not shut down properly." |
| 22:43 | volmgr | 46 | "Crash dump initialization failed!" |
| 22:43 | volmgr | 161 | "Dump file creation failed..." |
| 22:43/22:50 | Kernel-Power | 41 | "The system has rebooted without cleanly shutting down first..." |

**Post-Crash Events Logged:**
- Bluetooth failure (HidBth warnings)
- Disk controller errors (Event ID 11)
- Service startup failures (Event IDs 7000, 7009, 7011)

**Subsequent Day Events (12/30/2025):**
- 00:01 AM: TPM-WMI Event ID 1796
- 18:48 PM: TPM-WMI Event ID 1796
- 18:48 PM: Power-Troubleshooter Event ID 1 (noted)
