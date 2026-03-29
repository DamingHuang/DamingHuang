import json
import requests
import time
import os
import glob

def load_config(file_path):
    """Intelligently load config file, auto-handle different encodings"""
    try:
        # Method 1: Try UTF-8
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except UnicodeDecodeError:
        # Method 2: Try UTF-8-sig (handle BOM)
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                return json.load(f)
        except:
            # Method 3: Try UTF-16
            try:
                with open(file_path, 'r', encoding='utf-16') as f:
                    return json.load(f)
            except:
                # Method 4: Last resort - auto-detect encoding
                import chardet
                with open(file_path, 'rb') as f:
                    raw_data = f.read()
                    result = chardet.detect(raw_data)
                    encoding = result['encoding']
                    if encoding:
                        return json.loads(raw_data.decode(encoding))
                    else:
                        raise Exception("Unable to detect file encoding")
    except Exception as e:
        print(f"❌ Configuration Error: {e}")
        print(f"💡 Hint: Please ensure config.json exists and has correct format")
        return None

def send_discord_alert(webhook_url, message, color=15158332):
    payload = {
        "embeds": [{
            "title": "🚨 Cleanup Log Alert",
            "description": message,
            "color": color,
            "footer": {"text": f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}"}
        }]
    }
    try:
        resp = requests.post(webhook_url, json=payload, timeout=5)
        if resp.status_code == 204:
            print("✅ Discord message delivered")
        else:
            print(f"⚠️ Discord returned: {resp.status_code}")
    except Exception as e:
        print(f"❌ Failed to send alert: {e}")

def monitor_log(log_path):
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "config.json")
    
    # Load configuration
    config = load_config(config_path)
    if not config:
        print("❌ Failed to load config file, please check config.json")
        return
    
    print("🚀 Starting log processing...")
    print(f"📁 File: {log_path}")
    
    try:
        # Check if file exists
        if not os.path.exists(log_path):
            print(f"❌ Log file does not exist: {log_path}")
            return
        
        with open(log_path, "r", encoding="utf-8", errors='ignore') as f:
            lines = f.readlines()
        
        print(f"📄 Found {len(lines)} log lines")
        
        for line in lines:
            print(f"Processing: {line.strip()}")
            
            if "❌" in line or "failed" in line.lower():
                send_discord_alert(
                    config['webhook_url'],
                    f"Error detected:\n```{line.strip()}```",
                    color=15158332
                )
            elif "🔁" in line or "reboot" in line.lower():
                send_discord_alert(
                    config['webhook_url'],
                    f"Reboot required:\n```{line.strip()}```",
                    color=16776960
                )
            elif "✅" in line:
                send_discord_alert(
                    config['webhook_url'],
                    f"Success:\n```{line.strip()}```",
                    color=3066993
                )
        
        print(f"✅ Processing completed! Processed {len(lines)} log lines")
        
    except Exception as e:
        print(f"⚠️ Error reading log: {e}")

if __name__ == "__main__":
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Find the latest log file
    log_files = glob.glob(os.path.join(script_dir, "cleanup_log_*.txt"))
    
    if log_files:
        # Find the most recently modified log file
        latest_log = max(log_files, key=os.path.getmtime)
        print(f"📂 Found latest log: {os.path.basename(latest_log)}")
        monitor_log(latest_log)
    else:
        print("❌ No cleanup_log_*.txt files found!")
        print(f"📁 Please place log files in {script_dir} directory")
        print("💡 Hint: You can create an empty test log file first")	
