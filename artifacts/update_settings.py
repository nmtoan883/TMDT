import os

with open('d:/TMDT/config/settings.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("'SEPAY_API_9f3a7c1e4b6d8a2f5c0e7b1d9a4c3e8f'", "os.environ.get('SEPAY_API_KEY', '')")
content = content.replace("'96247TV2OT'", "os.environ.get('SEPAY_ACCOUNT_NUMBER', '')")
content = content.replace("'BIDV'", "os.environ.get('SEPAY_BANK', 'BIDV')")
content = content.replace("'NGUYEN MINH TOAN'", "os.environ.get('SEPAY_ACCOUNT_NAME', '')")

with open('d:/TMDT/config/settings.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Replaced settings successfully.")
