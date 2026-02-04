"""
File Upload Endpoints
Handles file uploads for videos, images, documents, and avatars
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import os

from app.db.session import get_db
from app.core.security import get_current_user, require_admin
from app.models.models import User
from app.services.storage_service import storage_service

router = APIRouter()


def validate_upload(file: UploadFile, content: bytes, file_type: str) -> None:
    """
    验证上传文件是否符合系统设置

    Args:
        file: 上传的文件
        content: 文件内容
        file_type: 文件类型 ('image', 'video', 'document')

    Raises:
        HTTPException: 如果验证失败
    """
    from app.core.system_settings import get_storage_settings
    storage_settings = get_storage_settings()

    # 检查文件大小
    max_size_bytes = storage_settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文件过大，最大允许 {storage_settings.max_upload_size_mb}MB"
        )

    # 获取文件扩展名
    filename = file.filename or ""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    # 根据文件类型检查扩展名
    allowed_types: List[str] = []
    if file_type == "image":
        allowed_types = storage_settings.allowed_image_types
    elif file_type == "video":
        allowed_types = storage_settings.allowed_video_types
    elif file_type == "document":
        allowed_types = storage_settings.allowed_document_types

    if ext and allowed_types and ext not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型 .{ext}，允许的类型: {', '.join(allowed_types)}"
        )


# ============ File Upload Endpoints ============

@router.post("/video")
async def upload_video(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload video file (Admin only)

    Accepts video files and stores them for course content
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a video"
        )

    # Read content for validation
    content = await file.read()
    await file.seek(0)  # Reset file pointer

    # 使用系统设置验证上传
    validate_upload(file, content, "video")

    # Save video
    try:
        file_info = await storage_service.save_file(
            file,
            category="videos",
            prefix="video"
        )

        return {
            "message": "Video uploaded successfully",
            "file_url": file_info["file_url"],
            "filename": file_info["filename"],
            "file_size": file_info["file_size"],
            "mime_type": file_info["mime_type"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload video: {str(e)}"
        )


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    category: str = Form("images"),
    max_width: int = Form(1920),
    max_height: int = Form(1080),
    quality: int = Form(85),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload and optimize image (Admin only)

    Accepts image files, optimizes them, and stores for course content
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )

    # Read content for validation
    content = await file.read()
    await file.seek(0)

    # 使用系统设置验证上传
    validate_upload(file, content, "image")

    # Validate category
    valid_categories = ["images", "thumbnails"]
    if category not in valid_categories:
        category = "images"

    # Validate quality
    if quality < 1 or quality > 100:
        quality = 85

    # Save and optimize image
    try:
        file_info = await storage_service.save_image(
            file,
            max_size=(max_width, max_height),
            quality=quality,
            category=category
        )

        return {
            "message": "Image uploaded successfully",
            "file_url": file_info["file_url"],
            "filename": file_info["filename"],
            "file_size": file_info["file_size"],
            "width": file_info["width"],
            "height": file_info["height"],
            "mime_type": file_info["mime_type"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}"
        )


@router.post("/document")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload document file (Admin only)

    Accepts PDF, Word, Excel, and other document files
    """
    # Read content for validation
    content = await file.read()
    await file.seek(0)

    # 使用系统设置验证上传
    validate_upload(file, content, "document")

    # Save document
    try:
        file_info = await storage_service.save_file(
            file,
            category="documents",
            prefix="doc"
        )

        return {
            "message": "Document uploaded successfully",
            "file_url": file_info["file_url"],
            "filename": file_info["filename"],
            "file_size": file_info["file_size"],
            "mime_type": file_info["mime_type"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload user avatar

    Accepts image files, crops to square, and optimizes for avatar use
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )

    # Read content for validation
    content = await file.read()
    await file.seek(0)

    # 使用系统设置验证上传（头像使用图片类型限制）
    validate_upload(file, content, "image")

    # Save avatar
    try:
        file_info = await storage_service.save_avatar(file, current_user.id)

        # Update user's avatar_url in database
        current_user.avatar_url = file_info["file_url"]
        await db.commit()

        return {
            "message": "Avatar uploaded successfully",
            "avatar_url": file_info["file_url"],
            "filename": file_info["filename"],
            "file_size": file_info["file_size"]
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload avatar: {str(e)}"
        )


@router.post("/thumbnail")
async def create_thumbnail(
    source_url: str = Form(...),
    width: int = Form(400),
    height: int = Form(300),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Create thumbnail from existing image (Admin only)

    Generates a thumbnail from an uploaded image
    """
    # Parse source URL to get file path
    # Expected format: /media/images/filename.jpg
    if not source_url.startswith("/media/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid source URL"
        )

    # Extract category and filename
    parts = source_url.split("/")
    if len(parts) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid source URL format"
        )

    category = parts[2]
    filename = parts[3]

    # Get file path
    file_path = storage_service.get_file_path(category, filename)
    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source image not found"
        )

    # Create thumbnail
    try:
        thumbnail_info = await storage_service.create_thumbnail(
            str(file_path),
            size=(width, height)
        )

        return {
            "message": "Thumbnail created successfully",
            "thumbnail_url": thumbnail_info["file_url"],
            "filename": thumbnail_info["filename"],
            "file_size": thumbnail_info["file_size"],
            "width": thumbnail_info["width"],
            "height": thumbnail_info["height"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create thumbnail: {str(e)}"
        )


# ============ File Serving Endpoints ============

@router.get("/media/{category}/{filename}")
async def serve_media_file(
    category: str,
    filename: str
):
    """
    Serve media files

    Returns the requested media file
    """
    # Get file path
    file_path = storage_service.get_file_path(category, filename)

    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    # Determine media type
    mime_type = None
    if category == "videos":
        mime_type = "video/mp4"
    elif category in ["images", "avatars", "thumbnails", "diagrams"]:
        mime_type = "image/jpeg"
    elif category == "documents":
        import mimetypes
        mime_type = mimetypes.guess_type(str(file_path))[0]

    return FileResponse(
        path=str(file_path),
        media_type=mime_type,
        filename=filename
    )


@router.delete("/media/{category}/{filename}")
async def delete_media_file(
    category: str,
    filename: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete media file (Admin only)

    Removes the specified media file from storage
    """
    # Get file path
    file_path = storage_service.get_file_path(category, filename)

    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    # Delete file
    success = storage_service.delete_file(str(file_path))

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file"
        )

    return {
        "message": "File deleted successfully",
        "filename": filename
    }


@router.get("/media/{category}/{filename}/info")
async def get_media_file_info(
    category: str,
    filename: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get media file information

    Returns metadata about the specified media file
    """
    # Get file path
    file_path = storage_service.get_file_path(category, filename)

    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    # Get file info
    file_info = storage_service.get_file_info(str(file_path))

    if not file_info:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get file information"
        )

    return file_info
