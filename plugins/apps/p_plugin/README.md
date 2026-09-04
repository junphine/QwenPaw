# P Plugin v5.5.1 - PawApp SDK 版本

## 迁移说明

此版本将 P Plugin 从 FastAPI 原生模式迁移到 **PawApp SDK** 模式，兼容 QwenPaw v2.0.1+。

### 主要变更

#### 1. 后端架构 (backend/main.py)

**之前 (v3.9.0):**
```python
from fastapi import APIRouter
router = APIRouter()
# 直接定义路由
```

**现在 (v5.5.1):**
```python
from qwenpaw.pawapp import PawApp, get_ctx
from fastapi import APIRouter

router = APIRouter()
app = PawApp(name="P", app_id="p_plugin")
app.include_router(router)

@app.on_launch
async def on_launch():
    """插件加载时调用"""
    pass

@app.on_terminate
async def on_terminate():
    """插件卸载时调用"""
    pass

plugin = app  # 导出插件变量
```

#### 2. 智能体调用

**之前:** HTTP API 调用 (`/api/agents/{id}/chats`)

**现在:** PawApp SDK (`ctx.chat_stream()`)
```python
async for ev in ctx.chat_stream(prompt, session_id=f"p_plugin:{room_id}:{agent_id}"):
    if hasattr(ev, 'content'):
        # 处理响应
```

#### 3. 生命周期钩子

新增 `@app.on_launch` 和 `@app.on_terminate`:
- **on_launch**: 加载数据、启动后台任务
- **on_terminate**: 保存数据、清理资源

#### 4. 插件配置 (plugin.json)

```json
{
  "type": "app",
  "entry": {
    "backend": "backend/main.py",
    "frontend": "ui/index.js"
  },
  "qwenpaw_version": {
    "min": "2.0.1"
  },
  "meta": {
    "pawapp": {
      "icon": "Q",
      "category": "productivity",
      "entry_page": "/apps/p_plugin",
      "launch_scope": "page"
    }
  }
}
```

### 保留的功能

- ✅ AI 群聊核心功能
- ✅ 智能体文件生成 (`[FILE:...][/FILE]`)
- ✅ 并发回复 + 随机延时
- ✅ WebSocket 实时通信
- ✅ 文件上传/下载/预览
- ✅ 微信频道集成
- ✅ 多语言支持

### 文件结构

```
p_plugin/
├── backend/
│   └── main.py          # PawApp SDK 后端 (新)
├── ui/
│   └── index.js         # 前端 (兼容)
├── data/                # 数据存储
├── plugin.json          # 插件配置 (更新)
└── README.md            # 本文档
```

### 兼容性

- **QwenPaw 版本**: >= 2.0.1
- **Python 版本**: >= 3.11 (与 QwenPaw v2.0.1 一致)

### 参考

- [Agent Kanban](https://github.com/agentscope-ai/QwenPaw/pull/6150) - 官方 PawApp SDK 示例
- [PawApp SDK 文档](https://qwenpaw.agentscope.io/docs/plugins)

---

**版本**: 4.0.0  
**更新日期**: 2026-07-27  
**作者**: Team
