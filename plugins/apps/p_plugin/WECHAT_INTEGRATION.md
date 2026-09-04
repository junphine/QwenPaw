# P Plugin 微信频道集成指南

## 概述

P Plugin 现在可以作为 QwenPaw 微信频道的**综合性智能体**使用。微信用户可以直接与 P-Chat 对话，创建 AI 群聊房间、发送消息、与多个 AI 智能体协作。

## 功能特性

| 功能 | 说明 |
|------|------|
| 🏠 创建房间 | 微信用户输入「创建房间」即可创建新的 AI 群聊 |
| 📋 房间列表 | 查看所有可用的群聊房间 |
| 💬 群聊对话 | 发送消息到房间，AI 智能体自动回复 |
| 🔗 分享链接 | 获取房间链接，邀请其他人加入 |
| 🤖 智能体管理 | 添加/移除 AI 智能体成员 |

## 快速配置

### 1. 确保 P Plugin 已安装

```bash
# 检查插件目录
ls ~/.qwenpaw/plugins/p_plugin/
```

应该包含以下文件：
- `p_plugin_main.py` - 主程序
- `plugin.json` - 插件配置
- `wechat_adapter.py` - 微信适配器
- `p_chat_agent.yaml` - 智能体配置

### 2. 重启 QwenPaw

```bash
qwenpaw restart
```

### 3. 配置微信频道

在 QwenPaw 配置文件中添加 P-Chat 智能体：

```yaml
# ~/.qwenpaw/config.yaml
channels:
  wechat:
    enabled: true
    agents:
      - id: p_chat
        name: P-Chat
        description: AI 群聊助手
        system_prompt: |
          你是 P-Chat，一个专业的 AI 群聊助手。
          你可以帮助用户创建 AI 群聊房间，与多个智能体协作。
        tools:
          - p_create_room
          - p_list_rooms
          - p_get_room_info
          - p_send_room_message
          - p_add_agent
```

### 4. 验证集成

在微信中发送消息：

```
创建房间
```

预期回复：
```
✅ 房间创建成功！

🏠 **微信用户的群聊**
🆔 房间ID: `abc123`

🔗 **分享链接**: http://...

💬 现在直接发送消息，我会转发到群聊中！
```

## 使用示例

### 创建房间并聊天

**微信用户**: `创建房间`

**P-Chat**: 
```
✅ 房间创建成功！
🏠 **微信用户的群聊**
🆔 房间ID: `abc123`
🔗 分享链接: http://localhost:8088/api/plugins/p_plugin/web/abc123
```

**微信用户**: `大家好！`

**P-Chat**:
```
🤖 **Default**: 你好！很高兴见到你。

🤖 **QA Agent**: 欢迎来到群聊！有什么我可以帮助的吗？
```

### 查看房间列表

**微信用户**: `房间列表`

**P-Chat**:
```
📋 **房间列表**

1. **微信用户的群聊**
   🆔 `abc123` | 🤖 2 个智能体

2. **官方聊天室**
   🆔 `official` | 🤖 5 个智能体

💡 输入「加入房间 xxx」加入指定房间
```

### 加入房间

**微信用户**: `加入房间 official`

**P-Chat**:
```
✅ 已加入房间: **官方聊天室**

🤖 智能体: Default, QA Agent, CloudPaw-Master, Assistant, Helper

💬 直接发送消息即可参与群聊！
```

## 命令参考

| 命令 | 说明 |
|------|------|
| `创建房间` | 创建新的 AI 群聊房间 |
| `房间列表` | 查看所有房间 |
| `加入房间 xxx` | 加入指定房间 |
| `帮助` / `?` | 显示帮助菜单 |
| `[任意文字]` | 发送消息到当前房间 |

## 技术架构

```
微信用户消息
    ↓
QwenPaw 微信频道
    ↓
P Plugin WeChat Handler (_handle_wechat_message)
    ↓
P Plugin Agent Tools (p_create_room, p_send_room_message, etc.)
    ↓
AI Group Chat Room
    ↓
AI Agents Response
    ↓
返回微信用户
```

## 故障排除

### 智能体不回复

1. 检查 QwenPaw 是否正常运行
2. 检查 P Plugin 是否已加载
3. 查看日志：`~/.qwenpaw/logs/p_plugin.log`

### 房间创建失败

1. 确保 `DATA_DIR` 有写入权限
2. 检查 `p_plugin/data/` 目录是否存在

### 消息发送失败

1. 检查用户是否已加入房间
2. 检查房间 ID 是否正确

## 更新日志

- **v3.8.0**: 添加微信频道原生支持
- **v3.7.0**: 添加多语言支持、权限控制
- **v3.6.0**: 添加 Emoji 选择器、消息搜索
- **v3.5.0**: 添加微信集成 API

## 相关文件

- `p_plugin_main.py` - 主程序，包含微信处理器
- `wechat_adapter.py` - 微信适配器（备用）
- `p_chat_agent.yaml` - 智能体配置
- `web_chat.html` - 网页版聊天界面
