# QwenPaw Email Plugin 📧

给 QwenPaw / OpenClaw / Hermes Agent 增加完整的电子邮件能力：发送、读取、搜索、回复邮件。

## 功能

- **多后端统一接口**：一套 CLI，背后可切换 IMAP/SMTP、OpenClaw、Hermes
- **专用邮箱支持**：QQ、Gmail、163、Outlook 等标准 IMAP/SMTP 邮箱
- **托管服务支持**：OpenClaw 托管邮箱（REST API 或本地 CLI）
- **Hermes 预留**：接口已定义，后续直接补齐实现
- **配置驱动**：通过 `credentials.yaml` 选择后端，无需改代码
- **自动检测**：不填 `provider` 时自动判断用哪种后端

## 架构

```
email.py (CLI 入口)
    │
    ▼
backends/
    ├── types.py          ← EmailBackend 抽象基类 + EmailMessage
    ├── imap_smtp.py      ← QQ/Gmail/163/Outlook 等
    ├── openclaw.py       ← OpenClaw 托管服务
    └── hermes.py         ← Hermes 服务（预留）
```

## 安装

### 方式一：QwenPaw Plugin 市场（推荐）

1. 打开 QwenPaw Plugin 广场
2. 搜索 `qwenpaw-email`
3. 点击安装

### 方式二：手动安装

```bash
git clone https://github.com/YOUR_USERNAME/qwenpaw-email.git
cd qwenpaw-email
```

## 快速开始

### 1. 配置 `credentials.yaml`

在 workspace 根目录创建：

```yaml
email/agent:
  kind: static
  provider: imap_smtp   # 可选，默认自动检测
  public:
    address: "your-email@example.com"
    smtp_host: "smtp.example.com"
    smtp_port: "465"
    imap_host: "imap.example.com"
    imap_port: "993"
    # OpenClaw 示例：
    # api_base: "https://openclaw.ai/api/v1"
    # cli_path: "claw"
  secrets:
    password: "your-password-or-app-token"
    # OpenClaw 示例：
    # api_key: "your-api-key"
```

### 2. 使用 CLI

```bash
# 发送邮件
python cli.py send \
  --to "recipient@example.com" \
  --subject "Hello" \
  --body "World"

# 查看收件箱
python cli.py list --count 10

# 读取最新邮件
python cli.py latest

# 搜索邮件
python cli.py search "发票" --from "财务"

# 回复邮件
python cli.py reply 123 --body "收到，我尽快处理"
```

### 3. 在 QwenPaw 中使用

配置完成后，直接对 Agent 说：

- "发邮件给 alice@example.com，主题是 项目进度，内容是 本周已完成..."
- "查看收件箱最新邮件"
- "搜索关于 发票 的邮件"
- "回复那封邮件，说 收到，我尽快处理"

## 配置参考

### 专用邮箱（IMAP/SMTP）

| 服务商 | SMTP Host | SMTP Port | IMAP Host | IMAP Port |
|--------|-----------|-----------|-----------|-----------|
| claw.163.com | claw.163.com | 465 | claw.163.com | 993 |
| 163.com | smtp.163.com | 465 | imap.163.com | 993 |
| QQ邮箱 | smtp.qq.com | 465 | imap.qq.com | 993 |
| Gmail | smtp.gmail.com | 587 | imap.gmail.com | 993 |
| Outlook | smtp.office365.com | 587 | outlook.office365.com | 993 |

> **注意**：QQ/Gmail/Outlook 需要使用**应用专用密码**，而非登录密码。

### OpenClaw 托管邮箱

```yaml
email/agent:
  provider: openclaw
  public:
    address: "aristotle@openclaw.ai"
    api_base: "https://openclaw.ai/api/v1"
  secrets:
    api_key: "your-openclaw-api-key"
```

或使用本地 CLI（需已登录 `claw`）：

```yaml
email/agent:
  provider: openclaw
  public:
    address: "aristotle@openclaw.ai"
    cli_path: "claw"
```

### Hermes 邮件服务（预留）

```yaml
email/agent:
  provider: hermes
  public:
    address: "user@hermes.ai"
    api_base: "https://hermes.ai/api/v1"
  secrets:
    api_key: "your-hermes-api-key"
```

## 开发

### 运行测试

```bash
python tests/test_backends.py
```

### 添加新后端

1. 在 `backends/` 下新建 `your_backend.py`
2. 继承 `backends.types.EmailBackend`
3. 实现 6 个抽象方法
4. 在 `backends/__init__.py` 的 `build_backend()` 中注册

## 依赖

- Python 3.8+
- `pyyaml` (`pip install pyyaml`)

## 许可证

Apache 2.0 — 详见 [LICENSE](LICENSE) 文件。

## 作者

Aristotle Agent — 基于真实邮件交互需求构建。
