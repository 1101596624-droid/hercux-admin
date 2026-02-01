"""
System Settings Loader
系统设置加载器 - 提供全局访问系统设置的功能
"""
import json
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from functools import lru_cache
import time


class PlatformSettings(BaseModel):
    """平台基础设置"""
    platform_name: str = "HERCU"
    platform_description: str = "深度认知学习平台"
    logo_url: Optional[str] = None
    announcement: Optional[str] = None
    announcement_enabled: bool = False
    maintenance_mode: bool = False
    maintenance_message: str = "系统维护中，请稍后再试"


class CourseDefaultSettings(BaseModel):
    """课程默认设置"""
    default_difficulty: str = "intermediate"
    default_tags: list = ["通用"]
    ai_generation_steps: int = 8
    ai_content_min_length: int = 100
    auto_publish: bool = False
    require_review: bool = True


class UserSettings(BaseModel):
    """用户设置"""
    allow_registration: bool = True
    default_user_role: str = "user"
    login_fail_lock_threshold: int = 5
    login_fail_lock_minutes: int = 30
    session_timeout_minutes: int = 1440
    require_email_verification: bool = False


class StorageSettings(BaseModel):
    """存储设置"""
    max_upload_size_mb: int = 100
    allowed_image_types: list = ["jpg", "jpeg", "png", "gif", "webp"]
    allowed_video_types: list = ["mp4", "webm", "mov"]
    allowed_document_types: list = ["pdf", "doc", "docx", "ppt", "pptx"]
    storage_path: str = "/www/wwwroot/hercu-backend/media"
    auto_cleanup_days: int = 30


class LogSettings(BaseModel):
    """日志设置"""
    log_level: str = "INFO"
    log_retention_days: int = 30
    enable_access_log: bool = True
    enable_error_log: bool = True


class AllSettings(BaseModel):
    """所有设置"""
    platform: PlatformSettings = PlatformSettings()
    course: CourseDefaultSettings = CourseDefaultSettings()
    user: UserSettings = UserSettings()
    storage: StorageSettings = StorageSettings()
    log: LogSettings = LogSettings()


# 缓存设置，每60秒刷新一次
_settings_cache: Optional[AllSettings] = None
_cache_time: float = 0
CACHE_TTL = 60  # 秒


def get_settings_file_path() -> Path:
    """获取设置文件路径"""
    server_path = Path("/www/wwwroot/hercu-backend/settings.json")
    if server_path.parent.exists():
        return server_path
    local_path = Path(__file__).parent.parent.parent / "settings.json"
    return local_path


def load_system_settings(force_reload: bool = False) -> AllSettings:
    """
    加载系统设置

    Args:
        force_reload: 是否强制重新加载（忽略缓存）

    Returns:
        AllSettings 对象
    """
    global _settings_cache, _cache_time

    current_time = time.time()

    # 检查缓存是否有效
    if not force_reload and _settings_cache is not None and (current_time - _cache_time) < CACHE_TTL:
        return _settings_cache

    settings_file = get_settings_file_path()

    if settings_file.exists():
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                _settings_cache = AllSettings(**data)
                _cache_time = current_time
                return _settings_cache
        except Exception as e:
            print(f"Failed to load settings: {e}")

    # 返回默认设置
    _settings_cache = AllSettings()
    _cache_time = current_time
    return _settings_cache


def get_platform_settings() -> PlatformSettings:
    """获取平台设置"""
    return load_system_settings().platform


def get_course_settings() -> CourseDefaultSettings:
    """获取课程默认设置"""
    return load_system_settings().course


def get_user_settings() -> UserSettings:
    """获取用户设置"""
    return load_system_settings().user


def get_storage_settings() -> StorageSettings:
    """获取存储设置"""
    return load_system_settings().storage


def get_log_settings() -> LogSettings:
    """获取日志设置"""
    return load_system_settings().log


def clear_settings_cache():
    """清除设置缓存"""
    global _settings_cache, _cache_time
    _settings_cache = None
    _cache_time = 0
