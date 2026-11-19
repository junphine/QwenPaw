# -*- coding: utf-8 -*-
"""Agent Flow Designer — PawApp backend.

A simplified agent workflow designer for the Agent Platform.

Persistence: a shared JSON file stored in the platform data directory
(``<QZAGENT_HOME>/data/agent-flow-designer/workflows.json`` or
``~/.qzagent/data/agent-flow-designer/workflows.json``).
Legacy data in ``<plugin_dir>/data/workflows.json`` is automatically
migrated on first access.
"""
import uuid

from fastapi import APIRouter, Depends, Header, Query
from main import *
from tools.qwenpaw_remote_client import QwenPawRemoteClient

class UserContext(BaseModel):
    user_id: Optional[str] = None
    user_code: Optional[str] = None
    account_code: Optional[str] = None
    account_name: Optional[str] = None
    email: Optional[str] = None
    wecom_id: Optional[str] = None
    dept_name: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    agent_id: str
    conversation_id: str
    internet: bool = False
    files: Optional[Any] = None
    user_context: Optional[UserContext] = None
    rewrite_history_turns: int = 3

@router.post("/stream/{agent_id}")
async def simple_post_execute_workflow_stream(
        agent_id: str,
        chat: ChatRequest,
        ctx: PawAppContext = Depends(get_scoped_ctx),
):
    """Stream workflow execution progress as Server-Sent Events.

    Uses the same graph engine and deployed-version isolation as ``/execute``,
    but surfaces each node transition live so the canvas can highlight the
    currently executing node. Kept as a separate endpoint (rather than a
    ``req.stream`` flag on ``/execute``) so existing synchronous callers are
    completely unaffected.
    """
    if agent_id=='file_process':
        agent_id = '0e1fcc76-25d1-4113-bf7e-e24c003601bf'

    attachments = []
    files = chat.files
    if files:
        if not isinstance(chat.files,list):
            files = [chat.files]

        for file in files:
            attach = ChatAttachment().model_construct()
            if isinstance(file,str):
                attach.url = file
            if isinstance(file,dict):
                attach.url = file['url']
                attach.name = file.get('name',file.get('filename',''))
                attach.type = file.get('type','file')
            attachments.append(attach)
    msg = ChatMessage.model_validate(dict(role="user",content=chat.message,attachments=attachments))

    req = ExecuteRequest.model_construct()
    if chat.user_context is not None:
        req.user_uid = chat.user_context.account_code
        req.user_name = chat.user_context.account_name

    req.workflow_id=agent_id
    req.conversation_id=chat.conversation_id
    req.messages = [msg]
    stream = await execute_workflow_stream(agent_id,req,False,ctx)
    return stream


@router.post("/run/{agent_id}")
def simple_post_execute_workflow_run(
        agent_id: str,
        chat: ChatRequest,
        ctx: PawAppContext = Depends(get_scoped_ctx),
):
    """Block run workflow execution progress as json result.

    Uses the same graph engine and deployed-version isolation as ``/execute``,
    but surfaces each node transition live so the canvas can highlight the
    currently executing node. Kept as a separate endpoint (rather than a
    ``req.stream`` flag on ``/execute``) so existing synchronous callers are
    completely unaffected.
    """
    attachments = []
    files = chat.files
    if files:
        if not isinstance(chat.files,list):
            files = [chat.files]

        for file in files:
            attach = ChatAttachment().model_construct()
            if isinstance(file,str):
                attach.url = file
            if isinstance(file,dict):
                attach.url = file['url']
                attach.name = file.get('name',file.get('filename',''))
                attach.type = file.get('type','file')
            attachments.append(attach)
    msg = ChatMessage.model_validate(dict(role="user",content=chat.message,attachments=attachments))

    req = ExecuteRequest.model_construct()
    if chat.user_context is not None:
        req.user_uid = chat.user_context.account_code
        req.user_name = chat.user_context.account_name

    req.workflow_id=agent_id
    req.conversation_id=chat.conversation_id
    req.messages = [msg]
    return execute_qwenpaw_client_block(agent_id,req,True,ctx)

