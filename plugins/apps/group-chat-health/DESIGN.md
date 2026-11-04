# QwenPaw 通用群聊插件设计说明

> 产品名称：Group Chat / 通用群聊
> 兼容 ID：`group-chat-health`
> 版本：`0.3.4`
> QwenPaw：`>=2.2.0,<2.3.0`

## 产品边界

插件只提供群聊编排，不定义成员的专业领域。成员列表实时来自 QwenPaw 当前配置中已启用的 Agent；每位 Agent 原有的人设、系统指令、知识、模型和工具权限继续生效。

插件额外拥有一个 `gc-message-router` 内部 Agent。它通过 QwenPaw 2.2 的 `ManagedAgentProfile` 注册并标记为 app-managed，只读取群成员的名称、描述和最近上下文来选择回复者，不直接回答用户问题。

## 核心流程

空群聊沿用即时通讯产品的会话起始样式：在消息流顶部显示创建时间、建群状态和成员加入状态，不用居中任务卡或预设问题干扰用户直接发言。

### 普通消息

1. 保存用户消息和附件引用。
2. 路由 Agent 通常选择一位最匹配成员；仅在用户明确要求多人或任务确实跨角色时选择多位。
3. 后端依次调用成员，并用 SSE 输出路由、文本分块和完成事件。
4. 路由不可用时只回退到群内首位可用成员，不使用领域关键词硬编码。

路由和接力事件属于内部编排信息。前端等待态只显示“成员正在输入”，不提前暴露具体回复者，也不在消息区重复生成临时输入气泡。

### 用户和 Agent 的 `@`

- 前端 `Mentions` 同时支持 `@` 和 `＠`，一条消息可按文本顺序提及多位成员。
- 消息高亮优先按当前群成员的完整 mention 名称匹配，并按长度降序处理，因此名称包含空格或存在前缀关系时不会被截断。
- 后端再次解析并验证目标仍在群内且处于启用状态。
- Agent 回复中的有效提及会创建下一轮接力；同一链路每个 Agent 最多回复一次，总深度不超过 `MAX_CHAIN_DEPTH=6`。
- 重名 Agent 必须使用 ID 作为唯一提及词，避免错误路由。

### 配置变化

- 新建或更新群成员时只接受当前存在且已启用的 Agent。
- 已保存群聊仍可加载，即使其中某成员后来被删除或停用；不可用成员不会被调用，用户可在群资料中更新成员。
- 当全部成员不可用时，发送会返回明确且不可重试的错误，不写入一条无法处理的新消息。

## QwenPaw 2.2 接入

- 清单使用 `type: "app"` 和 `qwenpaw_version`。
- 前端复用宿主的 React、Ant Design、图标、主题、认证 Fetch 和路由注册能力。
- 调用 `host.fetch` / `host.getApiUrl` 时只传插件相对路径 `/group-chat-health/...`；全局 `/api` 前缀由 QwenPaw 宿主统一添加。
- 后端通过 `PluginApi` 注册路由与生命周期钩子。
- 内部路由通过 `qwenpaw.pawapp.agent.ManagedAgentProfile` 管理；卸载时仅 detach，不删除工作区数据。
- 成员调用沿用 QwenPaw 的 Agent 管理协议和稳定群聊 session ID。

## 数据与兼容迁移

状态仍写入 `<QWENPAW_WORKING_DIR>/group_chat_health/`，以便 `0.2.x` 原地升级。`state.json` 通过同目录临时文件原子替换；损坏状态会在首次写入前备份为 `state.corrupt-<timestamp>.json`。

保留内部 ID、API 前缀和 session 前缀是有意的兼容决策，不代表产品仍限定为健康场景。旧版领域 Agent 由用户配置拥有，升级和卸载均不自动删除。

## API

所有路径继续挂载在 `/api/group-chat-health`：

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/agents` | 当前已启用、可选择的 QwenPaw Agent |
| `POST` / `GET` | `/chats` | 创建 / 列出群聊 |
| `GET` / `DELETE` | `/chats/{chat_id}` | 群聊详情 / 删除 |
| `PUT` | `/chats/{chat_id}/agents` | 更新成员 |
| `POST` | `/chats/{chat_id}/messages` | 发送消息并返回 SSE 回复链 |
| `POST` | `/chats/{chat_id}/messages/{message_id}/retry` | 重试成员回复 |
| `GET` | `/chats/{chat_id}/events` | 群聊事件流 |
| `POST` | `/upload` | 上传附件 |
| `PUT` | `/chats/{chat_id}/proactive` | 更新主动参与设置 |

## 安全与可靠性

- 消息最多 8000 字；单个附件最多 20 MB；文件名经过净化，落盘名由服务端生成。
- 路由结果必须属于当前群且当前可用，不能把消息转给群外 Agent。
- Agent 接力去重并限制深度，避免循环。
- 主动参与默认关闭，并受静默时段、每日次数、冷却和用户近期活跃约束。
- 插件不写死模型、API Key 或 Agent 工具权限，实际回复能力取决于用户的 QwenPaw 配置。
