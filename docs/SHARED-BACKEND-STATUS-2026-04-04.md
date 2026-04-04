# Shared Backend Status 2026-04-04

## 目的

这份文档只回答一个问题：

`F:/9/hercux-admin` 这份共享后台，到 2026-04-04 为止，当前真实开发状态到底是什么。`

重点不是复述 2 月旧文档，而是核对：

- 当前代码里实际已经有什么
- 哪些结论只写在外部文档里
- 哪些改动已经落地但还没有提交进 git

---

## 核心结论

### 1. “3 月 24 日凌晨已经开发好了”这件事，确实有证据

最直接的文字证据不在共享后台旧 README，而在移动端仓库的迁移文档：

- `F:/1/hercux  app/APP-API-BACKEND-MIGRATION-LEDGER.md`
- `F:/1/hercux  app/APK-SHARED-BACKEND-EXECUTION-PLAN.md`

这些文档明确记录了以下共享 backend 端点已经补齐：

- `POST /api/v1/voice/stt`
- `POST /api/v1/voice/tts`
- `POST /api/v1/studio/generate-image`
- `POST /api/v1/studio/generate-blackboard`
- `POST /api/v1/studio/generate-blackboard-stream`
- `POST /api/v1/studio/generate-lecture`
- `POST /api/v1/studio/generate-lecture-stream`
- `POST /api/v1/learning/chat`
- `POST /api/v1/question/recognize-v2`
- `POST /api/v1/question/plan-teaching-v2`
- `POST /api/v1/question/generate-teaching-stream-v2`
- `POST /api/v1/question/clarify-step-v2`

同时也记录了 question 相关回归测试和 `traceId` 补齐。

### 2. 这些能力当前确实在共享后台本地工作区里

本次核对到的关键文件时间如下：

- `backend/app/api/v1/endpoints/studio.py`：`2026-03-24 00:16:32`
- `backend/app/api/v1/endpoints/learning_chat.py`：`2026-03-24 00:30:45`
- `backend/app/api/v1/endpoints/question.py`：`2026-03-24 02:31:07`
- `backend/app/services/question_recognize_service.py`：`2026-03-24 02:55:20`
- `backend/tests/README.md`：`2026-03-24 02:57:02`

这和“3 月 24 日凌晨补齐 app 共享链路”的记忆相符。

### 3. 但这批改动目前不是 git 已提交基线，而是本地未提交工作区

当前工作区可见：

- `backend/app/api/v1/api.py` 已修改
- `backend/app/api/v1/endpoints/studio.py` 已修改
- `backend/tests/README.md` 已修改
- `backend/app/api/v1/endpoints/learning_chat.py` 未跟踪
- `backend/app/api/v1/endpoints/question.py` 未跟踪
- `backend/app/api/v1/endpoints/voice.py` 未跟踪
- `backend/app/services/learning_chat_service.py` 未跟踪
- `backend/app/services/question_legacy_service.py` 未跟踪
- `backend/app/services/question_recognize_service.py` 未跟踪
- `backend/app/services/question_v2_service.py` 未跟踪
- `backend/app/services/studio_blackboard_service.py` 未跟踪
- `backend/app/services/studio_lecture_service.py` 未跟踪
- `backend/tests/test_question_endpoints.py` 未跟踪
- `backend/tests/test_question_recognize_service.py` 未跟踪
- `backend/tests/test_task_queue_service.py` 未跟踪

因此当前正确判断是：

`这批共享能力已经在本地工作区里，但还没有形成仓库自己的已提交、已统一文档化基线。`

---

## 当前代码事实

### 已挂上的共享能力

`backend/app/api/v1/api.py` 当前已经挂上：

- `studio`
- `learning_chat`
- `question`
- `voice`

### 当前 question 端点

`backend/app/api/v1/endpoints/question.py` 当前包含：

- legacy 兼容：
  - `/recognize`
  - `/generate-teaching`
  - `/generate-teaching-stream`
  - `/clarify-step`
- v2 主链：
  - `/recognize-v2`
  - `/plan-teaching-v2`
  - `/generate-teaching-stream-v2`
  - `/clarify-step-v2`

并且已经具备：

- `traceId` 回填
- SSE error 返回
- provided plan 校验
- legacy adapter 保留

### 当前 learning chat 端点

`backend/app/api/v1/endpoints/learning_chat.py` 当前包含：

- `POST /chat`

能力形态：

- SSE 文本流
- artifact 事件输出
- 基于教学上下文包的学习对话

### 当前 voice 端点

`backend/app/api/v1/endpoints/voice.py` 当前包含：

- `POST /stt`
- `POST /tts`

定位：

- 给 mobile/web 客户端提供兼容接口
- 维持前端原来的请求/响应形状

### 当前 studio 端点

`backend/app/api/v1/endpoints/studio.py` 当前除原有 Studio 能力外，还包含：

- `POST /generate-image`
- `POST /generate-lecture`
- `POST /generate-lecture-stream`
- `POST /generate-blackboard`
- `POST /generate-blackboard-stream`

---

## 文档状态判断

### 1. 2026-04-04 已完成一轮文档清理

清理前，仓库同时存在：

- 根目录旧入口文档
- `docs/` 文档
- `backend/` 根目录镜像文档
- 多份阶段性状态报告

清理后，当前策略改为：

- `README.md` 只保留当前入口说明
- `docs/README.md` 作为统一文档索引
- `backend/README.md` 只保留后端目录入口说明
- `docs/` 保留参考文档
- 明显过时的阶段报告与重复副本已删除

### 2. 当前最接近真实状态的文字证据

第一类：移动端仓库里的迁移账本

- `F:/1/hercux  app/APP-API-BACKEND-MIGRATION-LEDGER.md`
- `F:/1/hercux  app/APK-SHARED-BACKEND-EXECUTION-PLAN.md`

第二类：共享后台本地测试说明

- `backend/tests/README.md`

其中 `backend/tests/README.md` 已明确覆盖：

- `recognize-v2`
- `plan-teaching-v2`
- `generate-teaching-stream-v2`
- `clarify-step-v2`
- fallback / cache / traceId 负路径回归

---

## 本次核验结果

### 1. 语法级检查

运行：

```bash
python -m compileall backend/app
```

结果：

- 新增的 `question.py`、`learning_chat.py`、`voice.py` 没有单独暴露出新的语法错误
- 但整个 `backend/app` 仍被既有旧文件阻断

本次实际命中的既有语法问题：

- `backend/app/scripts/analyze_quality_trends.py`
- `backend/app/services/deepseek_search_service.py`

### 2. 测试级检查

尝试运行：

```bash
python -m pytest backend/tests/test_question_endpoints.py -q
python -m pytest backend/tests/test_question_recognize_service.py -q
python -m pytest backend/tests/test_task_queue_service.py -q
```

结果：

- 未进入测试本体
- 在导入 `backend/tests/conftest.py` 时就被配置校验拦住

缺失环境变量包括：

- `DATABASE_URL`
- `REDIS_URL`
- `NEO4J_URI`
- `NEO4J_USER`
- `NEO4J_PASSWORD`
- `SECRET_KEY`

这说明：

- 当前测试不能在“无环境变量”的裸工作区直接跑起来
- 当前 question 回归说明可信，但本机当前会话没有足够配置去直接复现

---

## 当前开发状态总结

### 已确认落在本地代码里的

- app 共享 backend 的 `question v2` 主链
- `learning/chat`
- `voice/stt`、`voice/tts`
- `studio` 的 lecture / blackboard / image 兼容接口
- question 的 fallback / trace / 回归测试文件

### 已确认还没收口完的

- 这批 3 月 24 日凌晨改动尚未提交进 git
- 当前测试运行依赖环境变量，不是开箱即跑
- 工作区里还有既有语法问题文件，导致 `compileall backend/app` 不能算通过

---

## 建议下一步

1. 把 `question.py / learning_chat.py / voice.py / 相关 services / tests` 收成一次正式提交。
2. 保持当前文档入口只收口到：
   - `README.md`
   - `ARCHITECTURE.md`
   - `docs/README.md`
   - `backend/tests/README.md`
3. 单独处理与本轮无关的既有语法问题文件：
   - `backend/app/scripts/analyze_quality_trends.py`
   - `backend/app/services/deepseek_search_service.py`

---

## 一句话结论

“凌晨已经开发好了”这件事是对的。

但它现在的真实形态是：

- 代码已经在共享后台本地工作区里
- app 侧迁移账本文档已经明确记录
- 共享后台测试说明也有补充
- 只是这批内容还没有变成共享后台仓库自己的已提交正式基线
