# ARCHITECTURE.md — hercux-admin 管理后台

## 系统架构

```
hercux-admin
├── Next.js 14 前端 (管理界面)
├── Electron 桌面壳
└── Python FastAPI 后端
    ├── 课程生成 AI 系统 (Supervisor + Generator)
    ├── PostgreSQL 数据库 (30 张表)
    ├── Redis 缓存
    └── 外部 AI API (Claude, Gemini, Tavily)
```

## 前端模块边界

### 路由层 (`app/`)

```
app/
├── layout.tsx              # 根布局（字体、bg-slate-50）
├── admin/
│   ├── layout.tsx          # 管理布局（Sidebar + 认证检查）
│   ├── login/              # 登录页（公开）
│   ├── dashboard/          # 系统概览
│   ├── courses/            # 课程管理
│   ├── editor/[courseId]/  # 课程编辑器（全屏，无侧边栏）
│   ├── studio/             # AI 内容工作室
│   ├── users/              # 用户管理
│   ├── progress/           # 进度管理
│   ├── analytics/          # 数据分析
│   └── ai-monitor/         # AI 监控
```

### 组件层 (`components/`)
### 组件层 (`components/`)

| 目录 | 职责 |
|------|------|
| `layout/` | Sidebar 侧边栏导航 |
| `editor/` | 课程编辑器（center/, left/, right/ 三栏） |
| `editor/center/SimulatorConfigEditor.tsx` | SDL 场景编辑器 |
| `editor/center/PreviewPanel.tsx` | 模拟器预览面板 |
| `simulator-engine/` | 模拟引擎（与学生端共享架构） |
| `simulator-engine/CustomRenderer.tsx` | AI 代码运行时（画布 800×500） |

### 状态层 (`stores/`)

```
stores/
├── admin/useAdminAuthStore.ts  # 管理员认证
├── editor/useEditorStore.ts    # 课程编辑器状态（SDL 传递）
└── useStudioStore.ts           # AI 工作室生成状态
```

### API 层 (`lib/`)

```
lib/
├── api/admin/courses.ts    # 管理端课程 API
├── api/admin/analytics.ts  # 数据分析 API
├── api/studio.ts           # AI 工作室 API（SSE 流式生成）
└── services/studioGenerationService.ts  # 生成服务（暂停/继续/重试）
```

## 后端架构

### 目录结构

```
backend/app/
├── main.py                    # FastAPI 应用入口
├── api/v1/
│   ├── api.py                 # 路由聚合
│   └── endpoints/
│       ├── auth.py            # 认证
│       ├── courses.py         # 课程 CRUD
│       ├── nodes.py           # 课程节点
│       ├── studio.py          # AI 工作室 + SSE 端点
│       ├── upload.py          # 文件上传
│       ├── admin_courses.py   # 管理端课程
│       └── ...
├── models/models.py           # SQLAlchemy ORM (30 张表)
├── schemas/                   # Pydantic 请求/响应模型
├── services/
│   ├── course_generation/     # ★ 课程生成 AI 系统（核心）
│   │   ├── service.py         # 主编排层
│   │   ├── supervisor.py      # 监督者 AI
│   │   ├── generator.py       # 生成者 AI (2000+ 行)
│   │   └── models.py          # 数据模型 + 质量标准
│   ├── studio/                # Studio 服务（处理器、模板、SDL 编译）
│   ├── grinder/               # 做题家服务
│   ├── claude_service.py      # Claude API 封装
│   ├── gemini_service.py      # Gemini API（图片生成）
│   ├── tavily_service.py      # Tavily 搜索 API
│   ├── email_service.py       # 邮件服务（QQ SMTP）
│   ├── storage_service.py     # 文件存储
│   └── ...
├── db/
│   ├── session.py             # PostgreSQL 异步连接
│   └── redis.py               # Redis 连接
└── core/
    ├── config.py              # 环境配置
    ├── security.py            # JWT + bcrypt
    ├── middleware.py           # 日志 + 性能监控
    ├── errors.py              # 异常处理
    └── utils.py               # 枚举兼容工具
```

### 课程生成 AI 系统（核心模块）

