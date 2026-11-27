"""
QwenPaw 代码编辑器插件 v0.1.12
在线代码编辑：浏览/打开/编辑/新建/保存工作区文本与代码文件。
基于 Monaco Editor（VSCode 同款编辑器核心，CDN 加载，前端无构建）。

访问范围（安全默认）：
  - 工作区模式（默认）：仅允许 WORKING_DIR 内路径。
  - 平台模式（WORKING_DIR 位于 /run/csi/mount-root/nas 之下自动判定）：
    允许访问所有可访问路径（遵循系统权限），与 file-browser 一致；
    access_root 仍指向 NAS 持久层根，作为默认文件树根。
  - 越界路径返回 403（工作区模式）。

接口（挂载于 /api/qwenpaw-code-editor/）：
  - GET  /status            插件状态、版本、WORKING_DIR、当前模式、快捷根目录列表
  - GET  /ls?path=          列出目录（path 支持绝对路径或相对 WORKING_DIR；空 = WORKING_DIR）
  - GET  /read?path=        读取文本文件内容（二进制/超大文件安全拦截；默认上限 2MB）
  - POST /write             保存文件 {path, content}（UTF-8；自动创建父目录；拒绝覆盖目录）
  - POST /rename            重命名 {path, new_name}（仅同级改名，不可跨目录）
  - POST /delete            删除文件或目录 {path}（目录递归删除；前端需二次确认）
  - GET  /download?path=    下载文件（attachment；目录拒绝）
"""
import logging
import os
import shutil
import stat
import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

PLUGIN_VERSION = "0.1.12"

# 编辑器适合打开的文件大小上限（默认 2MB，超出提示用文件浏览器下载）
MAX_READ_BYTES = 2 * 1024 * 1024

# 二进制检测：读取头部若干字节，含 NUL 即视为二进制
_BIN_PROBE = 8192

_WORKING_DIR = Path(os.environ.get("QWENPAW_WORKING_DIR", Path.home() / ".qwenpaw"))

router = APIRouter()

# ---------- 路径与访问控制 ----------

def _platform_root() -> Path:
    """平台 NAS 持久层根（WORKING_DIR 挂载点之上）。"""
    return Path("/run/csi/mount-root/nas").resolve()

def _working_dir() -> Path:
    """运行时数据根目录（与 QwenPaw / file-browser 一致：优先 QWENPAW_WORKING_DIR）。"""
    return _WORKING_DIR.resolve()

def _is_platform_env() -> bool:
    """WORKING_DIR 位于 /run/csi/mount-root/nas 下即判定为平台环境。"""
    wd = _working_dir()
    try:
        wd.relative_to(_platform_root())
        return True
    except ValueError:
        return False

def _mode() -> str:
    return "platform" if _is_platform_env() else "workdir"

def _access_root() -> Path:
    """当前模式允许访问的根（仅用于 status 展示 / 前端默认树根）。

    - 平台模式：默认树根为 NAS 持久层根，但访问不限（遵循系统权限）
    - 工作区模式：仅允许 WORKING_DIR
    """
    return _platform_root() if _is_platform_env() else _working_dir()

def _check_access(p: Path) -> None:
    """工作区模式下限制路径必须在 WORKING_DIR 内（判定用 realpath）。

    与 file-browser 一致：``wd/../etc`` 和工作区内指向外部的符号链接都会被
    解析到真实位置后拒绝，不能靠软链接绕过。
    """
    if _is_platform_env():
        return
    wd = _working_dir().resolve()
    try:
        real = p.resolve(strict=False)
    except (OSError, RuntimeError, ValueError) as e:
        raise HTTPException(400, f"路径解析失败: {e}") from e
    try:
        real.relative_to(wd)
    except ValueError:
        raise HTTPException(403, "路径超出访问范围（当前模式：workdir）")


def _resolve(path: str) -> Path:
    """把输入路径解析为绝对路径：绝对路径直接使用；相对路径基于 WORKING_DIR。

    只做**词法**规范化（normpath），不解析最后一级符号链接——列目录、重命名、
    删除因此作用于链接本身，而不是它指向的目标文件（v0.1.11 修复：此前
    ``resolve()`` 会让「删除链接」变成「删除目标」）。越界判定由 ``_check_access``
    用 realpath 完成。
    """
    p = (path or "").strip()
    try:
        if not p:
            pp = _working_dir()
        else:
            pp = Path(p).expanduser()
            if not pp.is_absolute():
                pp = _working_dir() / pp
        pp = Path(os.path.normpath(str(pp)))
    except (OSError, ValueError) as e:
        # 含 NUL 字节等非法路径：返回 400 而不是 500
        raise HTTPException(400, f"路径解析失败: {e}") from e
    _check_access(pp)
    return pp


