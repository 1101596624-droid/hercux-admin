# HERCU Backend Tests

This directory contains unit and integration tests for the shared backend.

## Test Structure

```text
tests/
├── conftest.py
├── test_auth.py
├── test_courses.py
├── test_nodes.py
├── test_progress.py
├── test_ai.py
├── test_users.py
├── test_statistics_service.py
├── test_question_endpoints.py
├── test_question_recognize_service.py
└── test_task_queue_service.py
```

## Prerequisites

当前测试不是“零配置即跑”。

在导入 `app.main` 前，至少需要提供这些环境变量：

- `DATABASE_URL`
- `REDIS_URL`
- `NEO4J_URI`
- `NEO4J_USER`
- `NEO4J_PASSWORD`
- `SECRET_KEY`

如果这些变量缺失，pytest 会在加载 `conftest.py` 时直接失败，而不会进入具体测试用例。

## Running Tests

安装依赖：

```bash
pip install -r requirements.txt
```

运行全部测试：

```bash
pytest
```

运行单个测试文件：

```bash
pytest tests/test_courses.py
```

app question teaching 回归：

```bash
python -m pytest tests/test_question_endpoints.py
```

recognize-v2 service 回归：

```bash
python -m pytest tests/test_question_recognize_service.py
```

task queue 回归：

```bash
python -m pytest tests/test_task_queue_service.py
```

## Question Regression Coverage

- `test_question_endpoints.py` 覆盖：
  - `recognize-v2`
  - `plan-teaching-v2`
  - `generate-teaching-stream-v2`
  - `clarify-step-v2`
  - legacy stream adapter 的 `traceId` / 协议回归
- 负路径覆盖：
  - `recognize-v2` service exception
  - `plan-teaching-v2` service exception
  - `generate-teaching-stream-v2` 非法 provided plan
  - `clarify-step-v2` 参数缺失与 service exception
- `test_question_recognize_service.py` 覆盖：
  - 上游视觉失败时的保守草稿 fallback
  - 相同请求的缓存命中
  - electrical domain 的 fallback skeleton

## Fixtures

`conftest.py` 提供的常用 fixture 包括：

- `db_session`
- `client`
- `test_user`
- `test_user_token`
- `auth_headers`
- `test_course`
- `test_nodes`
- `test_progress`

## Notes

- 当前 question 相关测试说明比旧 README 更接近 2026-03-24 之后的共享后端现状。
- 如果测试行为与旧文档冲突，以代码和本文件为准。
