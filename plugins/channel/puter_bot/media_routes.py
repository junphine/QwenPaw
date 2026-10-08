import os
from fastapi import APIRouter,Request, HTTPException
from fastapi.responses import FileResponse
from qwenpaw.constant import WORKING_DIR,DEFAULT_MEDIA_DIR


def register_app_routes(app):
    """注册该频道的 HTTP 路由。"""
    router = APIRouter()

    @router.get("/api/media/{file_path:path}")
    async def serve_media(file_path: str):
        """
        提供 DEFAULT_MEDIA_DIR 下的静态媒体文件服务。
        路径示例: /media/images/photo.jpg
        """
        # 1. 构建完整路径并校验，防止目录遍历攻击
        full_path = os.path.join(DEFAULT_MEDIA_DIR.__str__(), file_path)
        real_path = os.path.realpath(full_path)
        real_base = os.path.realpath(DEFAULT_MEDIA_DIR)

        # 2. 安全检查：确保最终路径在允许的目录内
        if not real_path.startswith(real_base):
            raise HTTPException(status_code=403, detail="Forbidden")

        # 3. 检查文件是否存在且是文件（不是目录）
        if not os.path.isfile(real_path):
            raise HTTPException(status_code=404, detail="File not found")

        # 4. 返回文件
        return FileResponse(real_path)

    @router.get("/api/workspaces/{file_path:path}")
    async def serve_media(file_path: str):
        """
        提供 WORKING_DIR 下的静态媒体文件服务。
        路径示例: WORKING_DIR/workspaces/{agent}/media/images/photo.jpg
        """
        # 1. 构建完整路径并校验，防止目录遍历攻击
        full_path = os.path.join(WORKING_DIR.__str__(), "workspaces", file_path)
        real_path = os.path.realpath(full_path)
        media_path_pos = full_path.find('/media/')
        if media_path_pos>0:
            media_path = full_path[:media_path_pos+len('/media/')]
            real_base = os.path.realpath(media_path)
        else:
            raise HTTPException(status_code=403, detail="Forbidden")

        # 2. 安全检查：确保最终路径在允许的目录内
        if not real_path.startswith(real_base):
            raise HTTPException(status_code=403, detail="Forbidden")

        # 3. 检查文件是否存在且是文件（不是目录）
        if not os.path.isfile(real_path):
            raise HTTPException(status_code=404, detail="File not found")

        # 4. 返回文件
        return FileResponse(real_path)

    # 将 router 包含到 QwenPaw 的 app 中
    app.include_router(router)