# Docs Index

2026-04-04 文档清理后，当前仓库只保留一套主阅读路径。

## 先读这些

1. [SHARED-BACKEND-STATUS-2026-04-04.md](SHARED-BACKEND-STATUS-2026-04-04.md)
2. [../README.md](../README.md)
3. [../ARCHITECTURE.md](../ARCHITECTURE.md)
4. [../backend/tests/README.md](../backend/tests/README.md)

## 当前保留文档

### 当前状态

- [SHARED-BACKEND-STATUS-2026-04-04.md](SHARED-BACKEND-STATUS-2026-04-04.md)

### 参考架构

- [ARCHITECTURE_LEARNING_SYSTEM.md](ARCHITECTURE_LEARNING_SYSTEM.md)
- [AGENT_LEARNING_SYSTEM.md](AGENT_LEARNING_SYSTEM.md)
- [DEPLOYMENT_GUIDE_LEARNING_SYSTEM.md](DEPLOYMENT_GUIDE_LEARNING_SYSTEM.md)

### 后端与数据库参考

- [QUICKSTART.md](QUICKSTART.md)
- [QUICKSTART-DB.md](QUICKSTART-DB.md)
- [DATABASE.md](DATABASE.md)
- [DATABASE-SETUP.md](DATABASE-SETUP.md)
- [database-schema.md](database-schema.md)

### 课程相关参考

- [COURSE-API-CRUD.md](COURSE-API-CRUD.md)
- [COURSE-PACKAGING-GUIDE.md](COURSE-PACKAGING-GUIDE.md)

## 代码优先入口

当前共享后端真实能力优先看代码：

- `../backend/app/api/v1/api.py`
- `../backend/app/api/v1/endpoints/studio.py`
- `../backend/app/api/v1/endpoints/learning_chat.py`
- `../backend/app/api/v1/endpoints/question.py`
- `../backend/app/api/v1/endpoints/voice.py`

## 本轮清理原则

- 删除了 `backend/` 下与 `docs/` 完全重复的文档副本
- 删除了明显过时的阶段性报告和任务状态文档
- 保留仍有参考价值的指南类和架构类文档

如果后续新增文档，请优先放到 `docs/`，不要再在 `backend/` 根目录复制一份镜像。
