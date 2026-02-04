"""
Admin Management API
管理员账号管理
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime

from app.db.session import get_db
from app.models.models import User
from app.core.security import get_current_admin_user, get_password_hash

router = APIRouter()


# ============ Schemas ============

class AdminCreate(BaseModel):
    """创建管理员请求"""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    admin_level: int = 3  # 默认普通管理员


class AdminUpdate(BaseModel):
    """更新管理员请求"""
    full_name: Optional[str] = None
    admin_level: Optional[int] = None
    is_active: Optional[int] = None


class AdminResponse(BaseModel):
    """管理员响应"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    admin_level: int
    is_active: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class AdminListResponse(BaseModel):
    """管理员列表响应"""
    items: List[AdminResponse]
    total: int
    page: int
    page_size: int


# ============ API Endpoints ============

@router.get("/admins/me", response_model=AdminResponse)
async def get_current_admin(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前管理员信息
    """
    return AdminResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        admin_level=current_user.admin_level or 3,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@router.get("/admins", response_model=AdminListResponse)
async def get_admins(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    level: Optional[int] = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取管理员列表

    需要管理员权限
    """
    # 构建查询
    query = select(User).where(User.is_admin == 1)

    # 搜索过滤
    if search:
        query = query.where(
            or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%")
            )
        )

    # 等级过滤
    if level is not None:
        query = query.where(User.admin_level == level)

    # 计算总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(User.admin_level.asc(), User.created_at.desc())

    result = await db.execute(query)
    admins = result.scalars().all()

    return AdminListResponse(
        items=[AdminResponse(
            id=admin.id,
            username=admin.username,
            email=admin.email,
            full_name=admin.full_name,
            admin_level=admin.admin_level or 3,
            is_active=admin.is_active,
            created_at=admin.created_at,
            updated_at=admin.updated_at
        ) for admin in admins],
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/admins", response_model=AdminResponse)
async def create_admin(
    admin_data: AdminCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建新管理员

    只有1级和2级管理员可以创建新管理员
    1级管理员可以创建任何等级的管理员
    2级管理员只能创建3级管理员
    """
    # 检查权限
    current_level = current_user.admin_level or 3
    if current_level > 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，只有1级和2级管理员可以创建新管理员"
        )

    # 2级管理员只能创建3级管理员
    if current_level == 2 and admin_data.admin_level < 3:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="2级管理员只能创建3级管理员"
        )

    # 检查用户名是否已存在
    existing = await db.execute(
        select(User).where(
            or_(User.username == admin_data.username, User.email == admin_data.email)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名或邮箱已存在"
        )

    # 创建管理员
    new_admin = User(
        username=admin_data.username,
        email=admin_data.email,
        hashed_password=get_password_hash(admin_data.password),
        full_name=admin_data.full_name,
        is_admin=1,
        admin_level=admin_data.admin_level,
        is_active=1
    )

    db.add(new_admin)
    await db.commit()
    await db.refresh(new_admin)

    return AdminResponse(
        id=new_admin.id,
        username=new_admin.username,
        email=new_admin.email,
        full_name=new_admin.full_name,
        admin_level=new_admin.admin_level or 3,
        is_active=new_admin.is_active,
        created_at=new_admin.created_at,
        updated_at=new_admin.updated_at
    )


@router.put("/admins/{admin_id}", response_model=AdminResponse)
async def update_admin(
    admin_id: int,
    admin_data: AdminUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新管理员信息

    只有1级管理员可以修改其他管理员的等级
    """
    # 获取目标管理员
    result = await db.execute(select(User).where(User.id == admin_id, User.is_admin == 1))
    admin = result.scalar_one_or_none()

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="管理员不存在"
        )

    current_level = current_user.admin_level or 3
    target_level = admin.admin_level or 3

    # 不能修改比自己等级高或相同的管理员（除非是自己）
    if admin_id != current_user.id and target_level <= current_level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="不能修改等级高于或等于自己的管理员"
        )

    # 只有1级管理员可以修改等级
    if admin_data.admin_level is not None and current_level != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有1级管理员可以修改管理员等级"
        )

    # 不能将1级管理员降级
    if target_level == 1 and admin_data.admin_level and admin_data.admin_level > 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="不能降级1级管理员"
        )

    # 更新字段
    if admin_data.full_name is not None:
        admin.full_name = admin_data.full_name
    if admin_data.admin_level is not None:
        admin.admin_level = admin_data.admin_level
    if admin_data.is_active is not None:
        admin.is_active = admin_data.is_active

    await db.commit()
    await db.refresh(admin)

    return AdminResponse(
        id=admin.id,
        username=admin.username,
        email=admin.email,
        full_name=admin.full_name,
        admin_level=admin.admin_level or 3,
        is_active=admin.is_active,
        created_at=admin.created_at,
        updated_at=admin.updated_at
    )


@router.delete("/admins/{admin_id}")
async def delete_admin(
    admin_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除管理员

    不能删除1级管理员
    只有1级和2级管理员可以删除其他管理员
    """
    # 不能删除自己
    if admin_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账号"
        )

    # 获取目标管理员
    result = await db.execute(select(User).where(User.id == admin_id, User.is_admin == 1))
    admin = result.scalar_one_or_none()

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="管理员不存在"
        )

    current_level = current_user.admin_level or 3
    target_level = admin.admin_level or 3

    # 检查权限
    if current_level > 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，只有1级和2级管理员可以删除管理员"
        )

    # 不能删除1级管理员
    if target_level == 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="不能删除1级管理员"
        )

    # 不能删除等级高于或等于自己的管理员
    if target_level <= current_level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="不能删除等级高于或等于自己的管理员"
        )

    # 删除管理员（实际上是取消管理员权限）
    admin.is_admin = 0
    admin.admin_level = 0

    await db.commit()

    return {"success": True, "message": "管理员已删除"}
