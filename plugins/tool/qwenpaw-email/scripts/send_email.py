#!/usr/bin/env python3
"""
Agent 邮件发送脚本
自动从 credentials.yaml 读取配置
用法: python send_email.py --to <收件人> --subject <主题> --body <正文> [--html]
"""
import argparse
import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

def load_credentials():
    """从 credentials.yaml 读取邮件配置"""
    workspace = os.environ.get('WORKSPACE_DIR', '')
    cred_path = os.path.join(workspace, 'credentials.yaml') if workspace else 'credentials.yaml'
    
    # Try workspace path first, then current dir
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
        'smtp_host': public.get('smtp_host'),
        'smtp_port': int(public.get('smtp_port', 465)),
        'imap_host': public.get('imap_host'),
        'imap_port': int(public.get('imap_port', 993)),
    }

def send_email(to, subject, body, html=False):
    """发送邮件"""
    try:
        creds = load_credentials()
    except Exception as e:
        print(f'❌ 配置加载失败: {e}')
        return False
    
    msg = MIMEMultipart()
    msg['From'] = f"Aristotle Agent <{creds['address']}>"
    msg['To'] = to
    msg['Subject'] = Header(subject, 'utf-8')

    if html:
        msg.attach(MIMEText(body, 'html', 'utf-8'))
    else:
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP_SSL(creds['smtp_host'], creds['smtp_port'], timeout=10)
        server.login(creds['address'], creds['password'])
        server.sendmail(creds['address'], [to], msg.as_string())
        server.quit()
        print(f"✅ 邮件发送成功")
        print(f"   收件人: {to}")
        print(f"   主题: {subject}")
        return True
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent 邮件发送脚本")
    parser.add_argument("--to", required=True, help="收件人邮箱")
    parser.add_argument("--subject", required=True, help="邮件主题")
    parser.add_argument("--body", required=True, help="邮件正文")
    parser.add_argument("--html", action="store_true", help="使用 HTML 格式")
    args = parser.parse_args()

    success = send_email(args.to, args.subject, args.body, args.html)
    sys.exit(0 if success else 1)
