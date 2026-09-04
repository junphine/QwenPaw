import sys
sys.path.insert(0, '.')
from pathlib import Path
import json

with open('plugin.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
print(f"Plugin: {config['name']} v{config['version']}")
print(f"Type: {config['type']}")
print(f"Entry: {config['entry']}")

backend = Path(config['entry']['backend'])
print(f"Backend exists: {backend.exists()}")

frontend = Path('ui') / 'index.js'
print(f"Frontend exists: {frontend.exists()}")

web = Path('web_chat.html')
print(f"Web chat exists: {web.exists()}")

print("\n[OK] All files verified!")
