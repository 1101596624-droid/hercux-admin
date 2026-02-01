#!/bin/bash
# HERCU 后端部署脚本
# 使用方法: bash deploy.sh

set -e

echo "=========================================="
echo "HERCU 后端部署脚本"
echo "=========================================="

# 配置
BACKEND_DIR="/www/wwwroot/hercu-backend"
VENV_DIR="$BACKEND_DIR/venv"
LOG_FILE="$BACKEND_DIR/output.log"

cd $BACKEND_DIR

# 1. 激活虚拟环境
echo ""
echo "[1/5] 激活虚拟环境..."
source $VENV_DIR/bin/activate

# 2. 安装/更新依赖
echo ""
echo "[2/5] 安装依赖..."
pip install -r requirements.txt -q

# 3. 验证依赖
echo ""
echo "[3/5] 验证依赖..."
python scripts/verify_dependencies.py
if [ $? -ne 0 ]; then
    echo "❌ 依赖验证失败，请检查上面的错误信息"
    exit 1
fi

# 4. 停止旧进程
echo ""
echo "[4/5] 停止旧服务..."
pkill -f "python run.py" 2>/dev/null || true
sleep 2

# 5. 启动新服务
echo ""
echo "[5/5] 启动服务..."
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
