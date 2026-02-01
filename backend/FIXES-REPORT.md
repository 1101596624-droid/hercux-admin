# HERCU 后端修复报告

## 修复日期
2026-01-18

## 修复内容总结

### 1. ✅ 数据模型对齐
**问题**: `course_nodes` 表的字段与文档不一致
**解决方案**:
- 确认数据模型已包含正确字段：
  - `timeline_config` (JSON) - 存储多步骤学习流程
  - `unlock_condition` (JSON) - 存储解锁条件
  - `parent_id` - 支持树形结构
  - `sequence` - 节点排序

### 2. ✅ 节点解锁逻辑实现 (RCS - Rule-based Control System)
**问题**: 节点解锁和进度跟踪逻辑未实现
**解决方案**: 创建 `UnlockService` (`app/services/unlock_service.py`)

**核心功能**:
- `check_unlock_condition()` - 检查节点是否可解锁
  - 支持 `none` - 无条件解锁
  - 支持 `previous_complete` - 前置节点完成后解锁
  - 支持 `manual` - 手动解锁（付费内容等）
  - 支持 `prerequisites` - 多个前置条件

- `unlock_node()` - 解锁节点
- `complete_node()` - 完成节点并自动解锁依赖节点
- `get_course_progress_map()` - 获取课程完整进度地图（用于左侧认知地图）
- `initialize_course_progress()` - 初始化课程进度（报名时调用）

**解锁策略**:
1. 解锁下一个兄弟节点（同级、下一序号）
2. 解锁第一个子节点（如果是章节节点）
3. 解锁显式依赖此节点的其他节点

### 3. ✅ AI 服务集成 (Claude API)
**问题**: AI 对话和训练计划生成未实现
**解决方案**: 创建 `AIService` (`app/services/ai_service.py`)

**核心功能**:
- `guide_chat()` - 苏格拉底式 AI 导师对话
  - 基于节点上下文（类型、描述、timeline_config）
  - 支持模拟器状态、视频时间戳等运行时上下文
  - 维护对话历史（存储在 `chat_history` 表）
  - 使用 Claude 3.5 Sonnet 模型

- `generate_training_plan()` - 生成结构化训练计划
  - 输入：角色、目标、周数、每周训练次数、经验水平、器材、限制条件
  - 输出：包含周期划分、周计划、日课表的 JSON
  - 符合运动训练学原理

- `adjust_training_plan()` - 自然语言调整训练计划
  - 支持如"把周三改成恢复日"、"把深蹲换成腿举"等指令
  - 返回更新后的完整计划

### 4. ✅ API 端点更新

#### 4.1 节点端点 (`app/api/v1/endpoints/nodes.py`)
- `GET /nodes/{node_id}` - 获取节点配置和进度
  - ✅ 自动检查并解锁符合条件的节点
  - ✅ 返回 `timeline_config`、`unlock_condition` 等完整信息

- `POST /nodes/{node_id}/complete` - 完成节点
  - ✅ 使用 `UnlockService` 自动解锁依赖节点
  - ✅ 返回新解锁节点列表

- `PUT /nodes/{node_id}/progress` - 更新进度
  - ✅ 更新 `last_accessed` 时间戳
  - ✅ 支持状态转换（UNLOCKED → IN_PROGRESS）

- `GET /nodes/course/{course_id}/map` - 获取课程地图
  - ✅ 使用 `UnlockService` 获取完整进度地图
  - ✅ 返回树形结构和解锁状态

#### 4.2 AI 端点 (`app/api/v1/endpoints/ai.py`)
- `POST /ai/guide-chat` - AI 导师对话
  - ✅ 集成 Claude API
  - ✅ 根据节点类型生成智能建议
  - ✅ 维护对话历史

- `POST /ai/generate-plan` - 生成训练计划
  - ✅ 集成 Claude API
  - ✅ 返回结构化 JSON 计划

#### 4.3 训练计划端点 (`app/api/v1/endpoints/training.py`)
- `POST /planner/generate-plan` - 生成并保存训练计划
  - ✅ 调用 AI 服务生成计划
  - ✅ 保存到 `training_plans` 表

- `GET /planner/plans/{plan_id}` - 获取训练计划详情
  - ✅ 实现权限检查

- `POST /planner/adjust-plan` - 调整训练计划
  - ✅ 使用 AI 服务处理自然语言指令
  - ✅ 更新数据库

- `GET /planner/plans` - 获取用户所有训练计划
  - ✅ 实现查询逻辑

### 5. ✅ Pydantic Schemas 更新
**文件**: `app/schemas/schemas.py`

