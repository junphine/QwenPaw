# -*- coding: utf-8 -*-
"""Tool invocation: platform / mcp / http, with SSRF and secret guards.

Host service resolution, the three invocation paths, output rendering,
credential-name validation and the DNS-pinning SSRF guard. The
PolicyGuardedTool governance steps in ``_invoke_platform_tool`` reproduce the
agent loop verbatim — the gate is authoritative and fails closed.

``_interpolate_template`` lives in ``afd/nodes.py``; nodes injects it into
this module's globals at import time (``tools._interpolate_template = ...``)
so ``_invoke_http_tool`` keeps its body byte-identical.
"""

import asyncio
import ipaddress
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from qwenpaw.pawapp import PawAppContext

from engine import ExecutionState, get_logger

from .routing import _resolve_variable_ex

logger = get_logger(__name__)


async def _build_tool_services(ctx: Optional[PawAppContext]) -> dict:
    """Resolve the live host handles a tool node needs, once per run.

    Returns ``{}`` when there is no authenticated context or no workspace: a
    platform/mcp tool node then fails with a readable message rather than
    half-working. Re-resolved on resume, because a paused run's handles died
    with the process that paused it (and the snapshot must stay JSON-safe).
    """
    if ctx is None:
        return {}
    workspace = await ctx._get_workspace()  # pylint: disable=protected-access
    if workspace is None:
        return {}
    agent_id = str(getattr(workspace, "agent_id", "") or getattr(ctx, "agent_id", "") or "")
    agent_config = None
    try:
        from qwenpaw.config.config import load_agent_config

        agent_config = load_agent_config(agent_id or "default")
    except Exception:  # noqa: BLE001  (agent-less workspaces still list tools)
        logger.debug("[tool services] agent config unavailable", exc_info=True)
    return {
        "workspace": workspace,
        "local_workspace": getattr(workspace, "local_workspace", None),
        "driver_manager": getattr(workspace, "driver_manager", None),
        "agent_config": agent_config,
        "agent_id": agent_id,
        "user_id": str(getattr(ctx, "user_id", "") or ""),
    }


def _build_tool_request_context(services: dict, state: ExecutionState) -> dict:
    """The request context handed to host tools, attributed to this run.

    ``session_id`` names the workflow execution so an approval card (should the
    host ever escalate inside ``__call__``) has a session to point at.
    """
    return {
        "agent_id": services.get("agent_id", ""),
        "user_id": services.get("user_id", ""),
        "session_id": f"workflow:{state.execution_id}",
        "channel": "workflow",
    }


class ToolApprovalRequired(Exception):
    """Governance decided ASK for a workflow tool call.

    Carries the question a human must answer. The ``tool`` handler turns it into
    a ``WF_PAUSE`` event, because the blocking chat approval the host uses has
    no place inside a workflow run: it would park the SSE connection on a card
    nobody in the canvas is watching.
    """

    def __init__(self, message: str, *, question: str = "") -> None:
        super().__init__(message)
        self.question = question


#: The three worlds a tool node can reach. One node type, not three types.
_TOOL_SOURCES = frozenset({"platform", "mcp", "http"})


def _resolve_tool_source(config: dict) -> str:
    """The tool node's source; legacy configs (only ``toolName``) mean platform."""
    raw = str(config.get("source") or "").strip().lower()
    return raw or "platform"


