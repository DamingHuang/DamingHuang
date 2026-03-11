# Discord System Resource Monitor 🚨

A lightweight Python-based monitoring agent designed to track system CPU and Memory utilization in real-time. It automatically pushes alerts to a Discord channel via Webhooks when resource thresholds are exceeded.

## 🌟 Key Features
- **Real-time Monitoring**: Utilizes `psutil` to capture low-level system metrics.
- **Instant Alerting**: Integrated Discord Webhook support with formatted Embed messages.
- **Self-Healing Logic**: Includes a "Recovery" notification when resource pressure subsides.
- **Environment Isolation**: Configured for Python Virtual Environments (`venv`) for consistent deployment.
- **Safe Config**: Uses a decoupled `config.json` to keep sensitive Webhook URLs out of the source code.

## 🛠 Prerequisites
- Python 3.x
- A Discord Webhook URL
