"""
Admin Achievement Center API
勋章中心管理接口
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, cast, Date
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel

from app.db.session import get_db
from app.models.models import (
    User, BadgeConfig, SkillTreeConfig, SkillAchievementConfig,
    TagDictionary, PendingDomain, UserBadge, UserSkillProgress, UserSkillAchievement,
    LearningProgress, CourseNode, NodeStatus, NodeType
)
from app.core.security import get_current_admin_user

router = APIRouter()


# ============ Pydantic Schemas ============

class BadgeCondition(BaseModel):
    type: str  # counter, streak, first_time, time_based, threshold
    metric: Optional[str] = None
    target: Optional[int] = None
    event: Optional[str] = None
    timeRange: Optional[List[int]] = None


class BadgeCreate(BaseModel):
    id: str
    name: str
    name_en: Optional[str] = None
    icon: str
    description: str
    category: str
    rarity: str = "common"
    points: int = 10
    condition: dict
    is_active: bool = True


class BadgeUpdate(BaseModel):
    name: Optional[str] = None
    name_en: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    rarity: Optional[str] = None
    points: Optional[int] = None
    condition: Optional[dict] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class SkillTreeCreate(BaseModel):
    id: str
    name: str
    name_en: Optional[str] = None
    icon: str
    color: str
    description: Optional[str] = None
    match_rules: dict
    level_thresholds: List[int] = [0, 50, 150, 300, 500]
    prerequisites: List[dict] = []
    unlocks: List[str] = []
    is_advanced: bool = False
    is_active: bool = True


class SkillTreeUpdate(BaseModel):
    name: Optional[str] = None
    name_en: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    match_rules: Optional[dict] = None
    level_thresholds: Optional[List[int]] = None
    prerequisites: Optional[List[dict]] = None
    unlocks: Optional[List[str]] = None
    is_advanced: Optional[bool] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class AchievementCreate(BaseModel):
    id: str
    name: str
    name_en: Optional[str] = None
    icon: str
    description: str
    points: int = 50
    condition: dict
    is_active: bool = True


class AchievementUpdate(BaseModel):
    name: Optional[str] = None
    name_en: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    points: Optional[int] = None
    condition: Optional[dict] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


# ============ Stats ============

@router.get("/achievement-center/stats")
async def get_achievement_center_stats(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """获取勋章中心总览统计"""
    # 勋章统计
    badge_total = await db.execute(select(func.count()).select_from(BadgeConfig))
    badge_active = await db.execute(
        select(func.count()).select_from(BadgeConfig).where(BadgeConfig.is_active == 1)
    )
    badge_unlocked = await db.execute(select(func.count()).select_from(UserBadge))

    # 技能树统计
    tree_total = await db.execute(select(func.count()).select_from(SkillTreeConfig))
    tree_active = await db.execute(
        select(func.count()).select_from(SkillTreeConfig).where(SkillTreeConfig.is_active == 1)
    )
    tree_users = await db.execute(
        select(func.count(func.distinct(UserSkillProgress.user_id))).select_from(UserSkillProgress)
    )

    # 成就统计
    ach_total = await db.execute(select(func.count()).select_from(SkillAchievementConfig))
    ach_active = await db.execute(
        select(func.count()).select_from(SkillAchievementConfig).where(SkillAchievementConfig.is_active == 1)
    )
    ach_unlocked = await db.execute(select(func.count()).select_from(UserSkillAchievement))

    # 待审核领域
    pending = await db.execute(
        select(func.count()).select_from(PendingDomain).where(PendingDomain.status == "pending")
    )

    return {
        "badges": {
            "total": badge_total.scalar() or 0,
            "active": badge_active.scalar() or 0,
            "totalUnlocked": badge_unlocked.scalar() or 0,
            "avgUnlockRate": 0
        },
        "skillTrees": {
            "total": tree_total.scalar() or 0,
            "active": tree_active.scalar() or 0,
            "totalUsers": tree_users.scalar() or 0,
            "avgLevel": 0,
            "avgCompletionRate": 0
        },
        "achievements": {
            "total": ach_total.scalar() or 0,
            "active": ach_active.scalar() or 0,
            "totalUnlocked": ach_unlocked.scalar() or 0,
            "avgUnlockRate": 0
        },
        "pendingDomains": pending.scalar() or 0
    }


# ============ Badges ============

@router.get("/achievement-center/badges")
async def get_badges(
    category: Optional[str] = Query(None),
    rarity: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """获取勋章列表"""
    query = select(BadgeConfig)
    filters = []

    if category:
        filters.append(BadgeConfig.category == category)
    if rarity:
        filters.append(BadgeConfig.rarity == rarity)
    if is_active is not None:
        filters.append(BadgeConfig.is_active == (1 if is_active else 0))

    if filters:
        query = query.where(and_(*filters))

    # 总数
    count_query = select(func.count()).select_from(BadgeConfig)
    if filters:
        count_query = count_query.where(and_(*filters))
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # 分页
    offset = (page - 1) * page_size
    query = query.order_by(BadgeConfig.sort_order, BadgeConfig.created_at.desc()).offset(offset).limit(page_size)

    result = await db.execute(query)
    badges = result.scalars().all()

    # 获取解锁统计
    data = []
    for badge in badges:
        unlocked_result = await db.execute(
            select(func.count()).select_from(UserBadge).where(UserBadge.badge_id == badge.id)
        )
        unlocked_count = unlocked_result.scalar() or 0

        data.append({
            "id": badge.id,
            "name": badge.name,
            "nameEn": badge.name_en,
            "icon": badge.icon,
            "description": badge.description,
            "category": badge.category.value if hasattr(badge.category, 'value') else badge.category,
            "rarity": badge.rarity.value if hasattr(badge.rarity, 'value') else badge.rarity,
            "points": badge.points,
            "condition": badge.condition,
            "isActive": badge.is_active == 1,
            "sortOrder": badge.sort_order,
            "stats": {
                "unlockedCount": unlocked_count,
                "unlockedRate": 0
            },
            "createdAt": badge.created_at.isoformat() if badge.created_at else None
        })

    return {
        "data": data,
        "pagination": {
            "total": total,
            "page": page,
            "pageSize": page_size
        }
    }


@router.post("/achievement-center/badges")
async def create_badge(
    badge: BadgeCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """创建勋章"""
    # 检查 ID 是否已存在
    existing = await db.execute(select(BadgeConfig).where(BadgeConfig.id == badge.id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="勋章 ID 已存在")

    db_badge = BadgeConfig(
        id=badge.id,
        name=badge.name,
        name_en=badge.name_en,
        icon=badge.icon,
        description=badge.description,
        category=badge.category,
        rarity=badge.rarity,
        points=badge.points,
        condition=badge.condition,
        is_active=1 if badge.is_active else 0,
        created_by=str(current_user.id)
    )
    db.add(db_badge)
    await db.commit()
    await db.refresh(db_badge)

    return {"message": "勋章创建成功", "id": db_badge.id}


@router.put("/achievement-center/badges/{badge_id}")
async def update_badge(
    badge_id: str,
    badge: BadgeUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """更新勋章"""
    result = await db.execute(select(BadgeConfig).where(BadgeConfig.id == badge_id))
    db_badge = result.scalar_one_or_none()
    if not db_badge:
        raise HTTPException(status_code=404, detail="勋章不存在")

    update_data = badge.model_dump(exclude_unset=True)
    if "is_active" in update_data:
        update_data["is_active"] = 1 if update_data["is_active"] else 0

    for key, value in update_data.items():
        setattr(db_badge, key, value)

    await db.commit()
    return {"message": "勋章更新成功"}


@router.patch("/achievement-center/badges/{badge_id}/status")
async def toggle_badge_status(
    badge_id: str,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """切换勋章状态"""
    result = await db.execute(select(BadgeConfig).where(BadgeConfig.id == badge_id))
    db_badge = result.scalar_one_or_none()
    if not db_badge:
        raise HTTPException(status_code=404, detail="勋章不存在")

    db_badge.is_active = 0 if db_badge.is_active == 1 else 1
    await db.commit()

    return {"message": "状态已更新", "isActive": db_badge.is_active == 1}


@router.delete("/achievement-center/badges/{badge_id}")
async def delete_badge(
    badge_id: str,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """删除勋章"""
    # 检查是否有用户已解锁
    unlocked = await db.execute(
        select(func.count()).select_from(UserBadge).where(UserBadge.badge_id == badge_id)
    )
    if unlocked.scalar() > 0:
        raise HTTPException(status_code=400, detail="已有用户解锁此勋章，无法删除，请改为禁用")

    result = await db.execute(select(BadgeConfig).where(BadgeConfig.id == badge_id))
    db_badge = result.scalar_one_or_none()
    if not db_badge:
        raise HTTPException(status_code=404, detail="勋章不存在")

    await db.delete(db_badge)
    await db.commit()

    return {"message": "勋章已删除"}


# ============ Skill Trees ============

@router.get("/achievement-center/skill-trees")
async def get_skill_trees(
    is_advanced: Optional[bool] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """获取技能树列表"""
    query = select(SkillTreeConfig)
    filters = []

    if is_advanced is not None:
        filters.append(SkillTreeConfig.is_advanced == (1 if is_advanced else 0))
    if is_active is not None:
        filters.append(SkillTreeConfig.is_active == (1 if is_active else 0))

    if filters:
        query = query.where(and_(*filters))

    query = query.order_by(SkillTreeConfig.sort_order, SkillTreeConfig.created_at)
    result = await db.execute(query)
    trees = result.scalars().all()

    data = []
    for tree in trees:
        # 获取用户数
        user_count_result = await db.execute(
            select(func.count(func.distinct(UserSkillProgress.user_id)))
            .select_from(UserSkillProgress)
            .where(UserSkillProgress.skill_tree_id == tree.id)
        )
        user_count = user_count_result.scalar() or 0

        # 获取平均等级
        avg_level_result = await db.execute(
            select(func.avg(UserSkillProgress.current_level))
            .select_from(UserSkillProgress)
            .where(UserSkillProgress.skill_tree_id == tree.id)
        )
        avg_level = avg_level_result.scalar() or 0

        data.append({
            "id": tree.id,
            "name": tree.name,
            "nameEn": tree.name_en,
            "icon": tree.icon,
            "color": tree.color,
            "description": tree.description,
            "matchRules": tree.match_rules,
            "levelThresholds": tree.level_thresholds,
            "prerequisites": tree.prerequisites,
            "unlocks": tree.unlocks,
            "isAdvanced": tree.is_advanced == 1,
            "isActive": tree.is_active == 1,
            "sortOrder": tree.sort_order,
            "stats": {
                "userCount": user_count,
                "avgLevel": round(avg_level, 1),
                "completionRate": 0
            }
        })

    return {"data": data}


@router.post("/achievement-center/skill-trees")
async def create_skill_tree(
    tree: SkillTreeCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """创建技能树"""
    existing = await db.execute(select(SkillTreeConfig).where(SkillTreeConfig.id == tree.id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="技能树 ID 已存在")

    db_tree = SkillTreeConfig(
        id=tree.id,
        name=tree.name,
        name_en=tree.name_en,
        icon=tree.icon,
        color=tree.color,
        description=tree.description,
        match_rules=tree.match_rules,
        level_thresholds=tree.level_thresholds,
        prerequisites=tree.prerequisites,
        unlocks=tree.unlocks,
        is_advanced=1 if tree.is_advanced else 0,
        is_active=1 if tree.is_active else 0
    )
    db.add(db_tree)
    await db.commit()

    return {"message": "技能树创建成功", "id": db_tree.id}


@router.put("/achievement-center/skill-trees/{tree_id}")
async def update_skill_tree(
    tree_id: str,
    tree: SkillTreeUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """更新技能树"""
    result = await db.execute(select(SkillTreeConfig).where(SkillTreeConfig.id == tree_id))
    db_tree = result.scalar_one_or_none()
    if not db_tree:
        raise HTTPException(status_code=404, detail="技能树不存在")

    update_data = tree.model_dump(exclude_unset=True)
    if "is_advanced" in update_data:
        update_data["is_advanced"] = 1 if update_data["is_advanced"] else 0
    if "is_active" in update_data:
        update_data["is_active"] = 1 if update_data["is_active"] else 0

    for key, value in update_data.items():
        setattr(db_tree, key, value)

    await db.commit()
    return {"message": "技能树更新成功"}


@router.patch("/achievement-center/skill-trees/{tree_id}/status")
async def toggle_skill_tree_status(
    tree_id: str,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """切换技能树状态"""
    result = await db.execute(select(SkillTreeConfig).where(SkillTreeConfig.id == tree_id))
    db_tree = result.scalar_one_or_none()
    if not db_tree:
        raise HTTPException(status_code=404, detail="技能树不存在")

    db_tree.is_active = 0 if db_tree.is_active == 1 else 1
    await db.commit()

    return {"message": "状态已更新", "isActive": db_tree.is_active == 1}


@router.post("/achievement-center/skill-trees/validate-prerequisites")
async def validate_prerequisites(
    data: dict,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """验证技能树依赖关系"""
    tree_id = data.get("treeId")
    prerequisites = data.get("prerequisites", [])

    errors = []
    warnings = []

    # 获取所有技能树
    result = await db.execute(select(SkillTreeConfig))
    all_trees = {t.id: t for t in result.scalars().all()}

    for prereq in prerequisites:
        prereq_id = prereq.get("treeId")
        required_level = prereq.get("requiredLevel", 1)

        # 检查前置树是否存在
        if prereq_id not in all_trees:
            errors.append(f"前置技能树 '{prereq_id}' 不存在")
            continue

        # 不能依赖自己
        if prereq_id == tree_id:
            errors.append("技能树不能依赖自己")

        # 等级范围检查
        if required_level < 1 or required_level > 5:
            errors.append("等级要求必须在 1-5 之间")

        # 依赖进阶树警告
        prereq_tree = all_trees[prereq_id]
        if prereq_tree.is_advanced == 1:
            warnings.append(f"依赖进阶树 '{prereq_tree.name}' 可能导致解锁困难")

    # TODO: 循环依赖检测

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "circularDependency": False
    }


# ============ Skill Achievements ============

@router.get("/achievement-center/skill-achievements")
async def get_skill_achievements(
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """获取技能成就列表"""
    query = select(SkillAchievementConfig)

    if is_active is not None:
        query = query.where(SkillAchievementConfig.is_active == (1 if is_active else 0))

    query = query.order_by(SkillAchievementConfig.sort_order, SkillAchievementConfig.created_at)
    result = await db.execute(query)
    achievements = result.scalars().all()

    data = []
    for ach in achievements:
        unlocked_result = await db.execute(
            select(func.count()).select_from(UserSkillAchievement)
            .where(UserSkillAchievement.achievement_id == ach.id)
        )
        unlocked_count = unlocked_result.scalar() or 0

        data.append({
            "id": ach.id,
            "name": ach.name,
            "nameEn": ach.name_en,
            "icon": ach.icon,
            "description": ach.description,
            "points": ach.points,
            "condition": ach.condition,
            "isActive": ach.is_active == 1,
            "sortOrder": ach.sort_order,
            "stats": {
                "unlockedCount": unlocked_count,
                "unlockedRate": 0
            }
        })

    return {"data": data}


@router.post("/achievement-center/skill-achievements")
async def create_skill_achievement(
    achievement: AchievementCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """创建技能成就"""
    existing = await db.execute(
        select(SkillAchievementConfig).where(SkillAchievementConfig.id == achievement.id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="成就 ID 已存在")

    db_ach = SkillAchievementConfig(
        id=achievement.id,
        name=achievement.name,
        name_en=achievement.name_en,
        icon=achievement.icon,
        description=achievement.description,
        points=achievement.points,
        condition=achievement.condition,
        is_active=1 if achievement.is_active else 0
    )
    db.add(db_ach)
    await db.commit()

    return {"message": "成就创建成功", "id": db_ach.id}


@router.put("/achievement-center/skill-achievements/{achievement_id}")
async def update_skill_achievement(
    achievement_id: str,
    achievement: AchievementUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """更新技能成就"""
    result = await db.execute(
        select(SkillAchievementConfig).where(SkillAchievementConfig.id == achievement_id)
    )
    db_ach = result.scalar_one_or_none()
    if not db_ach:
        raise HTTPException(status_code=404, detail="成就不存在")

    update_data = achievement.model_dump(exclude_unset=True)
    if "is_active" in update_data:
        update_data["is_active"] = 1 if update_data["is_active"] else 0

    for key, value in update_data.items():
        setattr(db_ach, key, value)

    await db.commit()
    return {"message": "成就更新成功"}


@router.patch("/achievement-center/skill-achievements/{achievement_id}/status")
async def toggle_achievement_status(
    achievement_id: str,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """切换成就状态"""
    result = await db.execute(
        select(SkillAchievementConfig).where(SkillAchievementConfig.id == achievement_id)
    )
    db_ach = result.scalar_one_or_none()
    if not db_ach:
        raise HTTPException(status_code=404, detail="成就不存在")

    db_ach.is_active = 0 if db_ach.is_active == 1 else 1
    await db.commit()

    return {"message": "状态已更新", "isActive": db_ach.is_active == 1}


# ============ Pending Domains ============

@router.get("/achievement-center/pending-domains")
async def get_pending_domains(
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """获取待审核领域列表"""
    query = select(PendingDomain)

    if status:
        query = query.where(PendingDomain.status == status)

    query = query.order_by(desc(PendingDomain.first_seen))
    result = await db.execute(query)
    domains = result.scalars().all()

    data = []
    for d in domains:
        data.append({
            "domain": d.domain,
            "nodeCount": d.node_count,
            "completedUsers": d.completed_users,
            "firstSeen": d.first_seen.isoformat() if d.first_seen else None,
            "status": d.status,
            "reviewedAt": d.reviewed_at.isoformat() if d.reviewed_at else None,
            "reviewedBy": d.reviewed_by,
            "rejectReason": d.reject_reason
        })

    return {"data": data}


@router.post("/achievement-center/pending-domains/{domain}/approve")
async def approve_domain(
    domain: str,
    data: Optional[dict] = None,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """批准领域"""
    result = await db.execute(select(PendingDomain).where(PendingDomain.domain == domain))
    pending = result.scalar_one_or_none()
    if not pending:
        raise HTTPException(status_code=404, detail="领域不存在")

    pending.status = "approved"
    pending.reviewed_at = datetime.now(timezone.utc)
    pending.reviewed_by = str(current_user.id)

    # 如果需要创建技能树
    if data and data.get("createTree"):
        tree_config = data.get("treeConfig", {})
        new_tree = SkillTreeConfig(
            id=domain,
            name=tree_config.get("name", domain),
            icon=tree_config.get("icon", "📚"),
            color=tree_config.get("color", "#3B82F6"),
            match_rules={"domains": [domain]},
            level_thresholds=[0, 50, 150, 300, 500],
            is_active=1
        )
        db.add(new_tree)

    await db.commit()
    return {"message": "领域已批准"}


@router.post("/achievement-center/pending-domains/{domain}/reject")
async def reject_domain(
    domain: str,
    data: dict,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """拒绝领域"""
    result = await db.execute(select(PendingDomain).where(PendingDomain.domain == domain))
    pending = result.scalar_one_or_none()
    if not pending:
        raise HTTPException(status_code=404, detail="领域不存在")

    pending.status = "rejected"
    pending.reviewed_at = datetime.now(timezone.utc)
    pending.reviewed_by = str(current_user.id)
    pending.reject_reason = data.get("reason", "")

    await db.commit()
    return {"message": "领域已拒绝"}


# ============ User Stats (从主应用同步的数据) ============

async def get_user_learning_stats(user_id: int, db: AsyncSession) -> dict:
    """获取用户学习统计数据"""

    # 完成的节点数
    completed_nodes = await db.scalar(
        select(func.count(LearningProgress.id)).where(
            and_(
                LearningProgress.user_id == user_id,
                LearningProgress.status == NodeStatus.COMPLETED
            )
        )
    ) or 0

    # 总学习时长
    total_seconds = await db.scalar(
        select(func.sum(LearningProgress.time_spent_seconds)).where(
            LearningProgress.user_id == user_id
        )
    ) or 0
    total_hours = round(total_seconds / 3600, 1)

    # 学习天数统计
    dates_query = select(
        func.distinct(cast(LearningProgress.last_accessed, Date))
    ).where(
        and_(
            LearningProgress.user_id == user_id,
            LearningProgress.last_accessed.isnot(None)
        )
    ).order_by(desc(cast(LearningProgress.last_accessed, Date)))

    result = await db.execute(dates_query)
    activity_dates = [row[0] for row in result.all()]

    total_learning_days = len(activity_dates)

    # 当前连续天数
    current_streak = 0
    if activity_dates:
        today = datetime.now(timezone.utc).date()
        if activity_dates[0] >= today - timedelta(days=1):
            current_streak = 1
            for i in range(1, len(activity_dates)):
                if activity_dates[i] == activity_dates[i-1] - timedelta(days=1):
                    current_streak += 1
                else:
                    break

    # 历史最长连续天数
    max_streak = 0
    if activity_dates:
        temp_streak = 1
        sorted_dates = sorted(activity_dates)
        for i in range(1, len(sorted_dates)):
            if sorted_dates[i] == sorted_dates[i-1] + timedelta(days=1):
                temp_streak += 1
            else:
                max_streak = max(max_streak, temp_streak)
                temp_streak = 1
        max_streak = max(max_streak, temp_streak)

    # 课程统计
    courses_query = select(
        func.distinct(CourseNode.course_id)
    ).select_from(
        LearningProgress
    ).join(
        CourseNode, LearningProgress.node_id == CourseNode.id
    ).where(
        LearningProgress.user_id == user_id
    )
    result = await db.execute(courses_query)
    course_ids = [row[0] for row in result.all()]

    enrolled_courses = len(course_ids)
    completed_courses = 0

    for course_id in course_ids:
        total_nodes = await db.scalar(
            select(func.count(CourseNode.id)).where(CourseNode.course_id == course_id)
        ) or 0

        completed = await db.scalar(
            select(func.count(LearningProgress.id)).where(
                and_(
                    LearningProgress.user_id == user_id,
                    LearningProgress.node_id.in_(
                        select(CourseNode.id).where(CourseNode.course_id == course_id)
                    ),
                    LearningProgress.status == NodeStatus.COMPLETED
                )
            )
        ) or 0

        if total_nodes > 0 and completed == total_nodes:
            completed_courses += 1

    # 测验和模拟器统计
    completed_quizzes = await db.scalar(
        select(func.count(LearningProgress.id)).where(
            and_(
                LearningProgress.user_id == user_id,
                LearningProgress.status == NodeStatus.COMPLETED,
                LearningProgress.node_id.in_(
                    select(CourseNode.id).where(CourseNode.type == NodeType.QUIZ)
                )
            )
        )
    ) or 0

    completed_simulators = await db.scalar(
        select(func.count(LearningProgress.id)).where(
            and_(
                LearningProgress.user_id == user_id,
                LearningProgress.status == NodeStatus.COMPLETED,
                LearningProgress.node_id.in_(
                    select(CourseNode.id).where(CourseNode.type == NodeType.SIMULATOR)
                )
            )
        )
    ) or 0

    # 已解锁勋章数
    unlocked_badges = await db.scalar(
        select(func.count()).select_from(UserBadge).where(UserBadge.user_id == user_id)
    ) or 0

    return {
        "completedNodes": completed_nodes,
        "totalHours": total_hours,
        "totalLearningDays": total_learning_days,
        "currentStreak": current_streak,
        "maxStreak": max_streak,
        "enrolledCourses": enrolled_courses,
        "completedCourses": completed_courses,
        "completedQuizzes": completed_quizzes,
        "completedSimulators": completed_simulators,
        "unlockedBadges": unlocked_badges,
    }


@router.get("/achievement-center/users")
async def get_users_with_stats(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户列表及其学习统计"""
    query = select(User).where(User.is_active == 1)

    if search:
        query = query.where(
            User.username.ilike(f"%{search}%") | User.email.ilike(f"%{search}%")
        )

    # 总数
    count_query = select(func.count()).select_from(User).where(User.is_active == 1)
    if search:
        count_query = count_query.where(
            User.username.ilike(f"%{search}%") | User.email.ilike(f"%{search}%")
        )
    total = await db.scalar(count_query) or 0

    # 分页
    offset = (page - 1) * page_size
    query = query.order_by(desc(User.created_at)).offset(offset).limit(page_size)

    result = await db.execute(query)
    users = result.scalars().all()

    data = []
    for user in users:
        stats = await get_user_learning_stats(user.id, db)
        data.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "fullName": user.full_name,
            "avatarUrl": user.avatar_url,
            "createdAt": user.created_at.isoformat() if user.created_at else None,
            "stats": stats
        })

    return {
        "data": data,
        "pagination": {
            "total": total,
            "page": page,
            "pageSize": page_size
        }
    }


