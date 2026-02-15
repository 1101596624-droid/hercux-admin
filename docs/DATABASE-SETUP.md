# HERCU 数据库设置指南

## 环境要求

- PostgreSQL 15+
- Redis 7.x
- Python 3.11+

## 快速开始

### 1. 安装 PostgreSQL

#### Windows
```bash
# 下载并安装 PostgreSQL 15
# https://www.postgresql.org/download/windows/

# 或使用 Chocolatey
choco install postgresql15
```

#### macOS
```bash
brew install postgresql@15
brew services start postgresql@15
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql-15 postgresql-contrib
sudo systemctl start postgresql
```

### 2. 创建数据库

```bash
# 连接到 PostgreSQL
psql -U postgres

# 创建数据库
CREATE DATABASE hercu_db;

# 创建用户（可选）
CREATE USER hercu_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE hercu_db TO hercu_user;

# 退出
\q
```

### 3. 配置环境变量

创建 `.env` 文件：

```bash
# 数据库配置
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/hercu_db

# Redis 配置
REDIS_URL=redis://localhost:6379/0

# Claude API 配置
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# JWT 配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 应用配置
PROJECT_NAME=HERCU
VERSION=1.0.0
API_V1_STR=/api/v1
```

### 4. 运行数据库迁移

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 运行迁移
alembic upgrade head
```

### 5. 加载种子数据（可选）

```bash
# 运行种子数据脚本
python scripts/seed_data.py
```

## 数据库架构

### 核心表

#### users - 用户表
```sql
- id: 主键
- email: 邮箱（唯一）
- username: 用户名（唯一）
- hashed_password: 加密密码
- full_name: 全名
- avatar_url: 头像 URL
- is_active: 是否激活
- is_premium: 是否高级会员
- created_at: 创建时间
- updated_at: 更新时间
```

#### courses - 课程表
```sql
- id: 主键
- name: 课程名称
- description: 课程描述
- difficulty: 难度等级 (beginner/intermediate/advanced/expert)
- tags: 标签数组 (JSON)
- instructor: 讲师
- duration_hours: 课程时长（小时）
- thumbnail_url: 缩略图 URL
- is_published: 是否发布
- created_at: 创建时间
- updated_at: 更新时间
```

#### course_nodes - 课程节点表（核心）
```sql
- id: 主键
- course_id: 课程 ID（外键）
- parent_id: 父节点 ID（外键，支持树形结构）
- node_id: 节点唯一标识（如 "node_biomech_01"）
- type: 节点类型 (video/simulator/quiz/reading/practice)
- component_id: 组件 ID（如 "force-balance-sim"）
- title: 节点标题
- description: 节点描述
- sequence: 排序序号（同一父节点下的顺序）
- timeline_config: 时间轴配置 (JSON)
  {
    "steps": [
      {"type": "video", "duration": 300},
      {"type": "simulator", "duration": 600},
      {"type": "quiz", "duration": 180}
    ]
  }
- unlock_condition: 解锁条件 (JSON)
  {
    "type": "previous_complete"  // 或 "manual", "prerequisites"
    "prerequisites": [1, 2, 3]   // 前置节点 ID（可选）
  }
- created_at: 创建时间
- updated_at: 更新时间
```

#### learning_progress - 学习进度表
```sql
- id: 主键
- user_id: 用户 ID（外键）
- node_id: 节点 ID（外键）
- status: 状态 (locked/unlocked/in_progress/completed)
- completion_percentage: 完成百分比
- time_spent_seconds: 花费时间（秒）
- last_accessed: 最后访问时间
- completed_at: 完成时间
- created_at: 创建时间
- updated_at: 更新时间
```

#### training_plans - 训练计划表
```sql
- id: 主键
- user_id: 用户 ID（外键）
- title: 计划标题
- plan_data: 计划数据 (JSON)
  {
    "periods": [
      {
        "name": "基础期",
        "weeks": 4,
        "focus": "建立基础力量",
        "sessions": [...]
      }
    ]
  }
- status: 状态 (active/completed/archived)
- start_date: 开始日期
- end_date: 结束日期
- created_at: 创建时间
- updated_at: 更新时间
```

#### chat_history - AI 对话历史表
```sql
- id: 主键
- user_id: 用户 ID（外键）
- node_id: 节点 ID（外键）
- role: 角色 (user/assistant)
- content: 对话内容
- created_at: 创建时间
```

#### achievements - 成就表
```sql
- id: 主键
- user_id: 用户 ID（外键）
- badge_id: 徽章 ID
- badge_name: 徽章名称
- badge_description: 徽章描述
- rarity: 稀有度 (common/rare/epic/legendary)
- icon_url: 图标 URL
- unlocked_at: 解锁时间
```

#### user_courses - 用户课程关联表
```sql
- id: 主键
- user_id: 用户 ID（外键）
- course_id: 课程 ID（外键）
- enrolled_at: 注册时间
- last_accessed: 最后访问时间
- is_favorite: 是否收藏
```

#### learning_statistics - 学习统计表
```sql
- id: 主键
- user_id: 用户 ID（外键）
- date: 日期
- total_time_seconds: 总学习时间（秒）
- nodes_completed: 完成节点数
- streak_days: 连续学习天数
- created_at: 创建时间
```

## Alembic 迁移管理

### 常用命令

```bash
# 查看当前版本
alembic current

