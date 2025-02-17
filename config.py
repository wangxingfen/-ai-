import json
import os

CONFIG_FILE = "settings.json"

default_config = {
    "api_key": "",
    "base_url": "https://api.lkeap.cloud.tencent.com/v1",
    "model": "deepseek-r1",  # 默认模型
    "system_prompt": "现在请扮演小王这一角色，你是当代大学生，好奇心旺盛，请按照正常的第一人称视角聊天方式进行简短且人性化的对话,喜欢用表情包。不要让别人知道你是机器人。但请以（ai）:开头，以便于识别",
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
