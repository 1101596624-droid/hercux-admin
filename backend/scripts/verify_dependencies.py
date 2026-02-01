#!/usr/bin/env python3
"""
部署依赖验证脚本
在部署后运行此脚本，确保所有必需的依赖都已正确安装

使用方法:
    python scripts/verify_dependencies.py
"""

import sys
from typing import List, Tuple

# 定义所有必需的依赖及其用途
REQUIRED_DEPENDENCIES: List[Tuple[str, str, str]] = [
    # (导入名, 包名, 用途)
    # FastAPI 核心
    ("fastapi", "fastapi", "Web框架"),
    ("uvicorn", "uvicorn", "ASGI服务器"),
    ("pydantic", "pydantic", "数据验证"),

    # 数据库
    ("sqlalchemy", "sqlalchemy", "ORM"),
    ("aiosqlite", "aiosqlite", "SQLite异步驱动"),
    ("alembic", "alembic", "数据库迁移"),

    # Redis
    ("redis", "redis", "Redis客户端"),

    # Neo4j
    ("neo4j", "neo4j", "Neo4j驱动"),

    # 认证
    ("jose", "python-jose", "JWT处理"),
    ("passlib", "passlib", "密码哈希"),
    ("bcrypt", "bcrypt", "密码加密"),

    # AI
    ("anthropic", "anthropic", "Claude API"),
    ("openai", "openai", "OpenAI API"),
    ("httpx", "httpx", "HTTP客户端"),
    ("certifi", "certifi", "SSL证书"),

    # 文档解析 (关键!)
    ("pypdf", "pypdf", "PDF解析"),
    ("docx", "python-docx", "Word文档解析"),
    ("bs4", "beautifulsoup4", "HTML解析"),
    ("ebooklib", "EbookLib", "EPUB解析"),
    ("lxml", "lxml", "XML解析"),

    # 工具
    ("PIL", "Pillow", "图片处理"),
    ("aiohttp", "aiohttp", "异步HTTP"),
    ("dotenv", "python-dotenv", "环境变量"),
]

# 可选依赖
OPTIONAL_DEPENDENCIES: List[Tuple[str, str, str]] = [
    ("boto3", "boto3", "AWS SDK"),
    ("asyncpg", "asyncpg", "PostgreSQL异步驱动"),
]


def check_dependency(import_name: str, package_name: str, purpose: str) -> Tuple[bool, str]:
    """检查单个依赖是否可用"""
    try:
        __import__(import_name)
        return True, f"✅ {package_name}: {purpose}"
    except ImportError as e:
        return False, f"❌ {package_name}: {purpose} - pip install {package_name}"


def main():
    print("=" * 60)
    print("HERCU 后端依赖验证")
    print("=" * 60)
    print()

    failed = []
    passed = []

    print("【必需依赖】")
    print("-" * 40)
    for import_name, package_name, purpose in REQUIRED_DEPENDENCIES:
        ok, msg = check_dependency(import_name, package_name, purpose)
        print(msg)
        if ok:
            passed.append(package_name)
        else:
            failed.append(package_name)

    print()
    print("【可选依赖】")
    print("-" * 40)
    for import_name, package_name, purpose in OPTIONAL_DEPENDENCIES:
        ok, msg = check_dependency(import_name, package_name, purpose)
        print(msg)

    print()
    print("=" * 60)
    print(f"结果: {len(passed)} 通过, {len(failed)} 失败")
    print("=" * 60)

    if failed:
        print()
        print("⚠️  缺失依赖，请运行:")
        print(f"    pip install {' '.join(failed)}")
        print()
        sys.exit(1)
    else:
        print()
        print("✅ 所有必需依赖已安装，可以启动服务")
        print()
        sys.exit(0)


if __name__ == "__main__":
    main()
