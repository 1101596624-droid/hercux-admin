from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List
from datetime import datetime, timezone

from app.db.session import get_db
from app.models.models import CourseNode, LearningProgress, NodeStatus, User
from app.schemas.schemas import CourseNodeResponse, CourseNodeWithProgress, ProgressUpdate
from app.services.unlock_service import UnlockService
from app.core.security import get_current_user

router = APIRouter()


@router.get("/{node_id}", response_model=CourseNodeWithProgress)
async def get_node(
    node_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get course node configuration and user progress

    This is the CORE endpoint for the Learning Workstation.
    Returns the node's config JSON which drives the canvas component.

    Returns:
    - Node metadata (type, component_id, title, description)
    - Config JSON (component-specific parameters)
    - User progress (status, completion, time spent)
    """
    # Get node
    result = await db.execute(
        select(CourseNode).where(CourseNode.node_id == node_id)
    )
    node = result.scalar_one_or_none()

    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node '{node_id}' not found"
        )

    # Get user progress for this node
    progress_result = await db.execute(
        select(LearningProgress).where(
            LearningProgress.user_id == current_user.id,
            LearningProgress.node_id == node.id
        )
    )
    progress = progress_result.scalar_one_or_none()

    # Check unlock status if node is locked
    unlock_service = UnlockService(db)
    if not progress or progress.status == NodeStatus.LOCKED:
        can_unlock, reason = await unlock_service.check_unlock_condition(node, current_user.id)
        if can_unlock:
            # Auto-unlock if conditions are met
            await unlock_service.unlock_node(current_user.id, node.id)
            # Refresh progress
            await db.refresh(progress) if progress else None
            if not progress:
                progress_result = await db.execute(
                    select(LearningProgress).where(
                        LearningProgress.user_id == current_user.id,
                        LearningProgress.node_id == node.id
                    )
                )
                progress = progress_result.scalar_one_or_none()

    # Build response
    node_data = CourseNodeWithProgress(
        id=node.id,
        course_id=node.course_id,
        node_id=node.node_id,
        type=node.type,
        component_id=node.component_id,
        title=node.title,
        description=node.description,
        timeline_config=node.timeline_config,
        sequence=node.sequence,
        parent_id=node.parent_id,
        unlock_condition=node.unlock_condition or {},
        created_at=node.created_at,
        status=progress.status if progress else NodeStatus.LOCKED,
        completion_percentage=progress.completion_percentage if progress else 0.0,
        time_spent_seconds=progress.time_spent_seconds if progress else 0
    )

    return node_data


@router.post("/{node_id}/complete")
async def complete_node(
    node_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark node as completed

    Triggers:
    - Update node status to 'completed'
    - Unlock next nodes (check prerequisites)
    - Update user statistics
    - Potentially unlock achievements

    Supports both string node_id and numeric database id
    """
    # Try to get node by string node_id first, then by numeric id
    result = await db.execute(
        select(CourseNode).where(CourseNode.node_id == node_id)
    )
    node = result.scalar_one_or_none()

    # If not found by node_id, try by numeric id
    if not node:
        try:
            numeric_id = int(node_id)
            result = await db.execute(
                select(CourseNode).where(CourseNode.id == numeric_id)
            )
            node = result.scalar_one_or_none()
        except ValueError:
            pass

    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node '{node_id}' not found"
        )

    # Use UnlockService to complete node and unlock dependent nodes
    unlock_service = UnlockService(db)
    newly_unlocked_ids = await unlock_service.complete_node(current_user.id, node.id)

    # Get details of newly unlocked nodes
    unlocked_nodes = []
    if newly_unlocked_ids:
        result = await db.execute(
            select(CourseNode).where(CourseNode.id.in_(newly_unlocked_ids))
        )
        unlocked_nodes = [
            {"node_id": n.node_id, "title": n.title, "type": n.type.value}
            for n in result.scalars().all()
        ]

    # Check and unlock achievements
    from app.api.v1.endpoints.achievements import check_and_unlock_achievements
    newly_unlocked_achievements = await check_and_unlock_achievements(current_user.id, db)

    return {
        "message": "Node completed successfully",
        "node_id": node_id,
        "unlocked_nodes": unlocked_nodes,
        "newly_unlocked_achievements": newly_unlocked_achievements
    }


