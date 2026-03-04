"""
Admin Knowledge Tracking API
管理后台 - 知识追踪管理接口
"""

import asyncio
import logging
import time
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case
from typing import Optional, List
from datetime import datetime

from app.db.session import get_db
from app.models.models import (
    Subject, KnowledgeNode, StudentKnowledgeState,
    StudentEvent, StudentMisconception, User
)
from app.schemas.schemas import (
    SubjectCreate, SubjectResponse,
    KnowledgeNodeCreate, KnowledgeNodeResponse,
    StudentEventResponse,
)

router = APIRouter()
logger = logging.getLogger(__name__)

_OVERVIEW_CACHE_TTL_SECONDS = 10.0
_OVERVIEW_QUERY_TIMEOUT_SECONDS = 8.0
_OVERVIEW_SUBJECT_FALLBACK_TIMEOUT_SECONDS = 3.0
_overview_cache: dict = {"ts": 0.0, "data": None}
_overview_cache_lock = asyncio.Lock()


def _build_overview_payload(rows) -> list[dict]:
    return [
        {
            "subject_id": r.subject_id,
            "subject_name": r.subject_name,
            "total_nodes": int(r.total_nodes or 0),
            "avg_mastery": round(float(r.avg_mastery or 0.0), 3),
            "active_students": int(r.active_students or 0),
            "weak_node_count": int(r.weak_node_count or 0),
        }
        for r in rows
    ]


async def _build_subject_only_fallback(db: AsyncSession) -> list[dict]:
    try:
        result = await asyncio.wait_for(
            db.execute(
                select(
                    Subject.id.label("subject_id"),
                    Subject.name.label("subject_name"),
                ).order_by(Subject.id)
            ),
            timeout=_OVERVIEW_SUBJECT_FALLBACK_TIMEOUT_SECONDS,
        )
        rows = result.all()
        return [
            {
                "subject_id": r.subject_id,
                "subject_name": r.subject_name,
                "total_nodes": 0,
                "avg_mastery": 0.0,
                "active_students": 0,
                "weak_node_count": 0,
            }
            for r in rows
        ]
    except Exception:
        logger.exception("Knowledge overview subject-only fallback failed")
        return []


# ============ 学科管理 ============

@router.get("/subjects", response_model=List[SubjectResponse])
async def get_subjects(db: AsyncSession = Depends(get_db)):
    """获取学科列表"""
    result = await db.execute(select(Subject).order_by(Subject.id))
    return result.scalars().all()


