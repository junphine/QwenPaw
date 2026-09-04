"""
IMAP + SMTP 邮件后端

支持所有标准 IMAP/SMTP 邮箱服务商：
  - 163.com / claw.163.com
  - QQ邮箱
  - Gmail
  - Outlook
  - 其他标准 IMAP/SMTP 服务

配置示例（credentials.yaml）：

```yaml
email/agent:
  kind: static
  provider: imap_smtp          # 可选，默认自动检测
  public:
    address: "user@example.com"
    smtp_host: "smtp.example.com"
    smtp_port: "465"
    imap_host: "imap.example.com"
    imap_port: "993"
  secrets:
    password: "your-password"
```

注意：
- QQ/Gmail/Outlook 需要使用**应用专用密码**，而非登录密码。
- 部分服务商（如 Gmail）需要先在设置中开启 IMAP/SMTP 访问。
"""

from __future__ import annotations

import imaplib
import smtplib
import email
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from typing import List, Optional

from .types import EmailBackend, EmailMessage


def _decode_mime_header(header_value: str) -> str:
    """解码 MIME 编码的邮件头"""
    if not header_value:
        return ''
    decoded_parts = decode_header(header_value)
    result = []
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            result.append(part.decode(charset or 'utf-8', errors='replace'))
        else:
            result.append(part)
    return ' '.join(result)


def _get_email_body(msg) -> str:
    """提取邮件正文（优先纯文本）"""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == 'text/plain':
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode('utf-8', errors='replace')
        return '(no plain text body)'
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            return payload.decode('utf-8', errors='replace')
        return '(empty body)'


class ImapSmtpBackend(EmailBackend):
    """基于 IMAP + SMTP 的邮件后端"""
    
    def __init__(self, config: dict):
        """
        config 结构：
        {
            'address': str,
            'password': str,
            'smtp_host': str,
            'smtp_port': int,
            'imap_host': str,
            'imap_port': int,
        }
        """
        self.address = config['address']
        self.password = config['password']
        self.smtp_host = config.get('smtp_host', 'smtp.example.com')
        self.smtp_port = int(config.get('smtp_port', 465))
        self.imap_host = config.get('imap_host', 'imap.example.com')
        self.imap_port = int(config.get('imap_port', 993))
    
    def _connect_imap(self) -> imaplib.IMAP4_SSL:
        """连接 IMAP 服务器"""
        mail = imaplib.IMAP4_SSL(self.imap_host, self.imap_port)
        mail.login(self.address, self.password)
        return mail
    
    def send(self, to: str, subject: str, body: str, html: bool = False) -> bool:
        """通过 SMTP 发送邮件"""
        msg = MIMEMultipart()
        msg['From'] = f"{self.address}"
        msg['To'] = to
        msg['Subject'] = Header(subject, 'utf-8')
        
        if html:
            msg.attach(MIMEText(body, 'html', 'utf-8'))
        else:
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        try:
            server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=10)
            server.login(self.address, self.password)
            server.sendmail(self.address, [to], msg.as_string())
            server.quit()
            return True
        except Exception as e:
            print(f"SMTP 发送失败: {e}")
            return False
    
    def list(self, folder: str = 'INBOX', count: int = 10) -> List[EmailMessage]:
        """列出收件箱邮件"""
        mail = self._connect_imap()
        mail.select(folder)
        
        status, messages = mail.search(None, 'ALL')
        if status != 'OK':
            mail.logout()
            return []
        
        email_ids = messages[0].split()
        total = len(email_ids)
        count = min(count, total)
        
        result = []
        for eid in email_ids[-count:]:
            status, msg_data = mail.fetch(eid, '(RFC822)')
            if status != 'OK':
                continue
            msg = email.message_from_bytes(msg_data[0][1])
            
            subject = _decode_mime_header(msg.get('Subject', ''))
            from_ = _decode_mime_header(msg.get('From', ''))
            date_ = msg.get('Date', 'Unknown')
            body = _get_email_body(msg)
            
            result.append(EmailMessage(
                id=eid.decode(),
                subject=subject,
                from_=from_,
                to=self.address,
                date=date_,
                body=body,
                folder=folder,
            ))
        
        mail.logout()
        return result
    
    def read(self, email_id: str) -> Optional[EmailMessage]:
        """读取指定邮件"""
        mail = self._connect_imap()
        mail.select('INBOX')
        
        eid = email_id.encode()
        status, msg_data = mail.fetch(eid, '(RFC822)')
        if status != 'OK':
            mail.logout()
            return None
        
        msg = email.message_from_bytes(msg_data[0][1])
        subject = _decode_mime_header(msg.get('Subject', ''))
        from_ = _decode_mime_header(msg.get('From', ''))
        to_ = _decode_mime_header(msg.get('To', ''))
        date_ = msg.get('Date', 'Unknown')
        body = _get_email_body(msg)
        
        mail.logout()
        return EmailMessage(
            id=email_id,
            subject=subject,
            from_=from_,
            to=to_,
            date=date_,
            body=body,
        )
    
    def latest(self) -> Optional[EmailMessage]:
        """读取最新一封邮件"""
        mail = self._connect_imap()
        mail.select('INBOX')
        
        status, messages = mail.search(None, 'ALL')
        if status != 'OK' or not messages[0]:
            mail.logout()
            return None
        
        latest_id = messages[0].split()[-1].decode()
        mail.logout()
        return self.read(latest_id)
    
    def search(
        self,
        keyword: Optional[str] = None,
        from_: Optional[str] = None,
        subject: Optional[str] = None,
        folder: str = 'INBOX',
        count: int = 10,
    ) -> List[EmailMessage]:
        """搜索邮件"""
        mail = self._connect_imap()
        mail.select(folder)
        
        criteria = []
        if from_:
            criteria.append(f'(FROM "{from_}")')
        if subject:
            criteria.append(f'(SUBJECT "{subject}")')
        if keyword:
            criteria.append(f'(OR SUBJECT "{keyword}" BODY "{keyword}")')
        
        if not criteria:
            mail.logout()
            return []
        
        search_str = ' '.join(criteria)
        status, messages = mail.search(None, search_str)
        if status != 'OK':
            mail.logout()
            return []
        
        email_ids = messages[0].split()
        result = []
        for eid in email_ids[-count:]:
            status, msg_data = mail.fetch(eid, '(RFC822)')
            if status != 'OK':
                continue
            msg = email.message_from_bytes(msg_data[0][1])
            
            subject_decoded = _decode_mime_header(msg.get('Subject', ''))
            from_decoded = _decode_mime_header(msg.get('From', ''))
            date_ = msg.get('Date', 'Unknown')
            body = _get_email_body(msg)
            
            result.append(EmailMessage(
                id=eid.decode(),
                subject=subject_decoded,
                from_=from_decoded,
                to=self.address,
                date=date_,
                body=body,
                folder=folder,
            ))
        
        mail.logout()
        return result
    
    def reply(self, email_id: str, body: str, html: bool = False) -> bool:
        """回复邮件（需要先读取原邮件获取 To 和 Subject）"""
        original = self.read(email_id)
        if not original:
            return False
        
        reply_subject = f"Re: {original.subject}" if not original.subject.startswith('Re:') else original.subject
        return self.send(original.from_, reply_subject, body, html=html)
