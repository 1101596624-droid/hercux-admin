"""
Studio Endpoints
Complete API for Studio course generation tool
"""
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import Optional, List
import io
import re
import json
import uuid
import logging
from datetime import datetime

from app.db.session import get_db
from app.models.models import StudioProcessor, StudioPackage, StudioPackageStatus
from app.schemas.studio import (
    ProcessorWithConfig, ProcessorConfigUpdate, CreateProcessorRequest,
    PackageListItem, CoursePackageV2, GenerateRequestV2,
    UploadResponse, ProcessorListResponse, PackageListResponse, HealthResponse
)
from app.services.studio_service import get_studio_service, DEFAULT_PROCESSORS

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

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


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


@router.post("/upload", response_model=UploadResponse)
async def upload_and_extract(file: UploadFile = File(...)):
    """
    Upload file and extract text content for Studio
    Accepts PDF, Word, TXT, Markdown, EPUB, HTML files
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )

    filename = file.filename
    ext = filename.lower().split('.')[-1] if '.' in filename else ''
    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large (max 50MB)"
        )

    try:
        if ext == 'pdf':
            text = extract_text_from_pdf(content)
        elif ext in ['docx']:
            text = extract_text_from_docx(content)
        elif ext == 'doc':
            try:
                text = extract_text_from_docx(content)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Old .doc format not supported. Please convert to .docx"
                )
        elif ext in ['txt', 'md', 'markdown']:
            text = extract_text_from_txt(content, filename)
        elif ext == 'epub':
            text = extract_text_from_epub(content)
        elif ext in ['html', 'htm']:
            text = extract_text_from_html(content)
        else:
            try:
                text = extract_text_from_txt(content, filename)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported file type: {ext}"
                )

        text = clean_text(text)

        if not text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract any text from the file"
            )

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

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting text from {filename}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract text: {str(e)}"
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
                status=p.status.value if p.status else "draft",
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
# Generation API (SSE Streaming)
# ============================================

@router.post("/packages/generate-v2")
async def generate_course_v2(
    request: GenerateRequestV2,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate course with SSE streaming

    Returns Server-Sent Events stream with:
    - phase: Generation phase updates
    - structure: Course structure (meta, outline)
    - lesson_start: Starting new lesson
    - chunk: Content chunks
    - lesson_complete: Lesson completed
    - complete: Generation complete with full package
    - error: Error occurred
    """
    # Get processor system prompt if custom
    processor_prompt = None
    if request.processor_id:
        result = await db.execute(
            select(StudioProcessor).where(StudioProcessor.id == request.processor_id)
        )
        processor = result.scalar_one_or_none()
        if processor:
            processor_prompt = processor.system_prompt

    service = get_studio_service()

    async def event_generator():
        try:
            async for event in service.generate_course_stream(
                course_title=request.course_title,
                source_material=request.source_material,
                source_info=request.source_info,
                processor_id=request.processor_id,
                processor_prompt=processor_prompt,
                resume_from_lesson=request.resume_from_lesson,
                completed_lessons=request.completed_lessons,
                lessons_outline=request.lessons_outline,
                existing_meta=request.meta
            ):
                event_type = event.get("event", "message")
                event_data = event.get("data", {})

                # Save package to DB on complete (don't block the stream)
                if event_type == "complete" and "package" in event_data:
                    pkg = event_data["package"]
                    try:
                        await _save_package_to_db(db, pkg, request.processor_id)
                    except Exception as save_error:
                        logger.error(f"Failed to save package (non-blocking): {str(save_error)}")

                yield f"event: {event_type}\ndata: {json.dumps(event_data, ensure_ascii=False)}\n\n"

        except Exception as e:
            logger.error(f"Generation stream error: {str(e)}")
            yield f"event: error\ndata: {json.dumps({'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


async def _save_package_to_db(db: AsyncSession, pkg: dict, processor_id: str):
    """Save generated package to database"""
    try:
        # Debug: Log simulator_spec data before saving
        for lesson_idx, lesson in enumerate(pkg.get("lessons", [])):
            for step_idx, step in enumerate(lesson.get("script", [])):
                if step.get("type") == "simulator":
                    sim_spec = step.get("simulator_spec", {})
                    logger.info(f"[SavePackage] Lesson {lesson_idx}, Step {step_idx}: simulator_spec keys = {list(sim_spec.keys())}")
                    logger.info(f"[SavePackage] mode = {sim_spec.get('mode')}, custom_code exists = {bool(sim_spec.get('custom_code'))}")

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