@router.put("/{node_id}/progress")
async def update_node_progress(
    node_id: str,
    progress_update: ProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update node progress (for partial completion tracking)

    Use cases:
    - Video watch progress
    - Quiz partial completion
    - Simulator interaction time
    - Step-by-step reading progress

    Supports both string node_id and numeric database id
    """
    # Try to get node by string node_id first, then by numeric id
    result = await db.execute(
        select(CourseNode).where(CourseNode.node_id == node_id)
    )
    node = result.scalar_one_or_none()

    # If not found by node_id, try by numeric id
    if not node:
        try:
            numeric_id = int(node_id)
            result = await db.execute(
                select(CourseNode).where(CourseNode.id == numeric_id)
            )
            node = result.scalar_one_or_none()
        except ValueError:
            pass

    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node '{node_id}' not found"
        )

    # Get or create progress record
    progress_result = await db.execute(
        select(LearningProgress).where(
            LearningProgress.user_id == current_user.id,
            LearningProgress.node_id == node.id
        )
    )
    progress = progress_result.scalar_one_or_none()

    if not progress:
        progress = LearningProgress(
            user_id=current_user.id,
            node_id=node.id
        )
        db.add(progress)

    # Check if node is already completed - lock progress at 100%
    is_completed = progress.status == NodeStatus.COMPLETED

    # Update fields (but respect completion lock)
    if progress_update.status is not None:
        # Don't allow changing status away from COMPLETED
        if not is_completed:
            progress.status = progress_update.status

    if progress_update.completion_percentage is not None:
        # Don't allow changing completion percentage if already completed
        if not is_completed:
            progress.completion_percentage = progress_update.completion_percentage

    # Track time delta for user total update
    # Time can always be updated even for completed nodes
    time_delta = 0
    if progress_update.time_spent_seconds is not None:
        old_time = progress.time_spent_seconds or 0
        time_delta = progress_update.time_spent_seconds - old_time
        progress.time_spent_seconds = progress_update.time_spent_seconds

    # Update last_accessed timestamp
    progress.last_accessed = datetime.now(timezone.utc)

    # If status changed to IN_PROGRESS, mark as such
    if progress_update.status == NodeStatus.IN_PROGRESS and progress.status == NodeStatus.UNLOCKED:
        progress.status = NodeStatus.IN_PROGRESS

    # Update user's cumulative usage time if time increased
    # Note: Skipping as total_usage_seconds field may not exist in User model
    # if time_delta > 0:
    #     await db.execute(
    #         update(User)
    #         .where(User.id == current_user.id)
    #         .values(total_usage_seconds=User.total_usage_seconds + time_delta)
    #     )

    await db.commit()
    await db.refresh(progress)

    return {
        "message": "Progress updated successfully",
        "node_id": node_id,
        "status": progress.status,
        "completion_percentage": progress.completion_percentage
    }


@router.get("/course/{course_id}/map")
async def get_course_map(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get complete course node map with progress

    Used by the left sidebar "Cognitive Map" to display:
    - All nodes in order
    - Each node's status (locked/unlocked/in_progress/completed)
    - Prerequisites relationships
    """
    # Use UnlockService to get complete progress map
    unlock_service = UnlockService(db)
    progress_map = await unlock_service.get_course_progress_map(current_user.id, course_id)

    # Get all nodes for this course
    result = await db.execute(
        select(CourseNode)
        .where(CourseNode.course_id == course_id)
        .order_by(CourseNode.sequence)
    )
    nodes = result.scalars().all()

    # Build hierarchical map
    node_map = []
    for node in nodes:
        progress_info = progress_map.get(node.id, {})
        node_map.append({
            "id": node.id,
            "node_id": node.node_id,
            "title": node.title,
            "description": node.description,
            "type": node.type.value,
            "sequence": node.sequence,
            "parent_id": node.parent_id,
            "status": progress_info.get("status", NodeStatus.LOCKED.value),
            "completion_percentage": progress_info.get("completion_percentage", 0.0),
            "unlock_condition": node.unlock_condition or {},
            "content": node.content,  # Include lesson content
            "config": node.config,    # Include node config
        })

    return {
        "course_id": course_id,
        "total_nodes": len(nodes),
        "nodes": node_map
    }
