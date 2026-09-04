"""Disable all builtin tools for game NPC agents."""
import httpx

TOOL_NAMES = [
    'read_file', 'write_file', 'edit_file', 'grep_search', 'glob_search',
    'execute_shell_command', 'send_file_to_user', 'browser_use', 'web_search',
    'web_fetch', 'desktop_screenshot', 'view_image', 'view_video',
    'get_current_time', 'set_user_timezone', 'get_token_usage', 'list_agents',
    'chat_with_agent', 'submit_to_agent', 'check_agent_task', 'spawn_subagent',
    'materialize_skill', 'ast_search', 'pawgit', 'append_file', 'delegate_external_agent'
]

disabled_tools = {}
for name in TOOL_NAMES:
    disabled_tools[name] = {
        "name": name, "enabled": False, "description": "",
        "display_to_user": False, "async_execution": True, "icon": "", "config": {}
    }

agents = ['keeper', 'ling', 'xiaolu', 'mayor', 'game_master']
with httpx.Client(timeout=10) as client:
    for aid in agents:
        r = client.get(f'http://127.0.0.1:64987/api/agents/{aid}')
        if r.status_code != 200:
            print(f'{aid}: GET failed ({r.status_code})')
            continue
        cfg = r.json()
        cfg['tools'] = {'builtin_tools': disabled_tools}
        r2 = client.put(f'http://127.0.0.1:64987/api/agents/{aid}', json=cfg)
        print(f'{aid}: PUT {r2.status_code}')
