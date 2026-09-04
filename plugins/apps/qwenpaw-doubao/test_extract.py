#!/usr/bin/env python3
"""测试提取逻辑"""
import subprocess

prompt = "你是正方辩手。辩题：AI会不会取代人类的工作?\n\n请介绍正方观点\n\n请直接输出观点（200字内）："

result = subprocess.run(
    ["qwenpaw", "agents", "chat",
     "--from-agent", "default",
     "--to-agent", "default",
     "--text", prompt],
    capture_output=True,
    text=True,
    timeout=60
)

print(f"返回码: {result.returncode}")
print(f"输出:\n{result.stdout}")
print("\n" + "="*50)

# 新提取逻辑
if result.returncode == 0:
    lines = result.stdout.split('\n')
    response_lines = []
    in_content = False
    
    for line in lines:
        line_stripped = line.strip()
        if line_stripped.startswith('[SESSION:'):
            in_content = True
            continue
        if not in_content:
            continue
        if line_stripped == '---':
            break
        if line_stripped:
            response_lines.append(line)
    
    if response_lines:
        response_text = '\n'.join(response_lines).strip()
        print(f"提取结果:\n{response_text}")
        print(f"是否模拟: {response_text.startswith('【')}")
    else:
        print("未能提取")
