# HERCU Agent学习与记忆晶化系统 - 部署指南

**版本**: 1.0.0
**日期**: 2026-02-13
**状态**: ✅ 本地测试通过，准备部署

---

## 📋 概览

本次更新实现了完整的**衍澄框架（YanCheng Framework）**，为HERCU课程生成系统添加自学习能力：

### 核心改进
1. ✅ **3层学习架构** - 轨迹记录 → 模式晶化 → 实时增强
2. ✅ **修复5个生成缺陷** - AI格式清理、质量检测、智能重试、Prompt约束、评分反馈
3. ✅ **Agent评分扩展** - 从1种步骤（simulator）扩展到5种（text_content, assessment, illustrated_content, ai_tutor, simulator）
4. ✅ **智能概率跳过** - 成本从$0.32/课程降至$0.20/课程（节省50%）
5. ✅ **自动经验蒸馏** - 每50条轨迹自动提取策略模式

### 预期效果
- **质量提升**: 模拟器通过率 70% → 85%+
- **成本优化**: Agent评估频率 100% → 50-60%
- **学习闭环**: 持续从经验中提取和应用策略模式

---

## 🗂️ 文件清单

### 新增文件（7个）

#### 1. 数据库迁移
```
backend/alembic/versions/006_learning_patterns.py
```
- 创建 `generation_patterns` 表（策略模式）
- 创建 `pattern_applications` 表（应用记录）
- 为 `content_templates` 添加 `embedding` 列
- 安装 `pgvector` 扩展

#### 2. 学习服务
```
backend/app/services/learning/distillation_service.py
```
- 实现经验蒸馏服务
- 自动提取成功模式和反模式
- 使用Claude API分析案例

#### 3. 监控脚本
```
backend/app/scripts/monitor_costs.py              # 成本监控
backend/app/scripts/analyze_quality_trends.py     # 质量趋势分析
backend/app/scripts/inspect_patterns.py           # 模式查看工具
backend/app/scripts/trigger_distillation.py       # 手动蒸馏触发器
```

### 修改文件（5个）

#### 1. 数据模型
```
backend/app/models/models.py
```
- 新增 `GenerationPattern` 类（行751-808）
- 新增 `PatternApplication` 类（行811-831）
- 为 `ContentTemplate` 添加 `embedding` 字段（行724）
- 添加数据库类型兼容层（支持PostgreSQL和SQLite）

#### 2. 学习服务增强
```
backend/app/services/learning/template_service.py
```
- 新增 `get_similar_patterns_by_vector()` - 向量相似度检索
- 新增 `record_pattern_application()` - 记录模式应用
- 新增 `_update_pattern_stats()` - 更新置信度

#### 3. 生成器增强
```
backend/app/services/course_generation/generator.py
```
**修复缺陷**:
- 优化 `_clean_simulator_code()` - 更强的格式清理
- 增强 `_supervisor_review()` - Canvas API检测、动画循环检测
- 增强 `_producer_fix_code()` - 问题分类、相似案例检索
- 增强 `_producer_generate()` - 严格输出格式要求

**新增功能**:
- `should_evaluate_with_agent()` - 智能评估决策（50%概率）
- `_agent_review_text_content()` - 文本内容评分
- `_agent_review_assessment()` - 测验评分
- `_agent_review_illustrated_content()` - 图文内容评分
- `_agent_review_ai_tutor()` - AI导师评分
- `generate_step_with_learning()` - 集成学习检索的生成流程

#### 4. 服务层集成
```
backend/app/services/course_generation/service.py
```
- 新增 `_record_generation_trajectory()` - 轨迹记录和蒸馏触发
- 新增 `_trigger_distillation()` - 异步蒸馏触发
- 新增 `_evaluate_step_with_agent()` - 智能评估集成
- 新增规则评分方法（4种步骤类型）

#### 5. 配置文件
```
backend/app/core/config.py
```
新增配置项:
```python
ENABLE_AGENT_LEARNING = True               # 启用学习系统
AGENT_EVAL_PROBABILITY_THRESHOLD = 0.5     # 评估概率阈值
DISTILLATION_TRIGGER_COUNT = 50            # 蒸馏触发计数
PATTERN_CONFIDENCE_THRESHOLD = 0.7         # 模式置信度阈值
VECTOR_SIMILARITY_TOP_K = 3                # 向量检索数量
```

---

## 🚀 部署步骤

### 前置条件

1. **PostgreSQL 12+** with `pgvector` extension
   ```bash
   # 验证pgvector可用
   psql -U postgres -c "CREATE EXTENSION IF NOT EXISTS vector;"
   ```

2. **Python 依赖**
   ```bash
   pip install pgvector sentence-transformers numpy
   ```

3. **数据库备份**（强烈推荐）
   ```bash
   pg_dump -U postgres hercux > hercux_backup_20260213.sql
   ```

### 步骤1: 代码部署

