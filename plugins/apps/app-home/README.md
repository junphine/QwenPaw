# 应用首页（app-home）

QwenPaw 应用仪表盘首页插件。

## 功能

1. **应用列表**：展示本机已安装的应用（type=app 的插件）
2. **启动默认应用**：点击"设为启动默认"后，QwenPaw 桌面版启动时先打开该应用
3. **ON/OFF 开关**：控制是否启用"启动时自动打开默认应用"
4. **双显示模式**：同时出现在应用栏目和侧边栏设置分组
5. **轻应用**：创建/编辑/删除轻应用（name + url），在首页以卡片展示；删除操作放在编辑弹窗内。点击"打开"用 **iframe** 内嵌展示，并在 `src` 的 query 中带上身份/签名参数

## 数据流

```
前端 ui/index.js
  ↓ GET  /api/plugins/app-home/apps
  ↓ POST /api/plugins/app-home/default
  ↓ GET/POST/PUT/DELETE /api/plugins/app-home/lightapps
后端 backend/main.py
  ↓ 读写 ~/.qwenpaw/plugins/app-home/config.json
  ↓ 读写 $QWENPAW_WORKING_DIR/lightapp_data/apps.json
```

## 配置示例

```json
{
  "default_app_id": "qwenpaw-resource-monitor",
  "enabled": true
}
```

## 轻应用数据示例

轻应用数据与原 `qwenpaw-lightapp` 插件共用同一文件
（`$QWENPAW_WORKING_DIR/lightapp_data/apps.json`），迁移零成本：

```json
[
  {
    "name": "我的看板",
    "url": "https://example.com/board",
    "width": "100%",
    "height": "100%"
  }
]
```

## 轻应用 iframe 身份参数

打开轻应用时，会在其 `src` 的 query 中追加以下参数：

| 参数 | 含义 |
|------|------|
| `agent_id` | 当前选中的智能体 id（`getSelectedAgentId()`） |
| `user_id` | 当前登录账号用户名（`/api/auth/verify`） |
| `signature` | 数据签名：复用当前登录 API Token（HMAC-SHA256 签名令牌） |
| `timestamp` | 当前 Unix 时间戳（秒），供目标应用校验新鲜度 |

> 注意：`signature`（API Token）会出现在 iframe URL 中，目标应用应通过受控环境
> 校验；如对 token 泄露敏感，请改用后端 HMAC 签名方案。

## 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/plugins/app-home/apps` | 应用列表 + 当前默认 |
| GET | `/api/plugins/app-home/default` | 当前默认配置 |
| POST | `/api/plugins/app-home/default` | 设置默认应用 |
| GET | `/api/plugins/app-home/lightapps` | 轻应用列表 |
| POST | `/api/plugins/app-home/lightapps` | 创建轻应用 |
| PUT | `/api/plugins/app-home/lightapps/{id}` | 更新轻应用 |
| DELETE | `/api/plugins/app-home/lightapps/{id}` | 删除轻应用 |

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
- v0.3.0 — 系统概览/Agent 列表/工具入口等仪表盘聚合
- v0.4.0 — 合并 qwenpaw-lightapp：首页支持创建/编辑/删除并展示轻应用
