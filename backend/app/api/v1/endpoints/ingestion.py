"""
Course Ingestion API Endpoints
Internal API for uploading and managing course packages
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.services.ingestion import CourseIngestionService
from app.schemas.schemas import (
    CourseManifest,
    CoursePackageUpload,
    CourseIngestionResponse,
    CoursePackageValidation,
    CourseUpdate,
    NodeUpdate,
    PackageNodeConfig
)

router = APIRouter()


@router.post("/validate", response_model=CoursePackageValidation)
async def validate_course_package(
    manifest: CourseManifest,
    db: AsyncSession = Depends(get_db)
):
    """
    Validate a course package without ingesting it

    This endpoint checks if the course manifest is valid and can be ingested.
    Use this before uploading to catch errors early.

    Args:
        manifest: Course manifest to validate

    Returns:
        Validation result with errors and warnings
    """
    service = CourseIngestionService(db)
    validation = await service.validate_package(manifest)
    return validation


@router.post("/ingest", response_model=CourseIngestionResponse)
async def ingest_course_package(
    package: CoursePackageUpload,
    db: AsyncSession = Depends(get_db)
):
    """
    Ingest a course package into the system

    This is the main endpoint for uploading course packages.
    The package will be validated, and if valid, all course data
    will be written to the database.

    Args:
        package: Course package with manifest and options

    Returns:
        Ingestion result with course ID and status

    Example:
        ```json
        {
          "manifest": {
            "courseName": "运动生物力学基础",
            "difficulty": "beginner",
            "nodes": [...]
          },
          "publishImmediately": false
        }
        ```
    """
    service = CourseIngestionService(db)

    # Validate first
    validation = await service.validate_package(package.manifest)
    if not validation.isValid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Package validation failed",
                "errors": validation.errors,
                "warnings": validation.warnings
            }
        )

    # Ingest
    result = await service.ingest_course(
        package.manifest,
        package.publishImmediately
    )

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": result.message,
                "errors": result.errors
            }
        )

    return result


@router.post("/ingest-simple", response_model=CourseIngestionResponse)
async def ingest_course_simple(
    manifest: CourseManifest,
    db: AsyncSession = Depends(get_db)
):
    """
    Simplified ingestion endpoint (just manifest, no options)

    Args:
        manifest: Course manifest

    Returns:
        Ingestion result
    """
    package = CoursePackageUpload(
        manifest=manifest,
        publishImmediately=False
    )

    service = CourseIngestionService(db)
    result = await service.ingest_course(manifest, False)

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": result.message,
                "errors": result.errors
            }
        )

    return result


@router.delete("/course/{course_id}")
async def delete_course(
    course_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a course and all its nodes

    ⚠️ Warning: This is a destructive operation and cannot be undone.

    Args:
        course_id: ID of the course to delete

    Returns:
        Success message
    """
    service = CourseIngestionService(db)

    try:
        success = await service.delete_course(course_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course {course_id} not found"
            )

        return {
            "success": True,
            "message": f"Course {course_id} deleted successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete course: {str(e)}"
        )


@router.get("/course/{course_name}/exists")
async def check_course_exists(
    course_name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Check if a course with the given name already exists

    Args:
        course_name: Name of the course to check

    Returns:
        Existence status and course ID if found
    """
    service = CourseIngestionService(db)
    course = await service.get_course_by_name(course_name)

    if course:
        return {
            "exists": True,
            "courseId": course.id,
            "courseName": course.name,
            "isPublished": bool(course.is_published)
        }
    else:
        return {
            "exists": False,
            "courseId": None,
            "courseName": course_name,
            "isPublished": False
        }


# ============ Course Update Endpoints ============

@router.get("/course/{course_id}")
async def get_course(
    course_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get course details by ID

    Args:
        course_id: ID of the course

    Returns:
        Course details with all nodes
    """
    service = CourseIngestionService(db)
    course = await service.get_course_by_id(course_id)

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course {course_id} not found"
        )

    # Get all nodes for this course
    from sqlalchemy import select
    from app.models.models import CourseNode
    result = await db.execute(
        select(CourseNode)
        .where(CourseNode.course_id == course_id)
        .order_by(CourseNode.sequence)
    )
    nodes = result.scalars().all()

    return {
        "id": course.id,
        "name": course.name,
        "description": course.description,
        "difficulty": course.difficulty.value,
        "instructor": course.instructor,
        "tags": course.tags,
        "durationHours": course.duration_hours,
        "thumbnailUrl": course.thumbnail_url,
        "isPublished": course.is_published,
        "createdAt": course.created_at.isoformat() if course.created_at else None,
        "nodeCount": len(nodes),
        "nodes": [
            {
                "id": node.id,
                "nodeId": node.node_id,
                "type": node.type.value,
                "componentId": node.component_id,
                "title": node.title,
                "description": node.description,
                "sequence": node.sequence,
                "parentId": node.parent_id,
                "timelineConfig": node.timeline_config,
                "unlockCondition": node.unlock_condition,
                "content": node.content,
                "config": node.config
            }
            for node in nodes
        ]
    }