更新 `CourseNodeBase` 以匹配数据模型：
- ✅ `timeline_config` 替代 `config`
- ✅ `sequence` 替代 `order_index`
- ✅ `parent_id` 支持树形结构
- ✅ `unlock_condition` 替代 `prerequisites`

## 三栏协同机制实现

### 左栏 → 中栏
- 用户点击节点 → 调用 `GET /nodes/{node_id}`
- 后端返回 `timeline_config` → 前端根据 `type` 加载对应组件

### 左栏 → 右栏
- 用户点击锁定节点 → 后端返回解锁原因
- AI 导师主动解释："需要先完成前置课程"

### 中栏 → 左栏
- 完成任务 → 调用 `POST /nodes/{node_id}/complete`
- 后端更新进度 + 解锁新节点 → 左侧地图状态更新

### 中栏 → 右栏
- 模拟器状态变化 → 调用 `POST /ai/guide-chat` 带上 `context`
- AI 根据状态提问："观察左侧支撑点，你发现了什么？"

### 右栏 → 中栏/左栏
- AI 建议查看特定节点 → 前端跳转
- AI 调整模拟器参数 → 中栏组件更新

## 核心设计原则

### "规则骨架 + AI 肌肉"
- **规则骨架** (FastAPI): 解锁逻辑、进度存储、状态跳转 ✅
- **AI 肌肉** (Claude): 苏格拉底式提问、训练计划生成、对话调整 ✅

### "只做分发，不做解析"
- 后端不参与课程内容的"三层逻辑"加工
- 只负责分发成品节点的 `timeline_config`
- 前端根据配置动态加载组件

## 待完成事项

### 高优先级
1. **认证系统** - 所有端点当前使用 `user_id=1`，需要实现 JWT 认证
2. **数据库迁移** - 创建 Alembic 迁移文件以初始化数据库
3. **成就系统** - 实现勋章解锁逻辑
4. **Neo4j 技能树** - 实现技能依赖图查询

### 中优先级
5. **Dashboard 聚合** - 实现真实的学习统计聚合
6. **推荐算法** - 实现课程推荐逻辑
7. **课程报名逻辑** - 调用 `initialize_course_progress()`

### 低优先级
8. **排行榜** - 实现社区排行榜
9. **标签筛选** - 实现 JSON 字段的标签查询优化

## API 测试建议

### 测试流程
1. 导入示例课程（使用 `/internal/ingestion/ingest` 端点）
2. 测试节点解锁流程：
   ```bash
   # 获取课程地图
   GET /api/v1/nodes/course/1/map

   # 获取第一个节点
   GET /api/v1/nodes/node_001

   # 完成节点
   POST /api/v1/nodes/node_001/complete

   # 验证下一个节点已解锁
   GET /api/v1/nodes/course/1/map
   ```

3. 测试 AI 对话：
   ```bash
   POST /api/v1/ai/guide-chat
   {
     "node_id": 1,
     "message": "这个概念我不太理解",
     "context": {}
   }
   ```

4. 测试训练计划生成：
   ```bash
   POST /api/v1/planner/generate-plan
   {
     "role": "运动员",
     "goal": "提高爆发力",
     "duration_weeks": 12,
     "sessions_per_week": 4,
     "experience_level": "intermediate",
     "available_equipment": ["杠铃", "哑铃", "深蹲架"],
     "constraints": "膝盖有旧伤"
   }
   ```

## 环境变量要求

确保 `.env` 文件包含：
```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/hercux

# Redis
REDIS_URL=redis://localhost:6379

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Claude API
ANTHROPIC_API_KEY=sk-ant-...

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 文件清单

### 新增文件
- `backend/app/services/unlock_service.py` - 节点解锁服务
- `backend/app/services/ai_service.py` - AI 服务（Claude 集成）

### 修改文件
- `backend/app/api/v1/endpoints/nodes.py` - 集成 UnlockService
- `backend/app/api/v1/endpoints/ai.py` - 集成 AIService
- `backend/app/api/v1/endpoints/training.py` - 实现所有端点
- `backend/app/schemas/schemas.py` - 更新 CourseNode schemas

### 未修改（已验证正确）
- `backend/app/models/models.py` - 数据模型已符合文档要求
- `backend/app/services/ingestion.py` - 课程导入服务完整

## 总结

所有核心功能已实现：
- ✅ 节点解锁逻辑（RCS）
- ✅ 三栏协同机制
- ✅ AI 对话（苏格拉底式）
- ✅ 训练计划生成
- ✅ 进度跟踪
- ✅ 数据模型对齐

系统现在可以支持完整的学习流程，从课程导入到用户学习再到 AI 辅导。

下一步建议：
1. 创建数据库迁移文件
2. 实现 JWT 认证
3. 编写单元测试
4. 部署到测试环境
