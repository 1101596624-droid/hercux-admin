"""
Studio Endpoints
Complete API for Studio course generation tool
"""
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import Optional, List, Dict, Any
import asyncio
import io
import os
import re
import json
import uuid
import logging
from datetime import datetime
from pathlib import Path

from app.db.session import get_db
from app.models.models import StudioProcessor, StudioPackage, StudioPackageStatus
from app.schemas.studio import (
    ProcessorWithConfig, ProcessorConfigUpdate, CreateProcessorRequest,
    PackageListItem, CoursePackageV2, GenerateRequestV2,
    UploadResponse, UploadFileResponse,
    UploadTaskCreateResponse, UploadTaskStatusResponse, UploadTaskState,
    ProcessorListResponse, PackageListResponse, HealthResponse
)
from app.services.studio_service import DEFAULT_PROCESSORS

logger = logging.getLogger(__name__)

router = APIRouter()

# ============================================
# File Upload & Text Extraction
# ============================================

SUPPORTED_EXTENSIONS = {
    'pdf': 'PDF Document',
    'docx': 'Word Document',
    'doc': 'Word Document (Legacy)',
    'txt': 'Plain Text',
    'md': 'Markdown',
    'markdown': 'Markdown',
    'epub': 'EPUB eBook',
    'html': 'HTML Document',
    'htm': 'HTML Document',
}

# MIME type whitelist for upload validation
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/msword',
    'text/plain',
    'text/markdown',
    'text/html',
    'application/epub+zip',
    'application/xhtml+xml',
    'application/octet-stream',  # fallback for unknown types
}

# Dangerous file extensions that should be blocked
BLOCKED_EXTENSIONS = {
    'php', 'php3', 'php4', 'php5', 'phtml', 'phar',
    'exe', 'dll', 'bat', 'cmd', 'sh', 'bash', 'ps1',
    'js', 'jsx', 'ts', 'tsx', 'mjs', 'cjs',
    'py', 'pyc', 'pyo', 'pyw',
    'rb', 'pl', 'cgi',
    'asp', 'aspx', 'jsp', 'jspx',
    'jar', 'war', 'ear',
    'so', 'dylib',
    'sql', 'sqlite', 'db',
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
UPLOAD_EXTRACT_TIMEOUT_SEC = max(60, int(os.environ.get("STUDIO_UPLOAD_EXTRACT_TIMEOUT_SEC", "2160")))
UPLOAD_TASK_TTL_SEC = max(600, int(os.environ.get("STUDIO_UPLOAD_TASK_TTL_SEC", "86400")))
UPLOAD_FILE_TTL_SEC = max(600, int(os.environ.get("STUDIO_UPLOAD_FILE_TTL_SEC", "86400")))
UPLOAD_STORAGE_DIR = Path(
    os.environ.get("STUDIO_UPLOAD_STORAGE_DIR", "/tmp/hercu_studio_uploads")
)
UPLOAD_META_SUFFIX = ".meta.json"
UPLOAD_REF_PATTERN = re.compile(r"\[\[HERCU_UPLOAD_REF:([a-f0-9]{32})\|([^\]]+)\]\]")

_UPLOAD_TASKS: Dict[str, Dict[str, Any]] = {}
_UPLOAD_TASKS_LOCK = asyncio.Lock()
_UPLOADED_FILES: Dict[str, Dict[str, Any]] = {}
_UPLOADED_FILES_LOCK = asyncio.Lock()


def _utc_now_iso() -> str:
    return datetime.utcnow().isoformat() + "+00:00"


def _utc_from_ts_iso(ts: float) -> str:
    return datetime.utcfromtimestamp(ts).isoformat() + "+00:00"


def _validate_upload_filename_and_type(file: UploadFile) -> tuple[str, str]:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )

    filename = file.filename
    ext = filename.lower().split('.')[-1] if '.' in filename else ''

    # Security: double extension check (e.g., "file.php.pdf")
    name_parts = filename.lower().split('.')
    if len(name_parts) > 2:
        for part in name_parts[1:-1]:
            if part in BLOCKED_EXTENSIONS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Suspicious filename with blocked extension '{part}'"
                )

    if ext in BLOCKED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{ext}' is not allowed for security reasons"
        )

    # MIME type validation
    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        if ext not in SUPPORTED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"MIME type '{file.content_type}' is not allowed"
            )

    return filename, ext


def clean_text(text: str) -> str:
    """Clean and normalize extracted text"""
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = '\n'.join(line.rstrip() for line in text.split('\n'))
    return text.strip()


def extract_text_from_pdf(content: bytes) -> str:
    """Extract text from PDF file"""
    try:
        import pypdf
        pdf_reader = pypdf.PdfReader(io.BytesIO(content))
        text_parts = []
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        return "\n\n".join(text_parts)
    except ImportError:
        try:
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text_parts = []
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            return "\n\n".join(text_parts)
        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="PDF extraction requires: pypdf. Run: pip install pypdf"
            )


def extract_text_from_docx(content: bytes) -> str:
    """Extract text from Word document"""
    try:
        from docx import Document
        doc = Document(io.BytesIO(content))
        text_parts = []
        for para in doc.paragraphs:
            if para.text.strip():
                text_parts.append(para.text)
        return "\n\n".join(text_parts)
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Word extraction requires: python-docx. Run: pip install python-docx"
        )


def extract_text_from_txt(content: bytes, filename: str) -> str:
    """Extract text from plain text file"""
    encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
    for encoding in encodings:
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    return content.decode('utf-8', errors='replace')


