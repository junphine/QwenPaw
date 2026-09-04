#!/usr/bin/env python3
"""
Agent 邮件读取脚本
自动从 credentials.yaml 读取配置
用法:
  python read_email.py list [--count N] [--folder FOLDER]
  python read_email.py read <email_id>
  python read_email.py search <keyword> [--from SENDER] [--subject SUBJECT]
  python read_email.py latest
"""
import argparse
import imaplib
import email
from email.header import decode_header
import sys
import os

def load_credentials():
    """从 credentials.yaml 读取邮件配置"""
    workspace = os.environ.get('WORKSPACE_DIR', '')
    cred_path = os.path.join(workspace, 'credentials.yaml') if workspace else 'credentials.yaml'
    
    if not os.path.exists(cred_path):
        cred_path = 'credentials.yaml'
    
    if not os.path.exists(cred_path):
        raise FileNotFoundError('credentials.yaml not found')
    
    import yaml
    with open(cred_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Support both flat (email/agent) and nested (credentials.email/agent) structures
    email_config = config.get('email/agent') or config.get('credentials', {}).get('email/agent')
    if not email_config:
        raise ValueError('email/agent section not found in credentials.yaml')
    
    public = email_config.get('public', {})
    secrets = email_config.get('secrets', {})
    
    return {
        'address': public.get('address'),
        'password': secrets.get('password'),
        'imap_host': public.get('imap_host'),
        'imap_port': int(public.get('imap_port', 993)),
    }


def decode_mime_header(header_value):
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


def get_email_body(msg):
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


def connect():
    """连接 IMAP 服务器"""
    try:
        creds = load_credentials()
    except Exception as e:
        print(f'❌ 配置加载失败: {e}')
        sys.exit(1)
    
    mail = imaplib.IMAP4_SSL(creds['imap_host'], creds['imap_port'])
    mail.login(creds['address'], creds['password'])
    return mail


def cmd_list(args):
    """列出收件箱邮件"""
    mail = connect()
    mail.select(args.folder or 'INBOX')

    status, messages = mail.search(None, 'ALL')
    if status != 'OK':
        print('无法获取邮件列表')
        mail.logout()
        return

    email_ids = messages[0].split()
    total = len(email_ids)
    count = min(args.count, total) if args.count else min(total, 10)

    print(f'📬 收件箱共 {total} 封邮件，显示最近 {count} 封：\n')

    for eid in email_ids[-count:]:
        status, msg_data = mail.fetch(eid, '(RFC822)')
        if status != 'OK':
            continue
        msg = email.message_from_bytes(msg_data[0][1])

        subject = decode_mime_header(msg.get('Subject', ''))
        from_ = decode_mime_header(msg.get('From', ''))
        date_ = msg.get('Date', 'Unknown')

        # Truncate long subjects
        if len(subject) > 50:
            subject = subject[:47] + '...'

        print(f'[{eid.decode()}] {date_}')
        print(f'  发件人: {from_}')
        print(f'  主题: {subject}')
        print()

    mail.logout()


def cmd_read(email_id):
    """读取单封邮件详情"""
    mail = connect()
    mail.select('INBOX')

    eid = email_id.encode()
    status, msg_data = mail.fetch(eid, '(RFC822)')
    if status != 'OK':
        print('邮件不存在')
        mail.logout()
        return

    msg = email.message_from_bytes(msg_data[0][1])
    subject = decode_mime_header(msg.get('Subject', ''))
    from_ = decode_mime_header(msg.get('From', ''))
    to_ = decode_mime_header(msg.get('To', ''))
    date_ = msg.get('Date', 'Unknown')
    body = get_email_body(msg)

    print(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
    print(f'邮件 ID: {email_id}')
    print(f'发件人: {from_}')
    print(f'收件人: {to_}')
    print(f'主题: {subject}')
    print(f'日期: {date_}')
    print(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
    print(f'\n正文：\n{body}')
    print(f'\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')

    mail.logout()


def cmd_latest(args):
    """读取最新一封邮件"""
    mail = connect()
    mail.select('INBOX')

    status, messages = mail.search(None, 'ALL')
    if status != 'OK' or not messages[0]:
        print('收件箱为空')
        mail.logout()
        return

    latest_id = messages[0].split()[-1]
    mail.logout()
    cmd_read(latest_id.decode())


def cmd_search(args):
    """搜索邮件"""
    mail = connect()
    mail.select(args.folder or 'INBOX')

    # Build search criteria
    criteria = []
    if args.from_:
        criteria.append(f'(FROM "{args.from_}")')
    if args.subject:
        criteria.append(f'(SUBJECT "{args.subject}")')
    if args.keyword:
        criteria.append(f'(OR SUBJECT "{args.keyword}" BODY "{args.keyword}")')

    if not criteria:
        print('请提供搜索条件：--from, --subject, 或 --keyword')
        mail.logout()
        return

    search_str = ' '.join(criteria)
    status, messages = mail.search(None, search_str)
    if status != 'OK':
        print('搜索失败')
        mail.logout()
        return

    email_ids = messages[0].split()
    print(f'找到 {len(email_ids)} 封匹配邮件：\n')

    for eid in email_ids[-args.count if args.count else 10:]:
        status, msg_data = mail.fetch(eid, '(RFC822)')
        if status != 'OK':
            continue
        msg = email.message_from_bytes(msg_data[0][1])
        subject = decode_mime_header(msg.get('Subject', ''))
        from_ = decode_mime_header(msg.get('From', ''))
        date_ = msg.get('Date', 'Unknown')

        if len(subject) > 50:
            subject = subject[:47] + '...'

        print(f'[{eid.decode()}] {date_}')
        print(f'  发件人: {from_}')
        print(f'  主题: {subject}')
        print()

    mail.logout()


def main():
    parser = argparse.ArgumentParser(description='Agent 邮件读取工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # list
    p_list = subparsers.add_parser('list', help='列出收件箱邮件')
    p_list.add_argument('--count', type=int, default=10, help='显示数量（默认10）')
    p_list.add_argument('--folder', default='INBOX', help='文件夹（默认INBOX）')

    # read
    p_read = subparsers.add_parser('read', help='读取指定邮件')
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

    args = parser.parse_args()

    if args.command == 'list':
        cmd_list(args)
    elif args.command == 'read':
        cmd_read(args.email_id)
    elif args.command == 'latest':
        cmd_latest(args)
    elif args.command == 'search':
        cmd_search(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