# 顶层系统目录：整体删除会造成不可恢复的系统损坏，一律保护。
# 只保护目录本身及其祖先，不限制其子目录内的正常文件操作。
_SYSTEM_PROTECTED = tuple(
    Path(x)
    for x in (
        "/bin", "/boot", "/dev", "/etc", "/home", "/lib", "/lib64",
        "/proc", "/root", "/sbin", "/sys", "/usr", "/var", "/app",
        "/opt", "/srv", "/run", "/workspace", "/mnt", "/media", "/data",
    )
)


def _protected_paths() -> list:
    """不可删除 / 重命名的路径集合（精确匹配 + 祖先匹配）。"""
    candidates = [
        Path("/"),
        Path.home(),
        _working_dir(),
        Path(__file__).resolve().parent,          # 插件自身目录
        Path(__file__).resolve().parent.parent,   # plugins/ 目录（含其他插件与凭据）
    ]
    for env_name in ("QWENPAW_SECRET_DIR", "COPAW_SECRET_DIR"):
        value = os.environ.get(env_name)
        if value:
            candidates.append(Path(value))
    candidates.extend(_SYSTEM_PROTECTED)

    out = []
    for cand in candidates:
        try:
            resolved = cand.resolve()
        except OSError:
            continue
        if resolved not in out:
            out.append(resolved)
    return out


def _check_deletable(p: Path) -> None:
    """删除 / 重命名保护：精确路径 + 祖先路径 + 顶层系统目录。

    只做精确匹配挡不住「删 WORKING_DIR 的父目录」或「rename 掉 WORKING_DIR」，
    因此额外检查 p 是否为任一受保护路径的祖先。

    路径只解析**中间目录**的符号链接，末级保持原样：删除 / 重命名一个符号链接
    只影响链接本身，不该因为其目标受保护而被拒绝。
    """
    raw = Path(os.path.normpath(str(p)))
    try:
        real_parent = raw.parent.resolve(strict=False)
    except (OSError, RuntimeError, ValueError) as e:
        raise HTTPException(400, f"路径解析失败: {e}") from e
    target = real_parent / raw.name

    for protected in _protected_paths():
        if target == protected:
            raise HTTPException(400, f"受保护路径，禁止删除或重命名: {target}")
        try:
            protected.relative_to(target)
        except ValueError:
            continue
        raise HTTPException(400, f"该目录包含受保护路径 {protected}，禁止删除或重命名")

# ---------- 工具 ----------

