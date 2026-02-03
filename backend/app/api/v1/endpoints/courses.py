from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime, timezone
import json

from app.db.session import get_db
from app.models.models import Course, CourseNode, LearningProgress, DifficultyLevel, User, NodeStatus
from app.schemas.schemas import CourseResponse, CourseDetail
from app.core.security import get_current_user


def parse_tags(tags_value) -> list:
    """Parse tags from database - handles both list and JSON string formats"""
    if tags_value is None:
        return []
    if isinstance(tags_value, list):
        return tags_value
    if isinstance(tags_value, str):
        try:
            parsed = json.loads(tags_value)
            return parsed if isinstance(parsed, list) else []
        except (json.JSONDecodeError, TypeError):
            return []
    return []


router = APIRouter()


@router.get("", response_model=List[CourseResponse])
async def get_courses(
    difficulty: Optional[DifficultyLevel] = None,
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    search: Optional[str] = None,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=1000, description="Maximum number of records"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of courses with filtering

    Filters:
    - difficulty: Filter by difficulty level
    - tags: Filter by tags (comma-separated, e.g., "biomechanics,strength")
    - search: Search in course name and description
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return
    """
    query = select(Course).where(Course.is_published == 1)

    # Apply difficulty filter
    if difficulty:
        query = query.where(Course.difficulty == difficulty)

    # Apply search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (Course.name.ilike(search_pattern)) |
            (Course.description.ilike(search_pattern))
        )

    # Apply tag filter
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        if tag_list:
            # Filter courses that have ANY of the specified tags
            # Using JSON contains for PostgreSQL
            from sqlalchemy import or_, cast, String
            tag_conditions = []
            for tag in tag_list:
                # Check if tag exists in the tags JSON array
                tag_conditions.append(
                    cast(Course.tags, String).ilike(f'%"{tag}"%')
                )
            if tag_conditions:
                query = query.where(or_(*tag_conditions))

    # Apply pagination
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    courses = result.scalars().all()

    return courses


@router.get("/count/total")
async def get_courses_count(
    difficulty: Optional[DifficultyLevel] = None,
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get total count of courses matching filters

    Useful for pagination calculations
    """
    query = select(func.count(Course.id)).where(Course.is_published == 1)

    # Apply same filters as get_courses
    if difficulty:
        query = query.where(Course.difficulty == difficulty)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (Course.name.ilike(search_pattern)) |
            (Course.description.ilike(search_pattern))
        )

    if tags:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        if tag_list:
            from sqlalchemy import or_, cast, String
            tag_conditions = []
            for tag in tag_list:
                tag_conditions.append(
                    cast(Course.tags, String).ilike(f'%"{tag}"%')
                )
            if tag_conditions:
                query = query.where(or_(*tag_conditions))

    total = await db.scalar(query) or 0

    return {
        "total": total,
        "filters": {
            "difficulty": difficulty.value if difficulty else None,
            "tags": tags,
            "search": search
        }
    }


