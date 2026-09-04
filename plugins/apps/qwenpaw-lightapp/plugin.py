"""
QwenPaw 轻应用管理器插件 v0.1.0
支持通过iframe显示用户配置的URL，可指定启动时窗口大小，
数据以JSON方式保存在后端接口的磁盘上
"""

import json
import logging
import os
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

PLUGIN_VERSION = "0.1.0"

router = APIRouter()

# 数据存储路径
DATA_DIR = Path(os.environ.get("QWENPAW_WORKING_DIR", Path.home() / ".qwenpaw")) / "lightapp_data"
DATA_FILE = DATA_DIR / "apps.json"


def _ensure_data_dir():
    """确保数据目录存在"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_apps() -> List[dict]:
    """从JSON文件加载所有轻应用"""
    _ensure_data_dir()
    if not DATA_FILE.exists():
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception as e:
        logger.error(f"加载轻应用数据失败: {e}")
        return []


def _save_apps(apps: List[dict]):
    """保存轻应用到JSON文件"""
    _ensure_data_dir()
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(apps, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"保存轻应用数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存数据失败: {e}")


# ---------- 请求模型 ----------
class LightAppCreate(BaseModel):
    name: str
    url: str
    width: Optional[str] = "100%"
    height: Optional[str] = "100%"
    x: Optional[int] = 0
    y: Optional[int] = 0


class LightAppUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    width: Optional[str] = None
    height: Optional[str] = None
    x: Optional[int] = None
    y: Optional[int] = None


class LightAppResponse(BaseModel):
    id: int
    name: str
    url: str
    width: str
    height: str
    x: int
    y: int


# ---------- 接口 ----------
@router.get("/status")
async def status():
    """插件状态"""
    return {
        "ok": True,
        "name": "轻应用管理器",
        "version": PLUGIN_VERSION,
        "type": "lightapp-manager",
        "data_file": str(DATA_FILE),
        "apps_count": len(_load_apps()),
    }


@router.get("/apps")
async def list_apps():
    """获取所有轻应用"""
    apps = _load_apps()
    # 添加ID字段（基于索引）
    for i, app in enumerate(apps):
        app["id"] = i
    return {"ok": True, "apps": apps}


@router.post("/apps")
async def create_app(app: LightAppCreate):
    """创建新轻应用"""
    apps = _load_apps()

    # 验证URL
    if not app.url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="URL必须以http://或https://开头")

    new_app = {
        "name": app.name.strip(),
        "url": app.url.strip(),
        "width": app.width or "100%",
        "height": app.height or "100%",
        "x": app.x if app.x is not None else 0,
        "y": app.y if app.y is not None else 0,
    }

    apps.append(new_app)
    _save_apps(apps)

    return {"ok": True, "app": new_app, "id": len(apps) - 1}


@router.get("/apps/{app_id}")
async def get_app(app_id: int):
    """获取指定轻应用"""
    apps = _load_apps()
    if app_id < 0 or app_id >= len(apps):
        raise HTTPException(status_code=404, detail="轻应用不存在")

    app = apps[app_id].copy()
    app["id"] = app_id
    return {"ok": True, "app": app}


@router.put("/apps/{app_id}")
async def update_app(app_id: int, app_update: LightAppUpdate):
    """更新轻应用"""
    apps = _load_apps()
    if app_id < 0 or app_id >= len(apps):
        raise HTTPException(status_code=404, detail="轻应用不存在")

    app = apps[app_id]

    # 更新非空字段
    if app_update.name is not None:
        if not app_update.name.strip():
            raise HTTPException(status_code=400, detail="名称不能为空")
        app["name"] = app_update.name.strip()

    if app_update.url is not None:
        url = app_update.url.strip()
        if not url.startswith(("http://", "https://")):
            raise HTTPException(status_code=400, detail="URL必须以http://或https://开头")
        app["url"] = url

    if app_update.width is not None:
        app["width"] = app_update.width

    if app_update.height is not None:
        app["height"] = app_update.height

    if app_update.x is not None:
        app["x"] = app_update.x

    if app_update.y is not None:
        app["y"] = app_update.y

    _save_apps(apps)

    return {"ok": True, "app": app, "id": app_id}


@router.delete("/apps/{app_id}")
async def delete_app(app_id: int):
    """删除轻应用"""
    apps = _load_apps()
    if app_id < 0 or app_id >= len(apps):
        raise HTTPException(status_code=404, detail="轻应用不存在")

    deleted_app = apps.pop(app_id)
    _save_apps(apps)

    return {"ok": True, "deleted_app": deleted_app}


@router.delete("/apps")
async def delete_all_apps():
    """删除所有轻应用"""
    _save_apps([])
    return {"ok": True, "message": "所有轻应用已删除"}


# 插件实例
class LightAppPlugin:
    """轻应用管理器插件"""

    def __init__(self):
        self.name = "轻应用管理器"
        self.version = PLUGIN_VERSION
        self.id = "qwenpaw-lightapp"
        self.router = router

    def register(self, api) -> None:
        """注册插件"""
        if hasattr(api, "register_http_router"):
            api.register_http_router(
                self.router,
                prefix="/qwenpaw-lightapp",
                tags=["qwenpaw-lightapp"],
            )
            logger.info("[qwenpaw-lightapp] HTTP router registered at /api/qwenpaw-lightapp")

        if hasattr(api, "register_startup_hook"):
            api.register_startup_hook("qwenpaw_lightapp_startup", self._startup)

        if hasattr(api, "register_shutdown_hook"):
            api.register_shutdown_hook("qwenpaw_lightapp_shutdown", self._shutdown)

    async def _startup(self) -> None:
        logger.info(
            "[qwenpaw-lightapp] Plugin v%s started - data_dir=%s",
            PLUGIN_VERSION,
            DATA_DIR,
        )

    async def _shutdown(self) -> None:
        logger.info("[qwenpaw-lightapp] Plugin stopped")


# REQUIRED: 模块级 plugin 实例
plugin = LightAppPlugin()