@router.get("/achievement-center/users/{user_id}/stats")
async def get_user_stats(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """获取单个用户的详细学习统计"""
    # 检查用户是否存在
    user = await db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    stats = await get_user_learning_stats(user_id, db)

    # 获取用户已解锁的勋章详情
    badges_query = select(BadgeConfig).join(
        UserBadge, UserBadge.badge_id == BadgeConfig.id
    ).where(UserBadge.user_id == user_id)
    result = await db.execute(badges_query)
    unlocked_badges = [
        {
            "id": b.id,
            "name": b.name,
            "icon": b.icon,
            "rarity": b.rarity.value if hasattr(b.rarity, 'value') else b.rarity,
            "points": b.points
        }
        for b in result.scalars().all()
    ]

    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "fullName": user.full_name,
        },
        "stats": stats,
        "unlockedBadges": unlocked_badges
    }


@router.get("/achievement-center/metrics")
async def get_available_metrics(
    current_user: User = Depends(get_current_admin_user),
):
    """获取可用于勋章解锁条件的指标列表"""
    return {
        "metrics": [
            {
                "key": "completed_nodes",
                "name": "完成节点数",
                "description": "用户完成的学习节点总数",
                "type": "counter",
                "example": {"type": "counter", "metric": "completed_nodes", "target": 10}
            },
            {
                "key": "total_learning_days",
                "name": "累计学习天数",
                "description": "用户有学习记录的天数（不要求连续）",
                "type": "counter",
                "example": {"type": "counter", "metric": "total_learning_days", "target": 30}
            },
            {
                "key": "current_streak",
                "name": "当前连续天数",
                "description": "用户当前连续学习的天数",
                "type": "streak",
                "example": {"type": "streak", "target": 7}
            },
            {
                "key": "max_streak",
                "name": "历史最长连续天数",
                "description": "用户历史上最长的连续学习天数",
                "type": "max_streak",
                "example": {"type": "max_streak", "target": 30}
            },
            {
                "key": "total_hours",
                "name": "学习时长(小时)",
                "description": "用户累计学习时长",
                "type": "time_based",
                "example": {"type": "time_based", "target": 10}
            },
            {
                "key": "completed_courses",
                "name": "完成课程数",
                "description": "用户完成的课程数量",
                "type": "courses",
                "example": {"type": "courses", "target": 3}
            },
            {
                "key": "enrolled_courses",
                "name": "报名课程数",
                "description": "用户已报名的课程数量",
                "type": "counter",
                "example": {"type": "counter", "metric": "enrolled_courses", "target": 5}
            },
            {
                "key": "completed_quizzes",
                "name": "完成测验数",
                "description": "用户完成的测验数量",
                "type": "counter",
                "example": {"type": "counter", "metric": "completed_quizzes", "target": 10}
            },
            {
                "key": "completed_simulators",
                "name": "完成模拟器数",
                "description": "用户完成的模拟器数量",
                "type": "counter",
                "example": {"type": "counter", "metric": "completed_simulators", "target": 5}
            },
        ]
    }


