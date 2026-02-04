#!/bin/bash
# HERCU 后端部署脚本
# 使用方法: bash deploy.sh
# 选项: --fix 自动修复数据库schema问题

set -e

echo "=========================================="
echo "HERCU 后端部署脚本"
echo "=========================================="

# 解析参数
AUTO_FIX=""
for arg in "$@"; do
    case $arg in
        --fix)
            AUTO_FIX="--fix"
            ;;
    esac
done

# 配置
BACKEND_DIR="/www/wwwroot/hercu-backend"
VENV_DIR="$BACKEND_DIR/venv"
LOG_FILE="$BACKEND_DIR/output.log"

cd $BACKEND_DIR

# 1. 激活虚拟环境
echo ""
echo "[1/6] 激活虚拟环境..."
source $VENV_DIR/bin/activate

# 2. 安装/更新依赖
echo ""
echo "[2/6] 安装依赖..."
pip install -r requirements.txt -q

# 3. 验证依赖
echo ""
echo "[3/6] 验证依赖..."
python scripts/verify_dependencies.py
if [ $? -ne 0 ]; then
    echo "❌ 依赖验证失败，请检查上面的错误信息"
    exit 1
fi

# 4. 检查数据库 schema (关键步骤!)
echo ""
echo "[4/6] 检查数据库 schema..."
python scripts/check_db_schema.py --env production $AUTO_FIX
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 数据库 schema 不一致!"
    echo "   运行 'bash deploy.sh --fix' 自动修复"
    echo "   或手动修复后重新部署"
    exit 1
fi

# 5. 停止旧进程
echo ""
echo "[5/6] 停止旧服务..."
pkill -f "python run.py" 2>/dev/null || true
sleep 2

# 6. 启动新服务
echo ""
echo "[6/6] 启动服务..."
nohup python run.py > $LOG_FILE 2>&1 &
sleep 3

# 检查是否启动成功
if ss -tlnp | grep -q ":8001"; then
    echo ""
    echo "=========================================="
    echo "✅ 部署成功!"
    echo "   服务地址: http://0.0.0.0:8001"
    echo "   日志文件: $LOG_FILE"
    echo "=========================================="
else
    echo ""
    echo "❌ 服务启动失败，查看日志:"
    tail -20 $LOG_FILE
    exit 1
fi
