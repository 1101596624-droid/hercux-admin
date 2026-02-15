# HERCU Agent学习与记忆晶化系统 - 技术架构文档

**版本**: 1.0.0
**日期**: 2026-02-13
**作者**: HERCU开发团队

---

## 📐 系统架构概览

### 设计理念：衍澄框架 (YanCheng Framework)

衍澄框架是一个三层递进式学习架构，模拟人类学习过程：
1. **经历** → 记录原始轨迹（Raw Trajectories）
2. **反思** → 提炼策略模式（Pattern Crystallization）
3. **应用** → 实时增强生成（Real-time Enhancement）

```
┌─────────────────────────────────────────────────────────────┐
│                    衍澄框架 (YanCheng Framework)                    │
└─────────────────────────────────────────────────────────────┘

Layer 1: 轨迹记录层 (Trajectory Recording)
┌───────────────────────────────────────────────────────────┐
│  ┌──────────────┐   ┌──────────────────┐   ┌───────────┐  │
│  │ content_     │   │ quality_         │   │ pattern_  │  │
│  │ templates    │   │ evaluations      │   │ applic... │  │
│  └──────────────┘   └──────────────────┘   └───────────┘  │
│      高质量模板          质量评估历史            模式应用记录      │
└───────────────────────────────────────────────────────────┘
                           ↓
Layer 2: 模式晶化层 (Pattern Crystallization)
┌───────────────────────────────────────────────────────────┐
│  ┌─────────────────────────────────────────────────────┐  │
│  │         generation_patterns (策略模式表)              │  │
│  ├─────────────────────────────────────────────────────┤  │
│  │  • 成功模式 (Success Patterns)                       │  │
│  │    - 什么有效? 为什么有效?                            │  │
│  │  • 反模式 (Anti-Patterns)                            │  │
│  │    - 什么会失败? 如何避免/恢复?                       │  │
│  │  • 置信度 (Confidence)                               │  │
│  │    - success_count / use_count                      │  │
│  │  • 向量embedding (Vector Embedding)                  │  │
│  │    - 384维语义表示 (sentence-transformers)           │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│       每50条轨迹自动触发蒸馏 (Distillation)                   │
│       使用Claude分析案例 → 提取共性 → 保存为模式               │
└───────────────────────────────────────────────────────────┘
                           ↓
Layer 3: 实时增强层 (Real-time Enhancement)
┌───────────────────────────────────────────────────────────┐
│   生成前：检索相似模式 (Vector Similarity Search)            │
│   ──────────────────────────────────────────────────      │
│   用户请求 → embedding → 向量检索top-3模式 → 注入prompt     │
│                                                             │
│   生成中：智能概率评估 (Smart Probabilistic Evaluation)      │
│   ──────────────────────────────────────────────────      │
│   simulator: 100%评估 (关键步骤，永远评估)                    │
│   其他类型: 50%评估 (基于样本量、方差、概率)                   │
│                                                             │
│   生成后：记录轨迹并更新置信度                                │
│   ──────────────────────────────────────────────────      │
│   保存质量评分 → 记录模式应用 → 贝叶斯更新置信度              │
└───────────────────────────────────────────────────────────┘
```

---

## 🗄️ 数据模型设计

### 核心表结构

#### 1. generation_patterns (策略模式表)

**设计思想**: 存储从历史数据中蒸馏出的策略模式，支持语义检索和置信度评估。

```sql
CREATE TABLE generation_patterns (
    id SERIAL PRIMARY KEY,

    -- 元数据
    pattern_type VARCHAR(50) NOT NULL,  -- 'success' / 'anti_pattern'
    step_type VARCHAR(50) NOT NULL,     -- 步骤类型
    subject VARCHAR(100),                -- 学科领域

    -- 模式内容
    pattern_name VARCHAR(255) NOT NULL,
    pattern_description TEXT NOT NULL,
    trigger_conditions JSONB,           -- 何时触发
    solution_strategy TEXT,             -- 如何应用

    -- 学习统计
    confidence FLOAT DEFAULT 0.5,       -- 置信度 (贝叶斯更新)
    use_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,

    -- 向量检索
    embedding VECTOR(384),              -- pgvector索引

    -- 源数据追溯
    source_templates JSONB,
    created_from_count INTEGER,

    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    last_used_at TIMESTAMP,

    INDEX idx_embedding USING ivfflat (embedding vector_cosine_ops)
);
```

**关键设计点**:
- **向量embedding**: 使用sentence-transformers生成384维向量，支持语义相似度检索
- **置信度计算**: Bayesian update → `confidence = (success + 2) / (use + 4)`
- **JSONB字段**: 灵活存储复杂结构（触发条件、源模板列表）
- **IVFFlat索引**: 优化大规模向量检索性能

#### 2. pattern_applications (模式应用记录)

**设计思想**: 跟踪每次模式应用的效果，用于持续评估和改进模式。

```sql
CREATE TABLE pattern_applications (
    id SERIAL PRIMARY KEY,
    pattern_id INTEGER REFERENCES generation_patterns(id),

    -- 应用上下文
    step_type VARCHAR(50) NOT NULL,
    subject VARCHAR(100),
    topic VARCHAR(255),
    original_input JSONB,              -- 原始请求

    -- 应用结果
    applied_strategy TEXT,
    result_quality FLOAT,              -- 质量分数
    success BOOLEAN,                   -- 是否成功

    applied_at TIMESTAMP,

    INDEX idx_pattern_id (pattern_id),
    INDEX idx_success (success)
);
```

