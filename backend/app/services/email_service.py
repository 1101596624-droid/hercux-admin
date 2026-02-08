"""
Email Service for sending verification codes
Uses QQ SMTP server and Redis for code storage
"""
import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
from datetime import datetime, timedelta
from typing import Optional, Tuple
import json
import redis

# Redis connection for verification codes
_redis_client: Optional[redis.Redis] = None

def get_redis_client() -> redis.Redis:
    """Get or create Redis client"""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True)
    return _redis_client

# QQ SMTP Configuration
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465  # SSL port
SMTP_USER = "1101596624@qq.com"
SMTP_PASSWORD = "tumuhuzzdqfwjhae"  # Authorization code
SENDER_NAME = "HERCU 学习平台"

# Code settings
CODE_LENGTH = 6
CODE_EXPIRE_MINUTES = 10
REDIS_KEY_PREFIX = "hercu:verification_code:"


def generate_verification_code() -> str:
    """Generate a random 6-digit verification code"""
    return ''.join(random.choices(string.digits, k=CODE_LENGTH))


def store_verification_code(email: str, code: str, purpose: str = "register") -> None:
    """Store verification code in Redis with expiration"""
    redis_client = get_redis_client()
    key = f"{REDIS_KEY_PREFIX}{email.lower()}"
    data = json.dumps({
        "code": code,
        "purpose": purpose,
        "created_at": datetime.now().isoformat()
    })
    redis_client.setex(key, CODE_EXPIRE_MINUTES * 60, data)


def verify_code(email: str, code: str, purpose: str = "register") -> Tuple[bool, str]:
    """
    Verify the code for an email
    Returns: (is_valid, error_message)
    """
    redis_client = get_redis_client()
    key = f"{REDIS_KEY_PREFIX}{email.lower()}"

    data = redis_client.get(key)
    if not data:
        return False, "验证码不存在或已过期，请重新获取"

    try:
        stored = json.loads(data)
    except json.JSONDecodeError:
        redis_client.delete(key)
        return False, "验证码数据损坏，请重新获取"

    # Check purpose
    if stored.get("purpose") != purpose:
        return False, "验证码用途不匹配"

    # Check code
    if stored.get("code") != code:
        return False, "验证码错误"

    # Valid - remove the code after successful verification
    redis_client.delete(key)
    return True, ""


def can_send_code(email: str) -> Tuple[bool, int]:
    """
    Check if we can send a new code (rate limiting)
    Returns: (can_send, seconds_to_wait)
    """
    redis_client = get_redis_client()
    key = f"{REDIS_KEY_PREFIX}{email.lower()}"

    data = redis_client.get(key)
    if not data:
        return True, 0

    try:
        stored = json.loads(data)
        created_at = datetime.fromisoformat(stored.get("created_at", ""))
        # Allow resend after 60 seconds
        wait_until = created_at + timedelta(seconds=60)

        if datetime.now() < wait_until:
            seconds_left = int((wait_until - datetime.now()).total_seconds())
            return False, max(0, seconds_left)
    except (json.JSONDecodeError, ValueError):
        pass

    return True, 0


def send_verification_email(email: str, code: str, purpose: str = "register") -> Tuple[bool, str]:
    """
    Send verification code email via QQ SMTP
    Returns: (success, error_message)
    """
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = Header(f"【HERCU】您的验证码是 {code}", 'utf-8')
        msg['From'] = formataddr((str(Header(SENDER_NAME, 'utf-8')), SMTP_USER))
        msg['To'] = email

        # Purpose text
        purpose_text = {
            "register": "注册账户",
            "reset_password": "重置密码",
            "change_email": "更换邮箱"
        }.get(purpose, "验证")

        # Plain text version
        text_content = f"""
您好！

您正在{purpose_text}，验证码为：{code}

验证码有效期为 {CODE_EXPIRE_MINUTES} 分钟，请尽快完成验证。

如果这不是您本人的操作，请忽略此邮件。

---
HERCU 学习平台
"""

        # HTML version
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
        .code {{ font-size: 32px; font-weight: bold; color: #667eea; letter-spacing: 8px; text-align: center; padding: 20px; background: white; border-radius: 8px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #6c757d; font-size: 12px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0;">HERCU</h1>
            <p style="margin: 10px 0 0 0; opacity: 0.9;">运动科学学习平台</p>
        </div>
        <div class="content">
            <p>您好！</p>
            <p>您正在<strong>{purpose_text}</strong>，请使用以下验证码：</p>
            <div class="code">{code}</div>
            <p style="color: #6c757d; font-size: 14px;">
                验证码有效期为 <strong>{CODE_EXPIRE_MINUTES} 分钟</strong>，请尽快完成验证。
            </p>
            <p style="color: #6c757d; font-size: 14px;">
                如果这不是您本人的操作，请忽略此邮件。
            </p>
        </div>
        <div class="footer">
            <p>此邮件由系统自动发送，请勿回复</p>
            <p>&copy; 2026 HERCU 学习平台</p>
        </div>
    </div>
</body>
</html>
"""

        # Attach both versions
        part1 = MIMEText(text_content, 'plain', 'utf-8')
        part2 = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(part1)
        msg.attach(part2)

        # Send email via SSL
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, email, msg.as_string())

        return True, ""

    except smtplib.SMTPAuthenticationError:
        return False, "邮件服务器认证失败"
    except smtplib.SMTPRecipientsRefused:
        return False, "收件人邮箱地址无效"
    except smtplib.SMTPException as e:
        return False, f"邮件发送失败: {str(e)}"
    except Exception as e:
        return False, f"发送邮件时发生错误: {str(e)}"


async def send_code_to_email(email: str, purpose: str = "register") -> Tuple[bool, str]:
    """
    Main function to send verification code
    Returns: (success, message)
    """
    # Check rate limiting
    can_send, wait_seconds = can_send_code(email)
    if not can_send:
        return False, f"请等待 {wait_seconds} 秒后再试"

    # Generate code
    code = generate_verification_code()

    # Send email
    success, error = send_verification_email(email, code, purpose)

    if success:
        # Store code only if email was sent successfully
        store_verification_code(email, code, purpose)
        return True, "验证码已发送"
    else:
        return False, error