@router.put("/course/{course_id}")
async def update_course(
    course_id: int,
    update_data: CourseUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update course metadata

    Args:
        course_id: ID of the course to update
        update_data: Fields to update

    Returns:
        Updated course details
    """
    service = CourseIngestionService(db)
    course = await service.update_course(course_id, update_data)

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course {course_id} not found"
        )

    return {
        "success": True,
        "message": f"Course {course_id} updated successfully",
        "course": {
            "id": course.id,
            "name": course.name,
            "description": course.description,
            "difficulty": course.difficulty.value,
            "instructor": course.instructor,
            "tags": course.tags,
            "durationHours": course.duration_hours,
            "thumbnailUrl": course.thumbnail_url,
            "isPublished": course.is_published
        }
    }


@router.patch("/course/{course_id}/publish")
async def publish_course(
    course_id: int,
    publish: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """
    Publish or unpublish a course

    Args:
        course_id: ID of the course
        publish: True to publish, False to unpublish

    Returns:
        Success message
    """
    service = CourseIngestionService(db)
    update_data = CourseUpdate(isPublished=publish)
    course = await service.update_course(course_id, update_data)

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course {course_id} not found"
        )

    action = "published" if publish else "unpublished"
    return {
        "success": True,
        "message": f"Course {course_id} {action} successfully",
        "isPublished": course.is_published
    }


# ============ Node Update Endpoints ============

@router.get("/node/{node_id}")
async def get_node(
    node_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get node details by node_id

    Args:
        node_id: Node ID string

    Returns:
        Node details
    """
    service = CourseIngestionService(db)
    node = await service.get_node_by_node_id(node_id)

    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node '{node_id}' not found"
        )

    return {
        "id": node.id,
        "nodeId": node.node_id,
        "courseId": node.course_id,
        "type": node.type.value,
        "componentId": node.component_id,
        "title": node.title,
        "description": node.description,
        "sequence": node.sequence,
        "parentId": node.parent_id,
        "timelineConfig": node.timeline_config,
        "unlockCondition": node.unlock_condition,
        "createdAt": node.created_at.isoformat() if node.created_at else None
    }


@router.put("/node/{node_id}")
async def update_node(
    node_id: str,
    update_data: NodeUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a course node

    Args:
        node_id: Node ID string
        update_data: Fields to update

    Returns:
        Updated node details
    """
    service = CourseIngestionService(db)
    node = await service.update_node(node_id, update_data)

    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node '{node_id}' not found"
        )

    return {
        "success": True,
        "message": f"Node '{node_id}' updated successfully",
        "node": {
            "id": node.id,
            "nodeId": node.node_id,
            "courseId": node.course_id,
            "type": node.type.value,
            "componentId": node.component_id,
            "title": node.title,
            "description": node.description,
            "sequence": node.sequence,
            "parentId": node.parent_id,
            "timelineConfig": node.timeline_config,
            "unlockCondition": node.unlock_condition
        }
    }


@router.delete("/node/{node_id}")
async def delete_node(
    node_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a course node

    ⚠️ Warning: This will set children's parent_id to None

    Args:
        node_id: Node ID string

    Returns:
        Success message
    """
    service = CourseIngestionService(db)
    success = await service.delete_node(node_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node '{node_id}' not found"
        )

    return {
        "success": True,
        "message": f"Node '{node_id}' deleted successfully"
    }


@router.post("/course/{course_id}/node")
async def add_node_to_course(
    course_id: int,
    node_config: PackageNodeConfig,
    db: AsyncSession = Depends(get_db)
):
    """
    Add a new node to an existing course

    Args:
        course_id: ID of the course
        node_config: Node configuration

    Returns:
        Created node details
    """
    service = CourseIngestionService(db)

    try:
        node = await service.add_node_to_course(course_id, node_config)

        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course {course_id} not found"
            )

        return {
            "success": True,
            "message": f"Node '{node_config.nodeId}' added to course {course_id}",
            "node": {
                "id": node.id,
                "nodeId": node.node_id,
                "courseId": node.course_id,
                "type": node.type.value,
                "componentId": node.component_id,
                "title": node.title,
                "description": node.description,
                "sequence": node.sequence,
                "parentId": node.parent_id,
                "timelineConfig": node.timeline_config,
                "unlockCondition": node.unlock_condition
            }
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add node: {str(e)}"
        )