**关键设计点**:
- **双向关联**: pattern_id → 追踪来源模式；original_input → 复现上下文
- **成功率统计**: 用于更新pattern的confidence
- **时间索引**: 支持时间序列分析和趋势预测

#### 3. content_templates (增强版)

**修改内容**: 添加向量embedding字段，支持语义检索。

```sql
ALTER TABLE content_templates
ADD COLUMN embedding VECTOR(384);

CREATE INDEX idx_content_embedding
ON content_templates
USING ivfflat (embedding vector_cosine_ops);
```

### 数据流转图

```
┌────────────────┐
│  用户生成请求   │
└────────────────┘
         ↓
┌────────────────────────────────────────┐
│  1. 向量检索相似模式                     │
│     • embedding(request) → query       │
│     • cosine_distance < threshold      │
│     • SELECT TOP 3 patterns            │
└────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────┐
│  2. 增强Prompt生成                      │
│     • 原始prompt + 模式策略             │
│     • Claude API调用                   │
└────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────┐
│  3. 质量评估                            │
│     • 规则评分 (0-80)                   │
│     • Agent评分 (0-20, 50%概率)        │
│     • 总分 = 规则分 + Agent分           │
└────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────┐
│  4. 轨迹记录                            │
│     • INSERT quality_evaluations       │
│     • INSERT pattern_applications      │
│     • UPDATE pattern stats             │
└────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────┐
│  5. 触发蒸馏? (每50条)                  │
│     • YES → distill_patterns()         │
│     • NO → 继续累积                     │
└────────────────────────────────────────┘
```

---

## 🧠 核心算法

### 1. 向量相似度检索

**实现**: `template_service.py::get_similar_patterns_by_vector()`

```python
async def get_similar_patterns_by_vector(
    self,
    query_text: str,
    step_type: str,
    pattern_type: str = 'success',
    top_k: int = 3,
    min_confidence: float = 0.7
) -> List[GenerationPattern]:
    """基于余弦距离的向量相似度检索"""

    # 1. 生成query的embedding
    embedding = self.embedding_model.encode(query_text)

    # 2. 向量相似度查询 (余弦距离)
    query = (
        select(GenerationPattern)
        .where(
            and_(
                GenerationPattern.step_type == step_type,
                GenerationPattern.pattern_type == pattern_type,
                GenerationPattern.confidence >= min_confidence
            )
        )
        .order_by(
            GenerationPattern.embedding.cosine_distance(embedding)
        )
        .limit(top_k)
    )

    return await self.db.execute(query).scalars().all()
```

**算法特点**:
- **余弦距离**: `1 - cosine_similarity`，值越小越相似
- **过滤条件**: step_type匹配 + 置信度阈值
- **Top-K选择**: 默认返回3个最相似模式
- **IVFFlat索引**: 将O(n)降低至O(log n)

### 2. 智能概率评估

**实现**: `generator.py::should_evaluate_with_agent()`

```python
async def should_evaluate_with_agent(
    self,
    step_type: str,
    context: Dict[str, Any],
    recent_scores: List[float]
) -> tuple[bool, str]:
    """基于学习价值的智能决策"""

    # 规则1: simulator永远评估 (最关键)
    if step_type == 'simulator':
        return True, "simulator类型必须评估"

    # 规则2: 样本充足度检查
    sample_count = await self._count_samples(step_type, context['subject'])
    if sample_count < 30:
        return True, f"样本不足({sample_count}<30)"

    # 规则3: 分数方差检查 (稳定性)
    if recent_scores and len(recent_scores) >= 5:
        variance = np.var(recent_scores)
        if variance > 100:
            return True, f"分数不稳定(方差{variance:.1f})"

    # 规则4: 概率采样 (50%)
    if random.random() < 0.5:
        return True, "概率采样选中"
    else:
        estimated_score = self._estimate_agent_score(context['rule_score'])
        return False, f"跳过(估算Agent分:{estimated_score}/20)"
```

**决策树**:
```
                  [开始]
                     |
            step_type == 'simulator'?
                 /        \
               YES         NO
                |           |
              评估        样本<30?
                         /      \
                       YES       NO
                        |         |
                      评估      方差>100?
                               /      \
                             YES       NO
                              |         |
                            评估     random()<0.5?
                                     /        \
                                   YES        NO
                                    |          |
                                  评估      跳过(估算)
```

**成本分析**:
- **Before**: 100%评估 × 16步骤/课程 × $0.02/次 = **$0.32/课程**
- **After**: 50%评估 × 16步骤/课程 × $0.02/次 = **$0.16/课程**
- **节省**: **50%成本降低**

### 3. 经验蒸馏算法

**实现**: `distillation_service.py::distill_patterns()`