def _resolve_tool_params(config: dict, context: dict, node_outputs: dict) -> dict:
    """Turn the structured ``params`` bindings into a plain argument dict.

    platform / mcp take typed arguments, so a binding is ``{name, valueType,
    value}`` with ``valueType == "variable"`` resolved through the same
    reference engine the agent nodes use. Old nodes stored a bare mapping of
    literals; that shape is still accepted.
    """
    raw = config.get("params")
    resolved: Dict[str, Any] = {}
    if isinstance(raw, dict):
        resolved.update(raw)
        return resolved
    for item in raw or []:
        if not isinstance(item, dict):
            # R23：坏绑定不能静默丢弃 —— 少一个参数会让工具在几层之外报"缺必填参数"，
            # 与本功能"未知来源/未解析引用/缺环境变量一律显式失败"的规则自相矛盾。
            raise ValueError(f"工具参数绑定不是对象：{item!r}")
        name = str(item.get("name") or "").strip()
        if not name:
            raise ValueError(f"工具参数绑定缺少参数名：{item!r}")
        # R22：与 _resolve_tool_source 对称归一化，导入的工作流 JSON 里 "Variable"
        # 不能被当成字面值，把引用串本身喂给工具。
        value_type = str(item.get("valueType") or "literal").strip().lower()
        if value_type == "variable":
            ref = str(item.get("value") or "").strip()
            value, found = _resolve_variable_ex(ref, context, node_outputs)
            if not found:
                raise ValueError(
                    f"工具参数「{name}」引用的变量未解析：{ref}"
                )
            resolved[name] = value
        else:
            resolved[name] = item.get("value")
    return resolved


def _tool_block_text(block: Any) -> str:
    """One content block's text, regardless of whether it is a dict or a model."""
    if isinstance(block, dict):
        return str(block.get("text") or "")
    return str(getattr(block, "text", "") or "")


def _render_tool_output(value: Any, output_format: str = "") -> str:
    """Render one tool result as the node's text output.

    Host tools return an agentscope ``ToolChunk`` / ``ToolResponse`` (content
    blocks + state), a driver returns an arbitrary value, and HTTP returns text.

    The state check is an **allow-list**, not a deny-list (控制者裁定 R19):
    ``ToolResultState`` is ``success | error | interrupted | denied | running``
    and ``ToolChunk.state`` defaults to ``RUNNING``, so enumerating only the two
    failure states we happened to think of would let a sandbox kill, a user
    cancel, or a partial/incremental chunk become node output. Anything the host
    has not declared ``success`` is a call that did not produce this result.
    A value with no ``state`` (a plain driver dict) is not a tool result at all
    and falls through to the JSON branch.
    """
    if isinstance(value, str):
        text = value
    else:
        state = getattr(value, "state", None)
        state_value = str(getattr(state, "value", state) or "").lower()
        blocks = list(getattr(value, "content", None) or [])
        if state_value and state_value != "success":
            detail = " / ".join(t for t in (_tool_block_text(b) for b in blocks) if t)
            # 只有真被策略拒绝才说"被拒绝"；error / interrupted / running 是执行失败，
            # 说成拒绝会把排查指向治理层（控制者裁定 R21）。
            label = "被拒绝" if state_value == "denied" else "失败"
            raise RuntimeError(f"工具执行{label}（{state_value}）：{detail[:200]}")
        parts: List[str] = []
        for block in blocks:
            block_text = _tool_block_text(block)
            if block_text:
                parts.append(block_text)
                continue
            source = block.get("source") if isinstance(block, dict) else getattr(block, "source", None)
            if source is not None:
                # DataBlock（截图/音频）走占位符，绝不落进下面的 json.dumps ——
                # 那会把整段 base64 写进 node_outputs、暂停快照与导出（控制者裁定 R20）。
                media = str(getattr(source, "media_type", None)
                            or (source.get("media_type") if isinstance(source, dict) else "")
                            or "")
                parts.append(f"[二进制结果{'：' + media if media else ''}]")
        text = "\n".join(parts) if parts else json.dumps(
            value, ensure_ascii=False, default=str
        )

    if output_format == "json":
        parsed = value if isinstance(value, (dict, list)) else None
        if parsed is None:
            try:
                parsed = json.loads(text)
            except Exception:  # noqa: BLE001  (reported, not swallowed)
                raise RuntimeError(f"工具结果不是 JSON，无法按 json 格式输出：{text[:200]}") from None
        return json.dumps(parsed, ensure_ascii=False, indent=2, default=str)
    return text


def _finish_tool_output(
    value: Any, output_format: str, parsed_out: Optional[dict]
) -> str:
    """Render like _render_tool_output, optionally handing back the object.

    A schema-checked tool node needs the parsed object, not a dumps-then-loads
    round trip. The capture is an out-param so _render_tool_output's own
    contract — and the five tests that lock it — stay untouched.
    """
    text = _render_tool_output(value, output_format)
    if parsed_out is not None and output_format == "json":
        parsed_out["value"] = (
            value if isinstance(value, (dict, list)) else json.loads(text)
        )
    return text


