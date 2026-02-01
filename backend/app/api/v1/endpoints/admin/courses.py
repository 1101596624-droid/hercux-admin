"""
Admin Course Management API
Provides CRUD operations for course management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from typing import List, Optional
from datetime import datetime, timedelta, timezone

from app.db.session import get_db
from app.models.models import Course, CourseNode, User, UserCourse, LearningProgress, DifficultyLevel, NodeStatus, NodeType, ChatHistory, SimulatorResult
from app.schemas.schemas import CourseResponse, CourseCreate, CourseUpdate
from app.core.security import get_current_admin_user
from pydantic import BaseModel

router = APIRouter()


# ============ Course List with Filters ============

@router.get("/courses")
async def list_courses(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    difficulty: Optional[DifficultyLevel] = Query(None, description="Filter by difficulty"),
    is_published: Optional[bool] = Query(None, description="Filter by published status"),
    instructor: Optional[str] = Query(None, description="Filter by instructor"),
    sort_by: str = Query("created_at", description="Sort field: created_at, name, duration_hours"),
    sort_order: str = Query("desc", description="Sort order: asc, desc"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated list of courses with filters

    Admin endpoint for course management
    """
    # Build query
    query = select(Course)

    # Apply filters
    filters = []

    if search:
        search_pattern = f"%{search}%"
        filters.append(
            or_(
                Course.name.ilike(search_pattern),
                Course.description.ilike(search_pattern)
            )
        )

    if difficulty:
        filters.append(Course.difficulty == difficulty)

    if is_published is not None:
        filters.append(Course.is_published == is_published)

    if instructor:
        filters.append(Course.instructor.ilike(f"%{instructor}%"))

    if filters:
        query = query.where(and_(*filters))

    # Apply sorting
    sort_column = getattr(Course, sort_by, Course.created_at)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Get total count
    count_query = select(func.count()).select_from(Course)
    if filters:
        count_query = count_query.where(and_(*filters))
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    # Execute query
    result = await db.execute(query)
    courses = result.scalars().all()

    # Get statistics for each course
    course_list = []
    for course in courses:
        # Count total nodes
        nodes_count_query = select(func.count()).select_from(CourseNode).where(CourseNode.course_id == course.id)
        nodes_result = await db.execute(nodes_count_query)
        total_nodes = nodes_result.scalar()

        # Count enrolled users
        enrolled_count_query = select(func.count()).select_from(UserCourse).where(UserCourse.course_id == course.id)
        enrolled_result = await db.execute(enrolled_count_query)
        enrolled_users = enrolled_result.scalar()

        course_list.append({
            "id": course.id,
            "name": course.name,
            "description": course.description,
            "difficulty": course.difficulty.value if hasattr(course.difficulty, 'value') else course.difficulty,
            "instructor": course.instructor,
            "duration_hours": course.duration_hours,
            "thumbnail_url": course.thumbnail_url,
            "is_published": course.is_published,
            "tags": course.tags,
            "created_at": course.created_at,
            "total_nodes": total_nodes,
            "enrolled_users": enrolled_users
        })

    return {
        "items": course_list,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


# ============ Course Detail ============

@router.get("/courses/{course_id}")
async def get_course_detail(
    course_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed course information including statistics
    """
    # Get course
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course {course_id} not found"
        )

    # Get all nodes
    nodes_result = await db.execute(
        select(CourseNode)
        .where(CourseNode.course_id == course_id)
        .order_by(CourseNode.sequence)
    )
    nodes = nodes_result.scalars().all()

    # Get enrolled users count
    enrolled_result = await db.execute(
        select(func.count())
        .select_from(UserCourse)
        .where(UserCourse.course_id == course_id)
    )
    enrolled_count = enrolled_result.scalar()

    # Get completion statistics
    completed_result = await db.execute(
        select(func.count())
        .select_from(LearningProgress)
        .join(CourseNode, LearningProgress.node_id == CourseNode.id)
        .where(
            CourseNode.course_id == course_id,
            LearningProgress.status == NodeStatus.COMPLETED
        )
    )
    completed_count = completed_result.scalar()

    # Calculate average completion rate
    total_possible_completions = enrolled_count * len(nodes) if nodes else 0
    completion_rate = (completed_count / total_possible_completions * 100) if total_possible_completions > 0 else 0

    # Get recent enrollments (last 30 days)
    from datetime import timedelta
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    recent_enrollments_result = await db.execute(
        select(func.count())
        .select_from(UserCourse)
        .where(
            UserCourse.course_id == course_id,
            UserCourse.enrolled_at >= thirty_days_ago
        )
    )
    recent_enrollments = recent_enrollments_result.scalar()

    return {
        "id": course.id,
        "name": course.name,
        "description": course.description,
        "difficulty": course.difficulty.value if hasattr(course.difficulty, 'value') else course.difficulty,
        "instructor": course.instructor,
        "duration_hours": course.duration_hours,
        "thumbnail_url": course.thumbnail_url,
        "is_published": course.is_published,
        "tags": course.tags,
        "created_at": course.created_at,
        "statistics": {
            "total_nodes": len(nodes),
            "enrolled_users": enrolled_count,
            "completion_rate": round(completion_rate, 2),
            "recent_enrollments": recent_enrollments,
            "total_completions": completed_count
        },
        "nodes": [
            {
                "id": node.id,
                "node_id": node.node_id,
                "type": node.type.value if hasattr(node.type, 'value') else node.type,
                "title": node.title,
                "sequence": node.sequence,
                "parent_id": node.parent_id
            }
            for node in nodes
        ]
    }


# ============ Create Course ============

@router.post("/courses", status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: CourseCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new course

    Admin only
    """
    # 从系统设置获取默认值
    from app.core.system_settings import get_course_settings
    course_settings = get_course_settings()

    # 使用系统默认值填充未提供的字段
    difficulty = course_data.difficulty
    tags = course_data.tags if course_data.tags else course_settings.default_tags

    # 是否自动发布
    auto_publish = course_settings.auto_publish

    # Create course
    course = Course(
        name=course_data.name,
        description=course_data.description,
        difficulty=difficulty,
        instructor=course_data.instructor,
        duration_hours=course_data.duration_hours,
        tags=tags,
        is_published=auto_publish  # 根据系统设置决定是否自动发布
    )

    db.add(course)
    await db.commit()
    await db.refresh(course)

    return {
        "id": course.id,
        "name": course.name,
        "description": course.description,
        "difficulty": course.difficulty.value,
        "instructor": course.instructor,
        "duration_hours": course.duration_hours,
        "tags": course.tags,
        "is_published": course.is_published,
        "created_at": course.created_at,
        "message": "Course created successfully"
    }


# ============ Update Course ============

@router.put("/courses/{course_id}")
async def update_course(
    course_id: int,
    course_data: CourseUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update course information

    Admin only
    """
    # Get course
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course {course_id} not found"
        )

    # Update fields
    update_data = course_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)

    await db.commit()
    await db.refresh(course)

    return {
        "id": course.id,
        "name": course.name,
        "description": course.description,
        "difficulty": course.difficulty.value,
        "instructor": course.instructor,
        "duration_hours": course.duration_hours,
        "thumbnail_url": course.thumbnail_url,
        "tags": course.tags,
        "is_published": course.is_published,
        "created_at": course.created_at,
        "message": "Course updated successfully"
    }


# ============ Delete Course ============

@router.delete("/courses/{course_id}")
async def delete_course(
    course_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a course

    Admin only - This will also delete all associated data:
    - course_nodes (课程节点)
    - learning_progress (学习进度)
    - chat_history (聊天记录)
    - simulator_results (模拟器结果)
    - user_courses (用户课程注册)
    - user_notes (用户笔记)
    - course_packages (课程包导入记录)
    - studio_packages.course_id (重置为 NULL)
    """
    from sqlalchemy import delete as sql_delete, text
    import logging
    logger = logging.getLogger(__name__)

    try:
        # Get course
        result = await db.execute(select(Course).where(Course.id == course_id))
        course = result.scalar_one_or_none()

        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course {course_id} not found"
            )

        course_name = course.name
        logger.info(f"Deleting course {course_id}: {course_name}")

        # Get all node IDs for this course
        nodes_result = await db.execute(
            select(CourseNode.id).where(CourseNode.course_id == course_id)
        )
        node_ids = [row[0] for row in nodes_result.fetchall()]
        logger.info(f"Found {len(node_ids)} nodes to delete")

        # Delete data associated with nodes
        if node_ids:
            # Delete learning progress for all nodes in this course
            await db.execute(
                sql_delete(LearningProgress).where(LearningProgress.node_id.in_(node_ids))
            )
            logger.info("Deleted learning_progress")

            # Delete chat history for all nodes in this course
            await db.execute(
                sql_delete(ChatHistory).where(ChatHistory.node_id.in_(node_ids))
            )
            logger.info("Deleted chat_history")

            # Delete simulator results for all nodes in this course
            await db.execute(
                sql_delete(SimulatorResult).where(SimulatorResult.node_id.in_(node_ids))
            )
            logger.info("Deleted simulator_results")

            # Delete user notes for all nodes in this course
            try:
                await db.execute(
                    text("DELETE FROM user_notes WHERE node_id IN :node_ids"),
                    {"node_ids": tuple(node_ids)}
                )
                logger.info("Deleted user_notes by node_id")
            except Exception as e:
                logger.warning(f"Failed to delete user_notes by node_id: {e}")

        # Delete user notes for this course (including those without node_id)
        try:
            await db.execute(
                text("DELETE FROM user_notes WHERE course_id = :course_id"),
                {"course_id": course_id}
            )
            logger.info("Deleted user_notes by course_id")
        except Exception as e:
            logger.warning(f"Failed to delete user_notes by course_id: {e}")

        # Delete user course enrollments
        await db.execute(
            sql_delete(UserCourse).where(UserCourse.course_id == course_id)
        )
        logger.info("Deleted user_courses")

        # Delete all nodes for this course
        await db.execute(
            sql_delete(CourseNode).where(CourseNode.course_id == course_id)
        )
        logger.info("Deleted course_nodes")

        # Delete course_packages record
        try:
            await db.execute(
                text("DELETE FROM course_packages WHERE course_id = :course_id"),
                {"course_id": course_id}
            )
            logger.info("Deleted course_packages")
        except Exception as e:
            logger.warning(f"Failed to delete course_packages: {e}")

        # Reset studio_packages.course_id to NULL and status to draft
        try:
            await db.execute(
                text("UPDATE studio_packages SET course_id = NULL, status = 'draft' WHERE course_id = :course_id"),
                {"course_id": course_id}
            )
            logger.info("Reset studio_packages")
        except Exception as e:
            logger.warning(f"Failed to reset studio_packages: {e}")

        # Delete the course
        await db.delete(course)
        await db.commit()

        logger.info(f"Course {course_id} deleted successfully")

        return {
            "message": f"课程 '{course_name}' 及其所有相关数据已删除",
            "course_id": course_id,
            "deleted": {
                "nodes": len(node_ids),
                "related_data": ["learning_progress", "chat_history", "simulator_results", "user_notes", "user_courses", "course_packages"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete course error: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除失败: {str(e)}"
        )


# ============ Publish/Unpublish Course ============

@router.post("/courses/{course_id}/publish")
async def publish_course(
    course_id: int,
    publish: bool = True,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Publish or unpublish a course

    Admin only
    """
    # Get course
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course {course_id} not found"
        )

    course.is_published = publish
    await db.commit()

    return {
        "message": f"Course {'published' if publish else 'unpublished'} successfully",
        "course_id": course_id,
        "is_published": course.is_published
    }


# ============ Course Statistics ============

@router.get("/courses/{course_id}/statistics")
async def get_course_statistics(
    course_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed statistics for a course

    Admin only
    """
    # Verify course exists
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course {course_id} not found"
        )

    # Get enrolled users over time (last 12 months)
    from datetime import timedelta

    monthly_enrollments = []
    for i in range(12):
        month_start = datetime.now(timezone.utc) - timedelta(days=30 * (i + 1))
        month_end = datetime.now(timezone.utc) - timedelta(days=30 * i)

        count_result = await db.execute(
            select(func.count())
            .select_from(UserCourse)
            .where(
                UserCourse.course_id == course_id,
                UserCourse.enrolled_at >= month_start,
                UserCourse.enrolled_at < month_end
            )
        )
        count = count_result.scalar()
        monthly_enrollments.append({
            "month": month_start.strftime("%Y-%m"),
            "enrollments": count
        })

    monthly_enrollments.reverse()

    # Get completion rate by node
    nodes_result = await db.execute(
        select(CourseNode)
        .where(CourseNode.course_id == course_id)
        .order_by(CourseNode.sequence)
    )
    nodes = nodes_result.scalars().all()

    node_completion_rates = []
    for node in nodes:
        completed_result = await db.execute(
            select(func.count())
            .select_from(LearningProgress)
            .where(
                LearningProgress.node_id == node.id,
                LearningProgress.status == NodeStatus.COMPLETED
            )
        )
        completed = completed_result.scalar()

        started_result = await db.execute(
            select(func.count())
            .select_from(LearningProgress)
            .where(LearningProgress.node_id == node.id)
        )
        started = started_result.scalar()

        completion_rate = (completed / started * 100) if started > 0 else 0

        node_completion_rates.append({
            "node_id": node.node_id,
            "title": node.title,
            "type": node.type.value,
            "started": started,
            "completed": completed,
            "completion_rate": round(completion_rate, 2)
        })

    return {
        "course_id": course_id,
        "course_name": course.name,
        "monthly_enrollments": monthly_enrollments,
        "node_completion_rates": node_completion_rates
    }


# ============ Node Management ============

class NodeCreate(BaseModel):
    """Schema for creating a course node"""
    node_id: str
    type: NodeType
    component_id: str
    title: str
    description: Optional[str] = None
    sequence: int = 0
    parent_id: Optional[int] = None
    timeline_config: Optional[dict] = None
    unlock_condition: Optional[dict] = None
    content: Optional[dict] = None  # Node content (steps, etc.)
    config: Optional[dict] = None   # Node configuration


class NodeUpdate(BaseModel):
    """Schema for updating a course node"""
    node_id: Optional[str] = None
    type: Optional[NodeType] = None
    component_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    sequence: Optional[int] = None
    parent_id: Optional[int] = None
    timeline_config: Optional[dict] = None
    unlock_condition: Optional[dict] = None
    content: Optional[dict] = None  # Node content (steps, etc.)
    config: Optional[dict] = None   # Node configuration


@router.get("/courses/{course_id}/nodes")
async def list_course_nodes(
    course_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all nodes for a course with full configuration

    Admin only
    """
    # Verify course exists
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course {course_id} not found"
        )

    # Get all nodes
    nodes_result = await db.execute(
        select(CourseNode)
        .where(CourseNode.course_id == course_id)
        .order_by(CourseNode.sequence)
    )
    nodes = nodes_result.scalars().all()

    return {
        "course_id": course_id,
        "course_name": course.name,
        "nodes": [
            {
                "id": node.id,
                "node_id": node.node_id,
                "type": node.type.value if hasattr(node.type, 'value') else node.type,
                "component_id": node.component_id,
                "title": node.title,
                "description": node.description,
                "sequence": node.sequence,
                "parent_id": node.parent_id,
                "content": node.content,
                "config": node.config,
                "timeline_config": node.timeline_config,
                "unlock_condition": node.unlock_condition,
                "created_at": node.created_at,
                "updated_at": node.updated_at
            }
            for node in nodes
        ]
    }


@router.get("/nodes/{node_id}")
async def get_node_detail(
    node_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed node information including configuration

    Admin only
    """
    result = await db.execute(select(CourseNode).where(CourseNode.id == node_id))
    node = result.scalar_one_or_none()

    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node {node_id} not found"
        )

    # Get course info
    course_result = await db.execute(select(Course).where(Course.id == node.course_id))
    course = course_result.scalar_one()

    # Get progress statistics
    progress_count_result = await db.execute(
        select(func.count())
        .select_from(LearningProgress)
        .where(LearningProgress.node_id == node.id)
    )
    total_progress = progress_count_result.scalar()

    completed_count_result = await db.execute(
        select(func.count())
        .select_from(LearningProgress)
        .where(
            LearningProgress.node_id == node.id,
            LearningProgress.status == NodeStatus.COMPLETED
        )
    )
    completed = completed_count_result.scalar()

    return {
        "id": node.id,
        "node_id": node.node_id,
        "type": node.type.value,
        "component_id": node.component_id,
        "title": node.title,
        "description": node.description,
        "sequence": node.sequence,
        "parent_id": node.parent_id,
        "timeline_config": node.timeline_config,
        "unlock_condition": node.unlock_condition,
        "course": {
            "id": course.id,
            "name": course.name
        },
        "statistics": {
            "total_started": total_progress,
            "total_completed": completed,
            "completion_rate": round((completed / total_progress * 100) if total_progress > 0 else 0, 2)
        },
        "created_at": node.created_at,
        "updated_at": node.updated_at
    }


@router.post("/courses/{course_id}/nodes", status_code=status.HTTP_201_CREATED)
async def create_node(
    course_id: int,
    node_data: NodeCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new node for a course

    Admin only
    """
    # Verify course exists
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course {course_id} not found"
        )

    # Check if node_id already exists
    existing_result = await db.execute(
        select(CourseNode).where(CourseNode.node_id == node_data.node_id)
    )
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Node with node_id '{node_data.node_id}' already exists"
        )

    # Create node
    node = CourseNode(
        course_id=course_id,
        node_id=node_data.node_id,
        type=node_data.type,
        component_id=node_data.component_id,
        title=node_data.title,
        description=node_data.description,
        sequence=node_data.sequence,
        parent_id=node_data.parent_id,
        timeline_config=node_data.timeline_config,
        unlock_condition=node_data.unlock_condition,
        content=node_data.content,
        config=node_data.config
    )

    db.add(node)
    await db.commit()
    await db.refresh(node)

    return {
        "id": node.id,
        "node_id": node.node_id,
        "type": node.type.value,
        "component_id": node.component_id,
        "title": node.title,
        "description": node.description,
        "sequence": node.sequence,
        "parent_id": node.parent_id,
        "timeline_config": node.timeline_config,
        "unlock_condition": node.unlock_condition,
        "created_at": node.created_at,
        "message": "Node created successfully"
    }


@router.put("/courses/{course_id}/nodes/{node_id}")
async def update_course_node(
    course_id: int,
    node_id: int,
    node_data: NodeUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update node information and configuration (nested route)

    Admin only - Can update timeline_config to change API endpoints
    """
    # Get node and verify it belongs to the course
    result = await db.execute(
        select(CourseNode).where(
            CourseNode.id == node_id,
            CourseNode.course_id == course_id
        )
    )
    node = result.scalar_one_or_none()

    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node {node_id} not found in course {course_id}"
        )

    # Check if new node_id conflicts with existing
    if node_data.node_id and node_data.node_id != node.node_id:
        existing_result = await db.execute(
            select(CourseNode).where(CourseNode.node_id == node_data.node_id)
        )
        if existing_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Node with node_id '{node_data.node_id}' already exists"
            )

    # Update fields
    update_data = node_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(node, field, value)

    await db.commit()
    await db.refresh(node)

    return {
        "id": node.id,
        "node_id": node.node_id,
        "type": node.type.value,
        "component_id": node.component_id,
        "title": node.title,
        "description": node.description,
        "sequence": node.sequence,
        "parent_id": node.parent_id,
        "timeline_config": node.timeline_config,
        "unlock_condition": node.unlock_condition,
        "updated_at": node.updated_at,
        "message": "Node updated successfully"
    }


@router.put("/nodes/{node_id}")
async def update_node(
    node_id: int,
    node_data: NodeUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update node information and configuration

    Admin only - Can update timeline_config to change API endpoints
    """
    # Get node
    result = await db.execute(select(CourseNode).where(CourseNode.id == node_id))
    node = result.scalar_one_or_none()

    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node {node_id} not found"
        )

    # Check if new node_id conflicts with existing
    if node_data.node_id and node_data.node_id != node.node_id:
        existing_result = await db.execute(
            select(CourseNode).where(CourseNode.node_id == node_data.node_id)
        )
        if existing_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Node with node_id '{node_data.node_id}' already exists"
            )

    # Update fields
    update_data = node_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(node, field, value)

    await db.commit()
    await db.refresh(node)

    return {
        "id": node.id,
        "node_id": node.node_id,
        "type": node.type.value,
        "component_id": node.component_id,
        "title": node.title,
        "description": node.description,
        "sequence": node.sequence,
        "parent_id": node.parent_id,
        "timeline_config": node.timeline_config,
        "unlock_condition": node.unlock_condition,
        "updated_at": node.updated_at,
        "message": "Node updated successfully"
    }


@router.delete("/nodes/{node_id}")
async def delete_node(
    node_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a node

    Admin only - This will also delete all associated progress
    """
    # Get node
    result = await db.execute(select(CourseNode).where(CourseNode.id == node_id))
    node = result.scalar_one_or_none()

    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node {node_id} not found"
        )

    node_title = node.title

    # Delete node (cascade will handle related records)
    await db.delete(node)
    await db.commit()

    return {
        "message": f"Node '{node_title}' deleted successfully",
        "node_id": node_id
    }


# ============ Quiz Bank Generation ============

@router.post("/courses/{course_id}/generate-quiz-bank")
async def generate_course_quiz_bank(
    course_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    为课程的所有节点生成题库

    Admin only - 这会为课程中的每个节点生成13道测验题目并保存到数据库
    """
    from app.services.quiz_generator import generate_quiz_for_course

    # Verify course exists
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course {course_id} not found"
        )

    # Generate quiz bank for all nodes
    result = await generate_quiz_for_course(course_id)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["message"]
        )

    return {
        "message": result["message"],
        "course_id": course_id,
        "course_name": course.name,
        "generated": result["generated"],
        "failed": result["failed"],
        "total": result["total"]
    }


@router.post("/nodes/{node_id}/generate-quiz-bank")
async def generate_node_quiz_bank(
    node_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    为单个节点生成题库

    Admin only - 生成13道测验题目并保存到数据库
    """
    from app.services.quiz_generator import generate_quiz_for_node

    # Verify node exists
    result = await db.execute(select(CourseNode).where(CourseNode.id == node_id))
    node = result.scalar_one_or_none()

    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node {node_id} not found"
        )

    # Generate quiz bank
    success = await generate_quiz_for_node(node_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate quiz bank"
        )

    return {
        "message": f"Quiz bank generated for node '{node.title}'",
        "node_id": node_id,
        "node_title": node.title
    }
