# -*- coding: utf-8 -*-
"""QwenPaw 应用首页（app-home）· 后端入口。

功能：
  - 启动默认应用：让用户选定一个应用，QwenPaw 桌面版启动时先打开它
  - ON/OFF 开关：控制是否启用"启动默认应用"行为
  - 轻应用管理：创建/编辑/删除轻应用（name + url），并在首页展示

HTTP 接口（挂载在 /api/plugins/app-home）：

  =====================  =====================================================
  ``GET  /apps``          扫描 ~/.qwenpaw/plugins/*/plugin.json，返回可启动应用列表
  ``GET  /default``       当前默认启动应用 + ON/OFF 状态
  ``POST /default``       设置默认启动应用（{"id": "xxx", "enabled": true}）
  ``GET  /lightapps``     轻应用列表
  ``POST /lightapps``     创建轻应用（{"name": "...", "url": "..."}）
  ``PUT  /lightapps/{id}``  更新轻应用
  ``DELETE /lightapps/{id}`` 删除轻应用
  =====================  =====================================================

配置存储：
  - 默认启动配置：~/.qwenpaw/plugins/app-home/config.json（纯本地，只写本插件目录）
  - 轻应用数据：$QWENPAW_WORKING_DIR/lightapp_data/apps.json（与原 qwenpaw-lightapp 共用）
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from qwenpaw.plugins.api import PluginApi

logger = logging.getLogger("qwenpaw.plugins.app-home")

PLUGIN_VERSION = "0.4.0"
PLUGIN_ID = "app-home"
STARTED_AT = time.time()  # 后端启动时间戳，作为"本次启动"的判据

_PLUGIN_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
_CONFIG_FILE = _PLUGIN_DIR.parent / "config.json"  # ~/.qwenpaw/plugins/app-home/config.json
_PLUGINS_ROOT = Path(os.path.expanduser("~")) / ".qwenpaw" / "plugins"

# 轻应用数据（与原 qwenpaw-lightapp 共用同一数据文件，迁移零成本）
_WORKING_DIR = Path(os.environ.get("QWENPAW_WORKING_DIR", Path.home() / ".qwenpaw"))
_LIGHTAPP_DIR = _WORKING_DIR / "lightapp_data"
_LIGHTAPP_FILE = _LIGHTAPP_DIR / "apps.json"


# ---------- 配置读写 ----------

def _load_config() -> Dict[str, Any]:
    """读取本地配置（容错：文件不存在/损坏返回默认值）。"""
    default = {"default_app_id": "", "enabled": False}
    if not _CONFIG_FILE.exists():
        return default
    try:
        data = json.loads(_CONFIG_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return default
        out = dict(default)
        if isinstance(data.get("default_app_id"), str):
            out["default_app_id"] = data["default_app_id"]
        if isinstance(data.get("enabled"), bool):
            out["enabled"] = data["enabled"]
        return out
    except Exception as exc:  # noqa: BLE001
        logger.warning("[app-home] config read failed: %s", exc)
        return default


def _save_config(cfg: Dict[str, Any]) -> None:
    """写入本地配置（原子写：先写临时再 rename）。"""
    _CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = _CONFIG_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(_CONFIG_FILE)
    logger.info("[app-home] config saved: default_app_id=%s enabled=%s",
                cfg.get("default_app_id"), cfg.get("enabled"))


# ---------- 轻应用读写（与原 qwenpaw-lightapp 数据兼容） ----------

def _load_lightapps() -> List[Dict[str, Any]]:
    """读取所有轻应用（容错：目录/文件不存在或损坏返回空列表）。"""
    if not _LIGHTAPP_FILE.exists():
        return []
    try:
        data = json.loads(_LIGHTAPP_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            # 兼容旧格式 {"apps": [...]}
            return data.get("apps") if isinstance(data.get("apps"), list) else []
    except Exception as exc:  # noqa: BLE001
        logger.warning("[app-home] lightapps read failed: %s", exc)
    return []


def _save_lightapps(apps: List[Dict[str, Any]]) -> None:
    """写入轻应用（原子写：先写临时再 rename）。"""
    _LIGHTAPP_DIR.mkdir(parents=True, exist_ok=True)
    tmp = _LIGHTAPP_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(apps, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(_LIGHTAPP_FILE)
    logger.info("[app-home] lightapps saved: %d app(s)", len(apps))


def _validate_lightapp_url(url: str) -> str:
    """校验并规整轻应用 URL：必须以 http(s):// 开头。"""
    url = (url or "").strip()
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="URL必须以http://或https://开头")
    return url


# ---------- 应用扫描（只读，单坏目录隔离） ----------

