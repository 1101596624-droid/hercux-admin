# HERCU 后端数据库设置指南

## 快速开始

### 1. 启动数据库服务 (Docker)

```bash
# 启动所有数据库服务
cd backend
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

这将启动:
- PostgreSQL (端口 5432)
- Redis (端口 6379)
- Neo4j (端口 7474 HTTP, 7687 Bolt)

### 2. 安装 Python 依赖

```bash
# 创建虚拟环境 (推荐)
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 到 `.env` 并根据需要修改:

```bash
cp .env.example .env
```

默认配置已经匹配 Docker Compose 设置,通常不需要修改。

### 4. 初始化数据库

```bash
# 方法 1: 使用 Alembic (推荐用于生产)
alembic upgrade head

# 方法 2: 直接创建表 (开发环境快速启动)
python scripts/init_db.py init
```

### 5. 填充示例数据

```bash
python scripts/seed_data.py
```

这将创建:
- 2 个测试用户 (demo@hercu.com / demo123, student@hercu.com / student123)
- 3 门示例课程
- 多个课程节点 (包含视频、模拟器、测验)
- 学习进度记录

### 6. 启动后端服务

```bash
python run.py
```

或使用 uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问:
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## 数据库管理命令

### 使用 Alembic 进行迁移

```bash
# 创建新的迁移
alembic revision --autogenerate -m "描述你的更改"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1

# 查看迁移历史
alembic history

# 查看当前版本
alembic current
```

### 使用初始化脚本

```bash
# 初始化数据库 (创建所有表)
python scripts/init_db.py init

# 重置数据库 (删除并重新创建所有表)
python scripts/init_db.py reset

# 删除所有表
python scripts/init_db.py drop
```

### Docker 管理

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷 (⚠️ 会删除所有数据)
docker-compose down -v

# 重启服务
docker-compose restart

# 查看特定服务日志
docker-compose logs postgres
docker-compose logs redis
docker-compose logs neo4j
```

## 数据库访问

### PostgreSQL

```bash
# 使用 psql 连接
docker exec -it hercu_postgres psql -U hercu_user -d hercu_db

# 或使用任何 PostgreSQL 客户端
# Host: localhost
# Port: 5432
# Database: hercu_db
# User: hercu_user
# Password: hercu_password
```

### Redis

```bash
# 使用 redis-cli
docker exec -it hercu_redis redis-cli

# 测试连接
docker exec -it hercu_redis redis-cli ping
```

### Neo4j

访问 Neo4j Browser: http://localhost:7474

- 用户名: neo4j
- 密码: hercu_password

## 数据库架构

### 核心表

1. **users** - 用户账户
2. **courses** - 课程元数据
3. **course_nodes** - 课程节点 (核心表)
   - 支持树形结构 (parent_id)
   - timeline_config 存储学习步骤配置
   - unlock_condition 定义解锁条件
4. **learning_progress** - 用户学习进度
5. **training_plans** - AI 生成的训练计划
6. **user_courses** - 用户课程报名
7. **chat_history** - AI 对话历史
8. **achievements** - 用户成就徽章
9. **learning_statistics** - 学习统计数据

### timeline_config 结构示例

```json
{
  "steps": [
    {
      "stepId": "step-1",
      "type": "video",
      "videoUrl": "https://example.com/video.mp4",
      "duration": 300,
      "pauseAt": [120, 240],
      "aiPromptAtPause": "你理解这个概念了吗？"
    },
    {
      "stepId": "step-2",
      "type": "simulator",
      "simulatorId": "force-vector-sim",
      "props": {
        "force1": {"magnitude": 10, "angle": 0}
      },
      "completionCriteria": {
        "type": "attempts",
        "minAttempts": 3
      }
    },
    {
      "stepId": "step-3",
      "type": "quiz",
      "question": "问题内容",
      "options": ["选项1", "选项2", "选项3"],
      "correctAnswer": 0
    }
  ]
}
```

## 故障排除

### 数据库连接失败

1. 确认 Docker 服务正在运行:
   ```bash
   docker-compose ps
   ```

2. 检查端口是否被占用:
   ```bash
   # Windows
   netstat -ano | findstr :5432
   # Linux/Mac
   lsof -i :5432
   ```

3. 查看数据库日志:
   ```bash
   docker-compose logs postgres
   ```

### Alembic 迁移问题

如果遇到迁移冲突:

```bash
# 查看当前状态
alembic current

# 标记为最新版本 (不执行 SQL)
alembic stamp head

# 或者重置数据库
python scripts/init_db.py reset
```

### 清理并重新开始

```bash
# 1. 停止并删除所有容器和数据
docker-compose down -v

# 2. 重新启动服务
docker-compose up -d

# 3. 等待服务就绪 (约 10-15 秒)
sleep 15

# 4. 初始化数据库
python scripts/init_db.py init

# 5. 填充示例数据
python scripts/seed_data.py
```

## 生产环境注意事项

1. **修改默认密码**: 更新 `.env` 和 `docker-compose.yml` 中的所有密码
2. **使用 Alembic**: 生产环境必须使用 Alembic 管理迁移
3. **备份策略**: 设置定期备份 PostgreSQL 和 Neo4j 数据
4. **监控**: 配置数据库性能监控
5. **SSL/TLS**: 启用数据库连接加密

## 相关文档

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [Alembic 文档](https://alembic.sqlalchemy.org/)
- [PostgreSQL 文档](https://www.postgresql.org/docs/)
- [Neo4j 文档](https://neo4j.com/docs/)
