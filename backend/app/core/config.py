from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings"""

    # Environment
    ENV: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8001  # 统一端口为 8001
    DEBUG: bool = False
    TEST_MODE: bool = False
    PROJECT_NAME: str = "HERCU API"  # 统一项目名称
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 1800
    DATABASE_POOL_USE_LIFO: bool = True

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


    # AWS S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = ""

    # Email (SMTP)
    SMTP_SERVER: str = "smtp.qq.com"
    SMTP_PORT: int = 465
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""  # SMTP authorization code
    SMTP_SENDER_NAME: str = "HERCU 学习平台"

    # AI Monitor
    AI_MONTHLY_BUDGET: float = 5000.0  # 月度AI预算(美元)
    AI_DAILY_COST_THRESHOLD: float = 300.0  # 日成本告警阈值(美元)
    AI_USER_CALL_THRESHOLD: int = 100  # 单用户日调用告警阈值

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

    # Concurrent Generation (2026-02-23)
    # 并发课程生成配置 - 升配服务器只需改这些数字
    MAX_CONCURRENT_GENERATIONS: int = 5       # 最大并发生成数 (4核8G=5, 8核16G=12-15)
    GENERATION_QUEUE_MAX_SIZE: int = 50       # 队列最大长度
    GENERATION_TASK_TIMEOUT: int = 2160       # 单个任务超时(秒), 默认36分钟（与 Agent 超时口径同步）
    GENERATION_PROGRESS_TTL: int = 3600       # 进度数据Redis过期时间(秒)

    # Agent Learning System - Phase 3 (2026-02-13)
    # 智能学习系统配置
    AGENT_BASE_URL: str = "http://127.0.0.1:8100"  # hercu-agent 服务地址
    AGENT_MAX_CONCURRENT_SIMULATORS: int = 3  # Agent同时处理模拟器请求数
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