```python
async def distill_patterns(
    self,
    step_type: str,
    min_trajectories: int = 50
) -> Dict[str, Any]:
    """自动经验蒸馏流程"""

    # 1. 获取高质量案例 (质量分≥85)
    success_cases = await self._get_recent_trajectories(
        step_type,
        quality_threshold=85.0,
        limit=30
    )

    # 2. 获取失败案例 (质量分<60)
    failure_cases = await self._get_recent_trajectories(
        step_type,
        quality_threshold=60.0,
        success=False,
        limit=20
    )

    # 3. 使用Claude提取成功模式
    success_patterns = await self._extract_success_patterns(
        success_cases,
        step_type
    )

    # 4. 提取反模式 (失败模式)
    anti_patterns = await self._extract_anti_patterns(
        failure_cases,
        step_type
    )

    # 5. 保存到数据库 (去重)
    for pattern in success_patterns + anti_patterns:
        await self._save_pattern(pattern, step_type)

    return {
        'success_patterns': len(success_patterns),
        'anti_patterns': len(anti_patterns),
        'total_saved': saved_count
    }
```

**Claude Prompt示例** (提取成功模式):
```
分析以下30个高质量simulator步骤案例，提取成功模式。

【案例】
Case 1: {title}, Score: 92
{code_snippet}

Case 2: {title}, Score: 88
{code_snippet}
...

【任务】
找出这些成功案例的共同特征：
1. 结构模式 (如何组织代码)
2. 表达技巧 (如何传达概念)
3. 交互设计 (如何引导学习)

【输出格式】
[
  {
    "pattern_name": "物理模拟器-粒子运动模式",
    "description": "使用requestAnimationFrame + 粒子数组实现...",
    "trigger_conditions": {"subject": "physics", "has_particles": true},
    "solution_strategy": "1. 定义粒子类 2. 初始化数组 3. 动画循环...",
    "confidence": 0.8
  },
  ...
]
```

**去重策略**:
```python
async def _save_pattern(self, pattern: Dict, step_type: str):
    # 1. 生成内容hash
    content_hash = hashlib.sha256(
        f"{pattern['pattern_name']}{pattern['description']}".encode()
    ).hexdigest()

    # 2. 检查是否已存在相似模式
    existing = await self.db.query(GenerationPattern).filter(
        and_(
            GenerationPattern.step_type == step_type,
            GenerationPattern.pattern_name == pattern['pattern_name']
        )
    ).first()

    if existing:
        # 合并：增加created_from_count
        existing.created_from_count += pattern.get('source_count', 1)
        existing.confidence = (existing.confidence + pattern['confidence']) / 2
    else:
        # 新建
        new_pattern = GenerationPattern(**pattern)
        self.db.add(new_pattern)
```

### 4. 贝叶斯置信度更新

**实现**: `template_service.py::_update_pattern_stats()`

```python
async def _update_pattern_stats(self, pattern_id: int, success: bool):
    pattern = await self.db.get(GenerationPattern, pattern_id)

    # 更新计数
    pattern.use_count += 1
    if success:
        pattern.success_count += 1

    # 贝叶斯更新 (Beta先验)
    # Prior: Beta(α=2, β=2) → 先验置信度 = 0.5
    alpha_prior = 2
    beta_prior = 2

    confidence = (pattern.success_count + alpha_prior) / \
                 (pattern.use_count + alpha_prior + beta_prior)

    pattern.confidence = confidence
    pattern.last_used_at = datetime.utcnow()

    await self.db.commit()
```

**为什么使用贝叶斯更新？**
- **小样本鲁棒性**: 初始几次应用不会导致极端置信度（0或1）
- **Prior设置**: Beta(2,2) → 初始期望 = 0.5（中立态度）
- **收敛性**: 随着use_count增加，prior影响减弱，逐渐逼近真实成功率

**置信度演化示例**:
```
use_count  success_count  confidence  说明
    1           1          0.75       首次成功，略高于0.5
    2           1          0.60       第二次失败，回落
    5           4          0.67       多次验证，稳步上升
   20          18          0.83       大样本，高置信度
   50          25          0.52       接近真实50%成功率
```

---

## 🔧 服务层设计

### 服务依赖图

```
CourseGenerationService (主服务)
    │
    ├─→ CourseGenerator (生成器)
    │      ├─→ ClaudeService (Claude API)
    │      ├─→ UnifiedTemplateService (模板&模式检索)
    │      └─→ DistillationService (经验蒸馏)
    │
    ├─→ UnifiedTemplateService (学习服务)
    │      ├─→ SentenceTransformer (向量embedding)
    │      └─→ Database (PostgreSQL + pgvector)
    │
    └─→ DistillationService (蒸馏服务)
           ├─→ ClaudeService (案例分析)
           ├─→ UnifiedTemplateService (模式保存)
           └─→ Database (轨迹读取)
```

### 关键服务职责

#### CourseGenerationService
- **职责**: 课程生成主流程编排
- **核心方法**:
  - `generate_course()` - 生成完整课程
  - `_generate_chapter()` - 生成单个章节
  - `_generate_step_with_learning()` - 集成学习的步骤生成
  - `_record_generation_trajectory()` - 记录轨迹并触发蒸馏
  - `_trigger_distillation()` - 异步蒸馏触发

#### CourseGenerator
- **职责**: 单个步骤内容生成
- **核心方法**:
  - `generate_simulator_code_progressive()` - 模拟器渐进式生成
  - `_producer_generate()` - 内容生产（集成模式检索）
  - `_supervisor_review()` - 质量监督评审
  - `_producer_fix_code()` - 智能修复
  - `should_evaluate_with_agent()` - 智能评估决策
  - `_agent_review_*()` - 5种步骤类型的Agent评分

