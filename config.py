import json
import os

CONFIG_FILE = "settings.json"

default_config = {
    "api_key": "",
    "base_url": "https://api.lkeap.cloud.tencent.com/v1",
    "model": "deepseek-r1",  # 默认模型
    "system_prompt": "现在请扮演小王这一角色...",
    "whitelist": []
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default_config.copy()

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
