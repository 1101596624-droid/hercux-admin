"""
Phase 10: 跨学科推荐与知识推理 API 端点
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import get_current_user
from app.services.cross_disciplinary_service import CrossDisciplinaryService
from app.schemas.schemas import (
    ConceptBridgeCreate, TransferPredictionRequest,
    CrossDisciplinaryPathRequest,
)

router = APIRouter()


@router.get("/recommendations")
async def get_cross_recommendations(
    limit: int = Query(10, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """基于掌握度的跨学科知识推荐"""
    return await CrossDisciplinaryService.recommend_from_mastery(
        db, current_user.id, limit,
    )


@router.get("/concept-recommendations")
async def get_concept_recommendations(
    limit: int = Query(10, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """基于共享概念桥接的跨学科推荐"""
    return await CrossDisciplinaryService.recommend_by_concepts(
        db, current_user.id, limit,
    )


@router.post("/transfer-prediction")
async def predict_transfer(
    request: TransferPredictionRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """学习迁移预测：预测从学科A到学科B的迁移效果"""
    return await CrossDisciplinaryService.predict_transfer(
        db, current_user.id,
        request.source_subject_id, request.target_subject_id,
    )


@router.post("/learning-path")
async def generate_cross_path(
    request: CrossDisciplinaryPathRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """生成跨学科学习路径"""
    return await CrossDisciplinaryService.generate_cross_path(
        db, current_user.id,
        request.target_subject_id, request.session_minutes,
    )


@router.post("/concept-bridges")
async def add_concept_bridge(
    request: ConceptBridgeCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """添加概念桥接（管理员）"""
    bridge = await CrossDisciplinaryService.add_concept_bridge(
        db, request.model_dump(),
    )
    await db.commit()
    return {"id": bridge.id, "message": "概念桥接已添加"}


@router.get("/concept-bridges/{node_id}")
async def get_concept_bridges(
    node_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """获取知识节点的概念桥接"""
    return await CrossDisciplinaryService.get_concept_bridges(db, node_id)