#### UnifiedTemplateService
- **职责**: 模板和模式管理
- **核心方法**:
  - `get_similar_patterns_by_vector()` - 向量检索
  - `record_pattern_application()` - 记录应用
  - `_update_pattern_stats()` - 更新置信度
  - `_generate_embedding()` - 生成向量

#### DistillationService
- **职责**: 经验蒸馏
- **核心方法**:
  - `distill_patterns()` - 主蒸馏流程
  - `_extract_success_patterns()` - 提取成功模式
  - `_extract_anti_patterns()` - 提取反模式
  - `_get_recent_trajectories()` - 获取轨迹
  - `_save_pattern()` - 保存模式（去重）

---

## 🔄 生成流程详解

### 完整生成流程 (含学习增强)

```
┌─────────────────────────────────────────────────────────────┐
│                     用户请求生成课程                          │
│   {subject: "physics", topic: "projectile_motion"}          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 1: 检索相似模式 (Vector Search)                        │
│  ────────────────────────────────────────                   │
│  query = f"{subject} {topic} simulator"                     │
│  embedding = encode(query)  # 384-dim vector               │
│  patterns = SELECT * FROM generation_patterns               │
│             WHERE step_type = 'simulator'                   │
│             ORDER BY embedding <=> query_embedding          │
│             LIMIT 3                                         │
│                                                              │
│  Result: [                                                  │
│    Pattern1: "物理模拟器-抛体运动模式" (confidence: 0.85)       │
│    Pattern2: "Canvas粒子系统优化" (confidence: 0.78)          │
│    Pattern3: "交互控制最佳实践" (confidence: 0.82)             │
│  ]                                                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 2: 构建增强Prompt                                      │
│  ────────────────────────────────────────────               │
│  base_prompt = "生成抛体运动模拟器..."                         │
│                                                              │
│  enhanced_prompt = base_prompt + f"""                       │
│  【相关成功模式】                                              │
│  1. {Pattern1.solution_strategy}                           │
│     - 关键点: {Pattern1.description}                        │
│  2. {Pattern2.solution_strategy}                           │
│     ...                                                     │
│                                                              │
│  【避免以下反模式】                                            │
│  - 避免使用setInterval (使用requestAnimationFrame)          │
│  - 避免全局变量污染                                           │
│  """                                                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 3: 渐进式生成 (Progressive Generation)                │
│  ────────────────────────────────────────────               │
│  for round in range(1, 4):                                 │
│      # 生成内容                                              │
│      code = await claude.generate(enhanced_prompt)         │
│      code = _clean_simulator_code(code)                    │
│                                                              │
│      # 质量检查                                              │
│      rule_score, issues = _supervisor_review(code)         │
│                                                              │
│      if rule_score >= 60:  # 通过                           │
│          break                                              │
│      else:  # 修复                                          │
│          # 检索相似失败案例的解决方案                          │
│          fix_patterns = get_similar_patterns(              │
│              query=f"修复{', '.join(issues)}",              │
│              pattern_type='anti_pattern'                   │
│          )                                                  │
│          enhanced_prompt = build_fix_prompt(               │
│              code, issues, fix_patterns                    │
│          )                                                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 4: Agent评分 (Smart Evaluation)                       │
│  ────────────────────────────────────────────               │
│  # 智能决策                                                  │
│  should_eval, reason = should_evaluate_with_agent(         │
│      step_type='simulator',                                │
│      context={...},                                        │
│      recent_scores=[...]                                   │
│  )                                                          │
│                                                              │
│  if should_eval:                                            │
│      # 调用Claude Agent评分                                 │
│      agent_score, feedback = await _agent_review_simulator(│
│          code, title, learning_objectives                  │
│      )                                                      │
│  else:                                                      │
│      # 估算Agent分数                                         │
│      agent_score = _estimate_agent_score(rule_score)       │
│      feedback = "跳过Agent评估（估算）"                       │
│                                                              │
│  total_score = rule_score + agent_score  # 满分100         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 5: 记录轨迹和模式应用                                   │
│  ────────────────────────────────────────────               │
│  # 保存质量评估                                              │
│  INSERT INTO quality_evaluations (                         │
│      content_type='simulator',                             │
│      quality_score=total_score,                            │
│      score_breakdown={rule: 72, agent: 18},                │
│      ...                                                    │
│  )                                                          │
│                                                              │
│  # 记录模式应用                                              │
│  for pattern in patterns:                                  │
│      INSERT INTO pattern_applications (                    │
│          pattern_id=pattern.id,                            │
│          was_successful=(total_score >= 75),               │
│          quality_score=total_score,                        │
│          ...                                                │
│      )                                                      │
│      # 更新模式置信度                                         │
│      UPDATE generation_patterns                            │
│      SET use_count = use_count + 1,                        │
│          success_count = success_count + (total_score>=75),│
│          confidence = (success+2) / (use+4)                │
│      WHERE id = pattern.id                                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 6: 触发蒸馏? (Distillation Trigger)                   │
│  ────────────────────────────────────────────               │
│  trajectory_counter += 1                                   │
│                                                              │
│  if trajectory_counter % 50 == 0:                          │
│      # 异步触发蒸馏                                           │
│      asyncio.create_task(                                  │
│          _trigger_distillation()                           │
│      )                                                      │
│                                                              │
│      # 蒸馏流程 (后台运行):                                   │
│      # 1. 获取最近50条轨迹                                   │
│      # 2. 分类成功/失败案例                                  │
│      # 3. 使用Claude分析并提取模式                           │
│      # 4. 保存新模式到generation_patterns                   │
│      # 5. 触发向量索引重建                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛡️ 缺陷修复详解

### 缺陷1: AI返回格式化文本

**问题**: Claude有时返回markdown包裹或JSON包裹的代码。

**修复前**:
```python
def _clean_simulator_code(code: str) -> str:
    # 简单移除markdown标记
    if code.startswith('```'):
        code = '\n'.join(code.split('\n')[1:-1])
    return code
