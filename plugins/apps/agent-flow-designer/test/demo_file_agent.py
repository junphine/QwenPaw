import requests

def sync_call():
    res = requests.post(
        'http://127.0.0.1:8088/api/agent-flow-designer/workflows/0e1fcc76-25d1-4113-bf7e-e24c003601bf/run',
        json={"messages": [{"role": "user", "content": "你好，输入附件为: data.excel"}]}
    )

    data = res.json()['data']['result']
    blocks = data.split('\n')
    for line in blocks:
        print(line)
        print('\n')

def stream_call():
    res = requests.post(
        'http://127.0.0.1:8088/api/agent-flow-designer/workflows/0e1fcc76-25d1-4113-bf7e-e24c003601bf/execute/stream',
        json={"messages": [{"role": "user", "content": "你好，输入附件为: data.excel"}],'user_name':'default'}
    )

    data = res
    blocks = data
    for line in blocks:
        print(line)
        print('\n')

def stream_file_process_call():
    res = requests.post(
        'http://127.0.0.1:8088/api/agent-flow-designer/stream/file_process',
        json={"message": "你好，总结输入README.md附件",'user_name':'default', "files": ['D:/Code/copaw/plugins/apps/agent-flow-designer/README.md']}
    )

    data = res
    blocks = data
    for line in blocks:
        print(line)
        print('\n')

stream_file_process_call()