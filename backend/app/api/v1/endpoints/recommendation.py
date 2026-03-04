"""
Recommendation API - Phase 6 推荐系统
GET  /recommended-content    个性化推荐（小课堂+做题家+课程）
POST /course-relations       添加课程关联（Admin）
GET  /course-relations/{id}  获取课程关联
"""

import asyncio
import json
import logging
import time
from typing import Any

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.db.redis import get_redis
from app.db.session import get_db
from app.core.security import get_current_user
from app.models.models import User, CourseRecommendation
from app.schemas.schemas import CourseRecommendationCreate
from app.services.recommendation_service import RecommendationService

router = APIRouter()
logger = logging.getLogger(__name__)

_RECO_CACHE_TTL_SECONDS = 20
_RECO_CACHE_KEY_PREFIX = "hercu:reco:content:v1:"
_LOCAL_CACHE_TTL_SECONDS = 8.0
_LOCAL_CACHE_MAX_KEYS = 512
_local_reco_cache: dict[str, tuple[float, dict[str, Any]]] = {}
_reco_cache_locks: dict[str, asyncio.Lock] = {}
_reco_cache_locks_guard = asyncio.Lock()


def _build_reco_cache_key(user_id: int, limit: int) -> str:
    return f"{_RECO_CACHE_KEY_PREFIX}{user_id}:{limit}"


def _local_cache_get(key: str) -> dict[str, Any] | None:
    now = time.monotonic()
    cached = _local_reco_cache.get(key)
    if not cached:
        return None
    ts, payload = cached
    if now - ts > _LOCAL_CACHE_TTL_SECONDS:
        _local_reco_cache.pop(key, None)
        return None
    return payload


def _local_cache_set(key: str, payload: dict[str, Any]) -> None:
    now = time.monotonic()
    _local_reco_cache[key] = (now, payload)
    if len(_local_reco_cache) <= _LOCAL_CACHE_MAX_KEYS:
        return
    stale = [k for k, (ts, _) in _local_reco_cache.items() if now - ts > _LOCAL_CACHE_TTL_SECONDS]
    for k in stale:
        _local_reco_cache.pop(k, None)
    if len(_local_reco_cache) > _LOCAL_CACHE_MAX_KEYS:
        for idx, k in enumerate(list(_local_reco_cache.keys())):
            _local_reco_cache.pop(k, None)
            if idx >= 31:
                break


async def _redis_cache_get(key: str) -> dict[str, Any] | None:
    try:
        redis = await get_redis()
        raw = await redis.get(key)
        if not raw:
            return None
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
    except Exception as exc:
        logger.debug("Recommendation redis cache read failed: %s", exc)
    return None


async def _redis_cache_set(key: str, payload: dict[str, Any]) -> None:
    try:
        redis = await get_redis()
        await redis.setex(key, _RECO_CACHE_TTL_SECONDS, json.dumps(payload, ensure_ascii=False))
    except Exception as exc:
        logger.debug("Recommendation redis cache write failed: %s", exc)


async def _get_cache_lock(key: str) -> asyncio.Lock:
    async with _reco_cache_locks_guard:
        lock = _reco_cache_locks.get(key)
        if lock is None:
            lock = asyncio.Lock()
            _reco_cache_locks[key] = lock
        return lock


@router.get("/recommended-content")
async def get_recommended_content(
    limit: int = Query(12, ge=3, le=30),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取个性化推荐内容（小课堂+做题家+课程）"""
    cache_key = _build_reco_cache_key(int(current_user.id), limit)

    cached = _local_cache_get(cache_key)
    if cached is None:
        cached = await _redis_cache_get(cache_key)
        if cached is not None:
            _local_cache_set(cache_key, cached)
    if cached is not None:
        return cached

    lock = await _get_cache_lock(cache_key)
    async with lock:
        cached = _local_cache_get(cache_key)
        if cached is None:
            cached = await _redis_cache_get(cache_key)
            if cached is not None:
                _local_cache_set(cache_key, cached)
        if cached is not None:
            return cached

        result = await RecommendationService.get_recommended_content(
            db=db,
            user_id=current_user.id,
            limit=limit,
            persist=True,
        )
        await db.commit()
        _local_cache_set(cache_key, result)
        await _redis_cache_set(cache_key, result)
        return result


@router.post("/course-relations")
async def add_course_relation(
    data: CourseRecommendationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """添加课程推荐关联"""
    rec = CourseRecommendation(
        source_course_id=data.source_course_id,
        target_course_id=data.target_course_id,
        relation_type=data.relation_type,
        weight=data.weight,
        reason=data.reason,
    )
    db.add(rec)
    await db.commit()
    return {"id": rec.id, "message": "课程关联已添加"}


@router.get("/course-relations/{course_id}")
async def get_course_relations(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取课程的推荐关联"""
    result = await db.execute(
        select(CourseRecommendation).where(
            CourseRecommendation.source_course_id == course_id
        )
    )
    relations = result.scalars().all()
    return [
        {
            "id": r.id,
            "target_course_id": r.target_course_id,
            "relation_type": r.relation_type,
            "weight": r.weight,
            "reason": r.reason,
        }
        for r in relations
    ]