```

**修复后**: 4阶段统一清理流程
```python
def _clean_simulator_code(self, code: str) -> str:
    # Stage 1: 移除markdown包裹
    code = self._remove_markdown_wrapper(code)

    # Stage 2: 提取JSON包裹
    code = self._extract_from_json_wrapper(code)

    # Stage 3: 提取HTML核心
    code = self._extract_html_content(code)

    # Stage 4: 验证HTML完整性
    if not self._is_valid_html_structure(code):
        logger.warning("Incomplete HTML structure")

    return code.strip()

def _remove_markdown_wrapper(self, code: str) -> str:
    """移除```html ... ```包裹"""
    patterns = [
        r'^```html\s*\n(.*?)\n```$',
        r'^```\s*\n(.*?)\n```$',
        r'^~~~html\s*\n(.*?)\n~~~$',
    ]
    for pattern in patterns:
        match = re.search(pattern, code, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1)
    return code

def _extract_from_json_wrapper(self, code: str) -> str:
    """提取JSON包裹: {"code": "..."}"""
    try:
        parsed = json.loads(code)
        if isinstance(parsed, dict) and 'code' in parsed:
            return parsed['code']
    except json.JSONDecodeError:
        pass
    return code

def _extract_html_content(self, code: str) -> str:
    """提取完整HTML块"""
    match = re.search(
        r'<!DOCTYPE html>.*?</html>',
        code,
        re.DOTALL | re.IGNORECASE
    )
    if match:
        return match.group(0)
    return code
```

### 缺陷2: 机械式检测

**问题**: 只检查长度≥100/80字符，无法保证质量。

**修复前**:
```python
def _supervisor_review(self, code: str):
    score = 80
    if len(code) < 100:
        score -= 30
    return score, []
```

**修复后**: 多维度语义检测
```python
def _supervisor_review(self, code: str, ...) -> tuple:
    score = 80
    issues = []

    # 1. HTML语法验证
    try:
        HTMLParser().feed(code)
    except Exception as e:
        score -= 30
        issues.append(f"HTML语法错误: {e}")

    # 2. Canvas API完整性
    canvas_apis = self._extract_canvas_apis(code)
    # 检测: getContext, fillRect, arc, drawImage等
    if len(canvas_apis) < 10:
        score -= 15
        issues.append(f"Canvas API使用不足({len(canvas_apis)}<10)")

    # 3. 动画循环检测
    has_animation = (
        'requestAnimationFrame' in code and
        bool(re.search(r'function\s+\w*draw\w*\s*\(', code))
    )
    if not has_animation:
        score -= 10
        issues.append("缺少完整的动画循环")

    # 4. 交互响应检测
    input_controls = re.findall(r'<input.*?type=["\']range["\']', code)
    event_listeners = re.findall(r'addEventListener\s*\(', code)
    if len(input_controls) < 2 or len(event_listeners) < 2:
        score -= 10
        issues.append(f"交互性不足")

    # 5. 降低硬性阈值
    code_lines = len([l for l in code.split('\n') if l.strip()])
    if code_lines < 20:
        return 0, ["代码严重不足"]
    elif code_lines < 40:
        score -= 15
        issues.append(f"代码偏短({code_lines}行)")

    return max(0, score), issues

def _extract_canvas_apis(self, code: str) -> List[str]:
    """提取使用的Canvas API列表"""
    api_pattern = r'ctx\.(\w+)\s*\('
    return list(set(re.findall(api_pattern, code)))
```

### 缺陷3: 智能重试反馈

**问题**: 重试时只告诉"有问题"，不提供具体修复建议。

**修复前**:
```python
async def _producer_fix_code(self, code, issues):
    prompt = f"修复以下代码:\n{code}\n\n问题:\n{issues}"
    return await self.claude.generate(prompt)
```

**修复后**: 问题分类+相似案例检索
```python
async def _producer_fix_code(
    self,
    code: str,
    issues: List[str],
    round_num: int,
    history: List[Dict]
) -> str:
    # 1. 分类问题
    critical = [i for i in issues if self._is_critical(i)]
    minor = [i for i in issues if not self._is_critical(i)]

    # 2. 检索相似失败案例的解决方案
    similar_patterns = await self.template_service.get_similar_patterns_by_vector(
        query_text=f"修复{', '.join(critical)}",
        step_type='simulator',
        pattern_type='anti_pattern',  # 反模式
        top_k=2
    )

    # 3. 构建定制化修复prompt
    prompt = f"""修复以下HTML代码。这是第{round_num}轮修复。

【原代码】
{code}

【关键问题】（必须修复）
{self._format_issues(critical, priority='high')}

【次要问题】（建议修复）
{self._format_issues(minor, priority='low')}

【相似问题的解决方案】
{self._format_pattern_solutions(similar_patterns)}

【修复策略】
{self._suggest_fix_strategy(critical)}

【历史修复记录】
{self._format_history(history)}

【严格要求】
- 直接输出完整HTML代码
- 必须以<!DOCTYPE html>开头
- 不要markdown标记和JSON包裹
"""

    return await self._call_claude_api(prompt)

