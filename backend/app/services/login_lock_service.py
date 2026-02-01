"""
Login Lock Service
登录锁定服务 - 实现登录失败次数限制和账号锁定
"""
import time
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# 内存存储登录失败记录（生产环境建议使用 Redis）
# 格式: {email: {"count": int, "first_fail_time": float, "locked_until": float}}
_login_fail_records: Dict[str, Dict] = {}


def check_login_lock(email: str) -> Tuple[bool, Optional[str]]:
    """
    检查账号是否被锁定

    Args:
        email: 用户邮箱

    Returns:
        (is_locked, message) - 是否锁定及锁定消息
    """
    from app.core.system_settings import get_user_settings
    user_settings = get_user_settings()

    record = _login_fail_records.get(email)
    if not record:
        return False, None

    current_time = time.time()

    # 检查是否在锁定期内
    locked_until = record.get("locked_until", 0)
    if locked_until > current_time:
        remaining_minutes = int((locked_until - current_time) / 60) + 1
        return True, f"账号已被锁定，请在 {remaining_minutes} 分钟后重试"

    # 锁定期已过，清除记录
    if locked_until > 0 and locked_until <= current_time:
        del _login_fail_records[email]
        return False, None

    return False, None


def record_login_failure(email: str) -> Tuple[bool, Optional[str]]:
    """
    记录登录失败

    Args:
        email: 用户邮箱

    Returns:
        (is_now_locked, message) - 是否因此次失败被锁定及消息
    """
    from app.core.system_settings import get_user_settings
    user_settings = get_user_settings()

    threshold = user_settings.login_fail_lock_threshold
    lock_minutes = user_settings.login_fail_lock_minutes

    current_time = time.time()

    record = _login_fail_records.get(email, {
        "count": 0,
        "first_fail_time": current_time,
        "locked_until": 0
    })

    # 如果距离第一次失败超过锁定时间，重置计数
    if current_time - record.get("first_fail_time", 0) > lock_minutes * 60:
        record = {
            "count": 0,
            "first_fail_time": current_time,
            "locked_until": 0
        }

    # 增加失败计数
    record["count"] = record.get("count", 0) + 1

    # 检查是否达到锁定阈值
    if record["count"] >= threshold:
        record["locked_until"] = current_time + lock_minutes * 60
        _login_fail_records[email] = record
        logger.warning(f"Account locked due to too many failed attempts: {email}")
        return True, f"登录失败次数过多，账号已被锁定 {lock_minutes} 分钟"

    _login_fail_records[email] = record
    remaining = threshold - record["count"]
    return False, f"密码错误，还剩 {remaining} 次尝试机会"


def clear_login_failures(email: str):
    """
    清除登录失败记录（登录成功后调用）

    Args:
        email: 用户邮箱
    """
    if email in _login_fail_records:
        del _login_fail_records[email]


def get_login_status(email: str) -> Dict:
    """
    获取登录状态信息

    Args:
        email: 用户邮箱

    Returns:
        状态信息字典
    """
    from app.core.system_settings import get_user_settings
    user_settings = get_user_settings()

    record = _login_fail_records.get(email, {})
    current_time = time.time()

    locked_until = record.get("locked_until", 0)
    is_locked = locked_until > current_time

    return {
        "email": email,
        "fail_count": record.get("count", 0),
        "threshold": user_settings.login_fail_lock_threshold,
        "is_locked": is_locked,
        "locked_until": datetime.fromtimestamp(locked_until).isoformat() if is_locked else None,
        "remaining_lock_seconds": int(locked_until - current_time) if is_locked else 0
    }
