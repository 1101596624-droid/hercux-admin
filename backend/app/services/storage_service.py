"""
File Storage Service
Handles file uploads, storage, and retrieval
Supports both local storage and S3-compatible storage
"""
import os
import uuid
import hashlib
from pathlib import Path
from typing import Optional, BinaryIO, Tuple
from datetime import datetime, timezone
import mimetypes
import shutil

from fastapi import UploadFile
from PIL import Image
import io


class StorageService:
    """Service for managing file storage"""

    def __init__(self, storage_type: str = "local", base_path: str = "./uploads"):
        """
        Initialize storage service

        Args:
            storage_type: "local" or "s3"
            base_path: Base directory for local storage
        """
        self.storage_type = storage_type
        self.base_path = Path(base_path)

        # Create storage directories
        self.directories = {
            "videos": self.base_path / "videos",
            "images": self.base_path / "images",
            "documents": self.base_path / "documents",
            "avatars": self.base_path / "avatars",
            "thumbnails": self.base_path / "thumbnails",
            "diagrams": self.base_path / "diagrams",
        }

        for directory in self.directories.values():
            directory.mkdir(parents=True, exist_ok=True)

    def _generate_filename(self, original_filename: str, prefix: str = "") -> str:
        """
        Generate unique filename

        Args:
            original_filename: Original file name
            prefix: Optional prefix for the filename

        Returns:
            Unique filename with extension
        """
        # Get file extension
        _, ext = os.path.splitext(original_filename)

        # Generate unique ID
        unique_id = str(uuid.uuid4())

        # Create filename
        if prefix:
            filename = f"{prefix}_{unique_id}{ext}"
        else:
            filename = f"{unique_id}{ext}"

        return filename

    def _calculate_file_hash(self, file_content: bytes) -> str:
        """Calculate SHA256 hash of file content"""
        return hashlib.sha256(file_content).hexdigest()

    async def save_file(
        self,
        file: UploadFile,
        category: str = "documents",
        prefix: str = ""
    ) -> dict:
        """
        Save uploaded file

        Args:
            file: Uploaded file
            category: File category (videos, images, documents, avatars)
            prefix: Optional filename prefix

        Returns:
            Dictionary with file information
        """
        # Read file content
        content = await file.read()

        # Generate filename
        filename = self._generate_filename(file.filename, prefix)

        # Get storage directory
        storage_dir = self.directories.get(category, self.directories["documents"])
        file_path = storage_dir / filename

        # Save file
        with open(file_path, "wb") as f:
            f.write(content)

        # Calculate file hash
        file_hash = self._calculate_file_hash(content)

        # Get file info
        file_size = len(content)
        mime_type = file.content_type or mimetypes.guess_type(file.filename)[0]

        # Build file URL (relative path) - 使用 /upload/ 前缀匹配静态文件挂载路径
        file_url = f"/upload/{category}/{filename}"

        return {
            "filename": filename,
            "original_filename": file.filename,
            "file_path": str(file_path),
            "file_url": file_url,
            "file_size": file_size,
            "mime_type": mime_type,
            "file_hash": file_hash,
            "category": category,
            "uploaded_at": datetime.now(timezone.utc).isoformat()
        }

    async def save_image(
        self,
        file: UploadFile,
        max_size: Tuple[int, int] = (1920, 1080),
        quality: int = 85,
        category: str = "images"
    ) -> dict:
        """
        Save and optimize image

        Args:
            file: Uploaded image file
            max_size: Maximum dimensions (width, height)
            quality: JPEG quality (1-100)
            category: Storage category

        Returns:
            Dictionary with image information
        """
        # Read image
        content = await file.read()
        image = Image.open(io.BytesIO(content))

        # Convert RGBA to RGB if necessary
        if image.mode == "RGBA":
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image = background
        elif image.mode != "RGB":
            image = image.convert("RGB")

        # Resize if necessary
        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Generate filename
        filename = self._generate_filename(file.filename, "img")
        filename = os.path.splitext(filename)[0] + ".jpg"  # Always save as JPEG

        # Get storage directory
        storage_dir = self.directories.get(category, self.directories["images"])
        file_path = storage_dir / filename

        # Save optimized image
        image.save(file_path, "JPEG", quality=quality, optimize=True)

        # Get file info
        file_size = os.path.getsize(file_path)

        # Build file URL - 使用 /upload/ 前缀匹配静态文件挂载路径
        file_url = f"/upload/{category}/{filename}"

        return {
            "filename": filename,
            "original_filename": file.filename,
            "file_path": str(file_path),
            "file_url": file_url,
            "file_size": file_size,
            "mime_type": "image/jpeg",
            "width": image.size[0],
            "height": image.size[1],
            "category": category,
            "uploaded_at": datetime.now(timezone.utc).isoformat()
        }

    async def save_avatar(self, file: UploadFile, user_id: int) -> dict:
        """
        Save user avatar with specific processing

        Args:
            file: Uploaded avatar image
            user_id: User ID

        Returns:
            Dictionary with avatar information
        """
        # Read image
        content = await file.read()
        image = Image.open(io.BytesIO(content))

        # Convert to RGB
        if image.mode != "RGB":
            if image.mode == "RGBA":
                background = Image.new("RGB", image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
            else:
                image = image.convert("RGB")

        # Crop to square
        width, height = image.size
        size = min(width, height)
        left = (width - size) // 2
        top = (height - size) // 2
        right = left + size
        bottom = top + size
        image = image.crop((left, top, right, bottom))

        # Resize to standard avatar size
        image.thumbnail((400, 400), Image.Resampling.LANCZOS)

        # Generate filename with user ID
        filename = f"avatar_{user_id}_{uuid.uuid4().hex[:8]}.jpg"

        # Get storage directory
        storage_dir = self.directories["avatars"]
        file_path = storage_dir / filename

        # Save avatar
        image.save(file_path, "JPEG", quality=90, optimize=True)

        # Get file info
        file_size = os.path.getsize(file_path)

        # Build file URL
        file_url = f"/media/avatars/{filename}"

        return {
            "filename": filename,
            "original_filename": file.filename,
            "file_path": str(file_path),
            "file_url": file_url,
            "file_size": file_size,
            "mime_type": "image/jpeg",
            "width": image.size[0],
            "height": image.size[1],
            "category": "avatars",
            "uploaded_at": datetime.now(timezone.utc).isoformat()
        }

    async def create_thumbnail(
        self,
        source_path: str,
        size: Tuple[int, int] = (400, 300)
    ) -> dict:
        """
        Create thumbnail from image

        Args:
            source_path: Path to source image
            size: Thumbnail size (width, height)

        Returns:
            Dictionary with thumbnail information
        """
        # Open source image
        image = Image.open(source_path)

        # Convert to RGB if necessary
        if image.mode != "RGB":
            if image.mode == "RGBA":
                background = Image.new("RGB", image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
            else:
                image = image.convert("RGB")

        # Create thumbnail
        image.thumbnail(size, Image.Resampling.LANCZOS)

        # Generate filename
        source_filename = os.path.basename(source_path)
        filename = f"thumb_{source_filename}"
        filename = os.path.splitext(filename)[0] + ".jpg"

        # Get storage directory
        storage_dir = self.directories["thumbnails"]
        file_path = storage_dir / filename

        # Save thumbnail
        image.save(file_path, "JPEG", quality=85, optimize=True)

        # Get file info
        file_size = os.path.getsize(file_path)

        # Build file URL
        file_url = f"/media/thumbnails/{filename}"

        return {
            "filename": filename,
            "file_path": str(file_path),
            "file_url": file_url,
            "file_size": file_size,
            "mime_type": "image/jpeg",
            "width": image.size[0],
            "height": image.size[1],
            "category": "thumbnails",
            "created_at": datetime.now(timezone.utc).isoformat()
        }

    def delete_file(self, file_path: str) -> bool:
        """
        Delete file from storage

        Args:
            file_path: Path to file

        Returns:
            True if deleted successfully
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

    def get_file_path(self, category: str, filename: str) -> Optional[Path]:
        """
        Get full file path

        Args:
            category: File category
            filename: File name

        Returns:
            Full file path or None if not found
        """
        storage_dir = self.directories.get(category)
        if not storage_dir:
            return None

        file_path = storage_dir / filename
        if file_path.exists():
            return file_path

        return None

    def get_file_info(self, file_path: str) -> Optional[dict]:
        """
        Get file information

        Args:
            file_path: Path to file

        Returns:
            Dictionary with file information or None
        """
        path = Path(file_path)
        if not path.exists():
            return None

        stat = path.stat()
        mime_type = mimetypes.guess_type(str(path))[0]

        return {
            "filename": path.name,
            "file_path": str(path),
            "file_size": stat.st_size,
            "mime_type": mime_type,
            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
        }


# Global storage service instance - use absolute path for server deployment
import os
_base_path = os.environ.get('UPLOAD_DIR', '/www/wwwroot/hercu-backend/uploads')
storage_service = StorageService(base_path=_base_path)
