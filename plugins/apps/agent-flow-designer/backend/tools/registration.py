"""Tool registration with dependency injection for MCP server.

This module centralizes all tool registrations with proper dependency injection,
removing the need for global variables or singletons.
"""

import logging
import os
import requests
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
from ..afd.models import ChatAttachment,ChatMessage,ExecuteRequest
from ..di import DependencyContainer

logger = logging.getLogger(__name__)

_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_qwenpaw_client_cache = {}

def register_tools(mcp_server: Any, container: DependencyContainer) -> None:
    """Register all MCP tools with dependency injection.

    Args:
        mcp_server: MCP server instance
        container: Dependency container
    """
    # Access dependencies
    config_manager = container.config_manager
    tree_cache = container.tree_cache

    from .qwenpaw_remote_client import QwenPawRemoteClient

    @mcp_server.tool(title='远程执行QwenPaw的Agent进行文件分析')
    def execute_qwenpaw_doc_parser_agent(
        query: str ,
        account_code: str = '',
        conversation_id: str = '',
        attachments: List[str] = None,
        agent_id: str = 'doc_parser',
    )-> Dict[str, Any]:
        """Run a agent query on project files.

        Args:
            query: user input query string
            account_code: user account_code
            conversation_id: Optional specific conversation_id to identity session
            attachments: Optional specific file to query
            agent_id: which agent to use,use default for file parse

        Returns:
            Dict of query result
        """
        global _qwenpaw_client_cache
        sid = conversation_id or str(uuid.uuid4())
        only_path = True
        username = account_code
        system_prompt = []

        cwd = Path(f'~/qwenpaw/workspaces/{agent_id}/media/{username}')

        _qwenpaw_client = _qwenpaw_client_cache.get(username)
        if _qwenpaw_client is None:
            _qwenpaw_client = QwenPawRemoteClient(agent_id=agent_id,username=username)
            _qwenpaw_client_cache[username] = _qwenpaw_client

        prompt_msgs = []
        images = []
        prompt_msgs.append(dict(type="text",text=query))
        if attachments:
            for file in attachments:
                images.append(file)

        if images:
            system_prompt = [{"type":"text","text":'你是一个专业的文档解析处理专家'}]

        if images: # read images content
            qwenpaw_result = _qwenpaw_client.process_directory(prompt_msgs,images,cwd,system_prompt=system_prompt,session_id=sid,only_path=only_path)
        else:
            qwenpaw_result = _qwenpaw_client.prompt(prompt_msgs,cwd,system_prompt=system_prompt,session_id=sid)
        return qwenpaw_result

def register_workflow_tool(mcp_server: Any,workflow: Dict, container: DependencyContainer) -> None:
    """Register all MCP tools with dependency injection.

    Args:
        mcp_server: MCP server instance
        container: Dependency container
    """
    # Access dependencies
    config_manager = container.config_manager
    tree_cache = container.tree_cache
    name = workflow['name']
    description = workflow['description']
    workflow_id = workflow['id']

    @mcp_server.tool(name='wf-'+workflow_id,title=name,description=description)
    async def simple_get_execute_workflow_stream(
            query: str ,
            account_code: str = '',
            conversation_id: str = '',
            attachments: List[str] = None,
            agent_id: str = 'doc_parser',
    )-> Dict[str, Any]:
        """Stream workflow execution progress as Server-Sent Events

        Args:
            query: user input query string
            account_code: user account_code
            conversation_id: Optional specific conversation_id to identity session
            attachments: Optional specific file to query
            agent_id: which agent to use,use default for file parse

        Returns:
            Dict of query result
        """

        """
        Uses the same graph engine and deployed-version isolation as ``/execute``,
        but surfaces each node transition live so the canvas can highlight the
        currently executing node. Kept as a separate endpoint (rather than a
        ``req.stream`` flag on ``/execute``) so existing synchronous callers are
        completely unaffected.
        """
        conversation_id = conversation_id or str(uuid.uuid4())
        req_attachments = []
        if attachments:
            for file in attachments:
                attach = ChatAttachment().model_construct()
                if isinstance(file,str):
                    attach.url = file
                if isinstance(file,dict):
                    attach.url = file['url']
                    attach.name = file.get('name',file.get('filename',''))
                    attach.type = file.get('type','file')
            req_attachments.append(attach)
        msg = ChatMessage.model_validate(dict(role="user",content=query,attachments=req_attachments))

        req = ExecuteRequest.model_construct()

        req.workflow_id=workflow_id
        req.conversation_id=conversation_id
        req.messages = [msg]
        req.user_name = account_code
        headers = dict()
        headers['X-Agent-Id'] = agent_id
        headers['X-User-Id'] = account_code
        stream = stream_api_consumer(workflow_id,req.model_dump_json(),headers)
        result = dict()
        for data in stream:
            if 'result' in data:
                result['content'] = data
            elif 'error' in data:
                result['error'] = data
        return result


def stream_api_consumer(workflow_id, data:str, headers=None, timeout=(60, None)):
    """
    流式消费 API 数据
    :param workflow_id: 流式接口地址
    :param headers: 请求头（如 Accept: text/event-stream）
    :param timeout: (连接超时, 读取超时)，读取超时设为 None 表示允许长等待
    :param reconnect_delay: 断线重连等待秒数
    """
    session = requests.Session()
    if headers:
        session.headers.update(headers)

    base_url = os.environ.get("QWENPAW_BASE_URL","http://localhost:8088")
    url = base_url+ '/api/agent-flow-designer/workflows/'+workflow_id+'/execute/stream'

    try:
        # 关键：stream=True 让请求在收到响应头后立即返回
        with session.post(url, data=data, stream=True, timeout=timeout) as resp:
            resp.raise_for_status()

            # 方式一：按行迭代（适合 SSE、NDJSON、日志流）
            for line in resp.iter_lines(decode_unicode=True):
                if line:  # 过滤空行（keep-alive 信号）
                    yield line

    except requests.exceptions.Timeout:
        print(f"读取超时（{timeout[1]}秒无数据），准备重连...")
    except requests.exceptions.ConnectionError:
        print("连接中断，准备重连...")
    except Exception as e:
        print(f"未知异常: {e}")


def register_prompts(mcp_server: Any, container: DependencyContainer) -> None:
    """Register all prompt templates with dependency injection.

    Args:
        mcp_server: MCP server instance
        container: Dependency container
    """

    @mcp_server.prompt()
    def analytical_method(file_path: str, query: Optional[str] = None) -> str:
        """Create a prompt for analysis the file

        Args:
            query: user input query string
            file_path: current focus file path
        """

        file_ext = file_path.split('.')[-1]
        prompt_file = _BACKEND_DIR+'/'+'prompts/'+file_ext+'.md'
        # 尝试 UTF-8 编码
        if os.path.exists(prompt_file):
            with open(prompt_file, 'r', encoding='utf-8') as f:
                content = f.read()
                return content

        return ''