def _scan_apps() -> Dict[str, Any]:
    """扫描已安装应用，返回 {apps:[], errors:[], version}。

    只有 plugin.json 里 type=="app" 的插件才作为可启动应用。
    """
    apps: List[Dict[str, Any]] = []
    errors: List[str] = []
    if not _PLUGINS_ROOT.exists():
        return {"apps": apps, "errors": errors, "version": PLUGIN_VERSION}
    try:
        entries = sorted(_PLUGINS_ROOT.iterdir())
    except Exception as exc:  # noqa: BLE001
        return {"apps": apps, "errors": [str(exc)], "version": PLUGIN_VERSION}

    for pdir in entries:
        if not pdir.is_dir():
            continue
        if pdir.name.startswith(".") or "__pycache__" in pdir.name:
            continue
        pj = pdir / "plugin.json"
        if not pj.exists():
            continue
        try:
            data = json.loads(pj.read_text(encoding="utf-8"))
        except Exception:
            errors.append(pdir.name)
            continue
        # 仅应用类型 + 有前端入口 + 未禁用
        ptype = data.get("type")
        if ptype not in ("app", None):
            continue  # 非应用类型（tool/hub/general）不展示
        meta = data.get("meta") or {}
        pawapp = meta.get("pawapp") or {} if isinstance(meta, dict) else {}
        entry_page = (pawapp.get("entry_page") or "").strip()
        if not entry_page:
            # 兜底：/apps/{id}
            entry_page = "/apps/" + str(data.get("id") or pdir.name)
        icon = (meta.get("icon") or "🧩") if isinstance(meta, dict) else "🧩"
        if not str(icon).strip():
            icon = "🧩"
        apps.append({
            "id": data.get("id") or pdir.name,
            "name": data.get("name") or pdir.name,
            "version": data.get("version") or "",
            "icon": icon,
            "path": entry_page,
            "enabled": data.get("enabled", True),
        })
    return {"apps": apps, "errors": errors, "version": PLUGIN_VERSION}


# ---------- 请求模型 ----------

class DefaultAppPayload(BaseModel):
    id: str = Field(default="", description="应用 id，空字符串表示清除默认")
    enabled: Optional[bool] = Field(default=None, description="ON/OFF 开关；不传则保持原值")


class FrontendLogPayload(BaseModel):
    step: str = Field(default="", description="前端执行到的步骤")
    detail: str = Field(default="", description="附加信息（URL/错误等）")


class LightAppCreate(BaseModel):
    name: str = Field(description="轻应用名称")
    url: str = Field(description="轻应用 URL，须以 http(s):// 开头")
    width: str = Field(default="100%", description="展示宽度（如 100% 或 800px）")
    height: str = Field(default="100%", description="展示高度（如 100% 或 600px）")


class LightAppUpdate(BaseModel):
    name: Optional[str] = Field(default=None, description="轻应用名称")
    url: Optional[str] = Field(default=None, description="轻应用 URL")
    width: Optional[str] = Field(default=None, description="展示宽度")
    height: Optional[str] = Field(default=None, description="展示高度")


router = APIRouter()


@router.post("/log")
async def frontend_log(payload: FrontendLogPayload):
    """前端遥测：记录 autoOpen 各步骤，用于诊断启动跳转。"""
    logger.info("[app-home][frontend] step=%s detail=%s", payload.step,
                payload.detail[:300])
    return JSONResponse({"ok": True})


@router.get("/version")
async def get_version():
    return JSONResponse({"version": PLUGIN_VERSION, "id": PLUGIN_ID})


@router.get("/apps")
async def get_apps():
    """返回本机可启动应用列表 + 当前默认。"""
    scan = _scan_apps()
    cfg = _load_config()
    scan["default_app_id"] = cfg.get("default_app_id", "")
    scan["default_enabled"] = cfg.get("enabled", False)
    return JSONResponse(scan)


def _resolve_app_path(app_id: str) -> str:
    """按应用 id 解析入口路径（pawapp.entry_page 优先，兜底 /apps/{id}）。"""
    if not app_id:
        return ""
    pj = _PLUGINS_ROOT / app_id / "plugin.json"
    try:
        data = json.loads(pj.read_text(encoding="utf-8"))
        meta = data.get("meta") or {}
        pawapp = meta.get("pawapp") or {} if isinstance(meta, dict) else {}
        entry_page = (pawapp.get("entry_page") or "").strip()
        if entry_page:
            return entry_page
    except Exception:  # noqa: BLE001
        pass
    return "/apps/" + app_id