def _fmt_size(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    units = ["KB", "MB", "GB", "TB"]
    v = float(n)
    for u in units:
        v /= 1024.0
        if v < 1024:
            return f"{v:.1f} {u}"
    return f"{v:.1f} PB"

def _sorted_items(p: Path) -> list:
    """目录项：目录在前、名称自然排序。

    与 file-browser 一致：保留链接自身路径（不 resolve），返回 ``link`` /
    ``broken`` 标志；悬空链接仍然列出（用户可以删除它），信息取自链接本身。
    """
    items = []
    try:
        entries = list(p.iterdir())
    except PermissionError as e:
        raise HTTPException(403, f"没有权限读取目录：{p}") from e
    except OSError as e:
        raise HTTPException(500, f"读取目录失败：{e}") from e
    for e in entries:
        is_link = e.is_symlink()
        try:
            try:
                st = e.stat()
                broken = False
            except OSError:
                if not is_link:
                    raise
                st = e.lstat()
                broken = True
        except OSError:
            continue
        is_dir = e.is_dir()
        has_size = not is_dir and not broken
        items.append({
            "name": e.name,
            "path": str(e),
            "type": "dir" if is_dir else "file",
            "size": st.st_size if has_size else 0,
            "mtime": int(st.st_mtime),
            "link": is_link,
            "broken": broken,
        })
    items.sort(key=lambda x: (x["type"] != "dir", x["name"].lower()))
    return items


def _agent_workspace_dirs(wd: Path) -> list:
    """扫描各智能体工作区目录（兼容两种部署布局）。

    布局A：WORKING_DIR 自身即某个智能体工作区（<...>/workspaces/<agent_id>）
           → 扫描父级 workspaces/（结果含 WORKING_DIR 自身）
    布局B：WORKING_DIR 为平台根（<...>）→ 扫描其下 workspaces/ 子目录
    """
    if wd.parent.name == "workspaces" and wd.parent.is_dir():
        agent_root = wd.parent
    else:
        ws = wd / "workspaces"
        if not ws.is_dir():
            return []
        agent_root = ws
    try:
        return sorted(
            (c for c in agent_root.iterdir()
             if c.is_dir() and not c.name.startswith(".")),
            key=lambda c: c.name,
        )
    except OSError:
        return []


def _roots() -> list:
    """快捷根目录列表（与 file-browser 一致）：WORKING_DIR、系统路径、各智能体工作区、NAS 根。"""
    wd = _working_dir().resolve()
    if not _is_platform_env():
        out = [{"path": str(wd), "label": "WORKING_DIR"}]
        for d in _agent_workspace_dirs(wd):
            try:
                rr = d.resolve()
                rr.relative_to(wd)
            except (OSError, ValueError):
                continue
            if rr == wd:
                continue
            out.append({"path": str(rr), "label": "🤖 " + rr.name + "（工作区）"})
        return out

    roots = [wd, Path("/tmp"), Path("/home"), Path("/root"), Path("/workspace")]
    roots.extend(_agent_workspace_dirs(wd))
    nas = Path("/run/csi/mount-root/nas")
    if nas.is_dir():
        roots.append(nas)
    roots.append(Path("/app"))
    roots.append(Path("/"))
    agent_paths = set()
    for d in _agent_workspace_dirs(wd):
        try:
            agent_paths.add(d.resolve())
        except OSError:
            pass
    seen = set()
    out = []
    for r in roots:
        try:
            rr = r.resolve()
        except OSError:
            continue
        if rr in seen or not rr.exists():
            continue
        seen.add(rr)
        if rr == wd:
            label = "WORKING_DIR"
        elif rr == Path("/").resolve():
            label = "/ (文件系统根)"
        elif rr in agent_paths:
            label = "🤖 " + rr.name + "（工作区）"
        else:
            label = str(rr)
        out.append({"path": str(rr), "label": label})
    return out

# ---------- 数据模型 ----------

class WriteReq(BaseModel):
    path: str
    content: str

class RenameReq(BaseModel):
    path: str
    new_name: str

class DeleteReq(BaseModel):
    path: str

# ---------- 接口 ----------
#
# 约定：凡是要做文件 I/O 的处理器一律用**同步 def**（FastAPI 会自动把它们丢到
# 线程池执行）；禁止用 async def 直接做阻塞式文件 I/O —— 那会在事件循环线程上跑，
# 冻结整个 QwenPaw 服务（工作区在 NAS/NFS 上时尤其明显）。
# 只有纯计算、无 I/O 的处理器才写 async def。

@router.get("/status")
async def status():
    wd = _working_dir()
    return {
        "id": "qwenpaw-code-editor",
        "name": "代码编辑器",
        "version": PLUGIN_VERSION,
        "working_dir": str(wd),
        "mode": _mode(),
        "access_root": str(_access_root()),
        "roots": _roots(),
    }

@router.get("/ls")
def ls(path: str = Query("", description="目录路径（绝对或相对 WORKING_DIR；空 = WORKING_DIR）")):
    p = _resolve(path)
    if not p.exists():
        raise HTTPException(404, "路径不存在")
    if not p.is_dir():
        raise HTTPException(400, "不是目录")
    return {"path": str(p), "items": _sorted_items(p)}

@router.get("/read")
def read_file(path: str = Query("", description="文件路径（绝对或相对 WORKING_DIR）")):
    p = _resolve(path)
    if not p.exists() and not p.is_symlink():
        raise HTTPException(404, "文件不存在")
    if p.is_dir():
        raise HTTPException(400, "是目录，不是文件")
    if p.is_symlink() and not p.exists():
        raise HTTPException(404, "符号链接已失效")
    try:
        size = p.stat().st_size
    except OSError as e:
        raise HTTPException(404, f"文件不存在或不可访问: {e}") from e
    if size > MAX_READ_BYTES:
        raise HTTPException(
            413,
            f"文件过大（{_fmt_size(size)}，上限 {_fmt_size(MAX_READ_BYTES)}），请在文件浏览器中下载查看",
        )
    # 只读前缀：先 stat 再读，避免文件在 check 与 read 之间变大导致全量读入内存
    try:
        with open(p, "rb") as fh:
            raw = fh.read(MAX_READ_BYTES + 1)
    except OSError as e:
        raise HTTPException(500, f"读取失败：{e}") from e
    if len(raw) > MAX_READ_BYTES:
        raise HTTPException(
            413,
            f"文件过大（超过 {_fmt_size(MAX_READ_BYTES)} 上限），请在文件浏览器中下载查看",
        )
    if b"\x00" in raw[:_BIN_PROBE]:
        raise HTTPException(415, "二进制文件不支持编辑，请在文件浏览器中下载")
    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(415, "非 UTF-8 文本文件暂不支持编辑")
    return {"path": str(p), "size": size, "content": content}

@router.post("/write")
def write_file(req: WriteReq):
    p = _resolve(req.path)
    if p.exists() and p.is_dir():
        raise HTTPException(400, "目标路径是目录，不能写入")
    # 自动创建父目录（新建文件场景）
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise HTTPException(500, f"保存失败：{e}") from e
    # 原子保存：先写同目录临时文件再 os.replace，避免写到一半崩溃/断连把原文件截断
    tmp = None
    try:
        fd, tmp = tempfile.mkstemp(prefix=".qce-save-", dir=str(p.parent))
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(req.content)
        if p.exists():
            # 保留原文件权限位（mkstemp 默认 0600）
            try:
                os.chmod(tmp, stat.S_IMODE(p.stat().st_mode))
            except OSError:
                pass
        os.replace(tmp, p)
        tmp = None
    except OSError as e:
        raise HTTPException(500, f"保存失败：{e}") from e
    finally:
        if tmp:
            try:
                os.unlink(tmp)
            except OSError:
                pass
    return {"path": str(p), "bytes": p.stat().st_size}

@router.post("/rename")
def rename_path(req: RenameReq):
    """重命名：仅同级改名（new_name 为 basename，不能含路径分隔符）。"""
    p = _resolve(req.path)
    # 悬空符号链接 exists() 为 False，但仍应允许重命名链接本身
    if not p.exists() and not p.is_symlink():
        raise HTTPException(404, "路径不存在")
    name = req.new_name.strip()
    if not name or "/" in name or "\\" in name or name in (".", ".."):
        raise HTTPException(400, "新名称无效（不能为空、不能包含路径分隔符）")
    # 重命名等同于把原路径移走：受保护路径（含 WORKING_DIR 的祖先）一律拒绝
    _check_deletable(p)
    target = p.parent / name
    if target.exists() or target.is_symlink():
        raise HTTPException(400, f"目标已存在：{name}")
    try:
        p.rename(target)
    except OSError as e:
        raise HTTPException(500, f"重命名失败：{e}")
    return {"path": str(target), "name": name}

@router.post("/delete")
def delete_path(req: DeleteReq):
    """删除文件或目录（目录递归删除；前端应二次确认）。

    符号链接只删除链接本身，绝不跟随到目标；WORKING_DIR、HOME、插件目录、
    ``plugins/`` 及其祖先等受保护路径一律拒绝（与 file-browser 一致）。
    """
    p = _resolve(req.path)
    if not p.exists() and not p.is_symlink():
        raise HTTPException(404, "路径不存在")
    _check_deletable(p)
    try:
        if p.is_symlink():
            p.unlink()
        elif p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
    except OSError as e:
        raise HTTPException(500, f"删除失败：{e}")
    return {"path": str(p)}

@router.get("/download")
def download_file(path: str = Query("", description="文件路径")):
    """下载文件（attachment；目录拒绝）。"""
    p = _resolve(path)
    if not p.exists():
        if p.is_symlink():
            raise HTTPException(404, "符号链接已失效")
        raise HTTPException(404, "文件不存在")
    if p.is_dir():
        raise HTTPException(400, "目录不支持下载")
    return FileResponse(p, filename=p.name)

# ---------- 插件注册 ----------

class CodeEditorPlugin:
    """代码编辑器插件"""

    def __init__(self):
        self.name = "代码编辑器"
        self.version = PLUGIN_VERSION
        self.id = "qwenpaw-code-editor"
        self.router = router

    def register(self, api) -> None:
        if hasattr(api, "register_http_router"):
            api.register_http_router(
                self.router,
                prefix="/qwenpaw-code-editor",
                tags=["qwenpaw-code-editor"],
            )
            logger.info("[qwenpaw-code-editor] HTTP router registered at /api/qwenpaw-code-editor")

        if hasattr(api, "register_startup_hook"):
            api.register_startup_hook("qwenpaw_code_editor_startup", self._startup)

        if hasattr(api, "register_shutdown_hook"):
            api.register_shutdown_hook("qwenpaw_code_editor_shutdown", self._shutdown)

    async def _startup(self) -> None:
        logger.info(
            "[qwenpaw-code-editor] Plugin v%s started - workdir=%s mode=%s",
            PLUGIN_VERSION,
            _working_dir().resolve(),
            _mode(),
        )

    async def _shutdown(self) -> None:
        logger.info("[qwenpaw-code-editor] Plugin stopped")

# REQUIRED: 模块级 plugin 实例
plugin = CodeEditorPlugin()

