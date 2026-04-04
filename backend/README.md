# Shared Backend

这个目录是共享 FastAPI 后端。

当前文档已统一到仓库根部 `docs/`，这里不再保留一套平行镜像文档。

## 当前入口

优先阅读：

1. [../docs/README.md](../docs/README.md)
2. [../docs/SHARED-BACKEND-STATUS-2026-04-04.md](../docs/SHARED-BACKEND-STATUS-2026-04-04.md)
3. [../ARCHITECTURE.md](../ARCHITECTURE.md)
4. [tests/README.md](tests/README.md)

## 本地启动

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

说明：

- 当前测试和启动都依赖环境变量。
- 不要把旧文档里的固定端口当成唯一事实来源。
- 当前真实路由入口是 `app/api/v1/api.py`。

## 当前重点模块

- `app/api/v1/endpoints/studio.py`
- `app/api/v1/endpoints/learning_chat.py`
- `app/api/v1/endpoints/question.py`
- `app/api/v1/endpoints/voice.py`

## 测试说明

详见 [tests/README.md](tests/README.md)。
