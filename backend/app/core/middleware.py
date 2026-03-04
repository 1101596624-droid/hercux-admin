"""
Logging middleware for request/response tracking
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse
import time
import logging
import uuid

logger = logging.getLogger(__name__)


class MaintenanceModeMiddleware(BaseHTTPMiddleware):
    """
    维护模式中间件
    当维护模式开启时，拦截所有非管理员请求
    """

    # 不受维护模式影响的路径
    EXCLUDED_PATHS = [
        "/health",
        "/api/v1/auth/login",
        "/api/v1/admin/",  # 管理员接口不受影响
        "/api/v1/docs",
        "/api/v1/openapi.json",
        "/api/v1/redoc",
    ]

    async def dispatch(self, request: Request, call_next):
        # 检查是否是排除的路径
        path = request.url.path
        for excluded in self.EXCLUDED_PATHS:
            if path.startswith(excluded) or path == excluded.rstrip('/'):
                return await call_next(request)

        # 加载系统设置检查维护模式
        try:
            from app.core.system_settings import get_platform_settings
            platform_settings = get_platform_settings()

            if platform_settings.maintenance_mode:
                # 检查是否是管理员请求（通过 Authorization header）
                auth_header = request.headers.get("Authorization", "")
                if auth_header.startswith("Bearer "):
                    # 有 token，检查是否是管理员
                    # 这里简化处理，允许有 token 的请求通过
                    # 实际可以进一步验证是否是管理员 token
                    token = auth_header.replace("Bearer ", "")
                    if token:
                        # 尝试验证是否是管理员
                        try:
                            from app.core.security import decode_token
                            payload = decode_token(token)
                            if payload and payload.get("admin"):
                                return await call_next(request)
                        except Exception as e:
                            logger.warning(f"Admin token decode failed: {e}")

                # 返回维护模式响应
                return JSONResponse(
                    status_code=503,
                    content={
                        "detail": platform_settings.maintenance_message,
                        "maintenance_mode": True
                    }
                )
        except Exception as e:
            logger.warning(f"Failed to check maintenance mode: {e}")

        return await call_next(request)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses"""

    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Log request
        start_time = time.time()

        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client_host": request.client.host if request.client else None
            }
        )

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Log response
            logger.info(
                f"Request completed: {request.method} {request.url.path} - {response.status_code}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2)
                }
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            duration = time.time() - start_time

            logger.error(
                f"Request failed: {request.method} {request.url.path} - {str(e)}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration * 1000, 2),
                    "error": str(e)
                }
            )

            raise


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for monitoring slow requests"""

    def __init__(self, app, slow_request_threshold: float = 1.0):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold  # seconds

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time

        # Log slow requests
        if duration > self.slow_request_threshold:
            logger.warning(
                f"Slow request detected: {request.method} {request.url.path}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration * 1000, 2),
                    "threshold_ms": self.slow_request_threshold * 1000
                }
            )

        return response
