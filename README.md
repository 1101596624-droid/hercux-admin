# HERCU Admin / Shared Backend

这个仓库当前包含三层内容：

- `app/`、`components/`、`stores/`：管理端 Next.js 应用
- `electron/`、`dist-electron*`：桌面壳与打包产物
- `backend/`：共享 FastAPI 后端

当前最需要按代码事实理解的部分在共享后端，尤其是：

- `backend/app/api/v1/endpoints/studio.py`
- `backend/app/api/v1/endpoints/learning_chat.py`
- `backend/app/api/v1/endpoints/question.py`
- `backend/app/api/v1/endpoints/voice.py`
- `backend/tests/README.md`

## 先读这些

按当前有效性，建议阅读顺序：

1. [docs/README.md](docs/README.md)
2. [docs/SHARED-BACKEND-STATUS-2026-04-04.md](docs/SHARED-BACKEND-STATUS-2026-04-04.md)
3. [ARCHITECTURE.md](ARCHITECTURE.md)
4. [backend/tests/README.md](backend/tests/README.md)

## 当前判断

- 仓库早期有大量 1 月和 2 月阶段性文档，很多已经不再代表当前共享后端现状。
- 2026-04-04 已做一轮文档清理：
  - 删除了重复副本
  - 删除了明显过时的阶段报告
  - 保留 `docs/` 作为主要文档目录
- 共享后端的 app 对接能力以代码和测试说明为准，不要只看旧 README 推断。

## 开发入口

管理端：

```bash
npm run dev
```

共享后端：

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

说明：

- 本地实际端口可能按你的 `.env`、代理或联调脚本调整，不应再把旧文档中的 `8000` 或 `8001` 当成唯一事实来源。
- 测试和后端启动都依赖环境变量，见 [backend/README.md](backend/README.md) 和 [backend/tests/README.md](backend/tests/README.md)。

## 文档策略

- 当前文档主目录：`docs/`
- 当前后端测试说明：`backend/tests/README.md`
- 代码级真实路由入口：`backend/app/api/v1/api.py`

如果你要继续整理或扩展共享后端，优先更新：

- `README.md`
- `ARCHITECTURE.md`
- `docs/README.md`
- `docs/SHARED-BACKEND-STATUS-2026-04-04.md`

而不是再新增一份平行状态报告。
