from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import os

from app.core.config import settings
from app.db.redis import get_redis, close_redis
from app.db.neo4j import neo4j_client
from app.api.v1.api import api_router
from app.api.v1.endpoints import studio as studio_router
from app.core.errors import setup_exception_handlers
from app.core.middleware import LoggingMiddleware, PerformanceMonitoringMiddleware, MaintenanceModeMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.ENV == "production" else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 设置课程生成模块的日志级别为ERROR（减少控制台输出）
if settings.ENV == "production":
    logging.getLogger('app.services.course_generation').setLevel(logging.ERROR)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Starting HERCU Admin API...")

    # Initialize Redis (optional)
    try:
        await get_redis()
        logger.info("✅ Redis connected")
    except Exception as e:
        logger.warning(f"⚠️  Redis connection failed: {e}")
        logger.warning("   Continuing without Redis...")

    # Initialize Neo4j (optional)
    try:
        await neo4j_client.connect()
        logger.info("✅ Neo4j connected")
    except Exception as e:
        logger.warning(f"⚠️  Neo4j connection failed: {e}")
        logger.warning("   Continuing without Neo4j...")

    yield

    # Shutdown
    logger.info("🛑 Shutting down HERCU Admin API...")
    try:
        await close_redis()
    except:
        pass
    try:
        await neo4j_client.close()
    except:
        pass
    logger.info("✅ Connections closed")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    lifespan=lifespan
)

# Setup exception handlers
setup_exception_handlers(app)

# Add custom middleware
app.add_middleware(MaintenanceModeMiddleware)  # 维护模式检查（最先执行）
app.add_middleware(LoggingMiddleware)
app.add_middleware(PerformanceMonitoringMiddleware, slow_request_threshold=2.0)

# Configure CORS - 使用配置的来源列表
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Include Studio router at /api level (for frontend compatibility)
app.include_router(studio_router.router, prefix="/api", tags=["Studio"])

# Mount static files for uploads (media files)
uploads_dir = os.environ.get('UPLOAD_DIR', '/www/wwwroot/hercu-backend/uploads')
if os.path.exists(uploads_dir):
    app.mount("/upload", StaticFiles(directory=uploads_dir), name="uploads")
    logger.info(f"✅ Static files mounted at /upload -> {uploads_dir}")
else:
    logger.warning(f"⚠️  Uploads directory not found: {uploads_dir}")

logger.info("Application configured successfully")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "HERCU Admin API - Course Management & Studio",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENV
    }