def extract_text_from_epub(content: bytes) -> str:
    """Extract text from EPUB file"""
    # 检查依赖
    missing_libs = []
    try:
        import ebooklib
        from ebooklib import epub
    except ImportError:
        missing_libs.append("EbookLib")

    try:
        from bs4 import BeautifulSoup
    except ImportError:
        missing_libs.append("beautifulsoup4")

    if missing_libs:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"EPUB extraction requires: {', '.join(missing_libs)}. Run: pip install {' '.join(missing_libs)}"
        )

    # 重新导入（已确认可用）
    import ebooklib
    from ebooklib import epub
    from bs4 import BeautifulSoup

    book = epub.read_epub(io.BytesIO(content))
    text_parts = []

    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            text = soup.get_text(separator='\n')
            if text.strip():
                text_parts.append(text.strip())

    return "\n\n".join(text_parts)


def extract_text_from_html(content: bytes) -> str:
    """Extract text from HTML file"""
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        for script in soup(["script", "style"]):
            script.decompose()
        return soup.get_text(separator='\n')
    except ImportError:
        text = content.decode('utf-8', errors='replace')
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<[^>]+>', '', text)
        return text


def _extract_text_by_extension(ext: str, content: bytes, filename: str) -> str:
    if ext == 'pdf':
        return extract_text_from_pdf(content)
    if ext in ['docx']:
        return extract_text_from_docx(content)
    if ext == 'doc':
        try:
            return extract_text_from_docx(content)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Old .doc format not supported. Please convert to .docx"
            )
    if ext in ['txt', 'md', 'markdown']:
        return extract_text_from_txt(content, filename)
    if ext == 'epub':
        return extract_text_from_epub(content)
    if ext in ['html', 'htm']:
        return extract_text_from_html(content)

    try:
        return extract_text_from_txt(content, filename)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {ext}"
        )


def _build_upload_response(filename: str, ext: str, text: str) -> UploadResponse:
    word_count = len(text.split())
    reading_time_minutes = max(1, round(word_count / 200))
    return UploadResponse(
        success=True,
        filename=filename,
        file_type=SUPPORTED_EXTENSIONS.get(ext, "Unknown"),
        char_count=len(text),
        word_count=word_count,
        reading_time_minutes=reading_time_minutes,
        text=text
    )


def _normalize_upload_ids(upload_ids: Optional[List[str]]) -> List[str]:
    if not upload_ids:
        return []
    normalized: List[str] = []
    seen: set[str] = set()
    for raw_id in upload_ids:
        upload_id = (raw_id or "").strip()
        if not upload_id or upload_id in seen:
            continue
        seen.add(upload_id)
        normalized.append(upload_id)
    return normalized


def _build_legacy_upload_ref_text(upload_id: str, filename: str) -> str:
    return f"[[HERCU_UPLOAD_REF:{upload_id}|{filename}]]"


def _extract_upload_refs_from_source_material(source_material: str) -> tuple[str, List[str]]:
    found_ids: List[str] = []

    def _replace(match: re.Match[str]) -> str:
        found_ids.append(match.group(1))
        return ""

    cleaned = UPLOAD_REF_PATTERN.sub(_replace, source_material)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned, _normalize_upload_ids(found_ids)


def _upload_meta_path(upload_id: str) -> Path:
    return UPLOAD_STORAGE_DIR / f"{upload_id}{UPLOAD_META_SUFFIX}"


def _write_upload_meta(item: Dict[str, Any]) -> None:
    upload_id = item["upload_id"]
    meta_path = _upload_meta_path(upload_id)
    meta_path.write_text(json.dumps(item, ensure_ascii=False), encoding="utf-8")


def _load_upload_meta(upload_id: str) -> Optional[Dict[str, Any]]:
    meta_path = _upload_meta_path(upload_id)
    if not meta_path.exists():
        return None
    try:
        content = meta_path.read_text(encoding="utf-8")
        loaded = json.loads(content)
        if isinstance(loaded, dict):
            return loaded
        return None
    except Exception:
        logger.warning("Failed to parse upload meta file: %s", meta_path)
        return None


async def _cleanup_uploaded_files_locked() -> None:
    now_ts = datetime.utcnow().timestamp()
    expired_ids: List[str] = []

    for upload_id, item in _UPLOADED_FILES.items():
        created_ts = item.get("created_ts")
        if created_ts is None:
            continue
        if now_ts - float(created_ts) > UPLOAD_FILE_TTL_SEC:
            expired_ids.append(upload_id)

    if UPLOAD_STORAGE_DIR.exists():
        for meta_file in UPLOAD_STORAGE_DIR.glob(f"*{UPLOAD_META_SUFFIX}"):
            upload_id = meta_file.stem.replace(".meta", "")
            if upload_id in expired_ids:
                continue
            item = _load_upload_meta(upload_id)
            if not item:
                continue
            created_ts = item.get("created_ts")
            if created_ts is None:
                continue
            if now_ts - float(created_ts) > UPLOAD_FILE_TTL_SEC:
                expired_ids.append(upload_id)

    for upload_id in expired_ids:
        item = _UPLOADED_FILES.pop(upload_id, None)
        if item is None:
            item = _load_upload_meta(upload_id)
        if not item:
            continue

        stored_path = item.get("stored_path")
        if stored_path:
            path = Path(stored_path)
            if path.exists():
                try:
                    path.unlink()
                except Exception:
                    logger.warning("Failed to remove expired upload file: %s", stored_path)

        meta_path = _upload_meta_path(upload_id)
        if meta_path.exists():
            try:
                meta_path.unlink()
            except Exception:
                logger.warning("Failed to remove expired upload meta: %s", meta_path)