@router.post("/subjects", response_model=SubjectResponse)
async def create_subject(
    data: SubjectCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建学科"""
    existing = await db.execute(
        select(Subject).where(Subject.name == data.name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(400, "学科名称已存在")

    subject = Subject(name=data.name, description=data.description)
    db.add(subject)
    await db.commit()
    await db.refresh(subject)
    return subject


# ============ 知识节点管理 ============

@router.get("/nodes", response_model=List[KnowledgeNodeResponse])
async def get_knowledge_nodes(
    subject_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """获取知识节点列表"""
    query = select(KnowledgeNode)
    if subject_id:
        query = query.where(KnowledgeNode.subject_id == subject_id)
    query = query.order_by(KnowledgeNode.code)
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/nodes", response_model=KnowledgeNodeResponse)
async def create_knowledge_node(
    data: KnowledgeNodeCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建知识节点"""
    # 检查学科存在
    subj = await db.execute(select(Subject).where(Subject.id == data.subject_id))
    if not subj.scalar_one_or_none():
        raise HTTPException(404, "学科不存在")

    # 检查 code 唯一
    existing = await db.execute(
        select(KnowledgeNode).where(KnowledgeNode.code == data.code)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(400, "知识节点编码已存在")

    node = KnowledgeNode(
        subject_id=data.subject_id,
        course_node_id=data.course_node_id,
        code=data.code,
        name=data.name,
        description=data.description,
        difficulty=data.difficulty,
        parent_code=data.parent_code,
        prerequisites=data.prerequisites or [],
    )
    db.add(node)
    await db.commit()
    await db.refresh(node)
    return node


# ============ 学生知识状态查看 ============

@router.get("/students/{user_id}/state")
async def get_student_state(
    user_id: int,
    subject_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """查看学生知识状态"""
    from app.services.bkt_service import BKTService
    states = await BKTService.get_user_knowledge_summary(db, user_id, subject_id)
    return {"user_id": user_id, "states": states}


@router.get("/students/{user_id}/events", response_model=List[StudentEventResponse])
async def get_student_events(
    user_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """查看学生事件历史"""
    result = await db.execute(
        select(StudentEvent)
        .where(StudentEvent.user_id == user_id)
        .order_by(StudentEvent.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return result.scalars().all()


@router.get("/students/{user_id}/misconceptions")
async def get_student_misconceptions(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """查看学生错误概念"""
    result = await db.execute(
        select(
            StudentMisconception,
            KnowledgeNode.name.label("node_name"),
        )
        .join(KnowledgeNode, StudentMisconception.knowledge_node_id == KnowledgeNode.id)
        .where(StudentMisconception.user_id == user_id)
        .order_by(StudentMisconception.last_seen_at.desc())
    )
    rows = result.all()
    return [
        {
            "id": row.StudentMisconception.id,
            "user_id": user_id,
            "knowledge_node_id": row.StudentMisconception.knowledge_node_id,
            "misconception": row.StudentMisconception.misconception,
            "frequency": row.StudentMisconception.frequency,
            "last_seen_at": row.StudentMisconception.last_seen_at,
            "resolved": row.StudentMisconception.resolved,
            "created_at": row.StudentMisconception.created_at,
            "node_name": row.node_name,
        }
        for row in rows
    ]


# ============ 全局概览 ============

@router.get("/overview")
async def get_knowledge_overview(db: AsyncSession = Depends(get_db)):
    """全局知识追踪概览"""
    now_ts = time.monotonic()
    cached = _overview_cache.get("data")
    if cached is not None and (now_ts - float(_overview_cache.get("ts", 0.0))) < _OVERVIEW_CACHE_TTL_SECONDS:
        return cached

    # 缓存失效时使用 single-flight，避免并发回源打爆数据库
    async with _overview_cache_lock:
        now_ts = time.monotonic()
        cached = _overview_cache.get("data")
        if cached is not None and (now_ts - float(_overview_cache.get("ts", 0.0))) < _OVERVIEW_CACHE_TTL_SECONDS:
            return cached
        stale_cached = cached

        try:
            # 子查询1: 每个学科的节点总数
            node_stats = (
                select(
                    KnowledgeNode.subject_id.label("subject_id"),
                    func.count(KnowledgeNode.id).label("total_nodes"),
                )
                .group_by(KnowledgeNode.subject_id)
                .subquery()
            )

            # 子查询2: 每个学科的掌握度/活跃学生/薄弱节点
            mastery_stats = (
                select(
                    KnowledgeNode.subject_id.label("subject_id"),
                    func.avg(StudentKnowledgeState.mastery).label("avg_mastery"),
                    func.count(func.distinct(StudentKnowledgeState.user_id)).label("active_students"),
                    func.count(
                        func.distinct(
                            case(
                                (StudentKnowledgeState.mastery < 0.4, StudentKnowledgeState.knowledge_node_id),
                                else_=None,
                            )
                        )
                    ).label("weak_node_count"),
                )
                .join(
                    KnowledgeNode,
                    StudentKnowledgeState.knowledge_node_id == KnowledgeNode.id,
                )
                .group_by(KnowledgeNode.subject_id)
                .subquery()
            )

            result = await asyncio.wait_for(
                db.execute(
                    select(
                        Subject.id.label("subject_id"),
                        Subject.name.label("subject_name"),
                        func.coalesce(node_stats.c.total_nodes, 0).label("total_nodes"),
                        func.coalesce(mastery_stats.c.avg_mastery, 0.0).label("avg_mastery"),
                        func.coalesce(mastery_stats.c.active_students, 0).label("active_students"),
                        func.coalesce(mastery_stats.c.weak_node_count, 0).label("weak_node_count"),
                    )
                    .outerjoin(node_stats, node_stats.c.subject_id == Subject.id)
                    .outerjoin(mastery_stats, mastery_stats.c.subject_id == Subject.id)
                    .order_by(Subject.id)
                ),
                timeout=_OVERVIEW_QUERY_TIMEOUT_SECONDS,
            )
            overview = _build_overview_payload(result.all())

            # 避免并发请求重复回源
            _overview_cache["ts"] = now_ts
            _overview_cache["data"] = overview
            return overview
        except asyncio.TimeoutError:
            logger.warning(
                "Knowledge overview query timed out after %.1fs, serving degraded response",
                _OVERVIEW_QUERY_TIMEOUT_SECONDS,
            )
        except Exception:
            logger.exception("Knowledge overview query failed, serving degraded response")

        if stale_cached is not None:
            return stale_cached

        return await _build_subject_only_fallback(db)


# ============ 情感状态查看 (Phase 2) ============

@router.get("/students/{user_id}/emotions")
async def get_student_emotions(
    user_id: int,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """查看学生情感状态历史"""
    from app.services.emotion_service import EmotionService
    history = await EmotionService.get_user_emotion_history(db, user_id, limit)
    return {"user_id": user_id, "emotions": history}


@router.get("/students/{user_id}/emotion/current")
async def get_student_current_emotion(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取学生当前情感状态"""
    from app.services.emotion_service import EmotionService
    current = await EmotionService.get_current_emotion(db, user_id)
    return {"user_id": user_id, "current_emotion": current}
