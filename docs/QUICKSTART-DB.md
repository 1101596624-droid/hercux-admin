# HERCU 后端数据库 - 快速启动指南

## 🚀 快速开始 (推荐)

### 方式 1: 使用 Docker (推荐)

#### 步骤 1: 启动数据库服务

```bash
cd backend
docker-compose up -d
```

**如果遇到网络问题 (无法拉取镜像):**

1. **配置 Docker 镜像加速器** (中国用户推荐):

   打开 Docker Desktop -> Settings -> Docker Engine

   添加以下配置:
   ```json
   {
     "registry-mirrors": [
       "https://docker.mirrors.ustc.edu.cn",
       "https://hub-mirror.c.163.com",
       "https://mirror.baidubce.com"
     ]
   }
   ```

   点击 "Apply & Restart"

2. **或者使用代理**:

   Docker Desktop -> Settings -> Resources -> Proxies

   配置你的 HTTP/HTTPS 代理

3. **手动拉取镜像**:
   ```bash
   docker pull postgres:15-alpine
   docker pull redis:7-alpine
   docker pull neo4j:5.16-community
   ```

#### 步骤 2: 等待服务启动

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

等待约 15-20 秒,直到所有服务都显示 "healthy"。

#### 步骤 3: 运行设置脚本

**Windows:**
```bash
setup_db.bat
```

**Linux/Mac:**
```bash
python scripts/setup_db.py
```

**或者手动执行:**
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 初始化数据库
python scripts/init_db.py init

# 3. 填充示例数据
python scripts/seed_data.py
```

#### 步骤 4: 启动后端服务

```bash
python run.py
```

访问 http://localhost:8000/docs 查看 API 文档

---

### 方式 2: 本地安装数据库 (不使用 Docker)

如果你不想使用 Docker,可以在本地安装数据库:

#### PostgreSQL

1. 下载并安装 PostgreSQL 15: https://www.postgresql.org/download/
2. 创建数据库:
   ```sql
   CREATE DATABASE hercu_db;
   CREATE USER hercu_user WITH PASSWORD 'hercu_password';
   GRANT ALL PRIVILEGES ON DATABASE hercu_db TO hercu_user;
   ```

#### Redis

1. 下载并安装 Redis: https://redis.io/download
2. 启动 Redis 服务:
   ```bash
   redis-server
   ```

#### Neo4j (可选)

1. 下载并安装 Neo4j Community: https://neo4j.com/download/
2. 设置密码为 `hercu_password`
3. 启动 Neo4j 服务

#### 更新 .env 文件

确保 `.env` 文件中的连接字符串正确:

```env
DATABASE_URL=postgresql+asyncpg://hercu_user:hercu_password@localhost:5432/hercu_db
REDIS_URL=redis://localhost:6379/0
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=hercu_password
```

然后运行设置脚本:

```bash
python scripts/init_db.py init
python scripts/seed_data.py
```

---

## 📊 验证安装

### 检查数据库连接

```bash
# PostgreSQL
docker exec -it hercu_postgres psql -U hercu_user -d hercu_db -c "\dt"

# Redis
docker exec -it hercu_redis redis-cli ping

# Neo4j (浏览器访问)
# http://localhost:7474
```

### 检查数据

```bash
# 查看用户表
docker exec -it hercu_postgres psql -U hercu_user -d hercu_db -c "SELECT * FROM users;"

# 查看课程表
docker exec -it hercu_postgres psql -U hercu_user -d hercu_db -c "SELECT * FROM courses;"
```

---

## 🔧 常用命令

### Docker 管理

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs postgres
docker-compose logs redis
docker-compose logs neo4j

# 停止并删除所有数据 (⚠️ 危险)
docker-compose down -v
```

### 数据库管理

```bash
# 初始化数据库
python scripts/init_db.py init

# 重置数据库 (删除并重建)
python scripts/init_db.py reset

# 填充示例数据
python scripts/seed_data.py
```

### Alembic 迁移

```bash
# 创建迁移
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1

# 查看历史
alembic history
```

---

## 🎯 测试账户

设置完成后,你可以使用以下账户登录:

| Email | Password | 类型 |
|-------|----------|------|
| demo@hercu.com | demo123 | 高级用户 |
| student@hercu.com | student123 | 普通用户 |

---

## 🐛 故障排除

### Docker 无法启动

1. 确认 Docker Desktop 正在运行
2. 检查端口是否被占用 (5432, 6379, 7474, 7687)
3. 查看 Docker 日志: `docker-compose logs`

### 数据库连接失败

1. 确认服务已启动: `docker-compose ps`
2. 检查 `.env` 文件配置
3. 等待服务完全启动 (约 15-20 秒)

### 端口冲突

如果端口被占用,修改 `docker-compose.yml`:

```yaml
services:
  postgres:
    ports:
      - "5433:5432"  # 改为 5433
```

然后更新 `.env`:
```env
DATABASE_URL=postgresql+asyncpg://hercu_user:hercu_password@localhost:5433/hercu_db
```

### 清理并重新开始

```bash
# 完全清理
docker-compose down -v
docker system prune -a

# 重新开始
docker-compose up -d
sleep 20
python scripts/init_db.py init
python scripts/seed_data.py
```

---

## 📚 相关文档

- [DATABASE.md](DATABASE.md) - 详细的数据库文档
- [API 文档](http://localhost:8000/docs) - FastAPI 自动生成的 API 文档
- [工程师执行手册](../HERCU-工程师执行手册.md) - 完整的开发指南

---

## 💡 提示

1. **开发环境**: 使用 Docker 最方便
2. **生产环境**: 使用托管数据库服务 (AWS RDS, Azure Database 等)
3. **备份**: 定期备份 PostgreSQL 数据
4. **监控**: 配置数据库性能监控
5. **安全**: 生产环境务必修改默认密码

---

**需要帮助?** 查看 [DATABASE.md](DATABASE.md) 获取更多详细信息。