async def _store_uploaded_file(file: UploadFile, filename: str, ext: str) -> Dict[str, Any]:
    UPLOAD_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    upload_id = uuid.uuid4().hex
    safe_ext = ext if re.match(r"^[a-z0-9]+$", ext or "") else "bin"
    stored_path = UPLOAD_STORAGE_DIR / f"{upload_id}.{safe_ext}"
    file_size = 0

    try:
        await file.seek(0)
        with stored_path.open("wb") as out:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                file_size += len(chunk)
                if file_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="File too large (max 50MB)"
                    )
                out.write(chunk)
    except HTTPException:
        if stored_path.exists():
            stored_path.unlink()
        raise
    except Exception as exc:
        if stored_path.exists():
            stored_path.unlink()
        logger.exception("Failed to store uploaded file: %s", filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store uploaded file: {exc}"
        )
    finally:
        await file.close()

    if file_size == 0:
        if stored_path.exists():
            stored_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File content is empty"
        )

    created_ts = datetime.utcnow().timestamp()
    created_at = _utc_from_ts_iso(created_ts)
    expires_at = _utc_from_ts_iso(created_ts + UPLOAD_FILE_TTL_SEC)
    item: Dict[str, Any] = {
        "upload_id": upload_id,
        "filename": filename,
        "ext": ext,
        "file_size": file_size,
        "file_type": SUPPORTED_EXTENSIONS.get(ext, "Unknown"),
        "content_type": file.content_type,
        "stored_path": str(stored_path),
        "created_ts": created_ts,
        "created_at": created_at,
        "expires_at": expires_at,
    }
    try:
        _write_upload_meta(item)
    except Exception as exc:
        if stored_path.exists():
            stored_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store upload metadata: {exc}"
        )
    async with _UPLOADED_FILES_LOCK:
        _UPLOADED_FILES[upload_id] = item
        await _cleanup_uploaded_files_locked()
    return item


async def _get_uploaded_file_item(upload_id: str) -> Dict[str, Any]:
    async with _UPLOADED_FILES_LOCK:
        await _cleanup_uploaded_files_locked()
        item = _UPLOADED_FILES.get(upload_id)
        if item is None:
            item = _load_upload_meta(upload_id)
            if item is not None:
                _UPLOADED_FILES[upload_id] = item
        if item is None:
            raise HTTPException(status_code=404, detail=f"Uploaded file not found: {upload_id}")

        created_ts = item.get("created_ts")
        if created_ts is not None and datetime.utcnow().timestamp() - float(created_ts) > UPLOAD_FILE_TTL_SEC:
            _UPLOADED_FILES.pop(upload_id, None)
            meta_path = _upload_meta_path(upload_id)
            if meta_path.exists():
                try:
                    meta_path.unlink()
                except Exception:
                    logger.warning("Failed to remove expired upload meta: %s", meta_path)
            stored_path = item.get("stored_path")
            if stored_path:
                file_path = Path(stored_path)
                if file_path.exists():
                    try:
                        file_path.unlink()
                    except Exception:
                        logger.warning("Failed to remove expired upload content: %s", file_path)
            raise HTTPException(status_code=404, detail=f"Uploaded file expired: {upload_id}")
        return dict(item)


async def _extract_uploaded_file_text(upload_id: str) -> str:
    item = await _get_uploaded_file_item(upload_id)
    filename = item.get("filename", upload_id)
    ext = item.get("ext", "")
    stored_path = Path(item["stored_path"])
    if not stored_path.exists():
        async with _UPLOADED_FILES_LOCK:
            _UPLOADED_FILES.pop(upload_id, None)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Uploaded file content missing: {upload_id}"
        )

    content = await asyncio.to_thread(stored_path.read_bytes)
    try:
        text = await asyncio.wait_for(
            asyncio.to_thread(_extract_text_by_extension, ext, content, filename),
            timeout=UPLOAD_EXTRACT_TIMEOUT_SEC,
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Text extraction exceeded {UPLOAD_EXTRACT_TIMEOUT_SEC}s for {filename}"
        )
    text = clean_text(text)
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not extract any text from {filename}"
        )
    return f"【来源: {filename}】\n{text}"


async def _build_generation_source_material(request: GenerateRequestV2) -> str:
    sections: List[str] = []
    source_material_raw = (request.source_material or "").strip()
    source_material, embedded_upload_ids = _extract_upload_refs_from_source_material(source_material_raw)
    if source_material:
        sections.append(source_material)

    upload_ids = _normalize_upload_ids((request.source_upload_ids or []) + embedded_upload_ids)
    if upload_ids:
        extracted_sections = await asyncio.gather(
            *[_extract_uploaded_file_text(upload_id) for upload_id in upload_ids]
        )
        sections.extend(extracted_sections)

    if not sections:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid source material. Provide text or uploaded files."
        )
    return "\n\n---\n\n".join(sections)


def _build_deferred_generation_source_material(request: GenerateRequestV2) -> str:
    """
    Build queued source material without extracting uploaded files.

    Only embeds normalized upload references. Actual file text extraction runs in worker.
    """
    sections: List[str] = []
    source_material_raw = (request.source_material or "").strip()
    source_material, embedded_upload_ids = _extract_upload_refs_from_source_material(source_material_raw)
    if source_material:
        sections.append(source_material)

    upload_ids = _normalize_upload_ids((request.source_upload_ids or []) + embedded_upload_ids)
    if upload_ids:
        sections.extend([_build_legacy_upload_ref_text(upload_id, upload_id) for upload_id in upload_ids])

    if not sections:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid source material. Provide text or uploaded files."
        )
    return "\n\n".join(sections)


async def _cleanup_upload_tasks_locked() -> None:
    now = datetime.utcnow().timestamp()
    remove_ids: list[str] = []
    for task_id, task in _UPLOAD_TASKS.items():
        finished_at = task.get("finished_at")
        if not finished_at:
            continue
        try:
            finished_ts = datetime.fromisoformat(finished_at.replace("Z", "+00:00")).timestamp()
        except Exception:
            continue
        if now - finished_ts > UPLOAD_TASK_TTL_SEC:
            remove_ids.append(task_id)

    for task_id in remove_ids:
        _UPLOAD_TASKS.pop(task_id, None)


