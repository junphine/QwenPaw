#!/usr/bin/env python3
"""
QwenPaw Email Plugin 统一入口

支持多后端：
  - imap_smtp（默认）：QQ / Gmail / 163 等标准邮箱
  - openclaw：OpenClaw 托管邮件服务
  - hermes：Hermes 邮件服务（预留）

用法:
  python email.py send --to <收件人> --subject <主题> --body <正文> [--html]
  python email.py list [--count N] [--folder FOLDER]
  python email.py read <id>
  python email.py latest
  python email.py search <keyword> [--from SENDER] [--subject SUBJECT] [--count N]
  python email.py reply <id> --body <正文> [--html]

环境变量:
  WORKSPACE_DIR - 指定 workspace 根目录（默认自动查找）
"""

from __future__ import annotations

import argparse
import os
import sys

# 确保 backends 包可导入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backends import EmailBackend, EmailMessage, ImapSmtpBackend, OpenClawBackend, HermesBackend, build_backend


def load_credentials() -> dict:
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
    
    # 支持多种结构
    email_config = (
        config.get('email/agent')
        or config.get('credentials', {}).get('email/agent')
    )
    if not email_config:
        raise ValueError('email/agent section not found in credentials.yaml')
    
    return email_config


def print_email(msg: EmailMessage, verbose: bool = False):
    """格式化输出单封邮件"""
    print(f'[{msg.id}] {msg.date}')
    print(f'  发件人: {msg.from_}')
    print(f'  收件人: {msg.to}')
    print(f'  主题: {msg.subject}')
    if verbose:
        print(f'  文件夹: {msg.folder}')
        print(f'\n正文：\n{msg.body}')
    print()


def main():
    parser = argparse.ArgumentParser(description='QwenPaw Email Plugin')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # send
    p_send = subparsers.add_parser('send', help='发送邮件')
    p_send.add_argument('--to', required=True, help='收件人邮箱')
    p_send.add_argument('--subject', required=True, help='邮件主题')
    p_send.add_argument('--body', required=True, help='邮件正文')
    p_send.add_argument('--html', action='store_true', help='使用 HTML 格式')
    
    # list
    p_list = subparsers.add_parser('list', help='列出邮件')
    p_list.add_argument('--count', type=int, default=10, help='显示数量')
    p_list.add_argument('--folder', default='INBOX', help='文件夹')
    
    # read
    p_read = subparsers.add_parser('read', help='读取邮件')
    p_read.add_argument('email_id', help='邮件 ID')
    
    # latest
    subparsers.add_parser('latest', help='读取最新邮件')
    
    # search
    p_search = subparsers.add_parser('search', help='搜索邮件')
    p_search.add_argument('keyword', nargs='?', help='搜索关键词')
    p_search.add_argument('--from', dest='from_', help='发件人')
    p_search.add_argument('--subject', help='主题关键词')
    p_search.add_argument('--count', type=int, default=10, help='显示数量')
    p_search.add_argument('--folder', default='INBOX', help='文件夹')
    
    # reply
    p_reply = subparsers.add_parser('reply', help='回复邮件')
    p_reply.add_argument('email_id', help='原邮件 ID')
    p_reply.add_argument('--body', required=True, help='回复正文')
    p_reply.add_argument('--html', action='store_true', help='使用 HTML 格式')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        config = load_credentials()
    except Exception as e:
        print(f'❌ 配置加载失败: {e}')
        sys.exit(1)
    
    try:
        backend = build_backend(config)
    except Exception as e:
        print(f'❌ 后端初始化失败: {e}')
        sys.exit(1)
    
    try:
        if args.command == 'send':
            ok = backend.send(args.to, args.subject, args.body, html=args.html)
            if ok:
                print(f"✅ 邮件发送成功")
                print(f"   收件人: {args.to}")
                print(f"   主题: {args.subject}")
            else:
                print("❌ 邮件发送失败")
            sys.exit(0 if ok else 1)
        
        elif args.command == 'list':
            emails = backend.list(folder=args.folder, count=args.count)
            print(f'📬 {args.folder} 共 {len(emails)} 封邮件：\n')
            for msg in emails:
                print_email(msg)
        
        elif args.command == 'read':
            msg = backend.read(args.email_id)
            if msg:
                print_email(msg, verbose=True)
            else:
                print(f'❌ 邮件 {args.email_id} 不存在')
                sys.exit(1)
        
        elif args.command == 'latest':
            msg = backend.latest()
            if msg:
                print_email(msg, verbose=True)
            else:
                print('📭 收件箱为空')
                sys.exit(1)
        
        elif args.command == 'search':
            emails = backend.search(
                keyword=args.keyword,
                from_=args.from_,
                subject=args.subject,
                folder=args.folder,
                count=args.count,
            )
            print(f'🔍 找到 {len(emails)} 封匹配邮件：\n')
            for msg in emails:
                print_email(msg)
        
        elif args.command == 'reply':
            ok = backend.reply(args.email_id, args.body, html=args.html)
            if ok:
                print(f"✅ 回复成功")
            else:
                print("❌ 回复失败")
            sys.exit(0 if ok else 1)
    
    except NotImplementedError as e:
        print(f'⚠️ 功能尚未实现: {e}')
        sys.exit(1)
    except Exception as e:
        print(f'❌ 操作失败: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
