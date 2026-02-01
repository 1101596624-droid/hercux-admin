"""
API Configuration Management Endpoints
管理所有 API 配置（API Key、Base URL、端口等）
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
from pathlib import Path

from app.core.config import settings

router = APIRouter()


class APIConfigItem(BaseModel):
    """单个 API 配置项"""
    key: str
    name: str
    description: str
    category: str
    value: str
    masked_value: str  # 脱敏后的值
    is_secret: bool
    is_configured: bool


class APIConfigCategory(BaseModel):
    """API 配置分类"""
    name: str
    description: str
    items: List[APIConfigItem]


class APIConfigResponse(BaseModel):
    """API 配置响应"""
    categories: List[APIConfigCategory]
    env_file_path: str


class UpdateAPIConfigRequest(BaseModel):
    """更新 API 配置请求"""
    key: str
    value: str


def mask_secret(value: str, show_chars: int = 8) -> str:
    """对敏感值进行脱敏处理"""
    if not value or value in ['', 'your-api-key-here', 'your-deepseek-api-key-here', 'your-aws-access-key', 'your-aws-secret-key']:
        return '未配置'
    if len(value) <= show_chars:
        return '*' * len(value)
    return value[:show_chars] + '*' * (len(value) - show_chars)


def get_env_file_path() -> Path:
    """获取 .env 文件路径"""
    # 优先使用服务器路径
    server_env = Path("/www/wwwroot/hercu-backend/.env")
    if server_env.exists():
        return server_env
    # 本地开发环境
    local_env = Path(__file__).parent.parent.parent.parent.parent.parent / ".env"
    return local_env


@router.get("/api-config", response_model=APIConfigResponse)
async def get_api_config():
    """
    获取所有 API 配置

    返回所有 API 相关的配置项，敏感信息会进行脱敏处理
    """
    categories = []

    # 1. 服务器配置
    server_items = [
        APIConfigItem(
            key="HOST",
            name="服务器地址",
            description="API 服务器监听地址",
            category="server",
            value=settings.HOST,
            masked_value=settings.HOST,
            is_secret=False,
            is_configured=True
        ),
        APIConfigItem(
            key="PORT",
            name="服务器端口",
            description="API 服务器监听端口",
            category="server",
            value=str(settings.PORT),
            masked_value=str(settings.PORT),
            is_secret=False,
            is_configured=True
        ),
        APIConfigItem(
            key="DEBUG",
            name="调试模式",
            description="是否启用调试模式",
            category="server",
            value=str(settings.DEBUG),
            masked_value=str(settings.DEBUG),
            is_secret=False,
            is_configured=True
        ),
        APIConfigItem(
            key="ENV",
            name="运行环境",
            description="当前运行环境 (development/production)",
            category="server",
            value=settings.ENV,
            masked_value=settings.ENV,
            is_secret=False,
            is_configured=True
        ),
    ]
    categories.append(APIConfigCategory(
        name="服务器配置",
        description="API 服务器基础配置",
        items=server_items
    ))

    # 2. 数据库配置
    db_items = [
        APIConfigItem(
            key="DATABASE_URL",
            name="数据库连接",
            description="数据库连接字符串",
            category="database",
            value=settings.DATABASE_URL,
            masked_value=mask_secret(settings.DATABASE_URL, 20),
            is_secret=True,
            is_configured=bool(settings.DATABASE_URL)
        ),
        APIConfigItem(
            key="REDIS_URL",
            name="Redis 连接",
            description="Redis 缓存服务器连接字符串",
            category="database",
            value=settings.REDIS_URL,
            masked_value=settings.REDIS_URL,
            is_secret=False,
            is_configured=bool(settings.REDIS_URL)
        ),
        APIConfigItem(
            key="NEO4J_URI",
            name="Neo4j URI",
            description="Neo4j 图数据库连接地址",
            category="database",
            value=settings.NEO4J_URI,
            masked_value=settings.NEO4J_URI,
            is_secret=False,
            is_configured=bool(settings.NEO4J_URI)
        ),
        APIConfigItem(
            key="NEO4J_USER",
            name="Neo4j 用户名",
            description="Neo4j 数据库用户名",
            category="database",
            value=settings.NEO4J_USER,
            masked_value=settings.NEO4J_USER,
            is_secret=False,
            is_configured=bool(settings.NEO4J_USER)
        ),
        APIConfigItem(
            key="NEO4J_PASSWORD",
            name="Neo4j 密码",
            description="Neo4j 数据库密码",
            category="database",
            value=settings.NEO4J_PASSWORD,
            masked_value=mask_secret(settings.NEO4J_PASSWORD),
            is_secret=True,
            is_configured=bool(settings.NEO4J_PASSWORD)
        ),
    ]
    categories.append(APIConfigCategory(
        name="数据库配置",
        description="数据库和缓存服务配置",
        items=db_items
    ))

    # 3. JWT 认证配置
    jwt_items = [
        APIConfigItem(
            key="SECRET_KEY",
            name="JWT 密钥",
            description="JWT 签名密钥（生产环境必须更改）",
            category="jwt",
            value=settings.SECRET_KEY,
            masked_value=mask_secret(settings.SECRET_KEY),
            is_secret=True,
            is_configured=bool(settings.SECRET_KEY)
        ),
        APIConfigItem(
            key="ALGORITHM",
            name="加密算法",
            description="JWT 加密算法",
            category="jwt",
            value=settings.ALGORITHM,
            masked_value=settings.ALGORITHM,
            is_secret=False,
            is_configured=True
        ),
        APIConfigItem(
            key="ACCESS_TOKEN_EXPIRE_MINUTES",
            name="Token 过期时间",
            description="访问令牌过期时间（分钟）",
            category="jwt",
            value=str(settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            masked_value=str(settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            is_secret=False,
            is_configured=True
        ),
    ]
    categories.append(APIConfigCategory(
        name="JWT 认证",
        description="JWT 令牌认证配置",
        items=jwt_items
    ))

    # 4. Claude AI (Anthropic) 配置
    anthropic_key = settings.anthropic_key
    claude_items = [
        APIConfigItem(
            key="ANTHROPIC_API_KEY",
            name="Anthropic API Key",
            description="Claude AI API 密钥",
            category="claude",
            value=anthropic_key,
            masked_value=mask_secret(anthropic_key),
            is_secret=True,
            is_configured=bool(anthropic_key)
        ),
        APIConfigItem(
            key="ANTHROPIC_BASE_URL",
            name="Anthropic Base URL",
            description="Claude AI API 基础地址（支持代理）",
            category="claude",
            value=settings.ANTHROPIC_BASE_URL,
            masked_value=settings.ANTHROPIC_BASE_URL,
            is_secret=False,
            is_configured=bool(settings.ANTHROPIC_BASE_URL)
        ),
    ]
    categories.append(APIConfigCategory(
        name="Claude AI (Anthropic)",
        description="Claude AI 对话和内容生成服务",
        items=claude_items
    ))

    # 5. DeepSeek AI 配置
    deepseek_items = [
        APIConfigItem(
            key="DEEPSEEK_API_KEY",
            name="DeepSeek API Key",
            description="DeepSeek AI API 密钥",
            category="deepseek",
            value=settings.DEEPSEEK_API_KEY,
            masked_value=mask_secret(settings.DEEPSEEK_API_KEY),
            is_secret=True,
            is_configured=bool(settings.DEEPSEEK_API_KEY) and settings.DEEPSEEK_API_KEY != "your-deepseek-api-key-here"
        ),
        APIConfigItem(
            key="DEEPSEEK_BASE_URL",
            name="DeepSeek Base URL",
            description="DeepSeek AI API 基础地址",
            category="deepseek",
            value=settings.DEEPSEEK_BASE_URL,
            masked_value=settings.DEEPSEEK_BASE_URL,
            is_secret=False,
            is_configured=bool(settings.DEEPSEEK_BASE_URL)
        ),
    ]
    categories.append(APIConfigCategory(
        name="DeepSeek AI",
        description="DeepSeek AI 对话服务（备选）",
        items=deepseek_items
    ))

    # 6. Gemini AI (图片生成) 配置
    gemini_items = [
        APIConfigItem(
            key="GEMINI_API_KEY",
            name="Gemini API Key",
            description="Gemini/DALL-E 图片生成 API 密钥",
            category="gemini",
            value=settings.GEMINI_API_KEY,
            masked_value=mask_secret(settings.GEMINI_API_KEY),
            is_secret=True,
            is_configured=bool(settings.GEMINI_API_KEY)
        ),
        APIConfigItem(
            key="GEMINI_BASE_URL",
            name="Gemini Base URL",
            description="图片生成 API 基础地址（支持 OpenAI 兼容格式）",
            category="gemini",
            value=settings.GEMINI_BASE_URL,
            masked_value=settings.GEMINI_BASE_URL,
            is_secret=False,
            is_configured=bool(settings.GEMINI_BASE_URL)
        ),
    ]
    categories.append(APIConfigCategory(
        name="图片生成 (Gemini/DALL-E)",
        description="教育图片和图表生成服务",
        items=gemini_items
    ))

    # 7. AWS S3 配置
    s3_items = [
        APIConfigItem(
            key="AWS_ACCESS_KEY_ID",
            name="AWS Access Key ID",
            description="AWS 访问密钥 ID",
            category="aws",
            value=settings.AWS_ACCESS_KEY_ID,
            masked_value=mask_secret(settings.AWS_ACCESS_KEY_ID),
            is_secret=True,
            is_configured=bool(settings.AWS_ACCESS_KEY_ID) and settings.AWS_ACCESS_KEY_ID != "your-aws-access-key"
        ),
        APIConfigItem(
            key="AWS_SECRET_ACCESS_KEY",
            name="AWS Secret Access Key",
            description="AWS 秘密访问密钥",
            category="aws",
            value=settings.AWS_SECRET_ACCESS_KEY,
            masked_value=mask_secret(settings.AWS_SECRET_ACCESS_KEY),
            is_secret=True,
            is_configured=bool(settings.AWS_SECRET_ACCESS_KEY) and settings.AWS_SECRET_ACCESS_KEY != "your-aws-secret-key"
        ),
        APIConfigItem(
            key="AWS_REGION",
            name="AWS 区域",
            description="AWS 服务区域",
            category="aws",
            value=settings.AWS_REGION,
            masked_value=settings.AWS_REGION,
            is_secret=False,
            is_configured=bool(settings.AWS_REGION)
        ),
        APIConfigItem(
            key="S3_BUCKET_NAME",
            name="S3 存储桶",
            description="S3 存储桶名称",
            category="aws",
            value=settings.S3_BUCKET_NAME,
            masked_value=settings.S3_BUCKET_NAME,
            is_secret=False,
            is_configured=bool(settings.S3_BUCKET_NAME)
        ),
    ]
    categories.append(APIConfigCategory(
        name="AWS S3 存储",
        description="文件存储服务配置（可选）",
        items=s3_items
    ))

    env_path = get_env_file_path()

    return APIConfigResponse(
        categories=categories,
        env_file_path=str(env_path)
    )


@router.put("/api-config")
async def update_api_config(request: UpdateAPIConfigRequest):
    """
    更新 API 配置

    更新指定的配置项，会写入 .env 文件
    """
    env_path = get_env_file_path()

    if not env_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"配置文件不存在: {env_path}"
        )

    # 读取现有配置
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"读取配置文件失败: {str(e)}"
        )

    # 查找并更新配置项
    key = request.key
    value = request.value
    found = False
    new_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith(f"{key}=") or stripped.startswith(f"{key} ="):
            # 更新这一行
            new_lines.append(f"{key}={value}\n")
            found = True
        else:
            new_lines.append(line)

    # 如果没找到，添加到文件末尾
    if not found:
        new_lines.append(f"\n{key}={value}\n")

    # 写回文件
    try:
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"写入配置文件失败: {str(e)}"
        )

    return {
        "success": True,
        "message": f"配置项 {key} 已更新",
        "note": "配置已保存，需要重启服务才能生效"
    }


@router.post("/api-config/test/{category}")
async def test_api_connection(category: str):
    """
    测试 API 连接

    测试指定类别的 API 是否可用
    """
    if category == "claude":
        # 测试 Claude API
        try:
            import aiohttp
            api_key = settings.anthropic_key
            base_url = settings.ANTHROPIC_BASE_URL.rstrip('/')

            if not api_key:
                return {"success": False, "message": "API Key 未配置"}

            async with aiohttp.ClientSession() as session:
                headers = {
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                }
                # 发送一个简单的请求测试连接
                async with session.post(
                    f"{base_url}/v1/messages",
                    json={
                        "model": "claude-3-haiku-20240307",
                        "max_tokens": 10,
                        "messages": [{"role": "user", "content": "Hi"}]
                    },
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        return {"success": True, "message": "Claude API 连接正常"}
                    else:
                        text = await response.text()
                        return {"success": False, "message": f"API 返回错误: {response.status} - {text[:200]}"}
        except Exception as e:
            return {"success": False, "message": f"连接失败: {str(e)}"}

    elif category == "gemini":
        # 测试 Gemini/图片生成 API
        try:
            import aiohttp
            api_key = settings.GEMINI_API_KEY
            base_url = settings.GEMINI_BASE_URL.rstrip('/')

            if not api_key:
                return {"success": False, "message": "API Key 未配置"}

            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                # 测试模型列表端点
                async with session.get(
                    f"{base_url}/models",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        return {"success": True, "message": "图片生成 API 连接正常"}
                    else:
                        text = await response.text()
                        return {"success": False, "message": f"API 返回错误: {response.status} - {text[:200]}"}
        except Exception as e:
            return {"success": False, "message": f"连接失败: {str(e)}"}

    elif category == "deepseek":
        # 测试 DeepSeek API
        try:
            import aiohttp
            api_key = settings.DEEPSEEK_API_KEY
            base_url = settings.DEEPSEEK_BASE_URL.rstrip('/')

            if not api_key or api_key == "your-deepseek-api-key-here":
                return {"success": False, "message": "API Key 未配置"}

            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                async with session.get(
                    f"{base_url}/models",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        return {"success": True, "message": "DeepSeek API 连接正常"}
                    else:
                        text = await response.text()
                        return {"success": False, "message": f"API 返回错误: {response.status} - {text[:200]}"}
        except Exception as e:
            return {"success": False, "message": f"连接失败: {str(e)}"}

    elif category == "database":
        # 测试数据库连接
        try:
            from app.db.session import engine
            from sqlalchemy import text
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return {"success": True, "message": "数据库连接正常"}
        except Exception as e:
            return {"success": False, "message": f"数据库连接失败: {str(e)}"}

    else:
        return {"success": False, "message": f"不支持的测试类别: {category}"}
