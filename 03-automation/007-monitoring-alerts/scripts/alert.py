import json
import requests
import psutil
import time

def load_config(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Configuration Error: {e}")
        return None

# The 'webhook_url' variable is used here; do not hardcode the URL directly
def send_discord_alert(webhook_url, message, color=15158332): 
    payload = {
        "embeds": [{
            "title": "🚨 System Resource Monitor Alert",
            "description": message,
            "color": color,
            "footer": {"text": f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}"}
        }]
    }
    try:
        # The webhook_url is automatically read from config.json and passed here
        resp = requests.post(webhook_url, json=payload, timeout=5)
        if resp.status_code == 204:
            print("✅ Discord message delivered")
        else:
            print(f"⚠️ Discord returned status code: {resp.status_code}")
    except Exception as e:
        print(f"❌ Failed to send alert: {e}")

def monitor():
    config = load_config('config.json')
    if not config: return
    
    already_alerted = False

    print("🚀 Monitoring script started...")
    while True:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent
        
        cpu_limit = config.get('cpu_threshold', 20)
        mem_limit = config.get('mem_threshold', 20)

        # Alert Trigger Logic
        if (cpu > cpu_limit or mem > mem_limit) and not already_alerted:
            msg = f"**CPU Usage**: {cpu}%\n**Memory Usage**: {mem}%"
            send_discord_alert(config['webhook_url'], msg)
            already_alerted = True
        
        # Recovery Logic
        elif cpu < (cpu_limit - 5) and mem < (mem_limit - 5) and already_alerted:
            send_discord_alert(config['webhook_url'], "✅ System resources have returned to normal", color=3066993)
            already_alerted = False

        print(f"[{time.strftime('%H:%M:%S')}] CPU: {cpu}% | MEM: {mem}%")
        time.sleep(60)

if __name__ == "__main__":
    monitor()
