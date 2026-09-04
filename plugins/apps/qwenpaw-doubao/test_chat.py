#!/usr/bin/env python3
"""测试智能体调用"""
import subprocess

prompt = "你是正方辩手。辩题：测试\n\n你好\n\n请直接输出观点（200字内）："

print("测试智能体调用...")
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
print(f"标准输出:\n{result.stdout}")
print(f"标准错误:\n{result.stderr}")

# 提取回复
if result.returncode == 0:
    output = result.stdout.strip()
    lines = output.split('\n')
    response_lines = []
    found_content = False
    
    for line in reversed(lines):
        line = line.strip()
        if line.startswith('INFO:') or line.startswith('[') or line.startswith('Using session'):
            if found_content:
                break
            continue
        if len(line) > 5:
            response_lines.insert(0, line)
            found_content = True
    
    if response_lines:
        response_text = '\n'.join(response_lines)
        print(f"\n提取的回复: {response_text}")
    else:
        print("\n未能提取回复")