# ============ AI Badge Generation ============

class GenerateBadgeRequest(BaseModel):
    """AI 生成勋章请求"""
    unlock_description: str  # 管理员描述的解锁方式
    badge_name: Optional[str] = None  # 可选的勋章名称
    badge_category: Optional[str] = None  # 可选的分类


@router.post("/achievement-center/generate-badge")
async def generate_badge_with_ai(
    request: GenerateBadgeRequest,
    current_user: User = Depends(get_current_admin_user),
):
    """使用 AI 根据描述生成勋章配置"""
    import anthropic
    from app.core.config import settings

    # 构建 prompt
    system_prompt = """你是一个勋章系统配置助手。根据管理员的描述，生成勋章的解锁条件 JSON。

可用的条件类型和指标：
1. counter 类型 - 计数器，达到目标数量解锁
   - metric: completed_nodes (完成节点数)
   - metric: total_learning_days (累计学习天数)
   - metric: enrolled_courses (报名课程数)
   - metric: completed_quizzes (完成测验数)
   - metric: completed_simulators (完成模拟器数)
   示例: {"type": "counter", "metric": "completed_nodes", "target": 10}

2. streak 类型 - 当前连续天数
   示例: {"type": "streak", "target": 7}

3. max_streak 类型 - 历史最长连续天数
   示例: {"type": "max_streak", "target": 30}

4. time_based 类型 - 学习时长（小时）
   示例: {"type": "time_based", "target": 10}

5. courses 类型 - 完成课程数
   示例: {"type": "courses", "target": 3}

6. days 类型 - 累计学习天数
   示例: {"type": "days", "target": 30}

请根据描述返回一个 JSON 对象，包含以下字段：
- id: 勋章ID (snake_case 格式，英文)
- name: 勋章名称 (中文)
- name_en: 勋章英文名称
- icon: 合适的 emoji 图标
- description: 勋章描述 (中文)
- category: 分类 (learning/persistence/practice/quiz/special)
- rarity: 稀有度 (common/rare/epic/legendary，根据难度判断)
- points: 积分 (10-200，根据难度)
- condition: 解锁条件 JSON

只返回 JSON，不要其他文字。"""

    user_message = f"管理员描述的解锁方式：{request.unlock_description}"
    if request.badge_name:
        user_message += f"\n勋章名称建议：{request.badge_name}"
    if request.badge_category:
        user_message += f"\n分类建议：{request.badge_category}"

    try:
        client = anthropic.Anthropic(
            api_key=settings.ANTHROPIC_API_KEY,
            base_url=settings.ANTHROPIC_BASE_URL
        )

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )

        # 解析 AI 返回的 JSON
        import json
        result_text = response.content[0].text.strip()

        # 尝试提取 JSON（处理可能的 markdown 代码块）
        if result_text.startswith("```"):
            lines = result_text.split("\n")
            json_lines = []
            in_json = False
            for line in lines:
                if line.startswith("```") and not in_json:
                    in_json = True
                    continue
                elif line.startswith("```") and in_json:
                    break
                elif in_json:
                    json_lines.append(line)
            result_text = "\n".join(json_lines)

        badge_config = json.loads(result_text)

        return {
            "success": True,
            "badge": badge_config
        }

    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"AI 返回的格式无法解析: {str(e)}",
            "raw_response": result_text if 'result_text' in locals() else None
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"AI 生成失败: {str(e)}"
        }


@router.get("/achievement-center/leaderboard")
async def get_admin_leaderboard(
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("completed_nodes", regex="^(completed_nodes|total_hours|learning_days|badges)$"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户排行榜"""
    # 获取所有活跃用户
    users_query = select(User).where(User.is_active == 1)
    result = await db.execute(users_query)
    users = result.scalars().all()

    leaderboard = []
    for user in users:
        stats = await get_user_learning_stats(user.id, db)
        leaderboard.append({
            "userId": user.id,
            "username": user.username,
            "fullName": user.full_name,
            "avatarUrl": user.avatar_url,
            **stats
        })

    # 排序
    sort_key_map = {
        "completed_nodes": "completedNodes",
        "total_hours": "totalHours",
        "learning_days": "totalLearningDays",
        "badges": "unlockedBadges"
    }
    sort_key = sort_key_map.get(sort_by, "completedNodes")
    leaderboard.sort(key=lambda x: x.get(sort_key, 0), reverse=True)

    # 添加排名
    for i, item in enumerate(leaderboard[:limit]):
        item["rank"] = i + 1

    return {"data": leaderboard[:limit]}