@router.get("/stream/{agent_id}")
async def simple_get_execute_workflow_stream(
        agent_id: str,
        query: str = Query(),
        account_code: str = Query('default'),
        conversation_id: str = Query(None),
        file_url: str = Query(None),
        ctx: PawAppContext = Depends(get_scoped_ctx),
):
    """Stream workflow execution progress as Server-Sent Events.

    Uses the same graph engine and deployed-version isolation as ``/execute``,
    but surfaces each node transition live so the canvas can highlight the
    currently executing node. Kept as a separate endpoint (rather than a
    ``req.stream`` flag on ``/execute``) so existing synchronous callers are
    completely unaffected.
    """
    if agent_id=='file_process':
        agent_id = '0e1fcc76-25d1-4113-bf7e-e24c003601bf'

    conversation_id = conversation_id or str(uuid.uuid4())
    attachments = []
    if file_url:
        attach = ChatAttachment.model_construct()
        attach.url = file_url
        attachments.append(attach)
    msg = ChatMessage.model_validate(dict(role="user",content=query,attachments=attachments))

    req = ExecuteRequest.model_construct()

    req.workflow_id=agent_id
    req.conversation_id=conversation_id
    req.messages = [msg]
    req.user_uid = account_code
    req.user_name = account_code
    stream = await execute_workflow_stream(agent_id,req,False,ctx)
    return stream


@router.get("/run/{agent_id}")
def simple_get_execute_workflow_run(
        agent_id: str,
        query: str = Query(),
        account_code: str = Query('default'),
        conversation_id: str = Query(None),
        file_url: str = Query(None),
        ctx: PawAppContext = Depends(get_scoped_ctx),
):
    """Run workflow execution progress as json result.

    Uses the same graph engine and deployed-version isolation as ``/execute``,
    but surfaces each node transition live so the canvas can highlight the
    currently executing node. Kept as a separate endpoint (rather than a
    ``req.stream`` flag on ``/execute``) so existing synchronous callers are
    completely unaffected.
    """
    conversation_id = conversation_id or str(uuid.uuid4())
    attachments = []
    if file_url:
        attach = ChatAttachment.model_construct()
        attach.url = file_url
        attachments.append(attach)
    msg = ChatMessage.model_validate(dict(role="user",content=query,attachments=attachments))

    req = ExecuteRequest.model_construct()
    req.workflow_id=agent_id
    req.conversation_id=conversation_id
    req.messages = [msg]
    req.user_uid = account_code
    req.user_name = account_code
    return execute_qwenpaw_client_block(agent_id,req,True,ctx)

def execute_qwenpaw_client_block(
        agent_id: str,
        req: ExecuteRequest,
        only_path: bool = True,
        ctx: PawAppContext = Depends(get_scoped_ctx)):
    """
    :param agent_id:
    :param req: ExecuteRequest
    :param only_path: 只发送路径，不发送文件内容
    :return:
    """
    username = req.user_name or req.user_id
    sid = req.conversation_id
    system_prompt = []
    if True:
        system_prompt = [{"type":"text","text":'你是一个专业的文档解析处理专家'}]

    cwd = Path(f'~/qwenpaw/workspaces/{agent_id}/media/{username}')
    qwenpaw_client = QwenPawRemoteClient(agent_id=agent_id,username=username)
    prompt_msgs = []
    images = []
    for msg in req.messages:
        prompt_msgs.append(dict(type="text",text=msg.content))
        if msg.attachments:
            for file in msg.attachments:
                images.append(file.url)

    if images: # read images content
        qwenpaw_result = qwenpaw_client.process_directory(prompt_msgs,images,cwd,system_prompt=system_prompt,session_id=sid,only_path=only_path)
    else:
        qwenpaw_result = qwenpaw_client.prompt(prompt_msgs,cwd,system_prompt=system_prompt,session_id=sid)
    return qwenpaw_result

# ── PawApp instance ─────────────────────────────────────────────────
app = PawApp("Agent Flow Designer", app_id="agent-flow-designer")
app.include_router(router)

# The 'plugin' variable is what PluginLoader looks for.
plugin = app
