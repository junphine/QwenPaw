#!/usr/bin/env python3
"""调试插件提取逻辑"""
import subprocess

def test_extract():
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
    print(f"输出长度: {len(result.stdout)}")
    print(f"输出前500字符:\n{result.stdout[:500]}")
    print("\n" + "="*50)
    
    if result.returncode == 0:
        output = result.stdout.strip()
        lines = output.split('\n')
        response_lines = []
        in_content = False
        
        for line in lines:
            line_stripped = line.strip()
            if line_stripped.startswith('[SESSION:'):
                in_content = True
                print(f"找到SESSION行: {line_stripped}")
                continue
            if not in_content:
                continue
            if line_stripped == '---':
                print(f"找到分隔符，停止提取")
                break
            if line_stripped:
                response_lines.append(line)
        
        print(f"\n提取到 {len(response_lines)} 行")
        if response_lines:
            response_text = '\n'.join(response_lines).strip()
            print(f"提取结果:\n{response_text[:200]}...")
            print(f"\n是否模拟: {response_text.startswith('【')}")
            return response_text
        else:
            print("未能提取到内容")
            return None
    else:
        print(f"命令失败: {result.stderr}")
        return None

if __name__ == "__main__":
    test_extract()
