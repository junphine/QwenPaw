"""
邮件后端包

统一导出：
  - EmailBackend
  - EmailMessage
  - ImapSmtpBackend
  - OpenClawBackend
  - HermesBackend
  - build_backend(config) -> EmailBackend
"""

from .types import EmailBackend, EmailMessage
from .imap_smtp import ImapSmtpBackend
from .openclaw import OpenClawBackend
from .hermes import HermesBackend


def build_backend(config: dict) -> EmailBackend:
    """根据配置创建对应的 backend"""
    provider = config.get('provider', '').lower()
    public = config.get('public', {})
    secrets = config.get('secrets', {})
    
    merged = {
        'address': public.get('address', ''),
        'password': secrets.get('password', ''),
        'smtp_host': public.get('smtp_host', ''),
        'smtp_port': public.get('smtp_port', '465'),
        'imap_host': public.get('imap_host', ''),
        'imap_port': public.get('imap_port', '993'),
        'api_base': public.get('api_base', ''),
        'api_key': secrets.get('api_key', ''),
        'cli_path': public.get('cli_path', 'claw'),
    }
    
    if not provider:
        if merged['api_base'] or merged['api_key']:
            provider = 'openclaw'
        else:
            provider = 'imap_smtp'
    
    if provider == 'imap_smtp':
        return ImapSmtpBackend(merged)
    elif provider == 'openclaw':
        return OpenClawBackend(merged)
    elif provider == 'hermes':
        return HermesBackend(merged)
    else:
        raise ValueError(f"不支持的邮件后端: {provider}")
