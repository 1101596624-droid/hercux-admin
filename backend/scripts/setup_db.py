#!/usr/bin/env python3
"""
HERCU Database Setup Script
一键设置数据库环境
"""
import asyncio
import subprocess
import sys
import time
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_info(text):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def run_command(command, description, check=True):
    """Run a shell command and handle errors"""
    print_info(f"{description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print_success(f"{description} - 完成")
            return True
        else:
            if check:
                print_error(f"{description} - 失败")
                if result.stderr:
                    print(result.stderr)
            return False
    except subprocess.CalledProcessError as e:
        print_error(f"{description} - 失败: {e}")
        if e.stderr:
            print(e.stderr)
        return False
    except Exception as e:
        print_error(f"{description} - 错误: {e}")
        return False


def check_docker():
    """Check if Docker is installed and running"""
    print_info("检查 Docker...")
    result = subprocess.run(
        "docker --version",
        shell=True,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print_error("Docker 未安装或未运行")
        print_info("请先安装 Docker: https://www.docker.com/get-started")
        return False

    print_success("Docker 已安装")
    return True


def check_docker_compose():
    """Check if Docker Compose is available"""
    print_info("检查 Docker Compose...")
    result = subprocess.run(
        "docker-compose --version",
        shell=True,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print_error("Docker Compose 未安装")
        return False

    print_success("Docker Compose 已安装")
    return True


def start_docker_services():
    """Start Docker services"""
    print_header("启动 Docker 服务")

    # Stop existing services
    print_info("停止现有服务...")
    subprocess.run("docker-compose down", shell=True, capture_output=True)

    # Start services
    if not run_command(
        "docker-compose up -d",
        "启动数据库服务 (PostgreSQL, Redis, Neo4j)"
    ):
        return False

    # Wait for services to be ready
    print_info("等待服务启动 (15秒)...")
    time.sleep(15)

    # Check service status
    run_command("docker-compose ps", "检查服务状态", check=False)

    return True


def check_python_packages():
    """Check if required Python packages are installed"""
    print_header("检查 Python 依赖")

    try:
        import fastapi
        import sqlalchemy
        import alembic
        print_success("所有必需的 Python 包已安装")
        return True
    except ImportError as e:
        print_warning(f"缺少依赖: {e}")
        print_info("正在安装依赖...")
        return run_command(
            "pip install -r requirements.txt",
            "安装 Python 依赖"
        )


def init_database():
    """Initialize database tables"""
    print_header("初始化数据库")

    sys.path.insert(0, str(Path(__file__).parent.parent))

    try:
        from scripts.init_db import init_db
        asyncio.run(init_db())
        return True
    except Exception as e:
        print_error(f"数据库初始化失败: {e}")
        return False


def seed_database():
    """Seed database with sample data"""
    print_header("填充示例数据")

    sys.path.insert(0, str(Path(__file__).parent.parent))

    try:
        from scripts.seed_data import seed_all
        asyncio.run(seed_all())
        return True
    except Exception as e:
        print_error(f"数据填充失败: {e}")
        return False


def print_summary():
    """Print setup summary"""
    print_header("设置完成!")

    print(f"{Colors.OKGREEN}🎉 数据库环境已成功设置!{Colors.ENDC}\n")

    print(f"{Colors.BOLD}服务访问信息:{Colors.ENDC}")
    print(f"  • PostgreSQL: localhost:5432")
    print(f"    - Database: hercu_db")
    print(f"    - User: hercu_user")
    print(f"    - Password: hercu_password")
    print()
    print(f"  • Redis: localhost:6379")
    print()
    print(f"  • Neo4j Browser: http://localhost:7474")
    print(f"    - User: neo4j")
    print(f"    - Password: hercu_password")
    print()

    print(f"{Colors.BOLD}测试账户:{Colors.ENDC}")
    print(f"  • Email: demo@hercu.com")
    print(f"    Password: demo123")
    print()
    print(f"  • Email: student@hercu.com")
    print(f"    Password: student123")
    print()

    print(f"{Colors.BOLD}下一步:{Colors.ENDC}")
    print(f"  1. 启动后端服务:")
    print(f"     {Colors.OKCYAN}python run.py{Colors.ENDC}")
    print()
    print(f"  2. 访问 API 文档:")
    print(f"     {Colors.OKCYAN}http://localhost:8000/docs{Colors.ENDC}")
    print()
    print(f"  3. 查看数据库管理命令:")
    print(f"     {Colors.OKCYAN}cat DATABASE.md{Colors.ENDC}")
    print()


def main():
    """Main setup function"""
    print_header("HERCU 数据库环境设置")

    # Check prerequisites
    if not check_docker():
        sys.exit(1)

    if not check_docker_compose():
        sys.exit(1)

    # Start Docker services
    if not start_docker_services():
        print_error("Docker 服务启动失败")
        sys.exit(1)

    # Check Python packages
    if not check_python_packages():
        print_error("Python 依赖安装失败")
        sys.exit(1)

    # Initialize database
    if not init_database():
        print_error("数据库初始化失败")
        sys.exit(1)

    # Seed data
    if not seed_database():
        print_warning("示例数据填充失败 (可选)")

    # Print summary
    print_summary()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\n\n设置已取消")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\n设置失败: {e}")
        sys.exit(1)
