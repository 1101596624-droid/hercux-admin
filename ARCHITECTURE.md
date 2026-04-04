# HERCU Architecture

## 当前结构

```text
hercux-admin/
├── app/                     Next.js 管理端
├── components/              管理端组件
├── stores/                  Zustand 状态
├── electron/                Electron 壳
├── backend/                 Shared FastAPI backend
└── docs/                    当前保留的项目文档
```

## 当前主判断

这个仓库不应再被理解成“只有后台管理页面”的项目。

当前真实结构是：

- 一个 Next.js 管理端
- 一个 Electron 桌面壳
- 一套共享 FastAPI 后端

其中后端不仅服务管理端，也承接 app 侧共享能力。

## 前端层

主要入口在 `app/admin/*`，当前仍保留这些典型模块：

- `dashboard`
- `courses`
- `editor/[courseId]`
- `studio`
- `users`
- `progress`
- `analytics`
- `ai-monitor`

前端和桌面壳不是这轮文档整理的重点，当前更需要按代码事实理解的是共享后端。

## 共享后端层

共享后端入口：

- `backend/app/main.py`
- `backend/app/api/v1/api.py`

当前比较活跃、与 app 共享链路直接相关的端点模块：

- `backend/app/api/v1/endpoints/studio.py`
- `backend/app/api/v1/endpoints/learning_chat.py`
- `backend/app/api/v1/endpoints/question.py`
- `backend/app/api/v1/endpoints/voice.py`
- `backend/app/api/v1/endpoints/auth.py`
- `backend/app/api/v1/endpoints/courses.py`
- `backend/app/api/v1/endpoints/nodes.py`
- `backend/app/api/v1/endpoints/progress.py`

对应服务层里近期活跃文件主要包括：

- `backend/app/services/learning_chat_service.py`
- `backend/app/services/question_recognize_service.py`
- `backend/app/services/question_v2_service.py`
- `backend/app/services/question_legacy_service.py`
- `backend/app/services/studio_lecture_service.py`
- `backend/app/services/studio_blackboard_service.py`
- `backend/app/services/course_generation/*`

## 后端能力分层

### 基础业务

- `auth`
- `courses`
- `nodes`
- `progress`
- `users`

### 内容生成与 Studio

- Studio 上传
- package 生成
- lecture 生成
- blackboard 生成
- image 生成

### app 共享能力

- `learning/chat`
- `question/recognize-v2`
- `question/plan-teaching-v2`
- `question/generate-teaching-stream-v2`
- `question/clarify-step-v2`
- `voice/stt`
- `voice/tts`

### 扩展学习能力

- `knowledge`
- `learning_path`
- `review`
- `assessment`
- `recommendation`
- `adaptive_agent`
- `predictive`
- `goals`
- `habits`

## 代码事实优先级

当前如果要判断“系统现在到底有什么”，优先级应是：

1. `backend/app/api/v1/api.py`
2. 具体 endpoint 文件
3. `backend/tests/README.md`
4. `docs/SHARED-BACKEND-STATUS-2026-04-04.md`
5. 其他保留的参考文档

不要再把 1 月和 2 月阶段性报告当成当前主事实来源。

## 当前文档入口

- 总入口：`README.md`
- 文档索引：`docs/README.md`
- 当前状态：`docs/SHARED-BACKEND-STATUS-2026-04-04.md`
- 测试说明：`backend/tests/README.md`