async def _invoke_platform_tool(
    config: dict,
    params: dict,
    services: dict,
    state: ExecutionState,
    *,
    approval_granted: bool = False,
    parsed_out: Optional[dict] = None,
) -> str:
    """Call a host built-in tool with governance intact.

    ``check_permissions`` is *not* part of ``PolicyGuardedTool.__call__`` — the
    agentscope permission engine calls it separately. So invoking a listed tool
    directly would skip policy evaluation, audit and sandbox assembly entirely.
    This function reproduces the four steps the agent loop performs and is the
    only place in the plugin that touches those private attributes.

    Its return value is an authoritative *gate*, not a sandbox assembler
    (控制者裁定 R26 第 1 条): anything but ``ALLOW`` fails closed here without
    running the tool. Its ASK branch parks the run on a chat approval card that
    nobody watches on the canvas, and its DENY branch is a human denial — either
    one executed anyway would be a governance bypass.

    Audit exactly once per call: DENY / ASK-not-approved / unrecognised record
    it here (those branches never reach ``check_permissions``); the executing
    branches let the gate record it, except the OFF short-circuit which returns
    before the host's audit — detectable because ``_qp_policy_decision`` is still
    ``None``, and only then do we back-fill one (裁定 R26 第 3 条).
    """
    from agentscope.permission import PermissionBehavior
    from qwenpaw.governance.policy import GovernanceAction
    from qwenpaw.security.tool_guard.execution_level import ToolExecutionLevel

    tool_name = str(config.get("toolName") or "").strip()
    if not tool_name:
        raise ValueError("工具节点未配置 toolName")
    # 三种来源共用同一个 outputFormat 语义：platform 不得比 mcp/http 少一个格式化能力。
    output_format = str(config.get("outputFormat") or "")
    local_ws = services.get("local_workspace")
    if local_ws is None:
        raise RuntimeError("无法访问宿主 Workspace，工具节点未执行任何操作")

    request_context = _build_tool_request_context(services, state)
    tools = await local_ws.list_tools(
        agent_config=services.get("agent_config"),
        agent_id=services.get("agent_id") or None,
        request_context=request_context,
    )
    tool = next((t for t in tools if getattr(t, "name", "") == tool_name), None)
    if tool is None:
        available = ", ".join(sorted(str(getattr(t, "name", "")) for t in tools)[:20])
        raise RuntimeError(
            f"当前 Agent（{services.get('agent_id', '')}）未启用工具「{tool_name}」。"
            f"可选工具：{available or '（无）'}"
        )
    tool._qp_raw_params = params
    governor = getattr(tool, "_qp_governor", None)
    if governor is None:
        return _finish_tool_output(await tool(**params), output_format, parsed_out)
        raise RuntimeError(
            f"治理层不可用，工具「{tool_name}」已按 fail-closed 策略拒绝执行"
        )

    # 1) 非阻塞预分类：assert_policy 是同步纯函数，绝不会停在审批等待里。
    #
    # 预分类必须与闸门用同一个**有效级别**，否则第 2 步的 fail-closed 只是把
    # "静默执行"换成"卡在审批卡上"（裁定 R26 第 2 条）。宿主在
    # _policy_tool_check_permissions 里先同步再评估（tool_adapter.py:323-324），
    # 有效级别 = request_context["approval_level"]（会话覆盖）优先 → agent profile
    # 兜底；这里用的是宿主自己的公共枚举同一个解析入口。工作流的请求上下文由
    # _build_tool_request_context 现造、不含 approval_level，所以只需要 agent_config，
    # 而 `agent_config` 缺失或没有 approval_level 时 from_config 按宿主默认 → AUTO。
    # F1 探索模式对工作流不会命中：宿主注册表按用户会话建键，工作流的 session_id
    # 形如 workflow:{execution_id}，因此这里不模仿 :296-303 的强制 STRICT，
    # 也不为此加任何防御代码。
    effective_level = ToolExecutionLevel.from_config(
        getattr(services.get("agent_config"), "approval_level", None)
    )
    tool._qp_raw_params = params          # noqa: SLF001  (spec §4.2 集中耦合)
    spec = tool._build_tc_spec()          # noqa: SLF001
    previous_level = governor.policy.execution_level
    governor.policy.execution_level = effective_level.value
    try:
        decision = governor.assert_policy(spec)
    finally:
        governor.policy.execution_level = previous_level
    action = getattr(decision, "action", None)

    # 2) 按决定行动。
    if action is GovernanceAction.DENY:
        governor.audit(spec, decision)
        raise RuntimeError(f"工具「{tool_name}」被策略拒绝：{decision.reason}")

    if action is GovernanceAction.ASK and not approval_granted:
        governor.audit(spec, decision)
        raise ToolApprovalRequired(
            f"工具「{tool_name}」需要人工审批：{decision.reason}",
            question=(
                f"是否允许执行工具「{tool_name}」？\n"
                f"策略理由：{decision.reason}\n"
                f"调用参数：{json.dumps(params, ensure_ascii=False, default=str)[:400]}\n"
                "（回复 批准 / 同意 / approve 予以放行；其他任何回答按拒绝处理）"
            ),
        )

    # 3) 下面三条路径都会真执行工具，共用同一段闸门逻辑。
    if action is GovernanceAction.ASK:
        # The human approved this exact call. ``approval_level`` in the request
        # context is the host's session-level override, and list_tools hands us a
        # fresh tool object, so setting it short-circuits only this invocation —
        # and only the "ask the user" step. The OFF branch still compiles a
        # sandbox_config for fail-closed tools, so isolation is not weakened.
        # (Recording a rule instead cannot work: a builtin_rules ASK is
        # deliberately not persisted on approval, so the node would pause again.)
        tool._qp_request_context = {**request_context, "approval_level": "off"}  # noqa: SLF001
    elif action not in (GovernanceAction.ALLOW, GovernanceAction.SANDBOX_FALLBACK):
        governor.audit(spec, decision)
        raise RuntimeError(
            f"工具「{tool_name}」的治理决定无法识别（{action}），已按拒绝处理：{decision.reason}"
        )

    # 闸门判定是权威结论，不是沙箱装配的副产品：非 ALLOW 一律 fail-closed，
    # 绝不调用 tool(**params)（裁定 R26 第 1 条）。
    permission = await tool.check_permissions(params, None)  # noqa: SLF001
    behavior = getattr(permission.behavior, "value", permission.behavior)
    if permission.behavior != PermissionBehavior.ALLOW:
        raise RuntimeError(
            f"工具「{tool_name}」的权限闸门判定为 {behavior}，已按 fail-closed 策略拒绝执行："
            f"{permission.message}"
        )
    # 宿主在正常路径先审计再写 _qp_policy_decision（:364/:367），OFF 短路则在写之前就
    # 返回（:311-317）。于是"宿主有没有记这笔账"有机械信号：还写着默认值就是没记，
    # 由我们补一次；否则宿主已记，不得重复（裁定 R26 第 3 条）。
    if getattr(tool, "_qp_policy_decision", None) is None:  # noqa: SLF001
        governor.audit(spec, decision)
    return _finish_tool_output(await tool(**params), output_format, parsed_out)


