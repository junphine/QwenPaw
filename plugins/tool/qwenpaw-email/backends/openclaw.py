"""
OpenClaw 托管邮件后端

通过 OpenClaw CLI / API 访问托管邮箱。
适用于使用 OpenClaw 作为邮件托管服务的场景。

配置示例（credentials.yaml）：

```yaml
email/agent:
  kind: static
  provider: openclaw
  public:
    address: "aristotle@openclaw.ai"
    api_base: "https://openclaw.ai/api/v1"
    # 或使用本地 CLI：
    # cli_path: "claw"
  secrets:
    api_key: "your-api-key"
    # 或使用已认证的 CLI 会话（无需 api_key）
```

使用方式：
- 优先使用 REST API（需要 api_key）
- 降级使用本地 CLI（需要已登录的 claw 会话）
"""

from __future__ import annotations

import json
import os
import subprocess
import urllib.request
import urllib.error
from typing import List, Optional

from .types import EmailBackend, EmailMessage


class OpenClawBackend(EmailBackend):
    """OpenClaw 托管邮件后端"""
    
    def __init__(self, config: dict):
        self.address = config['address']
        self.api_base = config.get('api_base', 'https://openclaw.ai/api/v1').rstrip('/')
        self.api_key = config.get('api_key', '')
        self.cli_path = config.get('cli_path', 'claw')
        self._use_api = bool(self.api_key)
    
    def _api_headers(self) -> dict:
        if not self._use_api:
            raise RuntimeError('API key not configured')
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
    
    def _api_get(self, path: str) -> dict:
        """调用 OpenClaw REST API (GET)"""
        url = f"{self.api_base}{path}"
        req = urllib.request.Request(url, headers=self._api_headers())
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', errors='replace')
            raise RuntimeError(f"OpenClaw API 错误 {e.code}: {body}")
        except Exception as e:
            raise RuntimeError(f"OpenClaw API 请求失败: {e}")
    
    def _api_post(self, path: str, payload: dict) -> dict:
        """调用 OpenClaw REST API (POST)"""
        url = f"{self.api_base}{path}"
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=data,
            headers=self._api_headers(),
            method='POST',
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', errors='replace')
            raise RuntimeError(f"OpenClaw API 错误 {e.code}: {body}")
        except Exception as e:
            raise RuntimeError(f"OpenClaw API 请求失败: {e}")
    
    def _cli_run(self, args: List[str]) -> str:
        """运行 OpenClaw CLI 命令"""
        cmd = [self.cli_path] + args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"OpenClaw CLI 错误: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError(f"OpenClaw CLI 未找到: {self.cli_path}")
    
    # ---- 统一接口实现 ----
    
    def send(self, to: str, subject: str, body: str, html: bool = False) -> bool:
        if self._use_api:
            payload = {
                'from': self.address,
                'to': to,
                'subject': subject,
                'body': body,
                'html': html,
            }
            resp = self._api_post('/email/send', payload)
            return resp.get('success', False)
        else:
            # CLI 模式
            format_flag = '--html' if html else '--text'
            cmd = [
                'email', 'send',
                '--to', to,
                '--subject', subject,
                '--body', body,
                format_flag,
            ]
            self._cli_run(cmd)
            return True
    
    def list(self, folder: str = 'INBOX', count: int = 10) -> List[EmailMessage]:
        if self._use_api:
            resp = self._api_get(f'/email/list?folder={folder}&count={count}')
            emails = resp.get('emails', [])
            return [
                EmailMessage(
                    id=str(e.get('id', '')),
                    subject=e.get('subject', ''),
                    from_=e.get('from', ''),
                    to=e.get('to', self.address),
                    date=e.get('date', ''),
                    body=e.get('body', ''),
                    folder=folder,
                )
                for e in emails
            ]
        else:
            out = self._cli_run(['email', 'list', '--folder', folder, '--count', str(count)])
            # CLI 输出解析（实际格式取决于 claw 实现）
            return self._parse_cli_list(out, folder)
    
    def read(self, email_id: str) -> Optional[EmailMessage]:
        if self._use_api:
            resp = self._api_get(f'/email/{email_id}')
            e = resp.get('email', {})
            return EmailMessage(
                id=str(e.get('id', email_id)),
                subject=e.get('subject', ''),
                from_=e.get('from', ''),
                to=e.get('to', self.address),
                date=e.get('date', ''),
                body=e.get('body', ''),
            )
        else:
            out = self._cli_run(['email', 'read', email_id])
            return self._parse_cli_read(out, email_id)
    
    def latest(self) -> Optional[EmailMessage]:
        if self._use_api:
            resp = self._api_get('/email/latest')
            e = resp.get('email', {})
            return EmailMessage(
                id=str(e.get('id', '')),
                subject=e.get('subject', ''),
                from_=e.get('from', ''),
                to=e.get('to', self.address),
                date=e.get('date', ''),
                body=e.get('body', ''),
            )
        else:
            out = self._cli_run(['email', 'latest'])
            # 假设 latest 返回 JSON
            try:
                data = json.loads(out)
                e = data.get('email', data)
                return EmailMessage(
                    id=str(e.get('id', '')),
                    subject=e.get('subject', ''),
                    from_=e.get('from', ''),
                    to=e.get('to', self.address),
                    date=e.get('date', ''),
                    body=e.get('body', ''),
                )
            except json.JSONDecodeError:
                return None
    
    def search(
        self,
        keyword: Optional[str] = None,
        from_: Optional[str] = None,
        subject: Optional[str] = None,
        folder: str = 'INBOX',
        count: int = 10,
    ) -> List[EmailMessage]:
        if self._use_api:
            params = [f'folder={folder}', f'count={count}']
            if keyword:
                params.append(f'q={urllib.parse.quote(keyword)}')
            if from_:
                params.append(f'from={urllib.parse.quote(from_)}')
            if subject:
                params.append(f'subject={urllib.parse.quote(subject)}')
            resp = self._api_get('/email/search?' + '&'.join(params))
            emails = resp.get('emails', [])
            return [
                EmailMessage(
                    id=str(e.get('id', '')),
                    subject=e.get('subject', ''),
                    from_=e.get('from', ''),
                    to=e.get('to', self.address),
                    date=e.get('date', ''),
                    body=e.get('body', ''),
                    folder=folder,
                )
                for e in emails
            ]
        else:
            args = ['email', 'search', '--folder', folder, '--count', str(count)]
            if keyword:
                args += ['--keyword', keyword]
            if from_:
                args += ['--from', from_]
            if subject:
                args += ['--subject', subject]
            out = self._cli_run(args)
            return self._parse_cli_list(out, folder)
    
    def reply(self, email_id: str, body: str, html: bool = False) -> bool:
        if self._use_api:
            payload = {
                'to': '',
                'subject': '',
                'body': body,
                'html': html,
                'in_reply_to': email_id,
            }
            # 先读取原邮件
            original = self.read(email_id)
            if not original:
                return False
            payload['to'] = original.from_
            payload['subject'] = f"Re: {original.subject}" if not original.subject.startswith('Re:') else original.subject
            resp = self._api_post('/email/send', payload)
            return resp.get('success', False)
        else:
            cmd = [
                'email', 'reply', email_id,
                '--body', body,
            ]
            if html:
                cmd.append('--html')
            self._cli_run(cmd)
            return True
    
    # ---- CLI 输出解析（占位，可根据实际 claw 输出调整） ----
    
    def _parse_cli_list(self, raw: str, folder: str) -> List[EmailMessage]:
        """解析 claw email list 输出"""
        messages = []
        lines = raw.strip().splitlines()
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # 假设格式：ID | FROM | SUBJECT | DATE
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 4:
                messages.append(EmailMessage(
                    id=parts[0],
                    from_=parts[1],
                    subject=parts[2],
                    to=self.address,
                    date=parts[3],
                    body='',
                    folder=folder,
                ))
        return messages
    
    def _parse_cli_read(self, raw: str, email_id: str) -> Optional[EmailMessage]:
        """解析 claw email read 输出"""
        try:
            data = json.loads(raw)
            e = data.get('email', data)
            return EmailMessage(
                id=str(e.get('id', email_id)),
                subject=e.get('subject', ''),
                from_=e.get('from', ''),
                to=e.get('to', self.address),
                date=e.get('date', ''),
                body=e.get('body', ''),
            )
        except json.JSONDecodeError:
            return None