async def _run_upload_extract_task(task_id: str, filename: str, ext: str, content: bytes) -> None:
    started_at = _utc_now_iso()
    async with _UPLOAD_TASKS_LOCK:
        task = _UPLOAD_TASKS.get(task_id)
        if not task:
            return
        task["status"] = UploadTaskState.extracting.value
        task["current_phase"] = "extracting"
        task["started_at"] = started_at

    try:
        text = await asyncio.wait_for(
            asyncio.to_thread(_extract_text_by_extension, ext, content, filename),
            timeout=UPLOAD_EXTRACT_TIMEOUT_SEC,
        )
        text = clean_text(text)
        if not text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract any text from the file"
            )
        result = _build_upload_response(filename, ext, text).model_dump()
        finished_at = _utc_now_iso()
        async with _UPLOAD_TASKS_LOCK:
            task = _UPLOAD_TASKS.get(task_id)
            if not task:
                return
            task["status"] = UploadTaskState.succeeded.value
            task["current_phase"] = "completed"
            task["finished_at"] = finished_at
            task["result"] = result
            await _cleanup_upload_tasks_locked()
    except asyncio.TimeoutError:
        finished_at = _utc_now_iso()
        async with _UPLOAD_TASKS_LOCK:
            task = _UPLOAD_TASKS.get(task_id)
            if not task:
                return
            task["status"] = UploadTaskState.failed.value
            task["current_phase"] = "failed"
            task["finished_at"] = finished_at
            task["error_code"] = "UPLOAD_EXTRACT_TIMEOUT"
            task["error_message"] = f"Text extraction exceeded {UPLOAD_EXTRACT_TIMEOUT_SEC}s"
            await _cleanup_upload_tasks_locked()
    except HTTPException as exc:
        finished_at = _utc_now_iso()
        detail = exc.detail if isinstance(exc.detail, str) else json.dumps(exc.detail, ensure_ascii=False)
        async with _UPLOAD_TASKS_LOCK:
            task = _UPLOAD_TASKS.get(task_id)
            if not task:
                return
            task["status"] = UploadTaskState.failed.value
            task["current_phase"] = "failed"
            task["finished_at"] = finished_at
            task["error_code"] = f"UPLOAD_EXTRACT_{exc.status_code}"
            task["error_message"] = detail
            await _cleanup_upload_tasks_locked()
    except Exception as exc:
        logger.exception("Upload extract task failed: %s", task_id)
        finished_at = _utc_now_iso()
        async with _UPLOAD_TASKS_LOCK:
            task = _UPLOAD_TASKS.get(task_id)
            if not task:
                return
            task["status"] = UploadTaskState.failed.value
            task["current_phase"] = "failed"
            task["finished_at"] = finished_at
            task["error_code"] = "UPLOAD_EXTRACT_INTERNAL_ERROR"
            task["error_message"] = str(exc)
            await _cleanup_upload_tasks_locked()


@router.post("/upload/files", response_model=UploadFileResponse)
async def upload_file_only(file: UploadFile = File(...)):
    """
    Pure upload endpoint:
    - only validates and stores file
    - no text extraction
    """
    filename, ext = _validate_upload_filename_and_type(file)
    item = await _store_uploaded_file(file, filename, ext)
    logger.info(
        "Studio file uploaded: upload_id=%s filename=%s size=%s",
        item["upload_id"],
        filename,
        item["file_size"],
    )
    return UploadFileResponse(
        success=True,
        upload_id=item["upload_id"],
        filename=filename,
        file_type=item["file_type"],
        file_size=item["file_size"],
        content_type=item.get("content_type"),
        created_at=item["created_at"],
        expires_at=item["expires_at"],
    )


@router.delete("/upload/files/{upload_id}")
async def delete_uploaded_file(upload_id: str):
    """Delete an uploaded file reference and stored content."""
    async with _UPLOADED_FILES_LOCK:
        item = _UPLOADED_FILES.pop(upload_id, None)
        if item is None:
            item = _load_upload_meta(upload_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Uploaded file not found: {upload_id}")

    stored_path = item.get("stored_path")
    if stored_path:
        path = Path(stored_path)
        if path.exists():
            try:
                path.unlink()
            except Exception:
                logger.warning("Failed to delete uploaded file path: %s", stored_path)

    meta_path = _upload_meta_path(upload_id)
    if meta_path.exists():
        try:
            meta_path.unlink()
        except Exception:
            logger.warning("Failed to delete uploaded meta path: %s", meta_path)
    return {"success": True, "upload_id": upload_id}


@router.post("/upload/tasks", response_model=UploadTaskCreateResponse)
async def create_upload_task(file: UploadFile = File(...)):
    """
    Create async upload extraction task.
    Returns immediately with task_id; extraction runs in background.
    """
    filename, ext = _validate_upload_filename_and_type(file)
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large (max 50MB)"
        )

    task_id = uuid.uuid4().hex
    created_at = _utc_now_iso()
    task_entry: Dict[str, Any] = {
        "task_id": task_id,
        "status": UploadTaskState.queued.value,
        "filename": filename,
        "file_size": len(content),
        "created_at": created_at,
        "started_at": None,
        "finished_at": None,
        "current_phase": "queued",
        "error_code": None,
        "error_message": None,
        "result": None,
    }

    async with _UPLOAD_TASKS_LOCK:
        _UPLOAD_TASKS[task_id] = task_entry
        await _cleanup_upload_tasks_locked()

    asyncio.create_task(_run_upload_extract_task(task_id, filename, ext, content))
    logger.info("Studio upload task created: task_id=%s filename=%s size=%s", task_id, filename, len(content))

    return UploadTaskCreateResponse(
        task_id=task_id,
        status=UploadTaskState.queued,
        filename=filename,
        file_size=len(content),
        created_at=created_at,
    )


@router.get("/upload/tasks/{task_id}", response_model=UploadTaskStatusResponse)
async def get_upload_task_status(task_id: str):
    """Get async upload extraction task status."""
    async with _UPLOAD_TASKS_LOCK:
        task = _UPLOAD_TASKS.get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Upload task not found")
        return UploadTaskStatusResponse(**task)