async def _invoke_mcp_tool(
    config: dict, params: dict, services: dict, state: ExecutionState,
    parsed_out: Optional[dict] = None,
) -> str:
    """Invoke one MCP capability through the host driver layer.

    Credentials stay in the driver card: AFD never sees, stores or forwards a
    key. The invocation returns a result object rather than raising, so a
    transport failure is an ordinary ``ok=False``.
    """
    from qwenpaw.drivers.capabilities import DriverInvocation

    capability_id = str(config.get("capabilityId") or "").strip()
    if not capability_id:
        raise ValueError("MCP 工具节点未配置 capabilityId")
    manager = services.get("driver_manager")
    if manager is None:
        raise RuntimeError("宿主 driver_manager 不可用，MCP 工具节点未执行")

    result = await manager.invoke_capability(
        DriverInvocation(
            capability_id=capability_id,
            payload=params,
            request_context=_build_tool_request_context(services, state),
        )
    )
    if not result.ok:
        raise RuntimeError(
            f"MCP 工具调用失败（{result.error_type}）：{result.message}"
        )
    return _finish_tool_output(result.value, str(config.get("outputFormat") or ""), parsed_out)


#: 一个节点吊住整条 SSE 是可观测的事故，所以超时钳到 120s。
_TOOL_TIMEOUT_MAX = 120.0
_HTTP_METHODS = frozenset({"GET", "POST", "PUT", "PATCH", "DELETE"})
_HTTP_BODY_LIMIT = 200_000

