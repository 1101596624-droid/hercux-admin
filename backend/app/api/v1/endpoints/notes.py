"""
User Notes API endpoints
用户笔记 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.db.session import get_db
from app.models.models import UserNote, User
from app.core.security import get_current_user

router = APIRouter()


class NoteCreate(BaseModel):
    course_id: int
    node_id: Optional[int] = None
    title: Optional[str] = None
    content: str


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_pinned: Optional[bool] = None
    is_archived: Optional[bool] = None


class NoteResponse(BaseModel):
    id: int
    course_id: int
    node_id: Optional[int]
    title: Optional[str]
    content: str
    is_pinned: bool
    is_archived: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


@router.get("/course/{course_id}", response_model=List[NoteResponse])
async def get_course_notes(
    course_id: int,
    node_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取课程笔记列表"""
    query = select(UserNote).where(
        and_(
            UserNote.user_id == current_user.id,
            UserNote.course_id == course_id,
            UserNote.is_archived == 0
        )
    )

    if node_id is not None:
        query = query.where(UserNote.node_id == node_id)

    query = query.order_by(UserNote.is_pinned.desc(), UserNote.updated_at.desc())

    result = await db.execute(query)
    notes = result.scalars().all()

    return [
        NoteResponse(
            id=note.id,
            course_id=note.course_id,
            node_id=note.node_id,
            title=note.title,
            content=note.content,
            is_pinned=bool(note.is_pinned),
            is_archived=bool(note.is_archived),
            created_at=note.created_at,
            updated_at=note.updated_at
        )
        for note in notes
    ]


@router.post("", response_model=NoteResponse)
async def create_note(
    note_data: NoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建笔记"""
    note = UserNote(
        user_id=current_user.id,
        course_id=note_data.course_id,
        node_id=note_data.node_id,
        title=note_data.title,
        content=note_data.content
    )

    db.add(note)
    await db.commit()
    await db.refresh(note)

    return NoteResponse(
        id=note.id,
        course_id=note.course_id,
        node_id=note.node_id,
        title=note.title,
        content=note.content,
        is_pinned=bool(note.is_pinned),
        is_archived=bool(note.is_archived),
        created_at=note.created_at,
        updated_at=note.updated_at
    )


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    note_data: NoteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新笔记"""
    result = await db.execute(
        select(UserNote).where(
            and_(
                UserNote.id == note_id,
                UserNote.user_id == current_user.id
            )
        )
    )
    note = result.scalar_one_or_none()

    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")

    if note_data.title is not None:
        note.title = note_data.title
    if note_data.content is not None:
        note.content = note_data.content
    if note_data.is_pinned is not None:
        note.is_pinned = 1 if note_data.is_pinned else 0
    if note_data.is_archived is not None:
        note.is_archived = 1 if note_data.is_archived else 0

    await db.commit()
    await db.refresh(note)

    return NoteResponse(
        id=note.id,
        course_id=note.course_id,
        node_id=note.node_id,
        title=note.title,
        content=note.content,
        is_pinned=bool(note.is_pinned),
        is_archived=bool(note.is_archived),
        created_at=note.created_at,
        updated_at=note.updated_at
    )


@router.delete("/{note_id}")
async def delete_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除笔记"""
    result = await db.execute(
        select(UserNote).where(
            and_(
                UserNote.id == note_id,
                UserNote.user_id == current_user.id
            )
        )
    )
    note = result.scalar_one_or_none()

    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")

    await db.delete(note)
    await db.commit()

    return {"message": "笔记已删除"}
