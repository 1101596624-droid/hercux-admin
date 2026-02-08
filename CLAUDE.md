# CLAUDE.md — hercux-admin 管理后台

## 项目概述
HERCU 深度认知学习系统 — 管理后台。Next.js 14 + Electron 桌面应用 + Python FastAPI 后端（含课程生成 AI 系统）。

## 技术栈
- **前端**: Next.js 14 (App Router) + React 18 + TypeScript
- **状态管理**: Zustand (persist middleware)
- **样式**: Tailwind CSS (浅色主题 bg-slate-50)
- **桌面**: Electron
- **后端**: Python FastAPI + PostgreSQL + Redis
- **AI**: Claude API (via code.aipor.cc) + Gemini API (图片生成)
- **进程管理**: Gunicorn 4 workers + Supervisor

## 常用命令
```bash
# 前端
npm run dev              # 启动 Next.js 开发服务器 (port 3001)
npm run build            # 构建 Next.js
npm run electron:dist:win # 打包 Windows 安装包

# 后端 (本地)
cd backend && python run.py

# 部署到服务器
scp "backend/app/services/course_generation/generator.py" root@106.14.180.66:/www/wwwroot/hercu-backend/app/services/course_generation/generator.py
scp "backend/app/services/course_generation/models.py" root@106.14.180.66:/www/wwwroot/hercu-backend/app/services/course_generation/models.py
scp "backend/app/services/course_generation/supervisor.py" root@106.14.180.66:/www/wwwroot/hercu-backend/app/services/course_generation/supervisor.py
scp "backend/app/services/course_generation/service.py" root@106.14.180.66:/www/wwwroot/hercu-backend/app/services/course_generation/service.py

# 重启后端
ssh root@106.14.180.66 "pkill -f gunicorn && sleep 2 && cd /www/wwwroot/hercu-backend && source venv/bin/activate && nohup gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app -b 0.0.0.0:8001 --timeout 600 --graceful-timeout 60 --keep-alive 30 > /dev/null 2>&1 &"
```

## 代码规范

### 前端
- 组件: PascalCase (`SimulatorConfigEditor.tsx`)
- Store: `use[Domain]Store.ts` (Zustand)
- API 服务: `lib/api/` 目录下按域划分
- 类型: `types/` 目录集中定义
- 浅色主题: `bg-slate-50` 背景，`text-slate-900` 文字
- 侧边栏固定宽度 240px (`ml-[240px]`)

### 后端 (Python)
- FastAPI 路由放 `app/api/v1/endpoints/`
- 业务逻辑放 `app/services/`
- 数据模型放 `app/models/`
- Pydantic schema 放 `app/schemas/`
- 课程生成系统放 `app/services/course_generation/`

### 课程生成系统规范
- 模拟器视觉风格: **因果关系函数图**（坐标系 + 函数曲线 + 当前值标注 + 数值面板）
- 坐标轴在 setup() 中固定，update() 中绝对不修改轴和刻度
- 禁止具象图形（人物、弹簧、建筑等），只画坐标系+曲线+标注+面板
- 模拟器变量数: 2-3 个
- 代码行数: 80-150 行
- 必须有 setup() + update() 函数
- 使用比例坐标 (width/height)，不硬编码像素值

## 重要约束
- **服务器**: 106.14.180.66:8001, 路径 `/www/wwwroot/hercu-backend/`
- **数据库**: PostgreSQL `hercu_db` (用户: hercu)
- **Electron 端口**: 生产模式 port 23001
- **模拟器画布**: 管理端 800×500，学生端 1000×650
- **Gunicorn timeout**: 600 秒（课程生成耗时长）
- **SSE 心跳**: 每 15 秒发送 `: heartbeat` 保活

## 常见陷阱
- 后端修改后必须 scp 上传 + 重启 Gunicorn，否则不生效
- `generator.py` 超过 2000 行，修改时注意行号偏移
- JSON 修复工具 (JSONRepairTool) 不依赖 in_string 状态追踪，使用分段处理
- 课程生成 SSE 连接需要心跳保活，否则 Gunicorn 会超时断开
- `models.py` 的 `SimulatorQualityStandards` 阈值影响所有新生成的模拟器
- 前端 `bg-slate-50` 已加到根 layout body，防止页面切换白闪
