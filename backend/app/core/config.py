from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings"""

    # Environment
    ENV: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8001  # 统一端口为 8001
    DEBUG: bool = True
    PROJECT_NAME: str = "HERCU API"  # 统一项目名称
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str

    # Neo4j
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1800  # 30小时 (默认)
    ACCESS_TOKEN_EXPIRE_MINUTES_APP: int = 10080  # 7天 (主应用)
    ACCESS_TOKEN_EXPIRE_MINUTES_ADMIN: int = 4320  # 3天 (后台应用)

    # Claude AI - 支持两种配置名称
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_AUTH_TOKEN: str = ""  # 兼容 hercux 的配置名
    ANTHROPIC_BASE_URL: str = "https://api.anthropic.com"
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"  # Claude 模型名称

    @property
    def anthropic_key(self) -> str:
        """获取 Anthropic API Key，优先使用 ANTHROPIC_API_KEY"""
        return self.ANTHROPIC_API_KEY or self.ANTHROPIC_AUTH_TOKEN

    # DeepSeek AI
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"  # DeepSeek 模型名称

    # Qwen (千问) AI
    QWEN_API_KEY: str = ""
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    QWEN_MODEL: str = "qwen-plus"  # Qwen 模型名称

    # LLM Provider Selection
    LLM_PROVIDER: str = "deepseek"  # 可选: "deepseek" 或 "qwen"

    # Gemini AI (图片生成)
    GEMINI_API_KEY: str = ""
    GEMINI_BASE_URL: str = "https://hiapi.online/v1"
    GEMINI_MODEL: str = "gemini-3-pro-image-preview-2k"  # Gemini 模型名称

    # Tavily Search API (网络搜索)
    TAVILY_API_KEY: str = ""

    # AWS S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = ""

    # CORS - 添加 Electron 应用支持
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
        "http://localhost:23000",  # Electron 主应用内置服务器
        "http://localhost:23001",  # Electron 管理后台内置服务器
        "app://.",  # Electron 应用
    ]

    # Agent Learning System - Phase 3 (2026-02-13)
    # 智能学习系统配置
    ENABLE_AGENT_LEARNING: bool = True  # 启用Agent学习系统
    AGENT_EVAL_PROBABILITY_THRESHOLD: float = 0.5  # Agent评估触发概率阈值（0-1）
    DISTILLATION_TRIGGER_COUNT: int = 50  # 自动蒸馏触发阈值（轨迹数量）
    PATTERN_CONFIDENCE_THRESHOLD: float = 0.7  # 模式识别置信度阈值
    VECTOR_SIMILARITY_TOP_K: int = 3  # 向量检索返回的相似模板数量

    model_config = SettingsConfigDict(
        env_file="/www/wwwroot/hercu-backend/.env" if __import__('os').path.exists("/www/wwwroot/hercu-backend/.env") else ".env",
        case_sensitive=True
    )


settings = Settings()