def _format_pattern_solutions(self, patterns: List[GenerationPattern]) -> str:
    """格式化模式解决方案"""
    if not patterns:
        return "（暂无相关案例）"

    result = []
    for i, p in enumerate(patterns, 1):
        result.append(f"""
{i}. {p.pattern_name} (置信度: {p.confidence:.2f})
   问题: {p.pattern_description}
   解决策略: {p.solution_strategy}
""")
    return '\n'.join(result)

def _suggest_fix_strategy(self, critical_issues: List[str]) -> str:
    """基于问题类型建议修复策略"""
    strategies = []

    for issue in critical_issues:
        if "HTML语法错误" in issue:
            strategies.append("检查标签闭合、属性引号、特殊字符转义")
        elif "Canvas API" in issue:
            strategies.append("增加绘图API调用：fillRect, arc, lineTo等")
        elif "动画循环" in issue:
            strategies.append("添加requestAnimationFrame递归调用")
        elif "交互性" in issue:
            strategies.append("添加<input type='range'>和addEventListener")

    return '\n'.join(f"- {s}" for s in strategies)
```

### 缺陷4: Prompt约束增强

**问题**: 即使明确禁止，AI仍返回markdown。

**修复前**:
```python
prompt = f"生成HTML代码。不要使用markdown标记。\n{requirements}"
```

**修复后**: 示例驱动的强制性约束
```python
OUTPUT_FORMAT_EXAMPLE = """
【输出格式示例 - 必须遵守】

✅ 正确示例（直接HTML）:
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>力学模拟器</title>
    <style>...</style>
</head>
<body>
    <canvas id="canvas"></canvas>
    <script>...</script>
</body>
</html>

❌ 错误示例（有markdown）:
```html          ← ❌ 禁止
<!DOCTYPE html>
...
```

❌ 错误示例（有JSON包裹）:
{                ← ❌ 禁止
    "code": "<!DOCTYPE html>..."
}

❌ 错误示例（有解释文字）:
这是一个模拟器...  ← ❌ 禁止
<!DOCTYPE html>

🎯 记住：你的输出应该可以直接保存为.html文件并运行！
"""

prompt = OUTPUT_FORMAT_EXAMPLE + "\n\n" + requirements
```

**原理**: 示例学习(Few-shot Learning) > 规则约束(Rule-based)

### 缺陷5: Agent评分反馈

**问题**: 生成失败后没有Agent的专业建议。

**修复**: 在修复流程中集成Agent反馈
```python
# 在 generate_simulator_code_progressive() 中
for round_num in range(1, 4):
    code = await self._producer_generate(...)
    rule_score, issues = self._supervisor_review(code)

    if rule_score >= 60:
        # 通过后才做Agent评估
        if should_evaluate:
            agent_score, agent_feedback = await self._agent_review_simulator(...)
            # 保存agent_feedback用于后续修复
        break
    else:
        # 修复时加入Agent反馈
        fix_prompt = self._build_fix_prompt(
            code, issues, agent_feedback  # ← 新增
        )
        code = await self._producer_fix_code(fix_prompt)
```

---

## 📊 监控与可视化

### 成本监控Dashboard

**实现**: `app/scripts/monitor_costs.py`

```python
# 运行方式
python app/scripts/monitor_costs.py --days 7

# 输出示例
===== Agent评估成本分析 (最近7天) =====

【总体统计】
总生成次数: 450
Agent评估次数: 234 (52.0%)
跳过次数: 216 (48.0%)

【按步骤类型统计】
simulator: 90次 (100%评估)  ← 关键步骤，永远评估
text_content: 180次 (45%评估)
assessment: 90次 (48%评估)
illustrated_content: 60次 (52%评估)
ai_tutor: 30次 (50%评估)

【成本对比】
实际成本: $4.68 ($0.20/课程 × 23课程)
潜在成本: $9.00 ($0.32/课程 × 23课程, 100%评估)
节省: $4.32 (48.0%)

【趋势分析】
Day 1: 100% → Day 2: 75% → ... → Day 7: 52%
(系统逐渐学习，跳过率上升)
```

### 质量趋势分析

**实现**: `app/scripts/analyze_quality_trends.py`

```python
# 运行方式
python app/scripts/analyze_quality_trends.py

# 输出示例
===== 质量趋势分析 =====

【质量分数演化】
平均分: 82.3 (+7.1 vs 上周)
中位数: 84.0
标准差: 8.5 (-2.3 vs 上周)  ← 稳定性提升

【模拟器通过率】
本周: 83.5% (+12.3% vs 上周)
上周: 71.2%
前周: 68.9%

【一次通过率】(无需重试)
本周: 68.2% (+15.4% vs 上周)
上周: 52.8%