@router.post("/upload", response_model=UploadResponse)
async def upload_and_extract(file: UploadFile = File(...)):
    """
    Legacy upload endpoint (compatibility mode):
    - only uploads file
    - returns upload reference marker in `text`
    - actual extraction happens when generation starts
    """
    filename, ext = _validate_upload_filename_and_type(file)
    item = await _store_uploaded_file(file, filename, ext)
    marker_text = _build_legacy_upload_ref_text(item["upload_id"], filename)
    logger.info(
        "Studio legacy upload accepted as deferred parse: upload_id=%s filename=%s size=%s",
        item["upload_id"],
        filename,
        item["file_size"],
    )
    return UploadResponse(
        success=True,
        filename=filename,
        file_type=item["file_type"],
        char_count=0,
        word_count=0,
        reading_time_minutes=0,
        text=marker_text,
    )


# ============================================
# Processors API
# ============================================

@router.get("/processors", response_model=ProcessorListResponse)
async def list_processors(
    include_disabled: bool = Query(False),
    db: AsyncSession = Depends(get_db)
):
    """Get all processors"""
    # First, ensure default processors exist in DB
    await _ensure_default_processors(db)

    # Query processors
    query = select(StudioProcessor)
    if not include_disabled:
        query = query.where(StudioProcessor.enabled == 1)
    query = query.order_by(StudioProcessor.display_order)

    result = await db.execute(query)
    processors = result.scalars().all()

    return ProcessorListResponse(
        processors=[
            ProcessorWithConfig(
                id=p.id,
                name=p.name,
                description=p.description or "",
                version=p.version or "1.0.0",
                author=p.author,
                tags=p.tags or [],
                color=p.color or "#3B82F6",
                icon=p.icon or "Sparkles",
                enabled=bool(p.enabled),
                display_order=p.display_order or 0,
                is_official=bool(p.is_official),
                is_custom=bool(p.is_custom),
                system_prompt=p.system_prompt
            )
            for p in processors
        ]
    )


@router.get("/processors/{processor_id}", response_model=ProcessorWithConfig)
async def get_processor(processor_id: str, db: AsyncSession = Depends(get_db)):
    """Get single processor"""
    result = await db.execute(
        select(StudioProcessor).where(StudioProcessor.id == processor_id)
    )
    processor = result.scalar_one_or_none()

    if not processor:
        raise HTTPException(status_code=404, detail="Processor not found")

    return ProcessorWithConfig(
        id=processor.id,
        name=processor.name,
        description=processor.description or "",
        version=processor.version or "1.0.0",
        author=processor.author,
        tags=processor.tags or [],
        color=processor.color or "#3B82F6",
        icon=processor.icon or "Sparkles",
        enabled=bool(processor.enabled),
        display_order=processor.display_order or 0,
        is_official=bool(processor.is_official),
        is_custom=bool(processor.is_custom),
        system_prompt=processor.system_prompt
    )


