from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    upload,
    package_import,
    studio,
    users,
    courses,
    nodes,
    progress,
    analytics,
    icons,
    simulator,
    notes,
    settings,
    ai,
    tts,
    # 学生端功能
    training,
    grinder,
    achievements,
)
from app.api.v1.endpoints import ai_tutor_refactored as ai_tutor
from app.api.v1.endpoints.admin import (
    courses as admin_courses,
    users as admin_users,
    progress as admin_progress,
    analytics as admin_analytics,
    ai_monitor as admin_ai_monitor,
    achievement_center as admin_achievement_center,
    api_config as admin_api_config,
    settings as admin_settings,
    admins as admin_admins
)

api_router = APIRouter()

# Authentication (for admin login)
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# User endpoints
api_router.include_router(users.router, prefix="/user", tags=["User"])

# Course endpoints (user-facing)
api_router.include_router(courses.router, prefix="/courses", tags=["Courses"])

# Node endpoints (user-facing)
api_router.include_router(nodes.router, prefix="/nodes", tags=["Nodes"])

# Progress endpoints (user-facing)
api_router.include_router(progress.router, prefix="/progress", tags=["Progress"])

# File upload (for Studio)
api_router.include_router(upload.router, prefix="/upload", tags=["File Upload"])

# Studio endpoints
api_router.include_router(studio.router, prefix="/studio", tags=["Studio"])

# Package import (for importing generated courses)
api_router.include_router(package_import.router, prefix="/internal", tags=["Package Import (Internal)"])

# Public analytics (token usage reporting)
api_router.include_router(analytics.router, tags=["Analytics"])

# 学生端功能路由
api_router.include_router(training.router, prefix="/planner", tags=["Training Plans"])
api_router.include_router(grinder.router, prefix="/grinder", tags=["Grinder"])
api_router.include_router(achievements.router, prefix="/achievements", tags=["Achievements"])
api_router.include_router(ai_tutor.router, prefix="/ai-tutor", tags=["AI Tutor"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI"])

# 图标库 API
api_router.include_router(icons.router, prefix="/icon-library", tags=["Icon Library"])

# 模拟器 API
api_router.include_router(simulator.router, prefix="/simulator", tags=["Simulator"])

# 笔记 API
api_router.include_router(notes.router, prefix="/notes", tags=["Notes"])

# 学习设置 API
api_router.include_router(settings.router, prefix="/settings", tags=["Settings"])

# Admin management endpoints
api_router.include_router(admin_courses.router, prefix="/admin", tags=["Admin - Course Management"])
api_router.include_router(admin_users.router, prefix="/admin", tags=["Admin - User Management"])
api_router.include_router(admin_progress.router, prefix="/admin", tags=["Admin - Progress Management"])
api_router.include_router(admin_analytics.router, prefix="/admin", tags=["Admin - Analytics"])
api_router.include_router(admin_ai_monitor.router, prefix="/admin", tags=["Admin - AI Monitor"])
api_router.include_router(admin_achievement_center.router, prefix="/admin", tags=["Admin - Achievement Center"])
api_router.include_router(admin_api_config.router, prefix="/admin", tags=["Admin - API Config"])
api_router.include_router(admin_settings.router, prefix="/admin", tags=["Admin - Settings"])
api_router.include_router(admin_admins.router, prefix="/admin", tags=["Admin - Admin Management"])

# TTS 语音合成
api_router.include_router(tts.router, prefix="/tts", tags=["TTS"])
