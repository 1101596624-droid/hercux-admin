# HERCU Backend API

FastAPI backend for HERCU Deep Cognitive Learning System

## 🚀 Quick Start

### 一键设置 (推荐)

**Windows:**
```bash
cd backend
setup_db.bat
```

**Linux/Mac:**
```bash
cd backend
python scripts/setup_db.py
```

这将自动:
- ✅ 启动 Docker 数据库服务 (PostgreSQL, Redis, Neo4j)
- ✅ 安装 Python 依赖
- ✅ 初始化数据库表
- ✅ 填充示例数据
- ✅ 创建测试账户

### 手动设置

#### 1. 启动数据库 (Docker)

```bash
cd backend
docker-compose up -d
```

等待约 15 秒让服务启动完成。

#### 2. 安装依赖

```bash
pip install -r requirements.txt
```

#### 3. 初始化数据库

```bash
python scripts/init_db.py init
python scripts/seed_data.py
```

#### 4. 启动开发服务器

```bash
python run.py
```

或使用 uvicorn:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 5. 访问 API 文档

- **Swagger UI**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

### 📚 详细文档

- **[DATABASE-SETUP.md](DATABASE-SETUP.md)** - 数据库设置完整指南
  - 环境准备和安装
  - 数据库架构详解
  - Alembic 迁移管理
  - 性能优化建议
  - 故障排查
- **[FIXES-REPORT.md](FIXES-REPORT.md)** - 后端修复完成报告
  - 数据模型对齐
  - UnlockService 实现
  - AIService 实现
  - API 端点更新
  - 三栏协作架构
- **[QUICKSTART-DB.md](QUICKSTART-DB.md)** - 数据库快速启动指南
- **[DATABASE.md](DATABASE.md)** - 完整数据库文档
- **[DATABASE-SETUP-REPORT.md](DATABASE-SETUP-REPORT.md)** - 数据库设置完成报告

### 🧪 测试账户

| Email | Password | 类型 |
|-------|----------|------|
| demo@hercu.com | demo123 | 高级用户 |
| student@hercu.com | student123 | 普通用户 |

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/      # API route handlers
│   │       │   ├── users.py
│   │       │   ├── courses.py
│   │       │   ├── nodes.py    # Core workstation endpoint
│   │       │   ├── ai.py
│   │       │   ├── training.py
│   │       │   └── achievements.py
│   │       └── api.py          # Router aggregation
│   ├── core/
│   │   └── config.py           # Settings management
│   ├── db/
│   │   ├── session.py          # PostgreSQL connection
│   │   ├── redis.py            # Redis connection
│   │   └── neo4j.py            # Neo4j connection
│   ├── models/
│   │   └── models.py           # SQLAlchemy models
│   ├── schemas/
│   │   └── schemas.py          # Pydantic schemas
│   ├── services/               # Business logic
│   │   ├── unlock_service.py   # RCS unlock system ✅
│   │   └── ai_service.py       # Claude AI integration ✅
│   └── main.py                 # FastAPI app
├── tests/                      # Unit tests (TODO)
├── requirements.txt
├── .env.example
└── README.md
```

## 🔌 Core API Endpoints

### Module 1: Dashboard
- `GET /api/v1/user/summary` - User learning summary
- `GET /api/v1/user/active-course` - Most recent course
- `GET /api/v1/recommendations` - Recommended courses

### Module 2: Course Center
- `GET /api/v1/courses` - List courses (with filters)
- `GET /api/v1/courses/{id}` - Course details
- `POST /api/v1/courses/{id}/enroll` - Enroll in course

### Module 3: Learning Workstation (Core)
- `GET /api/v1/nodes/{nodeId}` - **Get node config & progress**
- `POST /api/v1/nodes/{nodeId}/complete` - Mark node complete
- `PUT /api/v1/nodes/{nodeId}/progress` - Update progress
- `GET /api/v1/nodes/course/{courseId}/map` - Get course map

### Module 4: Achievements
- `GET /api/v1/achievements` - User achievements
- `GET /api/v1/achievements/skill-tree` - Skill tree (Neo4j)
- `GET /api/v1/achievements/leaderboard` - Leaderboard

### Module 5: AI Training Planner
- `POST /api/v1/ai/generate-plan` - Generate training plan
- `GET /api/v1/planner/plans/{id}` - Get plan details
- `POST /api/v1/ai/adjust-plan` - Adjust plan with NLP

### Module 6: User Profile
- `GET /api/v1/user/profile` - User profile
- `PUT /api/v1/user/profile` - Update profile
- `GET /api/v1/user/statistics` - Detailed statistics

### AI Services
- `POST /api/v1/ai/guide-chat` - AI tutor conversation

## 🧠 Business Logic Services

### UnlockService (`app/services/unlock_service.py`)

Implements the Rule-based Control System (RCS) for node unlocking:

```python
from app.services.unlock_service import UnlockService

# Check if a node can be unlocked
can_unlock, reason = await unlock_service.check_unlock_condition(node, user_id)

# Unlock a node
unlocked = await unlock_service.unlock_node(user_id, node_id)

# Complete a node (triggers cascade unlock)
newly_unlocked_ids = await unlock_service.complete_node(user_id, node_id)

