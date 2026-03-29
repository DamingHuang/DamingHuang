# Discord System Resource Monitor 🚨

A lightweight Python-based monitoring agent designed to track system CPU and Memory utilization in real-time. It automatically pushes alerts to a Discord channel via Webhooks when resource thresholds are exceeded.

## 🌟 Key Features
- **Real-time Monitoring**: Utilizes `psutil` to capture low-level system metrics.
- **Instant Alerting**: Integrated Discord Webhook support with formatted Embed messages.
- **Self-Healing Logic**: Includes a "Recovery" notification when resource pressure subsides.
- **Environment Isolation**: Configured for Python Virtual Environments (`venv`) for consistent deployment.
- **Safe Config**: Uses a decoupled `config.json` to keep sensitive Webhook URLs out of the source code.
### 1. Clone the repository
```bash
# Clone the project from GitHub
git clone [https://github.com/daminghuang/sre-monitor-bot.git](https://github.com/daminghuang/sre-monitor-bot.git)

# Enter the project directory
cd sre-monitor-bot/scripts

```

## 🛠 Prerequisites
- Python 3.x
- A Discord Webhook URL
## 🚀 Quick Start

### 1. Environment Setup
```bash
# Create a virtual environment
python3 -m venv venv

# Activate the environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate

# Install dependencies
pip install requests psutil

```

### 2. Configuration
Create a `config.json` file in the project root and add your details:

```json
{
  "cpu_threshold": 20,
  "mem_threshold": 20,
  "webhook_url": "[https://discord.com/api/webhooks/your_id_here](https://discord.com/api/webhooks/your_id_here)"
}
```
### 3. Run the Monitor

```bash
python alert.py
```