#: 工作流作者能引用的凭证变量只允许落在这个命名空间里。"只存变量名"挡不住
#: 填任意变量名：宿主进程环境里还有模型 Key、数据库口令、对象存储 AK/SK。
_SECRET_ENV_PREFIX = "AFD_HTTP_SECRET_"
_SECRET_ENV_NAME_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,127}")


def _checked_secret_env_name(env_name: str) -> str:
    """Return the name a workflow may read, or refuse before any request goes out."""
    if not _SECRET_ENV_NAME_RE.fullmatch(env_name):
        raise ValueError(
            f"凭证环境变量名「{env_name[:64]}」不合法：只允许字母、数字、下划线，"
            "且不能以数字开头"
        )
    if not env_name.startswith(_SECRET_ENV_PREFIX):
        raise ValueError(
            f"凭证环境变量必须以「{_SECRET_ENV_PREFIX}」开头，当前为「{env_name}」；"
            "宿主进程里的其它环境变量不能被工作流读取"
        )
    return env_name


_SECRET_REF_MAX_LEN = 120
_SECRET_FIELD_MAX_LEN = 64


def _checked_secret_ref(ref: str) -> str:
    """Return the credential ref a workflow may read, or refuse.

    ``env:`` refs are rejected outright: the store's env fallback would read
    any process variable, bypassing the ``AFD_HTTP_SECRET_`` namespace guard.
    """
    if not ref or len(ref) > _SECRET_REF_MAX_LEN:
        raise ValueError(
            f"密钥引用「{ref[:64]}」不合法：长度须在 1–{_SECRET_REF_MAX_LEN} 字符内"
        )
    if any(ch.isspace() for ch in ref):
        raise ValueError(f"密钥引用「{ref[:64]}」不合法：不能包含空白字符")
    if ref.lower().startswith("env:"):
        raise ValueError(
            "密钥引用不支持 env: 前缀；读环境变量请改用 authEnvVar（须以"
            f"「{_SECRET_ENV_PREFIX}」开头）"
        )
    return ref


def _checked_secret_field(field: str) -> str:
    if not field or len(field) > _SECRET_FIELD_MAX_LEN:
        raise ValueError(
            f"密钥字段名「{field[:64]}」不合法：长度须在 1–{_SECRET_FIELD_MAX_LEN} 字符内"
        )
    return field


def _workspace_credential_store(services: Optional[dict]):
    """Build the host per-workspace credential store, or ``None`` when the
    run has no workspace context (callers must fail closed on ``None``)."""
    workspace = (services or {}).get("workspace")
    workspace_dir = getattr(workspace, "workspace_dir", None)
    if not workspace_dir:
        return None
    from qwenpaw.drivers.credentials.store import AsyncCredentialStore

    return AsyncCredentialStore(Path(workspace_dir) / "credentials.yaml")


async def _resolve_host_ips(host: str) -> List[str]:
    """Resolve ``host`` to its address strings. Seam for the SSRF guard so
    tests can drive resolution without touching the network."""
    loop = asyncio.get_event_loop()
    infos = await loop.getaddrinfo(host, None)
    return [info[4][0] for info in infos]


def _ip_is_blocked(ip: "ipaddress.IPvAddress") -> bool:
    mapped = getattr(ip, "ipv4_mapped", None)
    if mapped is not None:
        ip = mapped
    return bool(
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    )