【按学科统计】
physics: 平均分85.2 (通过率91.2%)
mathematics: 平均分79.8 (通过率78.4%)
chemistry: 平均分81.5 (通过率82.1%)

【模式应用效果】
使用模式增强: 平均分83.7
未使用模式: 平均分76.2
提升: +7.5分 (+9.9%)
```

### 模式库查看工具

**实现**: `app/scripts/inspect_patterns.py`

```python
# 运行方式
python app/scripts/inspect_patterns.py --step-type simulator --top 5

# 输出示例
===== 成功模式 Top 5 (step_type=simulator) =====

1. [0.87] 物理模拟器-粒子运动模式
   使用次数: 28 | 成功次数: 25
   描述: 使用requestAnimationFrame + 粒子数组实现动态效果
   策略: 1. 定义Particle类 2. 初始化数组 3. 每帧更新位置 4. 边界处理
   触发条件: {"subject": "physics", "has_particles": true}
   源模板数: 8
   最后使用: 2小时前

2. [0.83] Canvas渲染优化模式
   使用次数: 22 | 成功次数: 19
   描述: 双缓冲+requestAnimationFrame避免闪烁
   策略: ...

...

===== 反模式 Top 3 (需要避免) =====

1. [0.78] 避免使用setInterval做动画
   使用次数: 15 | 失败次数: 12
   描述: setInterval会导致动画不流畅，应使用requestAnimationFrame
   恢复策略: 将setInterval替换为requestAnimationFrame递归

...
```

---

## 🔐 安全性与性能

### 安全性考虑

1. **SQL注入防护**
   - 使用SQLAlchemy ORM，参数化查询
   - 所有用户输入经过验证和转义

2. **向量注入防护**
   - embedding生成前清理输入
   - 限制query长度（<5000字符）

3. **API密钥管理**
   - 环境变量存储Claude API密钥
   - 不在代码或日志中记录密钥

4. **数据访问控制**
   - 模式库只读访问（除了DistillationService）
   - 轨迹数据定期归档

### 性能优化

1. **向量检索优化**
   ```sql
   -- IVFFlat索引配置
   CREATE INDEX idx_embedding ON generation_patterns
   USING ivfflat (embedding vector_cosine_ops)
   WITH (lists = 100);  -- 100个聚类中心

   -- 查询时设置探测列表数
   SET ivfflat.probes = 10;  -- 搜索10个最近聚类
   ```

2. **缓存策略**
   ```python
   # sentence-transformers模型单例
   @lru_cache(maxsize=1)
   def get_embedding_model():
       return SentenceTransformer('all-MiniLM-L6-v2')

   # 热门模式缓存
   @lru_cache(maxsize=100)
   async def get_pattern(pattern_id: int):
       return await db.get(GenerationPattern, pattern_id)
   ```

3. **异步处理**
   ```python
   # 蒸馏任务异步执行
   asyncio.create_task(self._trigger_distillation())

   # 向量检索使用连接池
   engine = create_async_engine(
       DATABASE_URL,
       pool_size=20,
       max_overflow=10
   )
   ```

4. **批量操作**
   ```python
   # 批量更新模式统计
   await db.execute(
       update(GenerationPattern)
       .where(GenerationPattern.id.in_(pattern_ids))
       .values(last_used_at=datetime.utcnow())
   )
   ```

### 性能指标

| 操作 | 耗时 | 优化前 | 优化后 |
|------|------|--------|--------|
| 向量检索 (top-3) | <50ms | 200ms | 45ms |
| 模式应用记录 | <20ms | - | 18ms |
| 经验蒸馏 (50条) | 2-3min | - | 2.5min |
| 单步骤生成 | 15-30s | 20-35s | 15-30s |
| 课程生成 (16步骤) | 8-12min | 10-15min | 8-12min |

---

## 🧪 测试策略

### 单元测试

```python
# tests/test_learning_system.py

async def test_vector_search():
    """测试向量相似度检索"""
    service = UnifiedTemplateService(db)

    patterns = await service.get_similar_patterns_by_vector(
        query_text="物理 抛体运动 模拟器",
        step_type='simulator',
        pattern_type='success',
        top_k=3
    )

    assert len(patterns) <= 3
    assert all(p.step_type == 'simulator' for p in patterns)
    assert all(p.confidence >= 0.7 for p in patterns)

async def test_pattern_confidence_update():
    """测试贝叶斯置信度更新"""
    service = UnifiedTemplateService(db)

    # 创建测试模式
    pattern = GenerationPattern(
        pattern_name="Test",
        confidence=0.5,
        use_count=0,
        success_count=0
    )
    db.add(pattern)
    await db.commit()

    # 第一次成功
    await service._update_pattern_stats(pattern.id, success=True)
    await db.refresh(pattern)
    assert pattern.confidence == 0.75  # (1+2)/(1+4)

    # 第二次失败
    await service._update_pattern_stats(pattern.id, success=False)
    await db.refresh(pattern)
    assert pattern.confidence == 0.60  # (1+2)/(2+4)
