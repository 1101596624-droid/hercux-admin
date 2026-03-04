"""
Phase 9: 学科知识图谱 API 端点
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import get_current_user
from app.services.subject_graph_service import SubjectGraphService
from app.schemas.schemas import SubjectRelationCreate

router = APIRouter()


@router.get("/graph")
async def get_subject_graph(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """获取完整学科知识图谱（节点+边）"""
    return await SubjectGraphService.get_subject_graph(db)


@router.get("/cross-disciplinary-recommendations")
async def get_cross_disciplinary_recommendations(
    limit: int = Query(10, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """获取跨学科课程推荐"""
    return await SubjectGraphService.get_cross_disciplinary_recommendations(
        db=db, user_id=current_user.id, limit=limit,
    )


@router.post("/relations")
async def add_subject_relation(
    request: SubjectRelationCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """添加学科间关系（管理员）"""
    rel = await SubjectGraphService.add_relation(db, request.model_dump())
    await db.commit()
    return {"id": rel.id, "message": "学科关系已添加"}


@router.get("/relations/{subject_id}")
async def get_subject_relations(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """获取指定学科的所有关系"""
    return await SubjectGraphService.get_subject_relations(db, subject_id)
