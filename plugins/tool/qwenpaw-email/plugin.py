#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QwenPaw Email Plugin 后端入口

通过 api.register_tool 向 Agent 注册邮件能力：
- send_email
- list_emails
- read_email
- search_emails
- reply_email
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, List, Optional

from qwenpaw.plugins.api import PluginApi

# 确保 backends 包可导入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backends import EmailBackend, EmailMessage, build_backend


def _get_backend() -> EmailBackend:
    """懒加载 backend，避免插件加载时就读取配置"""
    config = _load_credentials()
    return build_backend(config)


def _load_credentials() -> dict:
    """从 credentials.yaml 读取邮件配置"""
    workspace = os.environ.get('WORKSPACE_DIR', '')
    cred_path = os.path.join(workspace, 'credentials.yaml') if workspace else 'credentials.yaml'
    
    if not os.path.exists(cred_path):
        cred_path = 'credentials.yaml'
    if not os.path.exists(cred_path):
        raise FileNotFoundError('credentials.yaml not found')
    
    import yaml
    with open(cred_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    email_config = (
        config.get('email/agent')
        or config.get('credentials', {}).get('email/agent')
    )
    if not email_config:
        raise ValueError('email/agent section not found in credentials.yaml')
    
    return email_config


def _format_email(msg: EmailMessage) -> Dict[str, Any]:
    """将 EmailMessage 转为字典，方便 Agent 理解"""
    return {
        'id': msg.id,
        'subject': msg.subject,
        'from': msg.from_,
        'to': msg.to,
        'date': msg.date,
        'body': msg.body,
        'folder': msg.folder,
    }


# ---- Agent 可调用工具 ----

def send_email(to: str, subject: str, body: str, html: bool = False) -> Dict[str, Any]:
    """发送邮件。

    Args:
        to: 收件人邮箱地址
        subject: 邮件主题
        body: 邮件正文
        html: 是否使用 HTML 格式

    Returns:
        发送结果，包含 success 字段
    """
    backend = _get_backend()
    ok = backend.send(to=to, subject=subject, body=body, html=html)
    return {
        'success': ok,
        'to': to,
        'subject': subject,
        'message': '邮件发送成功' if ok else '邮件发送失败',
    }


def list_emails(folder: str = 'INBOX', count: int = 10) -> List[Dict[str, Any]]:
    """列出收件箱邮件。

    Args:
        folder: 文件夹名称，默认 INBOX
        count: 返回数量，默认 10

    Returns:
        邮件列表，每封邮件包含 id, subject, from, date
    """
    backend = _get_backend()
    emails = backend.list(folder=folder, count=count)
    return [_format_email(e) for e in emails]


def read_email(email_id: str) -> Optional[Dict[str, Any]]:
    """读取指定邮件详情。

    Args:
        email_id: 邮件 ID

    Returns:
        邮件详情，包含 id, subject, from, to, date, body, folder
    """
    backend = _get_backend()
    msg = backend.read(email_id)
    if msg is None:
        return None
    return _format_email(msg)


def latest_email() -> Optional[Dict[str, Any]]:
    """读取最新一封邮件。

    Returns:
        最新邮件详情，包含 id, subject, from, to, date, body, folder
    """
    backend = _get_backend()
    msg = backend.latest()
    if msg is None:
        return None
    return _format_email(msg)


def search_emails(
    keyword: Optional[str] = None,
    from_: Optional[str] = None,
    subject: Optional[str] = None,
    folder: str = 'INBOX',
    count: int = 10,
) -> List[Dict[str, Any]]:
    """搜索邮件。

    Args:
        keyword: 关键词（在主题和正文中搜索）
        from_: 发件人筛选
        subject: 主题关键词
        folder: 文件夹，默认 INBOX
        count: 返回数量，默认 10

    Returns:
        匹配的邮件列表
    """
    backend = _get_backend()
    emails = backend.search(
        keyword=keyword,
        from_=from_,
        subject=subject,
        folder=folder,
        count=count,
    )
    return [_format_email(e) for e in emails]


def reply_email(email_id: str, body: str, html: bool = False) -> Dict[str, Any]:
    """回复邮件。

    Args:
        email_id: 原邮件 ID
        body: 回复正文
        html: 是否使用 HTML 格式

    Returns:
        回复结果，包含 success 字段
    """
    backend = _get_backend()
    ok = backend.reply(email_id=email_id, body=body, html=html)
    return {
        'success': ok,
        'email_id': email_id,
        'message': '回复成功' if ok else '回复失败',
    }


# ---- 插件入口 ----

class QwenPawEmailPlugin:
    """QwenPaw Email Plugin."""

    def register(self, api: PluginApi):
        """注册邮件工具到 Agent。

        Args:
            api: PluginApi 实例
        """
        # 注册发送邮件工具
        api.register_tool(
            tool_name="send_email",
            tool_func=send_email,
            description="发送邮件。参数: to(收件人), subject(主题), body(正文), html(是否HTML格式)",
            icon="📧",
            enabled=True,
        )

        # 注册列出收件箱工具
        api.register_tool(
            tool_name="list_emails",
            tool_func=list_emails,
            description="列出收件箱邮件。参数: folder(文件夹,默认INBOX), count(数量,默认10)",
            icon="📬",
            enabled=True,
        )

        # 注册读取邮件工具
        api.register_tool(
            tool_name="read_email",
            tool_func=read_email,
            description="读取指定邮件详情。参数: email_id(邮件ID)",
            icon="📄",
            enabled=True,
        )

        # 注册读取最新邮件工具
        api.register_tool(
            tool_name="latest_email",
            tool_func=latest_email,
            description="读取最新一封邮件。无需参数",
            icon="🕐",
            enabled=True,
        )

        # 注册搜索邮件工具
        api.register_tool(
            tool_name="search_emails",
            tool_func=search_emails,
            description="搜索邮件。参数: keyword(关键词), from_(发件人), subject(主题), folder(文件夹), count(数量)",
            icon="🔍",
            enabled=True,
        )

        # 注册回复邮件工具
        api.register_tool(
            tool_name="reply_email",
            tool_func=reply_email,
            description="回复邮件。参数: email_id(原邮件ID), body(回复正文), html(是否HTML格式)",
            icon="↩️",
            enabled=True,
        )


# 导出 plugin 实例（QwenPaw 会调用 register）
plugin = QwenPawEmailPlugin()