```

### 集成测试

```python
async def test_learning_flow_end_to_end():
    """测试完整学习流程"""
    generator = CourseGenerator(...)

    # 1. 生成内容（集成模式检索）
    result = await generator.generate_step_with_learning(
        step_type='simulator',
        context={'subject': 'physics', 'topic': 'projectile_motion'}
    )

    # 2. 验证模式应用
    assert len(result['applied_patterns']) > 0

    # 3. 验证轨迹记录
    trajectory = await db.query(QualityEvaluation).filter(...).first()
    assert trajectory is not None

    # 4. 触发蒸馏
    await distillation_service.distill_patterns('simulator')

    # 5. 验证模式生成
    patterns = await db.query(GenerationPattern).all()
    assert len(patterns) > 0
```

### 性能测试

```bash
# 使用locust进行压力测试
locust -f tests/load_test.py --host=http://localhost:8000

# 测试场景：
# - 并发生成10个课程
# - 监控数据库连接池使用率
# - 监控向量检索延迟
# - 监控Claude API调用频率
```

---

## 📚 参考资料

### 论文与理论基础

1. **向量检索**
   - "Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs" (HNSW)
   - "Product Quantization for Nearest Neighbor Search" (PQ)

2. **经验蒸馏**
   - "Distilling the Knowledge in a Neural Network" (Hinton et al., 2015)
   - "Few-Shot Learning via Learning the Representation, Provably" (Allen-Zhu & Li, 2023)

3. **贝叶斯更新**
   - "A Tutorial on Bayesian Estimation and Tracking Techniques" (Ristic et al., 2004)
   - "Beta Distribution for Prior Beliefs" (Wikipedia)

### 技术文档

- pgvector官方文档: https://github.com/pgvector/pgvector
- sentence-transformers文档: https://www.sbert.net/
- Claude API文档: https://docs.anthropic.com/

### 相关项目

- LangChain: https://github.com/langchain-ai/langchain
- LlamaIndex: https://github.com/run-llama/llama_index
- AutoGen: https://github.com/microsoft/autogen

---

## 🎓 最佳实践

### 模式编写规范

**好的模式**:
```json
{
  "pattern_name": "物理模拟器-粒子运动模式",
  "description": "使用requestAnimationFrame + 粒子数组实现动态效果。适用于需要大量移动对象的场景（如雨滴、烟花、星空）。",
  "trigger_conditions": {
    "subject": "physics",
    "topic": ["projectile_motion", "particle_system"],
    "complexity": "high"
  },
  "solution_strategy": "1. 定义Particle类（位置、速度、加速度）\n2. 初始化粒子数组（100-500个）\n3. 每帧更新：位置+=速度，速度+=加速度\n4. 边界处理：超出画布则重置\n5. 渲染：clearRect → 遍历绘制",
  "confidence": 0.85
}
```

**坏的模式**:
```json
{
  "pattern_name": "代码模式1",  // ❌ 名称不具体
  "description": "写好代码",    // ❌ 描述太泛
  "trigger_conditions": {},      // ❌ 缺少触发条件
  "solution_strategy": "按照要求写",  // ❌ 策略不可操作
  "confidence": 0.5
}
```

### 蒸馏Prompt优化

**原则**:
1. **具体化**: 明确要提取什么（结构/技巧/设计）
2. **示例驱动**: 提供1-2个好模式示例
3. **约束输出**: 指定JSON格式，必填字段
4. **多样性**: 鼓励提取不同层次的模式

**示例**:
```
分析以下30个高质量simulator案例，提取3-5个成功模式。

【要求】
1. 每个模式必须：
   - 在至少5个案例中出现
   - 可操作性强（具体到代码结构）
   - 可迁移性好（适用于多个主题）

2. 提取层次：
   - 结构层：代码组织方式（如MVC分离）
   - 技巧层：实现细节（如双缓冲渲染）
   - 设计层：交互模式（如渐进式引导）

3. 输出格式：
   - pattern_name: 简短描述性名称（<30字）
   - description: 详细说明（100-200字）
   - trigger_conditions: JSONB格式，列出适用场景
   - solution_strategy: 分步骤说明（5-10步）
   - confidence: 初始置信度（基于出现频率，0.6-0.9）

【案例】
...
```

---

## 🔮 未来扩展

### 短期规划 (1-2个月)

1. **多模型支持**
   - 支持GPT-4、Gemini等其他大模型
   - 模型路由器：根据任务类型选择最优模型

2. **模式推荐系统**
   - 基于协同过滤推荐相关模式
   - "使用此模式的用户也使用了..."

3. **可视化Dashboard**
   - Grafana/Metabase集成
   - 实时监控质量趋势、成本变化

### 中期规划 (3-6个月)

1. **在线学习**
   - 实时更新模式置信度
   - 增量式蒸馏（不需要等50条）

2. **多模态学习**
   - 结合用户反馈（点赞/差评）
   - 结合实际使用数据（完成率）

3. **跨学科迁移**
   - 物理模式 → 化学模拟器
   - 数学可视化 → 经济学图表

### 长期愿景 (6个月+)

1. **自主Agent**
   - 自动发现新模式（无需人工触发蒸馏）
   - 自动优化prompt和生成策略

2. **联邦学习**
   - 多个HERCU实例共享模式库
   - 隐私保护的协同学习

3. **元学习**
   - 学习如何学习（Learning to Learn）
   - 快速适应新领域

---

**文档版本历史**:
- v1.0.0 (2026-02-13): 初始版本
- 待更新...

---

**文档维护**: dev@hercux.com
**最后更新**: 2026-02-13
