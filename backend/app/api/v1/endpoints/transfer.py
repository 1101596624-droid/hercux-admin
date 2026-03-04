"""Phase 16: 动态迁移系数 API"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.models import User
from app.schemas.schemas import TransferUpdateRequest
from app.services.dynamic_transfer_service import DynamicTransferService

router = APIRouter()


@router.get("/my-coefficients")
async def get_my_coefficients(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取个人化迁移系数"""
    return await DynamicTransferService.get_my_coefficients(db, current_user.id)


@router.post("/update")
async def update_transfer(
    req: TransferUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """触发迁移系数贝叶斯更新"""
    return await DynamicTransferService.update_transfer(
        db, current_user.id, req.source_subject_id, req.target_subject_id
    )
