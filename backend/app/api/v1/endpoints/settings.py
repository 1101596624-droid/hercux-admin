"""
User Learning Settings API endpoints
用户学习设置 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from app.db.session import get_db
from app.models.models import UserLearningSettings, User
from app.core.security import ClientType, get_current_user, get_request_client_type

router = APIRouter()


class SettingsUpdate(BaseModel):
    font_size: Optional[str] = None  # small, medium, large
    auto_play_next: Optional[bool] = None
    show_learning_time: Optional[bool] = None


class SettingsResponse(BaseModel):
    font_size: str
    auto_play_next: bool
    show_learning_time: bool

    class Config:
        from_attributes = True


@router.get("", response_model=SettingsResponse)
async def get_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户学习设置"""
    result = await db.execute(
        select(UserLearningSettings).where(
            UserLearningSettings.user_id == current_user.id
        )
    )
    settings = result.scalar_one_or_none()

    if not settings:
        # 创建默认设置
        settings = UserLearningSettings(
            user_id=current_user.id,
            font_size="medium",
            auto_play_next=1,
            show_learning_time=1
        )
        db.add(settings)
        await db.commit()
        await db.refresh(settings)

    return SettingsResponse(
        font_size=settings.font_size,
        auto_play_next=bool(settings.auto_play_next),
        show_learning_time=bool(settings.show_learning_time)
    )


@router.put("", response_model=SettingsResponse)
async def update_settings(
    settings_data: SettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新用户学习设置"""
    result = await db.execute(
        select(UserLearningSettings).where(
            UserLearningSettings.user_id == current_user.id
        )
    )
    settings = result.scalar_one_or_none()

    if not settings:
        # 创建新设置
        settings = UserLearningSettings(user_id=current_user.id)
        db.add(settings)

    # 验证并更新字段
    if settings_data.font_size is not None:
        if settings_data.font_size not in ["small", "medium", "large"]:
            raise HTTPException(status_code=400, detail="无效的字体大小")
        settings.font_size = settings_data.font_size

    if settings_data.auto_play_next is not None:
        settings.auto_play_next = 1 if settings_data.auto_play_next else 0

    if settings_data.show_learning_time is not None:
        settings.show_learning_time = 1 if settings_data.show_learning_time else 0

    await db.commit()
    await db.refresh(settings)

    return SettingsResponse(
        font_size=settings.font_size,
        auto_play_next=bool(settings.auto_play_next),
        show_learning_time=bool(settings.show_learning_time)
    )


@router.get("/client-capabilities")
async def get_client_capabilities(
    client_type: ClientType = Depends(get_request_client_type)
):
    """
    返回客户端能力矩阵，供桌面端 / APP 做功能开关。
    """
    resolved_client_type: ClientType = client_type if client_type != "unknown" else "desktop"

    capability_map = {
        "desktop": {
            "agent_api_enabled": True,
            "universe_enabled": False,
        },
        "app": {
            "agent_api_enabled": False,
            "universe_enabled": True,
        },
        "admin": {
            "agent_api_enabled": True,
            "universe_enabled": False,
        },
    }

    return {
        "client_type": resolved_client_type,
        "course_standard": {
            "version": "v3",
            "lesson_field": "steps",
            "simulator_html_field": "html_content",
        },
        "capabilities": capability_map[resolved_client_type],  # type: ignore[index]
    }