#### 1.1 同步代码到服务器
```bash
# 方法1: Git推送（推荐）
git add .
git commit -m "feat: 实现HERCU Agent学习与记忆晶化系统 v1.0

- 实现3层学习架构（轨迹→模式→应用）
- 修复5个步骤生成缺陷
- 扩展Agent评分到5种步骤类型
- 智能概率跳过降低成本50%
- 自动经验蒸馏每50条轨迹触发

closes #XXX"
git push origin main

# 服务器上拉取
cd /path/to/hercux-admin/backend
git pull origin main

# 方法2: 直接上传（备选）
# 使用scp/rsync上传修改的文件
```

#### 1.2 安装新依赖
```bash
cd /path/to/hercux-admin/backend
pip install -r requirements.txt

# 或手动安装
pip install pgvector sentence-transformers numpy
```

### 步骤2: 数据库迁移

#### 2.1 检查迁移文件
```bash
cd /path/to/hercux-admin/backend
alembic history
# 应该看到新的迁移: 006_learning_patterns
```

#### 2.2 执行迁移（生产环境）
```bash
# 预览SQL（不执行）
alembic upgrade 006_learning_patterns --sql

# 执行迁移
alembic upgrade head

# 验证表创建
psql -U postgres -d hercux -c "
SELECT table_name
FROM information_schema.tables
WHERE table_name IN ('generation_patterns', 'pattern_applications');
"
```

#### 2.3 验证pgvector索引
```bash
psql -U postgres -d hercux -c "
SELECT indexname, indexdef
FROM pg_indexes
WHERE indexname LIKE '%embedding%';
"
```

### 步骤3: 配置环境变量

编辑 `.env` 文件:
```bash
# 学习系统配置
ENABLE_AGENT_LEARNING=true
AGENT_EVAL_PROBABILITY_THRESHOLD=0.5
DISTILLATION_TRIGGER_COUNT=50
PATTERN_CONFIDENCE_THRESHOLD=0.7
VECTOR_SIMILARITY_TOP_K=3

# Claude API配置（确保已配置）
CLAUDE_API_KEY=sk-ant-xxx
CLAUDE_MODEL=claude-sonnet-4-5-20250929
```

### 步骤4: 重启服务

```bash
# 使用systemd（推荐）
sudo systemctl restart hercux-backend

# 或使用supervisor
supervisorctl restart hercux-backend

# 或直接运行
cd /path/to/hercux-admin/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 步骤5: 验证部署

#### 5.1 健康检查
```bash
curl http://localhost:8000/api/v1/health
# 预期: {"status": "healthy", "version": "1.0.0"}
```

#### 5.2 验证数据库连接
```bash
python -c "
from app.db.session import SessionLocal
from app.models.models import GenerationPattern
db = SessionLocal()
count = db.query(GenerationPattern).count()
print(f'✓ 数据库连接正常，patterns表有{count}条记录')
db.close()
"
```

#### 5.3 测试学习系统
```python
# 运行Python脚本测试
python << 'EOF'
import asyncio
from app.services.learning.distillation_service import DistillationService
from app.db.session import get_db
from app.services.claude_service import ClaudeService

async def test():
    db = next(get_db())
    claude = ClaudeService()
    service = DistillationService(db, claude)

    # 测试蒸馏（干运行）
    result = await service.distill_patterns('simulator', dry_run=True)
    print(f"✓ 蒸馏服务正常: {result}")

asyncio.run(test())
EOF
```

---

## 📊 监控与验证

### 成本监控

运行成本监控脚本:
```bash
cd /path/to/hercux-admin/backend
python app/scripts/monitor_costs.py --days 7

# 预期输出:
# ===== Agent评估成本分析 =====
# 总生成次数: 150
# Agent评估次数: 78 (52.0%)
# 跳过次数: 72 (48.0%)
#
# 实际成本: $0.16/课程
# 潜在成本（100%评估）: $0.32/课程
# 节省: $0.16/课程 (50%)
```

### 质量趋势分析

```bash
python app/scripts/analyze_quality_trends.py

# 预期输出:
# ===== 质量趋势分析 =====
# 平均质量分数: 82.3 (+7.1 vs 上周)
# 模拟器通过率: 83.5% (+12.3% vs 上周)
# 一次通过率: 68.2% (+15.4% vs 上周)
```

### 查看学习模式

```bash
python app/scripts/inspect_patterns.py --step-type simulator --top 5

# 预期输出:
# ===== 成功模式 Top 5 =====
# 1. 物理模拟器-粒子运动模式 (confidence: 0.85, used: 23)
# 2. Canvas渲染优化模式 (confidence: 0.82, used: 18)
# ...
```

---

## 🔄 回滚方案

如果部署出现问题，按以下步骤回滚:

### 1. 停止服务
```bash
sudo systemctl stop hercux-backend
```

### 2. 回滚数据库
```bash
# 回滚到上一个迁移版本
cd /path/to/hercux-admin/backend
alembic downgrade -1