@router.get("/default")
async def get_default():
    """当前默认启动应用 + ON/OFF 状态 + 解析好的入口路径 + 后端启动时间戳。"""
    cfg = _load_config()
    app_id = cfg.get("default_app_id", "")
    return JSONResponse({
        "id": app_id,
        "enabled": cfg.get("enabled", False),
        "path": _resolve_app_path(app_id) if app_id else "",
        "server_started_at": STARTED_AT,
    })


@router.post("/default")
async def set_default(payload: DefaultAppPayload):
    """设置默认启动应用。

    - id 非空：设为该应用为启动默认
    - id 空：清除默认（enabled 保持）
    - enabled 传了：同时切换 ON/OFF
    """
    cfg = _load_config()
    if payload.id is not None:
        cfg["default_app_id"] = payload.id.strip()
    if payload.enabled is not None:
        cfg["enabled"] = payload.enabled
    _save_config(cfg)
    app_id = cfg.get("default_app_id", "")
    return JSONResponse({
        "ok": True,
        "id": app_id,
        "enabled": cfg.get("enabled", False),
        "path": _resolve_app_path(app_id) if app_id else "",
    })


# ---------- 轻应用 CRUD ----------

def _lightapp_with_id(apps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """给轻应用补齐基于索引的 ``id`` 字段（与原 qwenpaw-lightapp 一致）。"""
    out = []
    for i, app in enumerate(apps):
        item = dict(app)
        item["id"] = i
        out.append(item)
    return out


@router.get("/lightapps")
async def list_lightapps():
    """获取所有轻应用。"""
    return JSONResponse({"ok": True, "apps": _lightapp_with_id(_load_lightapps())})


@router.post("/lightapps")
async def create_lightapp(payload: LightAppCreate):
    """创建新轻应用。"""
    name = (payload.name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="名称不能为空")
    url = _validate_lightapp_url(payload.url)

    apps = _load_lightapps()
    new_app = {
        "name": name,
        "url": url,
        "width": (payload.width or "100%").strip(),
        "height": (payload.height or "100%").strip(),
    }
    apps.append(new_app)
    _save_lightapps(apps)
    return JSONResponse({"ok": True, "app": new_app, "id": len(apps) - 1})


@router.put("/lightapps/{app_id}")
async def update_lightapp(app_id: int, payload: LightAppUpdate):
    """更新轻应用。"""
    apps = _load_lightapps()
    if app_id < 0 or app_id >= len(apps):
        raise HTTPException(status_code=404, detail="轻应用不存在")

    app = apps[app_id]
    if payload.name is not None:
        name = payload.name.strip()
        if not name:
            raise HTTPException(status_code=400, detail="名称不能为空")
        app["name"] = name
    if payload.url is not None:
        app["url"] = _validate_lightapp_url(payload.url)
    if payload.width is not None:
        app["width"] = payload.width.strip()
    if payload.height is not None:
        app["height"] = payload.height.strip()

    _save_lightapps(apps)
    return JSONResponse({"ok": True, "app": app, "id": app_id})


@router.delete("/lightapps/{app_id}")
async def delete_lightapp(app_id: int):
    """删除指定轻应用。"""
    apps = _load_lightapps()
    if app_id < 0 or app_id >= len(apps):
        raise HTTPException(status_code=404, detail="轻应用不存在")
    deleted = apps.pop(app_id)
    _save_lightapps(apps)
    return JSONResponse({"ok": True, "deleted_app": deleted})


# ---------- 启动钩子：把"默认应用 + enabled"广播给前端 ----------

def _broadcast_default() -> None:
    """插件启动时记录默认应用，供前端首次加载时读取。

    实际导航由前端 App 组件在 mount 时调用 /default 完成；
    此处仅写日志，便于排查。
    """
    cfg = _load_config()
    if cfg.get("enabled") and cfg.get("default_app_id"):
        logger.info("[app-home] startup: will auto-open default app %s",
                    cfg["default_app_id"])
    else:
        logger.info("[app-home] startup: default app feature disabled")


class AppHomePlugin:
    def __init__(self):
        self.name = "应用首页"
        self.version = PLUGIN_VERSION
        self.id = PLUGIN_ID
        self.router = router

    def register(self, api: PluginApi) -> None:
        api.register_http_router(self.router, prefix="/plugins/" + PLUGIN_ID,
                                 tags=[PLUGIN_ID])
        api.register_startup_hook("app-home_broadcast_default",
                                  _broadcast_default, priority=90)
        logger.info("[%s] v%s registered (API: /api/plugins/%s)",
                    PLUGIN_ID, self.version, PLUGIN_ID)


# REQUIRED: 模块级 plugin 实例
plugin = AppHomePlugin()
