# -*- coding: utf-8 -*-
"""Workflow CRUD / catalog / validation / publish / version / deploy routes.

The 16 route functions live at module level (tests call them directly);
``register_routes`` applies the original decorators programmatically in
BASE main.py order, so FastAPI registration order is unchanged.
"""

import uuid
import os
from dataclasses import asdict
from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException

from qwenpaw.pawapp import PawAppContext, get_scoped_ctx

from engine import get_logger
from engine.registry import list_node_type_defs
from engine.schema import build_node_contract

from .models import WorkflowDefinition, ValidateRequest, _SERVER_OWNED_KEYS
from .store import (
    _LOCK,_DATA_DIR,_VERSIONS_FILE,_load_from_disk,
    _read_all, _persist_to_disk, _find_workflow,
    _workflow_owner, _is_visible_to, _require_owner,
    _load_versions, _persist_versions,
)
from .tools import _build_tool_services
from .validation import _raise_if_invalid, validate_workflow

logger = get_logger(__name__)


async def create_workflow(
    definition: WorkflowDefinition,
    ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """Create a new workflow owned by the authenticated principal."""
    definition.id = definition.id or str(uuid.uuid4())
    # Ensure workflow has a valid name
    if not definition.name or not str(definition.name).strip():
        definition.name = f"未命名工作流 {datetime.utcnow().strftime('%m-%d %H:%M')}"
    now = datetime.utcnow().isoformat()
    definition.created_at = now
    definition.updated_at = now
    definition.created_by = ctx.user_id

    async with _LOCK(definition.id):
        _persist_to_disk(definition.model_dump())

    return {"success": True, "data": definition.model_dump()}


async def get_workflow(
    workflow_id: str,
    ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """Get a workflow by ID."""
    async with _LOCK(workflow_id):
        wf = _find_workflow(workflow_id)
        if wf is not None:
            _require_owner(wf, ctx.user_id, "查看")
            return {"success": True, "data": wf}
    raise HTTPException(status_code=404, detail="Workflow not found")


async def update_workflow(
    workflow_id: str,
    definition: WorkflowDefinition,
    ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """Update an existing workflow."""
    # Ensure workflow has a valid name
    if not definition.name or not str(definition.name).strip():
        definition.name = f"未命名工作流 {datetime.utcnow().strftime('%m-%d %H:%M')}"
    async with _LOCK(workflow_id):
        wf = _find_workflow(workflow_id)
        if wf.get("id") == workflow_id:
            _require_owner(wf, ctx.user_id, "修改")
            definition.id = workflow_id
            definition.updated_at = datetime.utcnow().isoformat()
            # Ownership is server-side: a payload that omits ``created_by``
            # must not silently hand the workflow to the first writer.
            definition.created_by = _workflow_owner(wf) or ctx.user_id
            record = definition.model_dump()
            # Publish and deploy pointers are server-owned. The editing
            # client never sends them, so replacing the record outright
            # would silently unpublish the workflow on every autosave — and
            # copying them unconditionally stops a forged payload from
            # claiming a deployment that never happened.
            for key in _SERVER_OWNED_KEYS:
                record[key] = wf.get(key)

            _persist_to_disk(record)
            return {"success": True, "data": record}
    raise HTTPException(status_code=404, detail="Workflow not found")


async def list_workflows(ctx: PawAppContext = Depends(get_scoped_ctx)) -> dict:
    """List the workflows this user may see."""
    workflows = _read_all()
    visible = [wf for wf in workflows if _is_visible_to(wf, ctx.user_id)]
    return {"success": True, "data": visible}


async def tools_catalog(ctx: PawAppContext = Depends(get_scoped_ctx)) -> dict:
    """List the tools a node can actually call, for the designer's pickers.

    The platform section comes from the same ``local_workspace.list_tools`` the
    agent loop uses, so the picker can never offer a tool the agent cannot call
    — permission narrowing stays in the host policy, not a second AFD whitelist.
    One unreachable MCP client degrades to nothing instead of failing the whole
    catalog, because a dead server must not make the designer unusable. A missing
    host workspace is different: that is not "no tools", it is "cannot answer",
    so it fails loudly instead of returning an empty list the UI cannot tell apart
    from an agent that legitimately has nothing to call.
    """
    services = await _build_tool_services(ctx)
    if not services:
        raise HTTPException(
            status_code=503,
            detail="工作区未就绪，无法列出工具目录",
        )
    items: List[dict] = []

    local_ws = services.get("local_workspace")
    if local_ws is not None:
        try:
            tools = await local_ws.list_tools(
                agent_config=services.get("agent_config"),
                agent_id=services.get("agent_id") or None,
                request_context={
                    "agent_id": services.get("agent_id", ""),
                    "user_id": services.get("user_id", ""),
                },
            )
            for tool in tools:
                name = str(getattr(tool, "name", "") or "")
                if not name:
                    continue
                items.append({
                    "source": "platform",
                    "id": name,
                    "label": name,
                    "description": str(getattr(tool, "description", "") or "")[:500],
                })
        except Exception as exc:  # noqa: BLE001  (a failed listing is empty, not fatal)
            logger.warning("[tools-catalog] platform listing failed: %s", exc)

    manager = services.get("driver_manager")
    if manager is not None:
        from qwenpaw.app.mcp.config_service import MCPConfigService
        from qwenpaw.drivers.constants import CAPABILITY_KIND_TOOL

        service = None
        clients: List[Any] = []
        try:
            service = MCPConfigService(services.get("workspace"))
            clients = await service.list_clients()
        except Exception as exc:  # noqa: BLE001
            logger.warning("[tools-catalog] MCP client listing failed: %s", exc)
        for client in clients:
            client_key = str(getattr(client, "key", "") or "")
            if not client_key or not getattr(client, "enabled", False) or service is None:
                continue
            try:
                tool_infos = await service.list_tools(client_key)
                # MCPToolInfo carries no capability id; align by tool name with
                # what the driver reports, and drop anything we cannot address.
                caps = await manager.list_driver_capabilities(
                    client_key, kind=CAPABILITY_KIND_TOOL, request_context={},
                )
                ids = {
                    str(getattr(c, "name", "")): str(getattr(c, "capability_id", ""))
                    for c in caps
                }
            except Exception as exc:  # noqa: BLE001  (dead server: skip this client)
                logger.warning(
                    "[tools-catalog] MCP client '%s' unavailable: %s", client_key, exc
                )
                continue
            for info in tool_infos:
                capability_id = ids.get(str(getattr(info, "name", "")), "")
                if not getattr(info, "enabled", False) or not capability_id:
                    continue
                items.append({
                    "source": "mcp",
                    "id": capability_id,
                    "clientKey": client_key,
                    "label": str(getattr(info, "name", "")),
                    "description": str(getattr(info, "description", "") or "")[:500],
                    "inputSchema": getattr(info, "input_schema", {}) or {},
                })

    return {"success": True, "data": items}


async def node_contract(ctx: PawAppContext = Depends(get_scoped_ctx)) -> dict:
    """Field names and types per node type, straight from the engine.

    The designer used to hardcode this table and drifted: it offered two
    fields the runtime can never resolve. Serving it removes the second copy.
    """
    return {"success": True, "data": build_node_contract()}


async def get_node_types(ctx: PawAppContext = Depends(get_scoped_ctx)) -> dict:
    """Return registered node type metadata for dynamic designer rendering."""
    defs = list_node_type_defs()
    payload = []
    for meta in defs:
        item = asdict(meta)
        # PropertyField is a dataclass but asdict handles nested dataclasses
        # automatically; no manual conversion needed.
        payload.append(item)
    return {"success": True, "data": payload}


async def delete_workflow(
    workflow_id: str,
    ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """Delete a workflow."""
    async with _LOCK(workflow_id):
        target = _find_workflow(workflow_id)
        if target is not None:
            _require_owner(target, ctx.user_id, "删除")

        if target is None:
            raise HTTPException(status_code=404, detail="Workflow not found")
        os.unlink(_DATA_DIR/ workflow_id)
    return {"success": True}


async def validate_workflow_route(
    workflow_id: str,
    req: Optional[ValidateRequest] = None,
    ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """Report structural and reference errors before publishing or deploying.

    When ``workflow`` is supplied the unsaved canvas graph is checked instead of
    the stored one, so the designer can validate without saving first.
    """
    inline = (req.workflow if req and req.workflow else None)
    if inline is not None:
        return validate_workflow(inline)

    async with _LOCK(workflow_id):
        wf = _find_workflow(workflow_id)
    if wf is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    _require_owner(wf, ctx.user_id, "校验")
    return validate_workflow(wf)


# ── Publish API Routes ──────────────────────────────────────────────

async def publish_workflow(
    workflow_id: str,
    ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """Publish a workflow: create an immutable version snapshot.
    
    The published version is decoupled from the editing state.
    """
    async with _LOCK(workflow_id):
        # Load current workflow
        wf = _find_workflow(workflow_id)
        if wf is None:
            raise HTTPException(status_code=404, detail="Workflow not found")
        _require_owner(wf, ctx.user_id, "发布")
        _raise_if_invalid(wf, "发布")
        
        # Load existing versions to determine next version number
        workflow_versions = _load_versions(workflow_id)
        next_version = 1
        if workflow_versions:
            next_version = max(v.get("version", 0) for v in workflow_versions) + 1
        
        now = datetime.utcnow().isoformat()
        version_record = {
            "id": str(uuid.uuid4()),
            "workflow_id": workflow_id,
            "version": next_version,
            "name": wf.get("name", ""),
            "description": wf.get("description", ""),
            "nodes": wf.get("nodes", []),
            "edges": wf.get("edges", []),
            "system_prompt": wf.get("system_prompt", ""),
            "created_at": wf.get("created_at", ""),
            "created_by": _workflow_owner(wf) or ctx.user_id,
            "published_at": now,
        }
        _persist_versions(version_record)
        w = wf
        # Update workflow with publish metadata
        w["published_version_id"] = version_record["id"]
        w["published_version"] = next_version
        w["published_at"] = now
        w["updated_at"] = now
        _persist_to_disk(w)
    
    return {
        "success": True,
        "data": {
            "version_id": version_record["id"],
            "version": next_version,
            "published_at": now,
        },
    }


async def list_workflow_versions(
    workflow_id: str,
    ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """List all published versions of a workflow."""
    async with _LOCK(workflow_id):
        wf = _find_workflow(workflow_id)
        if wf is not None:
            _require_owner(wf, ctx.user_id, "查看版本")
        versions = _load_versions(workflow_id)
        workflow_versions = [v for v in versions if v.get("workflow_id") == workflow_id]
        workflow_versions.sort(key=lambda v: v.get("version", 0), reverse=True)
    return {"success": True, "data": workflow_versions}


async def rollback_workflow(
    workflow_id: str,
    version_id: str,
    ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """Rollback a workflow to a specific published version.
    
    The current editing state is overwritten by the published version snapshot.
    """
    async with _LOCK(workflow_id):
        target_version = _load_from_disk(_VERSIONS_FILE(workflow_id,version_id))
        if target_version is None:
            raise HTTPException(status_code=404, detail="Version not found")
        
        wf = _find_workflow(workflow_id)
        if wf.get("id") == workflow_id:
            _require_owner(wf, ctx.user_id, "回滚")
            wf.update({
                "name": target_version.get("name", ""),
                "description": target_version.get("description", ""),
                "nodes": target_version.get("nodes", []),
                "edges": target_version.get("edges", []),
                "system_prompt": target_version.get("system_prompt", ""),
                "updated_at": datetime.utcnow().isoformat(),
            })
        else:
            raise HTTPException(status_code=404, detail="Workflow not found")
        _persist_to_disk(wf)
    
    return {"success": True, "data": {"version_id": version_id, "version": target_version.get("version")}}


async def get_published_workflow(
    workflow_id: str,
    ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """Get the latest published version of a workflow.
    
    Returns 404 if the workflow has never been published.
    """
    async with _LOCK(workflow_id):
        wf = _find_workflow(workflow_id)
        if wf is None:
            raise HTTPException(status_code=404, detail="Workflow not found")
        _require_owner(wf, ctx.user_id, "查看")
        
        published_version_id = wf.get("published_version_id")
        if not published_version_id:
            raise HTTPException(status_code=404, detail="Workflow has not been published")
        
        v = _load_from_disk(_VERSIONS_FILE(workflow_id,published_version_id))
        if v:
            if v.get("id") == published_version_id:
                return {"success": True, "data": v}
        
        raise HTTPException(status_code=404, detail="Published version not found")


# ── Deploy API Routes ───────────────────────────────────────────────

async def deploy_workflow(
    workflow_id: str,
    ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """Deploy the latest published version of a workflow.

    Once deployed, the workflow can be executed externally using the
    deployed version snapshot, completely isolated from the editing state.
    """
    async with _LOCK(workflow_id):
        wf = _find_workflow(workflow_id)
        if wf is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_type": "workflow_not_found",
                    "message": "工作流不存在",
                    "action": "请刷新页面或重新选择工作流",
                }
            )
        _require_owner(wf, ctx.user_id, "部署")

        published_version_id = wf.get("published_version_id")
        if not published_version_id:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_type": "workflow_not_published",
                    "message": "工作流尚未发布，无法部署",
                    "action": "请先点击「发布」按钮发布工作流，然后再进行部署",
                }
            )

        # Verify the published version exists
        target_version = _load_from_disk(_VERSIONS_FILE(workflow_id,published_version_id))
        if target_version is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_type": "published_version_not_found",
                    "message": "已发布版本不存在，可能是数据不一致",
                    "action": "请重新发布工作流后再试",
                }
            )

        # The snapshot is what goes live, so it — not the draft — is validated.
        _raise_if_invalid(target_version, "部署")
        
        now = datetime.utcnow().isoformat()
        wf["deployed_version_id"] = published_version_id
        wf["deployed_at"] = now
        
        _persist_to_disk(wf)
    
    return {
        "success": True,
        "data": {
            "version_id": published_version_id,
            "version": target_version.get("version"),
            "deployed_at": now,
        },
    }


async def undeploy_workflow(
    workflow_id: str,
    ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """Undeploy a workflow, removing its external service endpoint."""
    async with _LOCK(workflow_id):
        wf = _find_workflow(workflow_id)
        if wf is None:
            raise HTTPException(status_code=404, detail="Workflow not found")
        _require_owner(wf, ctx.user_id, "下线")
        
        wf["deployed_version_id"] = None
        wf["deployed_at"] = None
        
        _persist_to_disk(wf)
    
    return {"success": True, "data": {"message": "Workflow undeployed"}}


async def get_deployed_workflow(
    workflow_id: str,
    ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """Get the currently deployed version of a workflow."""
    async with _LOCK(workflow_id):
        wf = _find_workflow(workflow_id)
        if wf is None:
            raise HTTPException(status_code=404, detail="Workflow not found")
        _require_owner(wf, ctx.user_id, "查看")
        
        deployed_version_id = wf.get("deployed_version_id")
        if not deployed_version_id:
            raise HTTPException(status_code=404, detail="Workflow is not deployed")
        
        v = _load_from_disk(_VERSIONS_FILE(workflow_id,deployed_version_id))
        if v:
            if v.get("id") == deployed_version_id:
                return {"success": True, "data": v}
        
        raise HTTPException(status_code=404, detail="Deployed version not found")


def register_routes(router: APIRouter) -> None:
    """Apply the original route decorators, in BASE main.py order."""
    router.post("/workflows")(create_workflow)
    router.get("/workflows/{workflow_id}")(get_workflow)
    router.put("/workflows/{workflow_id}")(update_workflow)
    router.get("/workflows")(list_workflows)
    router.get("/tools-catalog")(tools_catalog)
    router.get("/node-contract")(node_contract)
    router.get("/node-types")(get_node_types)
    router.delete("/workflows/{workflow_id}")(delete_workflow)
    router.post("/workflows/{workflow_id}/validate")(validate_workflow_route)
    router.post("/workflows/{workflow_id}/publish")(publish_workflow)
    router.get("/workflows/{workflow_id}/versions")(list_workflow_versions)
    router.post("/workflows/{workflow_id}/rollback/{version_id}")(rollback_workflow)
    router.get("/workflows/{workflow_id}/published")(get_published_workflow)
    router.post("/workflows/{workflow_id}/deploy")(deploy_workflow)
    router.post("/workflows/{workflow_id}/undeploy")(undeploy_workflow)
    router.get("/workflows/{workflow_id}/deployed")(get_deployed_workflow)