```
┌─────────────────────────────────────────────────────────┐
│                    监督者 AI (Supervisor)                │
│  - 生成课程大纲（含网络搜索）                            │
│  - 审核章节（规则审核 + AI 语义审核）                    │
│  - 碎片化检查（骨架→文本→模拟器 逐步检查）              │
│  - 动态提示词调整（根据错误类型生成修复指导）            │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                    生成者 AI (Generator)                 │
│  - 分步生成：骨架→文本→模拟器代码                       │
│  - 3 轮渐进式模拟器生成 + 评分                          │
│  - JSON 修复工具（分段处理）                             │
│  - 代码质量评分（结构25+视觉25+交互25+教学25）          │
└─────────────────────────────────────────────────────────┘
```

**生成流程**:
```
POST /api/v1/studio/packages/generate-v3 (SSE)
  → service.generate_course_stream()
    → supervisor.generate_outline()           # 大纲
    → 循环每章:
      → generator.generate_chapter_stream()   # 骨架
      → supervisor.check_chapter_skeleton()   # 碎片检查 1
      → service._generate_all_content_with_check()  # 文本+检查
      → service._generate_simulator_codes_with_check()  # 模拟器+检查
        → generator.generate_simulator_code_progressive()  # 3轮渐进
          → _producer_generate() → _supervisor_review() → 循环
      → service._process_chapter_images()     # Gemini 图片生成
    → service._build_course_package()
```

**模拟器视觉标准（因果关系函数图）**:
- 坐标系: X轴=自变量, Y轴=因变量
- 函数曲线: createCurve + setCurvePoints
- 当前值标注: 竖线 + 亮点
- 数值面板: 右侧实时显示
- 坐标轴固定: setup() 中设定，update() 不修改
- 禁止: 具象图形、emoji、硬编码坐标

**质量评分 (models.py)**:
```
总分 100 = 结构(25) + 视觉(25) + 交互(25) + 教学(25)
阈值: ≥70 通过, <70 重试
```

### 数据库 (PostgreSQL, 30 张表)

**核心表**:
- `users`, `courses`, `course_nodes`, `user_courses`, `learning_progress`

**功能表**:
- `training_plans`, `training_sessions`, `simulator_results`
- `grinder_sessions`, `grinder_questions`

**勋章系统**:
- `badge_configs` (120个), `user_badges`, `skill_tree_configs`
- `user_skill_progress`, `user_quiz_stats`, `wrong_questions`

**AI 相关**:
- `ai_conversations`, `ai_messages`, `token_usage`

**管理后台**:
- `studio_processors`, `studio_packages`, `admin_users`
- `system_settings`, `api_configs`

## 数据流

### SSE 课程生成流
```
前端 startGeneration()
  → POST /packages/generate-v3
  → studio.py event_generator() [asyncio.Queue + 15s 心跳]
    → service.py generate_course_stream() [主编排]
  → 前端 studioGenerationService 更新 Zustand store

SSE 事件序列:
phase → outline → chapter_start → chunk(多次) → skeleton_check
  → simulator_progress → chapter_complete → ... → complete
```

### 模拟器预览流
```
编辑器 useEditorStore → SimulatorConfigEditor
  → simulator_spec.sdl → PreviewPanel
  → CustomRenderer (800×500 画布)
    → compileCode(custom_code) → setup(ctx) → animate → update(ctx)
```

### 文件上传流
```
前端选择文件 → POST /api/v1/studio/upload
  → 文本提取 (PDF/DOCX/EPUB/HTML)
  → 存储到服务器 /upload/{category}/
  → 返回文件 URL
```

## 关键接口契约

### 前端 → 后端 SSE
- Content-Type: `text/event-stream`
- 事件格式: `event: {type}\ndata: {json}\n\n`
- 心跳: `: heartbeat\n\n` (每 15 秒)
- 前端通过 `V3StreamCallbacks` 接口处理各事件类型

### 模拟器代码契约
- AI 生成的 JS 代码必须导出 `setup(ctx)` 和 `update(ctx)`
- `ctx` 对象由 CustomRenderer 的 `createContext()` 构建
- 可用 API 白名单定义在 `generator.py` 的 `VALID_CREATE_APIS` 和 `VALID_OPERATION_APIS`

### 管理员权限
- 3 级权限: 超级管理员(1), 高级管理员(2), 普通管理员(3)
- 权限定义在 `types/admin.ts` 的 `ADMIN_LEVEL_PERMISSIONS`
- 前端通过 `useAdminAuthStore` 检查权限
