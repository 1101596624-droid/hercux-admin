@echo off
chcp 65001 >nul
echo ============================================================
echo              HERCU 数据库环境设置
echo ============================================================
echo.

REM 检查 Docker
echo [1/6] 检查 Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker 未安装或未运行
    echo 请先安装 Docker Desktop: https://www.docker.com/get-started
    pause
    exit /b 1
)
echo ✅ Docker 已安装
echo.

REM 检查 Docker Compose
echo [2/6] 检查 Docker Compose...
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose 未安装
    pause
    exit /b 1
)
echo ✅ Docker Compose 已安装
echo.

REM 启动 Docker 服务
echo [3/6] 启动数据库服务...
echo 停止现有服务...
docker-compose down >nul 2>&1

echo 启动 PostgreSQL, Redis, Neo4j...
docker-compose up -d
if errorlevel 1 (
    echo ❌ 服务启动失败
    pause
    exit /b 1
)
echo ✅ 服务已启动
echo.

echo 等待服务就绪 (15秒)...
timeout /t 15 /nobreak >nul
echo.

REM 检查 Python 依赖
echo [4/6] 检查 Python 依赖...
python -c "import fastapi, sqlalchemy, alembic" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  缺少依赖，正在安装...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
)
echo ✅ Python 依赖已安装
echo.

REM 初始化数据库
echo [5/6] 初始化数据库...
python scripts\init_db.py init
if errorlevel 1 (
    echo ❌ 数据库初始化失败
    pause
    exit /b 1
)
echo.

REM 填充示例数据
echo [6/6] 填充示例数据...
python scripts\seed_data.py
if errorlevel 1 (
    echo ⚠️  示例数据填充失败 (可选)
) else (
    echo ✅ 示例数据已填充
)
echo.

REM 显示摘要
echo ============================================================
echo                   设置完成!
echo ============================================================
echo.
echo 🎉 数据库环境已成功设置!
echo.
echo 服务访问信息:
echo   • PostgreSQL: localhost:5432
echo     - Database: hercu_db
echo     - User: hercu_user
echo     - Password: hercu_password
echo.
echo   • Redis: localhost:6379
echo.
echo   • Neo4j Browser: http://localhost:7474
echo     - User: neo4j
echo     - Password: hercu_password
echo.
echo 测试账户:
echo   • Email: demo@hercu.com
echo     Password: demo123
echo.
echo   • Email: student@hercu.com
echo     Password: student123
echo.
echo 下一步:
echo   1. 启动后端服务:
echo      python run.py
echo.
echo   2. 访问 API 文档:
echo      http://localhost:8000/docs
echo.
echo   3. 查看数据库管理命令:
echo      type DATABASE.md
echo.
pause