@router.get("/enrolled", response_model=List[CourseResponse])
async def get_enrolled_courses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's enrolled courses with progress information

    Returns:
    - List of courses the user is enrolled in
    - Each course includes progress percentage
    """
    from app.models.models import UserCourse

    # Get user's enrolled course IDs
    enrolled_query = select(UserCourse.course_id).where(
        UserCourse.user_id == current_user.id
    )
    enrolled_result = await db.execute(enrolled_query)
    enrolled_course_ids = [row[0] for row in enrolled_result.all()]

    if not enrolled_course_ids:
        return []

    # Get courses with progress
    courses_query = select(Course).where(
        Course.id.in_(enrolled_course_ids)
    )
    courses_result = await db.execute(courses_query)
    courses = courses_result.scalars().all()

    # Calculate progress for each course
    result_courses = []
    for course in courses:
        # Get total nodes count
        total_nodes_query = select(func.count(CourseNode.id)).where(
            CourseNode.course_id == course.id
        )
        total_nodes = await db.scalar(total_nodes_query) or 0

        # Calculate progress based on completion_percentage of each node
        # This gives a more accurate progress that includes partial completion
        if total_nodes > 0:
            # Get sum of completion percentages for all nodes in this course
            progress_sum_query = select(func.sum(LearningProgress.completion_percentage)).where(
                LearningProgress.user_id == current_user.id,
                LearningProgress.node_id.in_(
                    select(CourseNode.id).where(CourseNode.course_id == course.id)
                )
            )
            total_completion = await db.scalar(progress_sum_query) or 0
            # Average completion across all nodes
            progress_percentage = total_completion / total_nodes
        else:
            progress_percentage = 0

        # Create response with progress
        result_courses.append(CourseResponse(
            id=course.id,
            name=course.name,
            description=course.description,
            difficulty=course.difficulty,
            tags=course.tags or [],
            instructor=course.instructor,
            duration_hours=course.duration_hours,
            thumbnail_url=course.thumbnail_url,
            is_published=bool(course.is_published),
            created_at=course.created_at,
            node_count=total_nodes,
            progress_percentage=round(progress_percentage, 2)
        ))

    return result_courses


@router.get("/recommendations", response_model=List[CourseResponse])
async def get_recommendations(
    current_user: User = Depends(get_current_user),
    limit: int = 5,
    db: AsyncSession = Depends(get_db)
):
    """
    Get recommended courses for user

    Recommendation algorithm based on:
    1. User's completed courses (avoid recommending completed courses)
    2. User's skill level (based on completion rate and time spent)
    3. Course difficulty progression (recommend next difficulty level)
    4. Popular courses (enrollment count)
    5. Course tags similarity
    """
    from app.models.models import UserCourse
    from sqlalchemy import func, case, and_

    # Get user's enrolled and completed courses
    enrolled_courses_query = select(UserCourse.course_id).where(
        UserCourse.user_id == current_user.id
    )
    enrolled_result = await db.execute(enrolled_courses_query)
    enrolled_course_ids = [row[0] for row in enrolled_result.all()]

    # Calculate user's average completion rate to determine skill level
    if enrolled_course_ids:
        # Get completion stats for enrolled courses
        completion_stats_query = select(
            Course.difficulty,
            func.count(LearningProgress.id).label("total_nodes"),
            func.sum(
                case((LearningProgress.status == NodeStatus.COMPLETED, 1), else_=0)
            ).label("completed_nodes")
        ).select_from(Course).join(
            CourseNode, Course.id == CourseNode.course_id
        ).join(
            LearningProgress, CourseNode.id == LearningProgress.node_id
        ).where(
            and_(
                LearningProgress.user_id == current_user.id,
                Course.id.in_(enrolled_course_ids)
            )
        ).group_by(Course.difficulty)

        completion_result = await db.execute(completion_stats_query)
        completion_data = completion_result.all()

        # Determine user's skill level based on completion
        user_skill_level = DifficultyLevel.BEGINNER
        if completion_data:
            # Calculate overall completion rate
            total_nodes = sum(row.total_nodes for row in completion_data)
            completed_nodes = sum(row.completed_nodes or 0 for row in completion_data)
            completion_rate = (completed_nodes / total_nodes * 100) if total_nodes > 0 else 0

            # Determine skill level
            if completion_rate >= 75:
                # Check highest difficulty completed
                for row in completion_data:
                    if row.completed_nodes and row.completed_nodes > 0:
                        if row.difficulty == DifficultyLevel.ADVANCED:
                            user_skill_level = DifficultyLevel.EXPERT
                        elif row.difficulty == DifficultyLevel.INTERMEDIATE:
                            user_skill_level = DifficultyLevel.ADVANCED
                        elif row.difficulty == DifficultyLevel.BEGINNER:
                            user_skill_level = DifficultyLevel.INTERMEDIATE
            elif completion_rate >= 50:
                user_skill_level = DifficultyLevel.INTERMEDIATE
    else:
        user_skill_level = DifficultyLevel.BEGINNER

    # Build recommendation query
    # Exclude already enrolled courses
    from sqlalchemy import and_
    base_query = select(
        Course,
        func.count(UserCourse.id).label("enrollment_count")
    ).outerjoin(
        UserCourse, Course.id == UserCourse.course_id
    ).where(
        and_(
            Course.is_published == 1,
            ~Course.id.in_(enrolled_course_ids) if enrolled_course_ids else True
        )
    ).group_by(Course.id)

    # Get courses matching user's skill level and one level above
    recommended_difficulties = [user_skill_level]
    if user_skill_level == DifficultyLevel.BEGINNER:
        recommended_difficulties.append(DifficultyLevel.INTERMEDIATE)
    elif user_skill_level == DifficultyLevel.INTERMEDIATE:
        recommended_difficulties.append(DifficultyLevel.ADVANCED)
    elif user_skill_level == DifficultyLevel.ADVANCED:
        recommended_difficulties.append(DifficultyLevel.EXPERT)

    query = base_query.where(
        Course.difficulty.in_(recommended_difficulties)
    ).order_by(
        # Prioritize courses at user's level
        case(
            (Course.difficulty == user_skill_level, 0),
            else_=1
        ),
        # Then by popularity
        func.count(UserCourse.id).desc(),
        # Then by creation date (newer first)
        Course.created_at.desc()
    ).limit(limit)

    result = await db.execute(query)
    courses = [row[0] for row in result.all()]

    # If not enough courses found, fill with popular courses
    if len(courses) < limit:
        remaining = limit - len(courses)
        excluded_ids = enrolled_course_ids + [c.id for c in courses]

        fallback_query = select(
            Course,
            func.count(UserCourse.id).label("enrollment_count")
        ).outerjoin(
            UserCourse, Course.id == UserCourse.course_id
        ).where(
            and_(
                Course.is_published == 1,
                ~Course.id.in_(excluded_ids) if excluded_ids else True
            )
        ).group_by(Course.id).order_by(
            func.count(UserCourse.id).desc()
        ).limit(remaining)

        fallback_result = await db.execute(fallback_query)
        fallback_courses = [row[0] for row in fallback_result.all()]
        courses.extend(fallback_courses)

    return courses


@router.get("/{course_id}", response_model=CourseDetail)
async def get_course_detail(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed course information including user progress

    Returns:
    - Course metadata
    - Total nodes count
    - Completed nodes count
    - Progress percentage
    """
    # Get course
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Get total nodes count
    nodes_count_query = select(func.count(CourseNode.id)).where(
        CourseNode.course_id == course_id
    )
    total_nodes = await db.scalar(nodes_count_query)

    # Get completed nodes count
    completed_query = select(func.count(LearningProgress.id)).where(
        LearningProgress.user_id == current_user.id,
        LearningProgress.node_id.in_(
            select(CourseNode.id).where(CourseNode.course_id == course_id)
        ),
        LearningProgress.status == "completed"
    )
    completed_nodes = await db.scalar(completed_query) or 0

    # Calculate progress
    progress_percentage = (completed_nodes / total_nodes * 100) if total_nodes > 0 else 0

    return CourseDetail(
        id=course.id,
        name=course.name,
        description=course.description,
        difficulty=course.difficulty,
        tags=parse_tags(course.tags),
        instructor=course.instructor,
        duration_hours=course.duration_hours,
        thumbnail_url=course.thumbnail_url,
        is_published=bool(course.is_published),
        created_at=course.created_at,
        total_nodes=total_nodes or 0,
        completed_nodes=completed_nodes,
        progress_percentage=round(progress_percentage, 2)
    )


