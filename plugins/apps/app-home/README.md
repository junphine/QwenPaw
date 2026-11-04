# 应用首页（app-home）

QwenPaw 应用仪表盘首页插件。

## 功能

1. **应用列表**：展示本机已安装的应用（type=app 的插件）
2. **启动默认应用**：点击"设为启动默认"后，QwenPaw 桌面版启动时先打开该应用
3. **ON/OFF 开关**：控制是否启用"启动时自动打开默认应用"
4. **双显示模式**：同时出现在应用栏目和侧边栏设置分组

## 数据流

```
前端 ui/index.js
  ↓ GET  /api/plugins/app-home/apps
  ↓ POST /api/plugins/app-home/default
后端 backend/main.py
  ↓ 读写 ~/.qwenpaw/plugins/app-home/config.json
```

## 配置示例

```json
{
  "default_app_id": "qwenpaw-resource-monitor",
  "enabled": true
}
```

## 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/plugins/app-home/apps` | 应用列表 + 当前默认 |
| GET | `/api/plugins/app-home/default` | 当前默认配置 |
| POST | `/api/plugins/app-home/default` | 设置默认应用 |

## 安装

```bash
# 复制到插件目录
cp -r app-home ~/.qwenpaw/plugins/

# 重启 QwenPaw 或热重载
curl -X POST http://127.0.0.1:56069/api/plugins/install \
  -H "Content-Type: application/json" \
  -d '{"source": "~/.qwenpaw/plugins/app-home", "force": true}'
```

## 版本

- v0.1.0 — 初始版本，支持应用列表、默认启动应用、ON/OFF 开关