def _url_pinned_to_ip(url: str, ip: str) -> str:
    """Rewrite ``url``'s host to an address already validated, keeping port and userinfo."""
    from urllib.parse import urlparse, urlunparse

    parsed = urlparse(url)
    host = f"[{ip}]" if ":" in ip else ip
    try:
        port = f":{parsed.port}" if parsed.port else ""
    except ValueError:
        port = ""
    split = parsed.netloc.rsplit("@", 1)
    prefix = f"{split[0]}@" if len(split) == 2 else ""
    return urlunparse(parsed._replace(netloc=f"{prefix}{host}{port}"))


async def _checked_http_target(url: str) -> Tuple[str, Optional[str]]:
    """Check the request host and, for a name, pin the URL to the address checked —
    otherwise httpx re-resolves after the check and a second DNS record moves the
    request to an internal address.

    The second element is the original hostname whenever the URL was rewritten; the
    caller must resend it as ``Host`` and as the TLS SNI name. It is ``None`` when
    the URL goes out as written: a literal IP, or a name that failed to resolve.
    Resolution failures still fail open on purpose so reserved hostnames like
    ``*.test`` keep working and httpx reports the real connect error.
    """
    from urllib.parse import urlparse

    host = urlparse(url).hostname
    if not host:
        raise ValueError(f"无法解析请求地址的主机名：{url}")

    try:
        literal = ipaddress.ip_address(host)
    except ValueError:
        literal = None
    if literal is not None:
        if _ip_is_blocked(literal):
            raise ValueError(f"出于安全考虑，禁止访问内网/本机地址：{host}")
        return url, None

    try:
        resolved = await _resolve_host_ips(host)
    except (OSError, ValueError):
        return url, None
    ips: List[ipaddress.IPvAddress] = []
    for item in resolved:
        try:
            ips.append(ipaddress.ip_address(item))
        except ValueError:
            continue
    blocked = next((str(ip) for ip in ips if _ip_is_blocked(ip)), None)
    if blocked is not None:
        raise ValueError(f"出于安全考虑，禁止访问内网/本机地址：{host} 指向 {blocked}")
    if not ips:
        return url, None
    # 绑死一个地址就不能再靠 httpx 逐个试：优先 IPv4，免得只有 v6 记录或
    # v6 不通的机器上，原来能连通的工具节点变成连不上。
    chosen = next((ip for ip in ips if isinstance(ip, ipaddress.IPv4Address)), ips[0])
    return _url_pinned_to_ip(url, str(chosen)), host