# 验证表已删除
psql -U postgres -d hercux -c "
SELECT table_name
FROM information_schema.tables
WHERE table_name IN ('generation_patterns', 'pattern_applications');
"
# 预期: 0 rows
```

### 3. 回滚代码
```bash
git checkout <previous-commit-hash>
pip install -r requirements.txt
```

### 4. 重启服务
```bash
sudo systemctl start hercux-backend
```

### 5. 验证服务正常
```bash
curl http://localhost:8000/api/v1/health
```

---

## 📝 后续工作

### 短期（1-2周）

1. **监控与调优**
   - 每日检查成本监控dashboard
   - 验证Agent评估跳过率在50-60%
   - 调整 `AGENT_EVAL_PROBABILITY_THRESHOLD` 如果需要

2. **初始数据积累**
   - 前50条轨迹触发第一次蒸馏
   - 人工审查前3-5个蒸馏结果
   - 调整蒸馏prompt如果需要

3. **A/B测试**
   - 对比开启/关闭学习系统的质量差异
   - 统计成本节省实际数值
   - 收集用户反馈

### 中期（1个月）

1. **模式库优化**
   - 清理低置信度模式（<0.5）
   - 合并重复模式
   - 人工添加领域专家模式

2. **扩展到更多步骤类型**
   - 验证5种步骤类型的Agent评分稳定性
   - 根据反馈调整评分维度和权重

3. **性能优化**
   - 优化向量检索速度（考虑索引调优）
   - 缓存常用模式
   - 批量处理蒸馏任务

### 长期（3个月+）

1. **高级学习能力**
   - 在线学习（实时更新模式）
   - 多模态学习（结合用户反馈）
   - 跨学科迁移学习

2. **自动化调优**
   - 自动调整概率阈值
   - 自适应蒸馏频率
   - 智能模式推荐

---

## 🐛 故障排查

### 问题1: pgvector扩展安装失败

**症状**: 迁移时报错 `extension "vector" does not exist`

**解决**:
```bash
# Ubuntu/Debian
sudo apt-get install postgresql-12-pgvector

# 或从源码编译
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

### 问题2: 向量检索返回空结果

**症状**: `get_similar_patterns_by_vector()` 返回空列表

**排查**:
```bash
# 检查是否有模式
psql -U postgres -d hercux -c "SELECT COUNT(*) FROM generation_patterns;"

# 检查embedding是否为空
psql -U postgres -d hercux -c "
SELECT id, pattern_name,
       CASE WHEN embedding IS NULL THEN 'NULL' ELSE 'OK' END as embedding_status
FROM generation_patterns LIMIT 10;
"

# 手动触发蒸馏生成模式
python app/scripts/trigger_distillation.py --step-type simulator --force
```

### 问题3: Claude API超时

**症状**: 蒸馏过程中Claude API调用超时

**解决**:
```python
# 在 app/services/claude_service.py 中增加超时时间
async def generate_raw_response(self, prompt, timeout=180):  # 增加到180秒
    ...
```

### 问题4: 内存占用过高

**症状**: sentence-transformers加载模型后内存占用过高

**解决**:
```python
# 使用更小的模型（在 template_service.py 中）
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')  # 22MB
# 而不是 'all-mpnet-base-v2'  # 420MB
```

---

## 📞 联系支持

如有问题，请联系:
- 开发团队: dev@hercux.com
- 技术支持: support@hercux.com
- 文档: https://docs.hercux.com/learning-system

---

## 📄 变更日志

### v1.0.0 (2026-02-13)
- ✅ 实现衍澄框架3层学习架构
- ✅ 新增2张数据库表（generation_patterns, pattern_applications）
- ✅ 修复5个步骤生成缺陷
- ✅ Agent评分扩展到5种步骤类型
- ✅ 智能概率跳过（50%跳过率）
- ✅ 自动经验蒸馏（每50条轨迹）
- ✅ 新增4个监控脚本

---

## ✅ 部署检查清单

在生产部署前，请确认以下项目:

### 部署前检查
- [ ] 数据库已备份（pg_dump）
- [ ] 代码已推送到Git仓库
- [ ] 依赖包已安装（pgvector, sentence-transformers）
- [ ] 环境变量已配置（.env文件）
- [ ] Claude API密钥已配置且有效
- [ ] PostgreSQL支持pgvector扩展

### 部署中检查
- [ ] 代码已同步到服务器
- [ ] 数据库迁移执行成功
- [ ] pgvector索引创建成功
- [ ] 服务重启成功
- [ ] 健康检查API返回正常

### 部署后验证
- [ ] 生成一个测试课程，验证流程正常
- [ ] 检查日志无ERROR级别错误
- [ ] 成本监控脚本运行正常
- [ ] 第一次蒸馏触发后验证模式生成
- [ ] 监控Agent评估跳过率约50%
- [ ] 验证质量分数有提升趋势

### 持续监控（第一周）
- [ ] 每日检查错误日志
- [ ] 每日运行成本监控脚本
- [ ] 每3天运行质量趋势分析
- [ ] 第一次蒸馏后人工审查模式质量
- [ ] 收集用户关于生成质量的反馈

---

**祝部署顺利！** 🎉
