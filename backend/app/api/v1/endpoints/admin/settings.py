"""
System Settings Management Endpoints
系统设置管理 - 平台配置、课程默认设置、用户设置、存储设置等
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.models.models import User, Course, CourseNode, LearningProgress
from app.core.config import settings

router = APIRouter()


# ============ 数据模型 ============

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
    default_tags: List[str] = ["通用"]
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
    allowed_image_types: List[str] = ["jpg", "jpeg", "png", "gif", "webp"]
    allowed_video_types: List[str] = ["mp4", "webm", "mov"]
    allowed_document_types: List[str] = ["pdf", "doc", "docx", "ppt", "pptx"]
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


class SystemInfo(BaseModel):
    """系统信息"""
    version: str
    environment: str
    server_time: datetime
    uptime_seconds: Optional[int] = None
    python_version: str
    database_type: str
    database_size_mb: Optional[float] = None


class SystemStats(BaseModel):
    """系统统计"""
    total_users: int
    total_admins: int
    total_courses: int
    published_courses: int
    total_nodes: int
    total_progress_records: int
    storage_used_mb: float


class CacheInfo(BaseModel):
    """缓存信息"""
    redis_connected: bool
    redis_url: str
    keys_count: Optional[int] = None
    memory_used_mb: Optional[float] = None


# ============ 设置文件路径 ============

def get_settings_file_path() -> Path:
    """获取设置文件路径"""
    # 优先使用服务器路径
    server_path = Path("/www/wwwroot/hercu-backend/settings.json")
    if server_path.parent.exists():
        return server_path
    # 本地开发环境
    local_path = Path(__file__).parent.parent.parent.parent.parent.parent / "settings.json"
    return local_path


def load_settings() -> AllSettings:
    """加载设置"""
    settings_file = get_settings_file_path()
    if settings_file.exists():
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return AllSettings(**data)
        except Exception as e:
            print(f"Failed to load settings: {e}")
    return AllSettings()


def save_settings(settings_data: AllSettings) -> bool:
    """保存设置"""
    settings_file = get_settings_file_path()
    try:
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings_data.model_dump(), f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Failed to save settings: {e}")
        return False


# ============ API 端点 ============

@router.get("/settings", response_model=AllSettings)
async def get_settings():
    """
    获取所有系统设置
    """
    return load_settings()


@router.put("/settings")
async def update_settings(new_settings: AllSettings):
    """
    更新所有系统设置
    """
    if save_settings(new_settings):
        return {"success": True, "message": "设置已保存"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="保存设置失败"
        )


@router.put("/settings/platform")
async def update_platform_settings(platform: PlatformSettings):
    """更新平台设置"""
    current = load_settings()
    current.platform = platform
    if save_settings(current):
        return {"success": True, "message": "平台设置已保存"}
    raise HTTPException(status_code=500, detail="保存失败")


@router.put("/settings/course")
async def update_course_settings(course: CourseDefaultSettings):
    """更新课程默认设置"""
    current = load_settings()
    current.course = course
    if save_settings(current):
        return {"success": True, "message": "课程设置已保存"}
    raise HTTPException(status_code=500, detail="保存失败")


@router.put("/settings/user")
async def update_user_settings(user: UserSettings):
    """更新用户设置"""
    current = load_settings()
    current.user = user
    if save_settings(current):
        return {"success": True, "message": "用户设置已保存"}
    raise HTTPException(status_code=500, detail="保存失败")


@router.put("/settings/storage")
async def update_storage_settings(storage: StorageSettings):
    """更新存储设置"""
    current = load_settings()
    current.storage = storage
    if save_settings(current):
        return {"success": True, "message": "存储设置已保存"}
    raise HTTPException(status_code=500, detail="保存失败")


@router.put("/settings/log")
async def update_log_settings(log: LogSettings):
    """更新日志设置"""
    current = load_settings()
    current.log = log
    if save_settings(current):
        return {"success": True, "message": "日志设置已保存"}
    raise HTTPException(status_code=500, detail="保存失败")


@router.get("/system-info", response_model=SystemInfo)
async def get_system_info():
    """
    获取系统信息
    """
    import sys
    import platform

    # 获取数据库类型
    db_url = settings.DATABASE_URL
    if "sqlite" in db_url:
        db_type = "SQLite"
    elif "postgresql" in db_url:
        db_type = "PostgreSQL"
    elif "mysql" in db_url:
        db_type = "MySQL"
    else:
        db_type = "Unknown"

    # 获取数据库大小（仅 SQLite）
    db_size = None
    if "sqlite" in db_url:
        try:
            # 提取文件路径
            if ":///" in db_url:
                db_path = db_url.split(":///")[-1]
            elif "://" in db_url:
                db_path = db_url.split("://")[-1]
            else:
                db_path = db_url

            if os.path.exists(db_path):
                db_size = os.path.getsize(db_path) / (1024 * 1024)
        except Exception as e:
            logger.debug(f"DB size calculation failed: {e}")

    return SystemInfo(
        version=settings.VERSION,
        environment=settings.ENV,
        server_time=datetime.now(),
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        database_type=db_type,
        database_size_mb=round(db_size, 2) if db_size else None
    )


@router.get("/system-stats", response_model=SystemStats)
async def get_system_stats(db: AsyncSession = Depends(get_db)):
    """
    获取系统统计数据
    """
    # 用户数
    total_users = await db.scalar(select(func.count(User.id))) or 0

    # 管理员数 (通过 is_admin 字段)
    total_admins = await db.scalar(select(func.count(User.id)).where(User.is_admin == 1)) or 0

    # 课程数
    total_courses = await db.scalar(select(func.count(Course.id))) or 0
    published_courses = await db.scalar(
        select(func.count(Course.id)).where(Course.is_published == 1)
    ) or 0

    # 节点数
    total_nodes = await db.scalar(select(func.count(CourseNode.id))) or 0

    # 学习进度记录数
    total_progress = await db.scalar(select(func.count(LearningProgress.id))) or 0

    # 存储使用量
    storage_used = 0.0
    current_settings = load_settings()
    storage_path = Path(current_settings.storage.storage_path)
    if storage_path.exists():
        try:
            for f in storage_path.rglob("*"):
                if f.is_file():
                    storage_used += f.stat().st_size
            storage_used = storage_used / (1024 * 1024)  # 转换为 MB
        except Exception as e:
            logger.debug(f"Storage calculation failed: {e}")

    return SystemStats(
        total_users=total_users,
        total_admins=total_admins,
        total_courses=total_courses,
        published_courses=published_courses,
        total_nodes=total_nodes,
        total_progress_records=total_progress,
        storage_used_mb=round(storage_used, 2)
    )


@router.get("/cache-info", response_model=CacheInfo)
async def get_cache_info():
    """
    获取缓存信息
    """
    redis_connected = False
    keys_count = None
    memory_used = None

    try:
        import aioredis
        redis = await aioredis.from_url(settings.REDIS_URL)
        await redis.ping()
        redis_connected = True

        # 获取键数量
        keys_count = await redis.dbsize()

        # 获取内存使用
        info = await redis.info("memory")
        if "used_memory" in info:
            memory_used = info["used_memory"] / (1024 * 1024)

        await redis.close()
    except Exception as e:
        print(f"Redis connection failed: {e}")

    return CacheInfo(
        redis_connected=redis_connected,
        redis_url=settings.REDIS_URL,
        keys_count=keys_count,
        memory_used_mb=round(memory_used, 2) if memory_used else None
    )


@router.post("/cache/clear")
async def clear_cache():
    """
    清除所有缓存
    """
    try:
        import aioredis
        redis = await aioredis.from_url(settings.REDIS_URL)
        await redis.flushdb()
        await redis.close()
        return {"success": True, "message": "缓存已清除"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"清除缓存失败: {str(e)}"
        )


@router.post("/settings/reset")
async def reset_settings():
    """
    重置所有设置为默认值
    """
    default_settings = AllSettings()
    if save_settings(default_settings):
        return {"success": True, "message": "设置已重置为默认值"}
    raise HTTPException(status_code=500, detail="重置失败")


# ============ 公开端点（无需认证） ============

@router.get("/public/platform-info")
async def get_public_platform_info():
    """
    获取公开的平台信息（无需认证）

    用于前端显示平台名称、公告等
    """
    current_settings = load_settings()
    platform = current_settings.platform

    return {
        "platform_name": platform.platform_name,
        "platform_description": platform.platform_description,
        "logo_url": platform.logo_url,
        "announcement": platform.announcement if platform.announcement_enabled else None,
        "announcement_enabled": platform.announcement_enabled,
        "maintenance_mode": platform.maintenance_mode,
        "maintenance_message": platform.maintenance_message if platform.maintenance_mode else None
    }
