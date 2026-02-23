import secrets
import yaml
from pathlib import Path

def generate_key():
    new_key = secrets.token_urlsafe(32)
    config_path = Path("/mnt/work/py_works/external_projects/MartletMolt/Config/settings.yaml")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    if 'gateway' not in config:
        config['gateway'] = {}
    
    config['gateway']['device_key'] = new_key
    
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(config, f, allow_unicode=True, sort_keys=False)
    
    print(f"✅ 成功生成萬能鑰匙: {new_key}")
    print("已同步更新至 Config/settings.yaml")

if __name__ == "__main__":
    generate_key()
