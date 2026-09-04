---
name: email
description: Use this skill when the user asks to send, read, search, or reply to emails. Supports SMTP sending and IMAP reading. Use for composing new emails, checking inbox, searching messages, and replying to threads.
metadata:
  builtin_skill_version: "2.0"
  qwenpaw:
    emoji: "📧"
---

# Email Plugin

## When to Use

Use this skill whenever the user interacts with email:

- Send a new email (`--to`, `--subject`, `--body`)
- Read inbox listing (`list`)
- Read a specific email (`read <id>`)
- Read the latest email (`latest`)
- Search emails (`search <keyword>`)
- Reply to an email (read first, then send a reply)

### Should Use
- "发邮件给 xxx"
- "查看收件箱"
- "给我看看最新的邮件"
- "搜索关于 xxx 的邮件"
- "回复那封邮件，说 ..."

### Should Not Use
- When the user is just chatting in the current session
- When email is only a minor detail and not the primary request

---

## Architecture

本插件采用**多后端抽象层**设计，统一接口，可插拔：

```
email.py (CLI 入口)
    │
    ▼
backends/
    ├── types.py          ← 抽象基类 EmailBackend + EmailMessage
    ├── imap_smtp.py      ← QQ / Gmail / 163 等标准邮箱
    ├── openclaw.py       ← OpenClaw 托管邮件服务
    └── hermes.py         ← Hermes 邮件服务（预留）
```

- **统一命令**：`cli.py send/list/read/latest/search/reply`
- **配置驱动**：通过 `credentials.yaml` 中的 `provider` 字段选择后端
- **自动检测**：未指定 `provider` 时，根据 `api_base` / `api_key` 自动判断

---

## Prerequisites

### 1. Configure credentials

在 agent workspace 根目录创建 `credentials.yaml`：

```yaml
email/agent:
  kind: static
  provider: imap_smtp   # 可选：imap_smtp | openclaw | hermes
  public:
    address: "your-email@example.com"
    smtp_host: "smtp.example.com"
    smtp_port: "465"
    imap_host: "imap.example.com"
    imap_port: "993"
    # OpenClaw / Hermes 可选：
    # api_base: "https://openclaw.ai/api/v1"
    # cli_path: "claw"
  secrets:
    password: "your-password-or-app-token"
    # OpenClaw / Hermes 可选：
    # api_key: "your-api-key"
```

### 2. Supported backends

| Backend | Provider | 适用场景 | 配置关键字段 |
|---------|----------|----------|--------------|
| IMAP/SMTP | `imap_smtp` | QQ / Gmail / 163 / Outlook 等标准邮箱 | `address`, `password`, `smtp_host`, `imap_host` |
| OpenClaw | `openclaw` | OpenClaw 托管邮件 | `address`, `api_key` 或本地 `claw` CLI 会话 |
| Hermes | `hermes` | Hermes 邮件服务（预留） | `address`, `api_key` |

### 3. Notes

- **专用邮箱**：QQ/Gmail/Outlook 需要使用**应用专用密码**，而非登录密码。
- **OpenClaw**：优先使用 REST API（配置 `api_key`）；也可降级使用本地 `claw` CLI（需已登录）。
- **Hermes**：当前为预留实现，接口已定义，后续补齐具体 API 对接即可。

---

## Commands

### Send an email

```bash
python cli.py send \
  --to "recipient@example.com" \
  --subject "Subject" \
  --body "Body text" \
  --html   # optional, send as HTML
```

### List inbox

```bash
python cli.py list --count 10
```

### Read specific email

```bash
python cli.py read <id>
```

### Read latest email

```bash
python cli.py latest
```

### Search emails

```bash
# By keyword
python cli.py search "keyword"

# By sender
python cli.py search --from "sender@example.com"

# By subject
python cli.py search --subject "meeting"

# Combined
python cli.py search "report" --from "boss" --subject "weekly"
```

### Reply to an email

```bash
python cli.py reply <email_id> \
  --body "收到，我尽快处理" \
  --html   # optional
```

---

## Workflow Examples

### Send a simple email

1. User says: "发邮件给 alice@example.com，主题是 项目进度，内容是 本周已完成..."
2. Run `cli.py send --to ... --subject ... --body ...`
3. Confirm success/failure to user

### Read and reply

1. User says: "查看收件箱最新邮件"
2. Run `cli.py latest`
3. Summarize content to user
4. User says: "回复那封邮件，说 收到，我尽快处理"
5. Run `cli.py reply <id> --body ...`

### Search and summarize

1. User says: "搜索关于 发票 的邮件"
2. Run `cli.py search "发票"`
3. List matching emails
4. If user wants details, run `cli.py read <id>`

---

## Extending

### Adding a new backend

1. 在 `backends/` 下新建文件，继承 `EmailBackend`
2. 实现 6 个抽象方法
3. 在 `backends/__init__.py` 中注册到 `build_backend()`
4. 在 `package.json` 的 `qwenpaw.backends` 中追加名称

### Adding attachments

在 `backends/imap_smtp.py` 的 `send()` 中使用 `MIMEMultipart` + `MIMEBase` 附件；
在 `backends/openclaw.py` 的 `send()` 中按 API 文档添加 `attachments` 字段。

### Scheduled checks

使用 `cron` skill 定时运行 `cli.py list`。