@router.post("/{course_id}/enroll")
async def enroll_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Enroll user in a course

    Creates initial progress records for all course nodes
    """
    # Check if course exists and is published
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    if not course.is_published:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course is not published yet"
        )

    # Check if user is already enrolled
    from app.models.models import UserCourse
    existing_enrollment = await db.execute(
        select(UserCourse).where(
            UserCourse.user_id == current_user.id,
            UserCourse.course_id == course_id
        )
    )
    if existing_enrollment.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already enrolled in this course"
        )

    # Get all course nodes
    nodes_result = await db.execute(
        select(CourseNode).where(CourseNode.course_id == course_id).order_by(CourseNode.sequence)
    )
    nodes = nodes_result.scalars().all()

    if not nodes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course has no nodes"
        )

    # Create UserCourse enrollment record
    user_course = UserCourse(
        user_id=current_user.id,
        course_id=course_id,
        enrolled_at=datetime.now(timezone.utc),
        last_accessed=datetime.now(timezone.utc)
    )
    db.add(user_course)

    # Create progress records for each node
    # First node is unlocked, rest are locked
    created_count = 0
    for idx, node in enumerate(nodes):
        # Check if progress already exists (shouldn't happen, but be safe)
        existing_progress = await db.execute(
            select(LearningProgress).where(
                LearningProgress.user_id == current_user.id,
                LearningProgress.node_id == node.id
            )
        )
        if existing_progress.scalar_one_or_none():
            continue

        # First node (sequence 0 or first in list) is unlocked
        initial_status = NodeStatus.UNLOCKED if idx == 0 else NodeStatus.LOCKED

        progress = LearningProgress(
            user_id=current_user.id,
            node_id=node.id,
            status=initial_status,
            completion_percentage=0.0,
            time_spent_seconds=0,
            last_accessed=datetime.now(timezone.utc) if idx == 0 else None
        )
        db.add(progress)
        created_count += 1

    await db.commit()

    return {
        "message": "Successfully enrolled in course",
        "course_id": course_id,
        "course_name": course.name,
        "total_nodes": len(nodes),
        "progress_records_created": created_count
    }


@router.delete("/{course_id}/enroll")
async def unenroll_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Unenroll user from a course

    Removes enrollment record and optionally clears progress
    """
    from app.models.models import UserCourse

    # Check if user is enrolled
    enrollment_result = await db.execute(
        select(UserCourse).where(
            UserCourse.user_id == current_user.id,
            UserCourse.course_id == course_id
        )
    )
    enrollment = enrollment_result.scalar_one_or_none()

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enrolled in this course"
        )

    # Delete enrollment record
    await db.delete(enrollment)
    await db.commit()

    return {
        "message": "Successfully unenrolled from course",
        "course_id": course_id
    }


