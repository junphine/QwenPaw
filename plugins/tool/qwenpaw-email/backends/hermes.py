"""
Hermes 邮件后端（预留）

Hermes 是另一个 agent 邮件生态。此处保留接口和最小实现，
后续补齐时只需实现 _call_api / _call_cli 两个底层方法。

配置示例（credentials.yaml）：

```yaml
email/agent:
  kind: static
  provider: hermes
  public:
    address: "user@hermes.ai"
    api_base: "https://hermes.ai/api/v1"
  secrets:
    api_key: "your-api-key"
```
"""

from __future__ import annotations

from typing import List, Optional

from .types import EmailBackend, EmailMessage


class HermesBackend(EmailBackend):
    """Hermes 邮件后端（占位实现）"""
    
    def __init__(self, config: dict):
        self.address = config['address']
        self.api_base = config.get('api_base', 'https://hermes.ai/api/v1').rstrip('/')
        self.api_key = config.get('api_key', '')
    
    def _ensure_api(self):
        if not self.api_key:
            raise RuntimeError('Hermes API key 未配置')
    
    # ---- 占位实现 ----
    
    def send(self, to: str, subject: str, body: str, html: bool = False) -> bool:
        self._ensure_api()
        # TODO: 接入 Hermes API
        raise NotImplementedError('Hermes send 尚未实现')
    
    def list(self, folder: str = 'INBOX', count: int = 10) -> List[EmailMessage]:
        self._ensure_api()
        raise NotImplementedError('Hermes list 尚未实现')
    
    def read(self, email_id: str) -> Optional[EmailMessage]:
        self._ensure_api()
        raise NotImplementedError('Hermes read 尚未实现')
    
    def latest(self) -> Optional[EmailMessage]:
        self._ensure_api()
        raise NotImplementedError('Hermes latest 尚未实现')
    
    def search(
        self,
        keyword: Optional[str] = None,
        from_: Optional[str] = None,
        subject: Optional[str] = None,
        folder: str = 'INBOX',
        count: int = 10,
    ) -> List[EmailMessage]:
        self._ensure_api()
        raise NotImplementedError('Hermes search 尚未实现')
    
    def reply(self, email_id: str, body: str, html: bool = False) -> bool:
        self._ensure_api()
        raise NotImplementedError('Hermes reply 尚未实现')