async def _invoke_http_tool(
    config: dict,
    context: dict,
    node_outputs: dict,
    timeout_log: Optional[List[float]] = None,
    parsed_out: Optional[dict] = None,
    services: Optional[dict] = None,
) -> str:
    """Call an external HTTP endpoint with ``{{ref}}`` interpolation.

    url / headers / query / body are free-text templates on purpose: this source
    takes untyped HTTP arguments, not a typed parameter table (spec §3.2). The
    credential comes from the platform credential store (``authSecretRef``) or
    an environment variable (``authEnvVar``) **at run time** — the secretRef
    wins when both are configured. Only the reference / variable name is ever
    stored, the name must sit under the ``AFD_HTTP_SECRET_`` namespace for env
    vars, and neither the value nor the assembled header map reaches the trace.
    """
    import httpx

    def _interpolate(template: str) -> str:
        return _interpolate_template(template, context, node_outputs)

    url = _interpolate(str(config.get("url") or "").strip())
    if not url:
        raise ValueError("HTTP 工具节点未配置 url")
    if url.split(":", 1)[0].lower() not in ("http", "https"):
        raise ValueError(
            f"仅允许 http/https 请求，当前 URL 协议为「{url.split(':', 1)[0] or '空'}」"
        )
    method = str(config.get("method") or "GET").strip().upper()
    if method not in _HTTP_METHODS:
        raise ValueError(f"不支持的 HTTP 方法：{method}")

    request_url, pinned_host = await _checked_http_target(url)

    def _interpolated(mapping_key: str) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for key, value in (config.get(mapping_key) or {}).items():
            out[str(key)] = _interpolate(str(value)) if isinstance(value, str) else value
        return out

    headers = _interpolated("headers")
    query = _interpolated("query")
    body = _interpolate(str(config.get("body") or ""))

    def _apply_auth_header(secret: str) -> None:
        auth_header_name = str(config.get("authHeader") or "Authorization")
        for stale in [k for k in headers if str(k).lower() == auth_header_name.lower()]:
            del headers[stale]
        headers[auth_header_name] = secret

    secret_ref = str(config.get("authSecretRef") or "").strip()
    if secret_ref:
        _checked_secret_ref(secret_ref)
        store = _workspace_credential_store(services)
        if store is None:
            raise RuntimeError(
                "无法解析平台密钥：当前运行上下文没有可用的工作区，"
                "已阻止发送无凭证请求"
            )
        field = str(config.get("authSecretField") or "").strip() or "value"
        _checked_secret_field(field)
        from qwenpaw.drivers.errors import CredentialNotFoundError

        try:
            record = await store.get(secret_ref)
        except CredentialNotFoundError as exc:
            raise RuntimeError(
                f"平台密钥「{secret_ref}」在工作区凭证库中不存在；"
                "已阻止发送无凭证请求，请先在凭证库中创建该密钥"
            ) from exc
        value = record.values.get(field)
        if not isinstance(value, str) or not value:
            raise RuntimeError(
                f"平台密钥「{secret_ref}」缺少字段「{field}」或该字段为空；"
                "已阻止发送无凭证请求"
            )
        _apply_auth_header(value)
    else:
        env_name = str(config.get("authEnvVar") or "").strip()
        if env_name:
            secret = os.environ.get(_checked_secret_env_name(env_name), "")
            if not secret:
                raise RuntimeError(
                    f"环境变量 {env_name} 未设置；已阻止发送无凭证请求，"
                    "请设置后重试（凭证值不会写入工作流或执行记录）"
                )
            _apply_auth_header(secret)

    # 已校验过的地址不能被重新解析顶掉；作者显式写过 Host 时尊重作者的选择。
    send_headers = headers
    extensions: Dict[str, Any] = {}
    if pinned_host is not None:
        if not any(str(k).lower() == "host" for k in send_headers):
            send_headers = {**send_headers, "Host": pinned_host}
        extensions["sni_hostname"] = pinned_host

    raw_timeout = config.get("timeoutSec")
    try:
        timeout = float(raw_timeout) if raw_timeout not in (None, "") else 15.0
    except (TypeError, ValueError):
        timeout = 15.0
    timeout = min(max(timeout, 1.0), _TOOL_TIMEOUT_MAX)
    if timeout_log is not None:
        timeout_log.append(timeout)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(
                method,
                request_url,
                headers=send_headers,
                params=query or None,
                content=body.encode("utf-8") if body else None,
                extensions=extensions,
            )
        response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise RuntimeError(f"工具 HTTP 调用超时（{timeout}s）：{url}") from exc
    except httpx.ConnectError as exc:
        raise RuntimeError(f"无法连接到工具服务端：{url}") from exc
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"工具 HTTP 调用失败（HTTP {exc.response.status_code}）："
            f"{(exc.response.text or '')[:200]}"
        ) from exc
    except httpx.HTTPError as exc:
        # 兜底：httpx 的异常家族比这里逐条列出的三个更宽（RemoteProtocolError、
        # TooManyRedirects、InvalidURL…）。漏网的必须仍是中文的 RuntimeError，
        # 但英文原文不能进 state.error 与用户可见 detail —— 只报异常类名和 URL。
        raise RuntimeError(
            f"工具 HTTP 调用失败（{type(exc).__name__}）：{url}"
        ) from exc

    text = response.text or ""
    if len(text) > _HTTP_BODY_LIMIT:
        text = (
            text[:_HTTP_BODY_LIMIT]
            + f"\n…（响应已截断，原始长度 {len(text)} 字符）"
        )
    return _finish_tool_output(text, str(config.get("outputFormat") or ""), parsed_out)