@router.put("/processors/{processor_id}/config")
async def update_processor_config(
    processor_id: str,
    config: ProcessorConfigUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update processor configuration"""
    result = await db.execute(
        select(StudioProcessor).where(StudioProcessor.id == processor_id)
    )
    processor = result.scalar_one_or_none()

    if not processor:
        raise HTTPException(status_code=404, detail="Processor not found")

    if config.enabled is not None:
        processor.enabled = 1 if config.enabled else 0
    if config.display_order is not None:
        processor.display_order = config.display_order

    await db.commit()

    return {"message": "Config updated", "config": config}


@router.post("/processors/{processor_id}/enable")
async def enable_processor(processor_id: str, db: AsyncSession = Depends(get_db)):
    """Enable processor"""
    await db.execute(
        update(StudioProcessor).where(StudioProcessor.id == processor_id).values(enabled=1)
    )
    await db.commit()
    return {"message": "Processor enabled"}


@router.post("/processors/{processor_id}/disable")
async def disable_processor(processor_id: str, db: AsyncSession = Depends(get_db)):
    """Disable processor"""
    await db.execute(
        update(StudioProcessor).where(StudioProcessor.id == processor_id).values(enabled=0)
    )
    await db.commit()
    return {"message": "Processor disabled"}


@router.post("/processors")
async def create_processor(
    data: CreateProcessorRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create custom processor"""
    processor_id = f"custom_{uuid.uuid4().hex[:8]}"

    processor = StudioProcessor(
        id=processor_id,
        name=data.name,
        description=data.description,
        color=data.color or "#3B82F6",
        icon=data.icon or "Sparkles",
        system_prompt=data.system_prompt,
        enabled=1,
        is_custom=1,
        is_official=0,
        tags=["custom"]
    )

    db.add(processor)
    await db.commit()

    return {
        "message": "Processor created",
        "processor": ProcessorWithConfig(
            id=processor.id,
            name=processor.name,
            description=processor.description or "",
            version="1.0.0",
            tags=processor.tags or [],
            color=processor.color or "#3B82F6",
            icon=processor.icon or "Sparkles",
            enabled=True,
            display_order=0,
            is_official=False,
            is_custom=True,
            system_prompt=processor.system_prompt
        )
    }


@router.put("/processors/{processor_id}")
async def update_processor(
    processor_id: str,
    data: CreateProcessorRequest,
    db: AsyncSession = Depends(get_db)
):
    """Update custom processor"""
    result = await db.execute(
        select(StudioProcessor).where(StudioProcessor.id == processor_id)
    )
    processor = result.scalar_one_or_none()

    if not processor:
        raise HTTPException(status_code=404, detail="Processor not found")

    if processor.is_official:
        raise HTTPException(status_code=400, detail="Cannot modify official processor")

    processor.name = data.name
    processor.description = data.description
    processor.color = data.color or processor.color
    processor.icon = data.icon or processor.icon
    processor.system_prompt = data.system_prompt

    await db.commit()

    return {"message": "Processor updated"}


@router.delete("/processors/{processor_id}")
async def delete_processor(processor_id: str, db: AsyncSession = Depends(get_db)):
    """Delete custom processor"""
    result = await db.execute(
        select(StudioProcessor).where(StudioProcessor.id == processor_id)
    )
    processor = result.scalar_one_or_none()

    if not processor:
        raise HTTPException(status_code=404, detail="Processor not found")

    if processor.is_official:
        raise HTTPException(status_code=400, detail="Cannot delete official processor")

    await db.execute(
        delete(StudioProcessor).where(StudioProcessor.id == processor_id)
    )
    await db.commit()

    return {"message": "Processor deleted"}


async def _ensure_default_processors(db: AsyncSession):
    """Ensure default processors exist in database"""
    for p in DEFAULT_PROCESSORS:
        result = await db.execute(
            select(StudioProcessor).where(StudioProcessor.id == p["id"])
        )
        if not result.scalar_one_or_none():
            processor = StudioProcessor(
                id=p["id"],
                name=p["name"],
                description=p["description"],
                version=p["version"],
                author=p["author"],
                tags=p["tags"],
                color=p["color"],
                icon=p["icon"],
                system_prompt=p["system_prompt"],
                enabled=1 if p["enabled"] else 0,
                display_order=p["display_order"],
                is_official=1 if p["is_official"] else 0,
                is_custom=1 if p["is_custom"] else 0
            )
            db.add(processor)

    await db.commit()


# ============================================
# Packages API
# ============================================

@router.get("/packages", response_model=PackageListResponse)
async def list_packages(
    status: Optional[str] = None,
    limit: int = Query(50, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get package list"""
    query = select(StudioPackage).order_by(StudioPackage.created_at.desc())

    if status:
        query = query.where(StudioPackage.status == status)

    query = query.limit(limit)
    result = await db.execute(query)
    packages = result.scalars().all()

    return PackageListResponse(
        packages=[
            PackageListItem(
                id=p.id,
                title=p.title,
                description=p.description or "",
                style=p.style or "default",
                status=(p.status.value if hasattr(p.status, 'value') else p.status) if p.status else "draft",
                total_nodes=p.total_lessons or 0,
                estimated_hours=p.estimated_hours or 0,
                created_at=p.created_at.isoformat() if p.created_at else "",
                updated_at=p.updated_at.isoformat() if p.updated_at else ""
            )
            for p in packages
        ],
        total=len(packages)
    )


@router.get("/packages/{package_id}")
async def get_package(package_id: str, db: AsyncSession = Depends(get_db)):
    """Get single package"""
    result = await db.execute(
        select(StudioPackage).where(StudioPackage.id == package_id)
    )
    package = result.scalar_one_or_none()

    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    return {
        "id": package.id,
        "version": "2.0.0",
        "meta": package.meta,
        "lessons": package.lessons or [],
        "edges": package.edges or [],
        "global_ai_config": package.global_ai_config or {}
    }


@router.delete("/packages/{package_id}")
async def delete_package(package_id: str, db: AsyncSession = Depends(get_db)):
    """Delete package"""
    await db.execute(
        delete(StudioPackage).where(StudioPackage.id == package_id)
    )
    await db.commit()
    return {"success": True}


@router.get("/packages/{package_id}/export")
async def export_package(package_id: str, db: AsyncSession = Depends(get_db)):
    """Export package as JSON"""
    result = await db.execute(
        select(StudioPackage).where(StudioPackage.id == package_id)
    )
    package = result.scalar_one_or_none()

    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    export_data = {
        "id": package.id,
        "version": "2.0.0",
        "meta": package.meta,
        "lessons": package.lessons or [],
        "edges": package.edges or [],
        "global_ai_config": package.global_ai_config or {}
    }

    return {"json": json.dumps(export_data, ensure_ascii=False, indent=2)}


@router.post("/packages/{package_id}/publish")
async def publish_package(package_id: str, db: AsyncSession = Depends(get_db)):
    """
    Publish package - imports to main course system

    This will:
    1. Create a course in the courses table
    2. Create course nodes from the package lessons
    3. Update package status to PUBLISHED
    """
    from app.services.package_importer import PackageImporterV2, CoursePackageV2

    # Get the package
    result = await db.execute(
        select(StudioPackage).where(StudioPackage.id == package_id)
    )
    package = result.scalar_one_or_none()

    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    if package.status == StudioPackageStatus.PUBLISHED:
        raise HTTPException(status_code=400, detail="Package already published")

    try:
        # Debug: Log the lessons data before import
        logger.info(f"[Publish] Package {package_id} lessons count: {len(package.lessons or [])}")
        for lesson_idx, lesson in enumerate(package.lessons or []):
            logger.info(f"[Publish] Lesson {lesson_idx}: {lesson.get('title', 'Unknown')}")
            for step_idx, step in enumerate(lesson.get('script', [])):
                step_type = step.get('type', 'unknown')
                step_title = step.get('title', 'Unknown')
                if step_type == 'simulator':
                    sim_spec = step.get('simulator_spec', {})
                    logger.info(f"[Publish] Step {step_idx} ({step_title}): simulator_spec keys = {list(sim_spec.keys())}")
                    logger.info(f"[Publish] Step {step_idx}: mode = {sim_spec.get('mode')}, custom_code exists = {bool(sim_spec.get('custom_code'))}")

        # Build the package data for import
        package_data = {
            "id": package.id,
            "version": "2.0.0",
            "meta": package.meta or {
                "title": package.title,
                "description": package.description or "",
                "source_info": package.source_info or "",
                "total_lessons": package.total_lessons or 0,
                "estimated_hours": package.estimated_hours or 0,
                "style": package.style or "default",
                "created_at": package.created_at.isoformat() if package.created_at else ""
            },
            "lessons": package.lessons or [],
            "edges": package.edges or [],
            "global_ai_config": package.global_ai_config or {}
        }

        # 给缺少 id 的 edges 补上
        import uuid as uuid_mod
        for edge in package_data["edges"]:
            if "id" not in edge:
                edge["id"] = str(uuid_mod.uuid4())

        # Parse and import
        course_package = CoursePackageV2(**package_data)
        importer = PackageImporterV2(db)
        import_result = await importer.import_package(course_package)

        # Update package status
        package.status = StudioPackageStatus.PUBLISHED
        package.course_id = import_result["course_id"]

        await db.commit()

        logger.info(f"Package {package_id} published successfully, course_id={import_result['course_id']}")

        return {
            "success": True,
            "course_id": import_result["course_id"],
            "nodes_created": import_result["nodes_created"],
            "message": f"课程发布成功，创建了 {import_result['nodes_created']} 个节点"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to publish package {package_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"发布失败: {str(e)}")


@router.post("/packages/{package_id}/archive")
async def archive_package(package_id: str, db: AsyncSession = Depends(get_db)):
    """Archive package"""
    await db.execute(
        update(StudioPackage)
        .where(StudioPackage.id == package_id)
        .values(status=StudioPackageStatus.ARCHIVED)
    )
    await db.commit()
    return {"success": True}


@router.post("/packages/{package_id}/duplicate")
async def duplicate_package(
    package_id: str,
    new_title: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Duplicate package"""
    result = await db.execute(
        select(StudioPackage).where(StudioPackage.id == package_id)
    )
    original = result.scalar_one_or_none()

    if not original:
        raise HTTPException(status_code=404, detail="Package not found")

    new_id = str(uuid.uuid4())
    new_meta = dict(original.meta) if original.meta else {}
    new_meta["title"] = new_title or f"{original.title} (副本)"

    new_package = StudioPackage(
        id=new_id,
        title=new_meta["title"],
        description=original.description,
        source_info=original.source_info,
        style=original.style,
        status=StudioPackageStatus.DRAFT,
        meta=new_meta,
        lessons=original.lessons,
        edges=original.edges,
        global_ai_config=original.global_ai_config,
        total_lessons=original.total_lessons,
        estimated_hours=original.estimated_hours,
        processor_id=original.processor_id
    )

    db.add(new_package)
    await db.commit()

    return {
        "success": True,
        "package": {
            "id": new_id,
            "version": "2.0.0",
            "meta": new_meta,
            "lessons": original.lessons or [],
            "edges": original.edges or [],
            "global_ai_config": original.global_ai_config or {}
        }
    }


# ============================================
# Generation API V3 (Supervisor-Generator Architecture)
# ============================================

@router.post("/packages/generate-v3")
async def generate_course_v3(
    request: GenerateRequestV2,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate course with Supervisor-Generator architecture (V3)

    This new architecture uses:
    - Supervisor AI: Generates outline, reviews chapters, decides retries
    - Generator AI: Generates individual chapters based on supervisor's instructions

    Returns Server-Sent Events stream with:
    - phase: Generation phase updates
    - outline: Course outline generated
    - chapter_start: Starting new chapter
    - chunk: Content chunks
    - chapter_review: Chapter review result
    - chapter_retry: Chapter needs retry
    - chapter_complete: Chapter completed
    - complete: Generation complete with full package
    - error: Error occurred
    """
    from app.services.course_generation import CourseGenerationService

    # Get processor system prompt if custom
    processor_prompt = None
    if request.processor_id:
        result = await db.execute(
            select(StudioProcessor).where(StudioProcessor.id == request.processor_id)
        )
        processor = result.scalar_one_or_none()
        if processor:
            processor_prompt = processor.system_prompt

    service = CourseGenerationService(db=db)

    async def event_generator():
        import asyncio

        queue = asyncio.Queue()
        done = False

        async def produce_events():
            nonlocal done
            try:
                upload_ids = _normalize_upload_ids(request.source_upload_ids)
                if upload_ids:
                    await queue.put({
                        "event": "phase",
                        "data": {
                            "phase": 0,
                            "message": "正在读取上传文件..."
                        }
                    })
                resolved_source_material = await _build_generation_source_material(request)
                if upload_ids:
                    await queue.put({
                        "event": "phase",
                        "data": {
                            "phase": 0,
                            "message": "上传素材读取完成，开始生成课程..."
                        }
                    })
                async for event in service.generate_course_stream(
                    course_title=request.course_title,
                    source_material=resolved_source_material,
                    source_info=request.source_info,
                    processor_id=request.processor_id,
                    processor_prompt=processor_prompt
                ):
                    await queue.put(event)
            except asyncio.CancelledError:
                logger.warning("Generation V3 producer cancelled (client disconnected)")
                raise
            except HTTPException as exc:
                detail = exc.detail if isinstance(exc.detail, str) else json.dumps(exc.detail, ensure_ascii=False)
                await queue.put({"_error": detail})
            except Exception as e:
                await queue.put({"_error": str(e)})
            finally:
                done = True
                await queue.put(None)

        async def produce_heartbeats():
            while not done:
                await asyncio.sleep(15)
                if not done:
                    await queue.put({"_heartbeat": True})

        event_task = asyncio.create_task(produce_events())
        heartbeat_task = asyncio.create_task(produce_heartbeats())

        try:
            # 先发送一个注释帧，尽快建立并刷新 SSE 通道
            yield ": stream-start\n\n"
            while True:
                item = await queue.get()
                if item is None:
                    break

                if isinstance(item, dict) and item.get("_heartbeat"):
                    yield ": heartbeat\n\n"
                    continue

                if isinstance(item, dict) and "_error" in item:
                    logger.error(f"Generation V3 stream error: {item['_error']}")
                    yield f"event: error\ndata: {json.dumps({'message': item['_error']})}\n\n"
                    break

                event_type = item.get("event", "message")
                event_data = item.get("data", {})

                if event_type == "complete" and "package" in event_data:
                    pkg = event_data["package"]
                    try:
                        await _save_package_to_db(db, pkg, request.processor_id)
                    except Exception as save_error:
                        logger.error(f"Failed to save package (non-blocking): {str(save_error)}")

                yield f"event: {event_type}\ndata: {json.dumps(event_data, ensure_ascii=False)}\n\n"

        except asyncio.CancelledError:
            logger.warning("Generation V3 stream cancelled (client disconnected)")
            raise
        except Exception as e:
            logger.error(f"Generation V3 stream error: {str(e)}", exc_info=True)
            yield f"event: error\ndata: {json.dumps({'message': str(e)})}\n\n"
        finally:
            heartbeat_task.cancel()
            if not event_task.done():
                event_task.cancel()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


async def _save_package_to_db(db: AsyncSession, pkg: dict, processor_id: str):
    """Save generated package to database"""
    try:
        meta = pkg.get("meta", {})
        package = StudioPackage(
            id=pkg.get("id", str(uuid.uuid4())),
            title=meta.get("title", "Untitled"),
            description=meta.get("description", ""),
            source_info=meta.get("source_info", ""),
            style=meta.get("style", processor_id),
            status=StudioPackageStatus.DRAFT,
            meta=meta,
            lessons=pkg.get("lessons", []),
            edges=pkg.get("edges", []),
            global_ai_config=pkg.get("global_ai_config", {}),
            total_lessons=meta.get("total_lessons", len(pkg.get("lessons", []))),
            estimated_hours=meta.get("estimated_hours", 0),
            processor_id=processor_id
        )
        db.add(package)
        await db.commit()
        logger.info(f"Package saved: {package.id}")
    except Exception as e:
        logger.error(f"Failed to save package: {str(e)}")


# ============================================
# Health API
# ============================================

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Studio API health check"""
    return HealthResponse(status="healthy", version="1.0.0")


# ============================================
# Templates API
# ============================================

@router.get("/templates")
async def list_templates():
    """Get all available SDL templates"""
    from app.services.studio.templates import list_templates
    return {"templates": list_templates()}


@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    """Get a specific SDL template by ID"""
    from app.services.studio.templates import get_template
    template = get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template {template_id} not found")
    return template


# ============================================
# Async Generation API (任务队列化并发生成)
# ============================================

@router.post("/packages/generate-async")
async def generate_course_async(
    request: GenerateRequestV2,
    admin_id: int = Query(default=1, description="管理员ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    异步提交课程生成任务 (2026-02-23)

    任务进入 Redis 队列，由后台 Worker 消费执行。
    返回 task_id，前端通过 /tasks/{task_id}/status 轮询进度。
    支持多管理员并发生成。
    """
    from app.services.course_generation.task_queue import TaskQueueService

    # 获取 processor prompt
    processor_prompt = None
    if request.processor_id:
        result = await db.execute(
            select(StudioProcessor).where(StudioProcessor.id == request.processor_id)
        )
        processor = result.scalar_one_or_none()
        if processor:
            processor_prompt = processor.system_prompt

    try:
        deferred_source_material = _build_deferred_generation_source_material(request)
        task_info = await TaskQueueService.submit_task(
            admin_id=admin_id,
            course_title=request.course_title,
            source_material=deferred_source_material,
            source_info=request.source_info,
            processor_id=request.processor_id,
            processor_prompt=processor_prompt,
            db=db,
        )
        return {"success": True, **task_info}
    except ValueError as e:
        raise HTTPException(status_code=429, detail=str(e))


@router.get("/tasks")
async def list_generation_tasks(
    admin_id: Optional[int] = Query(default=None, description="按管理员ID筛选"),
    limit: int = Query(default=20, ge=1, le=100),
):
    """获取课程生成任务列表"""
    from app.services.course_generation.task_queue import TaskQueueService
    tasks = await TaskQueueService.list_tasks(admin_id=admin_id, limit=limit)
    return {"tasks": tasks}


@router.get("/tasks/queue-info")
async def get_queue_info():
    """获取队列概况（排队数、运行数、最大并发）"""
    from app.services.course_generation.task_queue import TaskQueueService
    return await TaskQueueService.get_queue_info()


@router.get("/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    """获取单个任务的实时状态和进度"""
    from app.services.course_generation.task_queue import TaskQueueService
    status = await TaskQueueService.get_task_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="任务不存在")
    return status


@router.delete("/tasks/{task_id}")
async def cancel_task(
    task_id: str,
    admin_id: int = Query(default=1, description="管理员ID"),
):
    """取消课程生成任务"""
    from app.services.course_generation.task_queue import TaskQueueService
    success = await TaskQueueService.cancel_task(task_id, admin_id)
    if not success:
        raise HTTPException(status_code=404, detail="任务不存在或无法取消")
    return {"success": True, "message": "任务已取消"}


@router.delete("/tasks/{task_id}/record")
async def delete_task_record(
    task_id: str,
    admin_id: int = Query(default=1, description="管理员ID"),
):
    """删除任务记录（仅已完成/已取消/失败的任务）"""
    from app.services.course_generation.task_queue import TaskQueueService
    success = await TaskQueueService.delete_task(task_id, admin_id)
    if not success:
        raise HTTPException(status_code=404, detail="任务不存在或无法删除（进行中的任务不能删除）")
    return {"success": True, "message": "任务已删除"}


@router.post("/tasks/{task_id}/retry")
async def retry_task(
    task_id: str,
    admin_id: int = Query(default=1, description="管理员ID"),
):
    """重试已取消/失败的任务"""
    from app.services.course_generation.task_queue import TaskQueueService
    result = await TaskQueueService.retry_task(task_id, admin_id)
    if not result:
        raise HTTPException(status_code=404, detail="任务不存在或状态不允许重试")
    return {"success": True, **result}