# 查看迁移历史
alembic history

# 升级到最新版本
alembic upgrade head

# 升级到特定版本
alembic upgrade <revision>

# 降级一个版本
alembic downgrade -1

# 降级到特定版本
alembic downgrade <revision>

# 创建新的迁移
alembic revision -m "description"

# 自动生成迁移（基于模型变更）
alembic revision --autogenerate -m "description"
```

### 创建新迁移

```bash
# 1. 修改 app/models/models.py 中的模型

# 2. 生成迁移文件
alembic revision --autogenerate -m "add new field to users"

# 3. 检查生成的迁移文件
# 查看 alembic/versions/ 目录下的新文件

# 4. 运行迁移
alembic upgrade head
```

## 数据库备份和恢复

### 备份

```bash
# 备份整个数据库
pg_dump -U postgres hercu_db > hercu_backup.sql

# 备份特定表
pg_dump -U postgres -t users -t courses hercu_db > hercu_partial_backup.sql

# 压缩备份
pg_dump -U postgres hercu_db | gzip > hercu_backup.sql.gz
```

### 恢复

```bash
# 恢复数据库
psql -U postgres hercu_db < hercu_backup.sql

# 恢复压缩备份
gunzip -c hercu_backup.sql.gz | psql -U postgres hercu_db
```

## 性能优化

### 索引

已创建的索引：
- `users.email` - 唯一索引
- `users.username` - 唯一索引
- `course_nodes.node_id` - 唯一索引
- `learning_progress (user_id, node_id)` - 复合唯一索引
- `user_courses (user_id, course_id)` - 复合唯一索引
- `learning_statistics (user_id, date)` - 复合唯一索引

### 查询优化建议

```sql
-- 1. 使用 EXPLAIN ANALYZE 分析查询
EXPLAIN ANALYZE
SELECT * FROM course_nodes WHERE course_id = 1;

-- 2. 为常用查询添加索引
CREATE INDEX idx_learning_progress_status ON learning_progress(status);
CREATE INDEX idx_course_nodes_type ON course_nodes(type);

-- 3. 使用连接池（已在 app/db/session.py 中配置）
```

## 常见问题

### Q: 迁移失败，提示表已存在
**A:** 删除数据库并重新创建：
```bash
psql -U postgres
DROP DATABASE hercu_db;
CREATE DATABASE hercu_db;
\q
alembic upgrade head
```

### Q: 连接数据库失败
**A:** 检查以下几点：
1. PostgreSQL 服务是否运行
2. 数据库是否已创建
3. `.env` 文件中的 `DATABASE_URL` 是否正确
4. 防火墙是否允许连接

### Q: 如何重置数据库
**A:**
```bash
# 方法 1: 降级到初始状态
alembic downgrade base

# 方法 2: 删除并重新创建
psql -U postgres
DROP DATABASE hercu_db;
CREATE DATABASE hercu_db;
\q
alembic upgrade head
python scripts/seed_data.py
```

### Q: 如何查看数据库连接
**A:**
```sql
-- 查看当前连接
SELECT * FROM pg_stat_activity WHERE datname = 'hercu_db';

-- 终止特定连接
SELECT pg_terminate_backend(pid) FROM pg_stat_activity
WHERE datname = 'hercu_db' AND pid <> pg_backend_pid();
```

## 开发工作流

### 1. 添加新功能

```bash
# 1. 修改模型
vim app/models/models.py

# 2. 生成迁移
alembic revision --autogenerate -m "add feature X"

# 3. 检查迁移文件
cat alembic/versions/<new_revision>.py

# 4. 运行迁移
alembic upgrade head

# 5. 测试
pytest tests/
```

### 2. 修复数据

```bash
# 1. 创建数据修复脚本
vim scripts/fix_data.py

# 2. 运行脚本
python scripts/fix_data.py

# 3. 验证数据
psql -U postgres hercu_db
SELECT * FROM table_name WHERE condition;
```

## 监控和维护

### 数据库大小

```sql
-- 查看数据库大小
SELECT pg_size_pretty(pg_database_size('hercu_db'));

-- 查看表大小
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 清理和维护

```sql
-- 清理死元组
VACUUM ANALYZE;

-- 重建索引
REINDEX DATABASE hercu_db;

-- 更新统计信息
ANALYZE;
```

## 参考资源

- [PostgreSQL 官方文档](https://www.postgresql.org/docs/)
- [Alembic 文档](https://alembic.sqlalchemy.org/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [FastAPI 数据库指南](https://fastapi.tiangolo.com/tutorial/sql-databases/)

---

**快速开始**:
```bash
# 创建数据库
psql -U postgres -c "CREATE DATABASE hercu_db;"

# 运行迁移
cd backend
alembic upgrade head

# 加载种子数据
python scripts/seed_data.py
```
