import psutil
import datetime
import shutil

print(f"\n===== System Health Check {datetime.datetime.now()} =====")

# ── CPU ──────────────────────────
cpu_percent = psutil.cpu_percent(interval=1)
cpu_cores = psutil.cpu_count()
print(f"\n[CPU]")
print(f"  Cores:   {cpu_cores}")
print(f"  Usage:   {cpu_percent}%")
if cpu_percent > 80:
    print(" WARNING: CPU usage too high!")
else:
    print(" Normal")

# ── Memory ───────────────────────
mem = psutil.virtual_memory()
mem_total = mem.total / (1024**3)
mem_used = mem.used / (1024**3)
mem_percent = mem.percent
print(f"\n[Memory]")
print(f"  Total:   {mem_total:.1f} GB")
print(f"  Used:    {mem_used:.1f} GB")
print(f"  Usage:   {mem_percent}%")
if mem_percent > 80:
    print(" WARNING: Memory usage too high!")
else:
    print(" Normal")

# ── Disk ─────────────────────────
total, used, free = shutil.disk_usage("/")
disk_total = total / (1024**3)
disk_used = used / (1024**3)
disk_free = free / (1024**3)
disk_percent = (used / total) * 100
print(f"\n[Disk]")
print(f"  Total:   {disk_total:.1f} GB")
print(f"  Used:    {disk_used:.1f} GB")
print(f"  Free:    {disk_free:.1f} GB")
print(f"  Usage:   {disk_percent:.1f}%")
if disk_percent > 80:
    print("  ⚠️  WARNING: Disk usage too high!")
else:
    print("  ✅  Normal")

print(f"\n{'='*50}")
