"""
邮件后端单元测试

运行方式：
  python -m pytest tests/ -v
  或
  python tests/test_backends.py
"""

from __future__ import annotations

import sys
import os

# 确保可导入 backends
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backends import EmailMessage, ImapSmtpBackend, OpenClawBackend, HermesBackend


def test_email_message_dataclass():
    msg = EmailMessage(
        id='1',
        subject='Test',
        from_='a@b.com',
        to='c@d.com',
        date='2026-08-01',
        body='hello',
        folder='INBOX',
    )
    assert msg.id == '1'
    assert msg.subject == 'Test'
    assert msg.folder == 'INBOX'
    print('✅ EmailMessage dataclass OK')


def test_imap_smtp_backend_init():
    config = {
        'address': 'user@example.com',
        'password': 'secret',
        'smtp_host': 'smtp.example.com',
        'smtp_port': 465,
        'imap_host': 'imap.example.com',
        'imap_port': 993,
    }
    backend = ImapSmtpBackend(config)
    assert backend.address == 'user@example.com'
    assert backend.smtp_port == 465
    print('✅ ImapSmtpBackend init OK')


def test_openclaw_backend_init():
    config = {
        'address': 'user@openclaw.ai',
        'api_base': 'https://openclaw.ai/api/v1',
        'api_key': 'test-key',
    }
    backend = OpenClawBackend(config)
    assert backend._use_api is True
    print('✅ OpenClawBackend init OK')


def test_hermes_backend_init():
    config = {
        'address': 'user@hermes.ai',
        'api_base': 'https://hermes.ai/api/v1',
        'api_key': 'test-key',
    }
    backend = HermesBackend(config)
    assert backend.address == 'user@hermes.ai'
    print('✅ HermesBackend init OK')


def test_backend_interface_coverage():
    """确保所有 backend 都实现了统一接口"""
    for cls in [ImapSmtpBackend, OpenClawBackend, HermesBackend]:
        for method in ['send', 'list', 'read', 'latest', 'search', 'reply']:
            assert hasattr(cls, method), f"{cls.__name__} 缺少方法 {method}"
    print('✅ Backend interface coverage OK')


if __name__ == '__main__':
    test_email_message_dataclass()
    test_imap_smtp_backend_init()
    test_openclaw_backend_init()
    test_hermes_backend_init()
    test_backend_interface_coverage()
    print('\n所有测试通过 ✅')