# Get complete progress map for a course
progress_map = await unlock_service.get_course_progress_map(user_id, course_id)
```

**Supported unlock strategies:**
- `none` - Always unlocked
- `previous_complete` - Requires previous sibling completion
- `manual` - Requires manual unlock (e.g., premium content)
- `prerequisites` - Requires multiple prerequisite nodes

### AIService (`app/services/ai_service.py`)

Integrates Claude 3.5 Sonnet for AI-powered features:

```python
from app.services.ai_service import AIService

# AI tutor conversation (Socratic method)
response = await ai_service.guide_chat(
    user_id=1,
    node_id=5,
    user_message="I don't understand force composition",
    node_context={"title": "Force Vectors", "type": "simulator"}
)

# Generate training plan
plan = await ai_service.generate_training_plan(
    user_id=1,
    role="strength_coach",
    goal="Build muscle mass",
    weeks=12,
    sessions_per_week=4,
    experience_level="intermediate",
    available_equipment=["barbell", "dumbbells"],
    constraints="Knee injury history"
)

# Adjust training plan with natural language
adjusted_plan = await ai_service.adjust_training_plan(
    plan_id=1,
    current_plan=plan_data,
    adjustment_request="Make it 3 days per week instead"
)
```

## 🗄️ Database Models

### Core Tables

**users** - User accounts
- id, email, username, hashed_password, full_name, avatar_url, is_premium

**courses** - Course metadata
- id, name, description, difficulty, tags, instructor, duration_hours

**course_nodes** - Content distribution (CORE)
- id, course_id, parent_id, node_id, type, component_id
- **timeline_config** (JSON) - Multi-step learning flow
- **unlock_condition** (JSON) - Unlock logic

**learning_progress** - User progress tracking
- user_id, node_id, status, completion_percentage, time_spent_seconds

**training_plans** - AI-generated plans
- user_id, plan_data (JSON), status, start_date, end_date

**user_courses** - Course enrollment
- user_id, course_id, enrolled_at, last_accessed

**chat_history** - AI conversation history
- user_id, node_id, role, content

**achievements** - User badges
- user_id, badge_id, badge_name, rarity, unlocked_at

**learning_statistics** - Daily learning stats
- user_id, date, total_time_seconds, nodes_completed, streak_days

### Timeline Config Structure

```json
{
  "steps": [
    {
      "stepId": "step-1",
      "type": "video",
      "videoUrl": "https://...",
      "duration": 300,
      "pauseAt": [120, 240],
      "aiPromptAtPause": "你理解了吗？"
    },
    {
      "stepId": "step-2",
      "type": "simulator",
      "simulatorId": "force-vector-sim",
      "props": {...},
      "completionCriteria": {"type": "attempts", "minAttempts": 3}
    },
    {
      "stepId": "step-3",
      "type": "quiz",
      "question": "问题",
      "options": ["A", "B", "C"],
      "correctAnswer": 0
    }
  ]
}
```

## 🔧 Development

### Database Management

```bash
# 启动数据库服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f

# 初始化数据库
python scripts/init_db.py init

# 重置数据库
python scripts/init_db.py reset

# 填充示例数据
python scripts/seed_data.py
```

### Database Migrations (Alembic)

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# View history
alembic history
```

### Testing

```bash
pytest tests/
```

## 📝 Development Status

### ✅ Completed
- [x] Database models design (9 tables)
- [x] Alembic migration setup
- [x] Docker Compose configuration
- [x] Database initialization scripts
- [x] Seed data with examples
- [x] Timeline config system
- [x] Tree structure for course nodes
- [x] Unlock condition logic

### 🚧 In Progress
- [ ] Authentication (JWT) - Currently using hardcoded user_id=1
- [ ] Neo4j skill tree integration
- [ ] Achievement system implementation

### ✅ Recently Completed (2026-01-18)
- [x] **UnlockService** - RCS (Rule-based Control System) for node unlocking
  - Supports: none, previous_complete, manual, prerequisites
  - Auto-unlock on node access
  - Cascade unlock on node completion
- [x] **AIService** - Claude 3.5 Sonnet integration
  - Socratic dialogue for AI tutoring
  - Training plan generation
  - Natural language plan adjustments
- [x] **API Endpoints** - All core endpoints implemented
  - nodes.py - Integrated with UnlockService
  - ai.py - Integrated with AIService
  - training.py - Full training plan CRUD
- [x] **Database Migration** - Initial schema migration created
  - alembic/versions/001_initial_schema.py
- [x] **Documentation**
  - DATABASE-SETUP.md - Comprehensive database guide
  - FIXES-REPORT.md - Detailed implementation report

### 📋 TODO
- [ ] Implement JWT authentication (replace hardcoded user_id)
- [ ] Add comprehensive error handling
- [ ] Write unit tests
- [ ] Add logging middleware
- [ ] Implement Redis caching strategies
- [ ] Add rate limiting
- [ ] Setup CI/CD
- [ ] Implement Neo4j skill tree queries
- [ ] Complete achievement system
- [ ] Add dashboard aggregation logic

## 🔐 Security Notes

- Never commit `.env` file
- Use strong SECRET_KEY in production
- Enable HTTPS in production
- Implement proper authentication
- Validate all user inputs
- Use parameterized queries (SQLAlchemy handles this)

## 📚 References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Pydantic](https://docs.pydantic.dev/)
- [Claude API](https://docs.anthropic.com/)
