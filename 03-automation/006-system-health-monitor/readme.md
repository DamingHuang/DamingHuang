cat > ~/sre-practice/README.md << 'EOF'
# SRE System Health Monitor

A lightweight system monitoring script built with Python, designed for SRE learning and practice.

## What it does
- Monitors CPU usage
- Monitors memory usage  
- Monitors disk usage
- Alerts when any metric exceeds 80%
- Runs automatically every minute via cron

## Requirements
```
pip install psutil
```

## Usage
```
python3 health_check.py
```

## Auto-run with cron
```
* * * * * python3 /home/your-user/sre-practice/health_check.py >> /home/your-user/sre-practice/system.log
```

## Skills demonstrated
- Python scripting for system operations
- Linux cron job scheduling
- SRE monitoring concepts (thresholds, alerting, logging)
EOF
