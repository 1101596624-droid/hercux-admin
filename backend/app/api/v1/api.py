from fastapi import APIRouter, Depends
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
from app.api.v1.endpoints import agent
from app.api.v1.endpoints import admin_knowledge_tracking, knowledge, learning_path, review, report, diagnostic_tutor, recommendation, assessment, multi_task, subject_graph, cross_disciplinary, course_rec, smart_feedback, adaptive_agent
from app.api.v1.endpoints import predictive, goals, habits
from app.api.v1.endpoints import transfer, temporal
from app.core.security import require_non_app_client

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

# HERCU Agent 监控
api_router.include_router(
    agent.router,
    prefix="/agent",
    tags=["Agent"],
    dependencies=[Depends(require_non_app_client)],
)

# BKT 知识追踪
api_router.include_router(admin_knowledge_tracking.router, prefix="/admin/knowledge", tags=["Admin - Knowledge Tracking"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["Knowledge Tracking"])

# 自适应学习路径
api_router.include_router(learning_path.router, prefix="/knowledge", tags=["Learning Path"])

# 间隔复习
api_router.include_router(review.router, prefix="/review", tags=["Spaced Repetition"])

# 学习报告 + 元认知
api_router.include_router(report.router, prefix="/learning", tags=["Learning Report & Metacognitive"])

# 诊断式AI Tutor
api_router.include_router(diagnostic_tutor.router, prefix="/diagnostic-tutor", tags=["Diagnostic AI Tutor"])

# 推荐系统
api_router.include_router(recommendation.router, prefix="/recommendation", tags=["Recommendation"])

# 智能评估与自适应反馈
api_router.include_router(assessment.router, prefix="/assessment", tags=["Assessment"])

# 多任务学习与多目标优化
api_router.include_router(multi_task.router, prefix="/multi-task", tags=["Multi-Task Optimization"])

# 学科知识图谱
api_router.include_router(subject_graph.router, prefix="/subject-graph", tags=["Subject Knowledge Graph"])

# 跨学科推荐与知识推理
api_router.include_router(cross_disciplinary.router, prefix="/cross-disciplinary", tags=["Cross-Disciplinary"])

# 课程推荐与学习路径
api_router.include_router(course_rec.router, prefix="/course-rec", tags=["Course Recommendation"])

# 学习反馈与智能报告
api_router.include_router(smart_feedback.router, prefix="/smart-feedback", tags=["Smart Feedback & Report"])

# Agent 强化学习与自适应任务生成
api_router.include_router(
    adaptive_agent.router,
    prefix="/adaptive-agent",
    tags=["Adaptive Agent"],
    dependencies=[Depends(require_non_app_client)],
)

# Phase 15: 预测分析
api_router.include_router(predictive.router, prefix="/predictive", tags=["Predictive Analytics"])

# Phase 15: 目标管理
api_router.include_router(goals.router, prefix="/goals", tags=["Goal Management"])

# Phase 15: 学习习惯追踪
api_router.include_router(habits.router, prefix="/habits", tags=["Habit Tracking"])

# Phase 16: 动态迁移系数
api_router.include_router(transfer.router, prefix="/transfer", tags=["Dynamic Transfer"])

# Phase 16: 时间模式分析
api_router.include_router(temporal.router, prefix="/temporal", tags=["Temporal Patterns"])
