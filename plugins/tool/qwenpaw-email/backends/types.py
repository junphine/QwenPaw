"""
公共类型定义
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class EmailMessage:
    """标准化邮件结构"""
    id: str
    subject: str
    from_: str
    to: str
    date: str
    body: str
    folder: str = 'INBOX'


class EmailBackend(ABC):
    """所有邮件后端的基类"""
    
    @abstractmethod
    def send(self, to: str, subject: str, body: str, html: bool = False) -> bool:
        """发送邮件"""
        raise NotImplementedError
    
    @abstractmethod
    def list(self, folder: str = 'INBOX', count: int = 10) -> List[EmailMessage]:
        """列出文件夹中的邮件"""
        raise NotImplementedError
    
    @abstractmethod
    def read(self, email_id: str) -> Optional[EmailMessage]:
        """读取指定邮件"""
        raise NotImplementedError
    
    @abstractmethod
    def latest(self) -> Optional[EmailMessage]:
        """读取最新邮件"""
        raise NotImplementedError
    
    @abstractmethod
    def search(
        self,
        keyword: Optional[str] = None,
        from_: Optional[str] = None,
        subject: Optional[str] = None,
        folder: str = 'INBOX',
        count: int = 10,
    ) -> List[EmailMessage]:
        """搜索邮件"""
        raise NotImplementedError
    
    @abstractmethod
    def reply(self, email_id: str, body: str, html: bool = False) -> bool:
        """回复邮件"""
        raise NotImplementedError