@router.get("/{course_id}/progress")
async def get_course_progress(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's progress for a specific course

    Returns:
    - Total nodes count
    - Completed nodes count
    - In-progress nodes count
    - Completion percentage
    - Last accessed timestamp
    """
    # Check if course exists
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Get total nodes
    total_nodes_query = select(func.count(CourseNode.id)).where(
        CourseNode.course_id == course_id
    )
    total_nodes = await db.scalar(total_nodes_query) or 0

    # Get completed nodes
    completed_query = select(func.count(LearningProgress.id)).where(
        LearningProgress.user_id == current_user.id,
        LearningProgress.node_id.in_(
            select(CourseNode.id).where(CourseNode.course_id == course_id)
        ),
        LearningProgress.status == NodeStatus.COMPLETED
    )
    completed_nodes = await db.scalar(completed_query) or 0

    # Get in-progress nodes
    in_progress_query = select(func.count(LearningProgress.id)).where(
        LearningProgress.user_id == current_user.id,
        LearningProgress.node_id.in_(
            select(CourseNode.id).where(CourseNode.course_id == course_id)
        ),
        LearningProgress.status == NodeStatus.IN_PROGRESS
    )
    in_progress_nodes = await db.scalar(in_progress_query) or 0

    # Get last accessed
    last_accessed_query = select(func.max(LearningProgress.last_accessed)).where(
        LearningProgress.user_id == current_user.id,
        LearningProgress.node_id.in_(
            select(CourseNode.id).where(CourseNode.course_id == course_id)
        )
    )
    last_accessed = await db.scalar(last_accessed_query)

    # Get enrollment date
    from app.models.models import UserCourse
    enrollment_query = select(UserCourse.enrolled_at).where(
        UserCourse.user_id == current_user.id,
        UserCourse.course_id == course_id
    )
    enrolled_at = await db.scalar(enrollment_query)

    # Calculate progress percentage
    progress_percentage = (completed_nodes / total_nodes * 100) if total_nodes > 0 else 0

    return {
        "course_id": course_id,
        "user_id": current_user.id,
        "total_nodes": total_nodes,
        "completed_nodes": completed_nodes,
        "in_progress_nodes": in_progress_nodes,
        "completion_percentage": round(progress_percentage, 2),
        "last_accessed": last_accessed.isoformat() if last_accessed else None,
        "enrolled_at": enrolled_at.isoformat() if enrolled_at else None
    }
