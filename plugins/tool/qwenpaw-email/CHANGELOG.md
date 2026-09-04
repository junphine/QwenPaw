# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-08-01

### Added
- 多后端架构：统一 CLI 入口 `cli.py`，支持 `imap_smtp`、`openclaw`、`hermes`
- `backends/types.py`：抽象基类 `EmailBackend` + 标准化 `EmailMessage`
- `backends/imap_smtp.py`：完整 IMAP/SMTP 实现，支持 QQ/Gmail/163/Outlook
- `backends/openclaw.py`：OpenClaw 托管邮件后端（REST API + CLI 双模式）
- `backends/hermes.py`：Hermes 邮件后端（接口预留，待补齐）
- 配置驱动后端选择，支持自动检测
- 新增 `reply` 命令
- 单元测试 `tests/test_backends.py`

### Changed
- 版本号升级到 2.0.0
- 项目类型从 skill 升级为 plugin
- `package.json` 增加 `qwenpaw.backends` 和 `scripts.test`

### Fixed
- 修复 Python `email` 模块与项目文件名的循环导入问题

## [1.0.0] - 2026-08-01

### Added
- 初始版本发布
- SMTP 发送邮件支持（SSL）
- IMAP 收件箱读取支持
- 邮件列表、详情、搜索、最新邮件读取
- 从 `credentials.yaml` 自动读取配置
- 支持 163、QQ、Gmail、Outlook 等主流邮箱
- 完整的 SKILL.md 文档
