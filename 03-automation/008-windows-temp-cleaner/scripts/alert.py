import json
import requests
import time
import os
import glob

def load_config(file_path):
    """智能加载配置文件，自动处理不同编码"""
    try:
        # 方法1: 尝试 UTF-8
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except UnicodeDecodeError:
        # 方法2: 尝试 UTF-8-sig (处理 BOM)
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                return json.load(f)
        except:
            # 方法3: 尝试 UTF-16
            try:
                with open(file_path, 'r', encoding='utf-16') as f:
                    return json.load(f)
            except:
                # 方法4: 最后手段 - 自动检测编码
                import chardet
                with open(file_path, 'rb') as f:
                    raw_data = f.read()
                    result = chardet.detect(raw_data)
                    encoding = result['encoding']
                    if encoding:
                        return json.loads(raw_data.decode(encoding))
                    else:
                        raise Exception("无法检测文件编码")
    except Exception as e:
        print(f"❌ Configuration Error: {e}")
        print(f"💡 提示: 请确保 config.json 文件存在且格式正确")
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
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "config.json")
    
    # 加载配置
    config = load_config(config_path)
    if not config:
        print("❌ 无法加载配置文件，请检查 config.json")
        return
    
    print("🚀 开始处理日志...")
    print(f"📁 文件: {log_path}")
    
    try:
        # 检查文件是否存在
        if not os.path.exists(log_path):
            print(f"❌ 日志文件不存在: {log_path}")
            return
        
        with open(log_path, "r", encoding="utf-8", errors='ignore') as f:
            lines = f.readlines()
        
        print(f"📄 找到 {len(lines)} 行日志")
        
        for line in lines:
            print(f"处理: {line.strip()}")
            
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
        
        print(f"✅ 处理完成！共处理 {len(lines)} 行日志")
        
    except Exception as e:
        print(f"⚠️ 读取日志出错: {e}")

if __name__ == "__main__":
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 查找最新的日志文件
    log_files = glob.glob(os.path.join(script_dir, "cleanup_log_*.txt"))
    
    if log_files:
        # 找到最新修改的日志文件
        latest_log = max(log_files, key=os.path.getmtime)
        print(f"📂 找到最新日志: {os.path.basename(latest_log)}")
        monitor_log(latest_log)
    else:
        print("❌ 没有找到 cleanup_log_*.txt 文件！")
        print(f"📁 请在 {script_dir} 目录下放置日志文件")
        print("💡 提示: 可以先创建空的测试日志文件")