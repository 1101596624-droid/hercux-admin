# HERCU 模拟器系统升级文档

**版本**: 1.1.0  
**更新日期**: 2026-02-20  
**状态**: 完成 Phase 2 + 理文科分流

---

## 升级概述

本次升级将 HERCU 模拟器系统从 **固定6种样式** 升级为 **自由可视化元素组合系统**，并集成了：

- **22种可视化元素**：AI可自由组合，适用于K-12至大学级别所有学科
- **8套学科配色方案**：物理、化学、生物、数学、历史、地理、计算机、医学
- **12种交互类型**：从 click/drag 到 pinch_zoom/rotate
- **8个缓动函数 + 4种物理动画**：实现自然、流畅的动画效果
- **学科自动分类系统**：自动识别课程学科并推荐配色和元素
- **理文科分流系统**：只有理科科目（物理、化学、生物、数学）才生成模拟器，文科科目自动跳过

---

## 目录结构

```
backend/app/services/course_generation/
├── standards/                      # 标准文档目录（9个YAML文件）
│   ├── course_standards.yaml      # 课程质量标准
│   ├── simulator_standards.yaml   # 模拟器质量标净
│   ├── canvas_config.yaml         # 画布配置（学生端/管理端）
│   ├── visualization_elements.yaml # 22种可视化元素
│   ├── color_systems.yaml         # 8套学科配色方案
│   ├── visual_best_practices.yaml # 视觉最佳实践
│   ├── interaction_types.yaml     # 12种交互类型
│   ├── api_reference.yaml         # API完整参考
│   └── animation_easing.yaml      # 动画缓动函数
│
├── standards_loader.py           # 标准加载器（单例模式 + LRU缓存）
├── supervisor.py                 # 监督者（集成了标准推荐）
├── generator.py                  # 生成器（集成了标准加载）
├── service.py                    # 服务层（集成学科分类）
├── models.py                     # 数据模型
└── tests/                        # 测试文件
    └── test_standards_loader.py  # StandardsLoader单元测试
```

---

## 已完成功能

### Phase 1: 标准文档系统 (100% 完成)

✅ **任务 #7**: 创建了9个YAML标准文档（3804行）  
✅ **任务 #22**: 创建8套学科配色系统  
✅ **任务 #23**: 创建视觉元素最佳实践  
✅ **任务 #17**: 设计12种交互类型库  
✅ **任务 #21**: 更新API参考文档  
✅ **任务 #24**: 创建动画缓动函数库  

### Phase 2: 标准加载器与集成 (100% 完成)

✅ **任务 #8**: 创建StandardsLoader类（单例模式 + LRU缓存）  
✅ **任务 #9**: 监督者集成标准系统（添加可视化推荐）  
✅ **任务 #10**: 生成器集成标准系统  
✅ **任务 #14**: 学科自动分类系统  
✅ **任务 #16**: 测试和文档更新  

---

## 使用方法

### 1. StandardsLoader 基础使用

```python
from app.services.course_generation.standards_loader import get_standards_loader

# 获取全局单例
loader = get_standards_loader()

# 加载模拟器标准
sim_standards = loader.get_simulator_standards()
print(sim_standards['code_quality']['min_code_lines'])  # 80

# 加载可视化元素
viz_elements = loader.get_visualization_elements()
for elem in viz_elements['visualization_elements'][:5]:
    print(f"{elem['id']}: {elem['name']} - {elem['description']}")

# 获取学科配色方案
physics_colors = loader.get_subject_color_scheme('physics')
print(physics_colors['philosophy'])  # “理性、精确、能量感”
print(physics_colors['base_colors']['primary'])  # #3B82F6
```

### 2. 学科自动分类

```python
from app.services.course_generation.service import CourseGenerationService

service = CourseGenerationService()

# 自动识别课程学科
classification = service.detect_course_subject(
    course_title="牛顿力学与运动学基础",
    outline=None  # 可选：提供大纲可提高准确度
)

print(classification)
# {
#     'subject_id': 'physics',
#     'subject_name': '物理学',
#     'confidence': 0.95,
#     'matched_keywords': ['物理', '力学', '运动'],
#     'color_scheme': {...},
#     'visualization_elements': ['circles', 'lines', 'position_animation', ...]
# }
```

### 3. 理文科分流系统

```python
from app.services.course_generation.service import SCIENCE_SUBJECTS

# 理科科目集合 — 只有这些科目才会生成模拟器
print(SCIENCE_SUBJECTS)  # {'physics', 'chemistry', 'biology', 'mathematics'}

# 工作流程：
# 1. 课程标题 → detect_course_subject() → subject_id
# 2. subject_id in SCIENCE_SUBJECTS → is_science
# 3. is_science=True:  大纲包含 simulator 步骤，Agent 生成模拟器
# 4. is_science=False: 大纲不包含 simulator 步骤，跳过模拟器生成
```

### 4. 监督者自动推荐可视化方案

监督者现在会在生成章节提示词时自动加入：

- **学科识别**：基于课程标题和关键词自动识别学科
- **配色方案**：为该学科推荐主色、次色、强调色
- **可视化元素**：推荐适合该学科的元素组合
- **画布约束**：比例坐标、安全绘制区域
- **视觉质量要求**：颜色对比度、缓动函数推荐

---

## 标准文档详情

### 1. `visualization_elements.yaml` (308行)

**22种基础可视化元素**：

#### 几何图形类 (5种)
- `circles` - 圆形：节点、粒子、原子
- `rectangles` - 矩形：柱状图、状态块、容器
- `lines` - 直线：坐标轴、连接线、箭头
- `curves` - 曲线：函数图、轨迹、流动路径
- `polygons` - 多边形：不规则形状、箭头头部

#### 文本标注类 (3种)
- `labels` - 标签：元素名称、数值标注
- `title` - 标题：场景标题
- `legend` - 图例：颜色/符号说明

#### 动画效果类 (4种)
- `position_animation` - 位置动画
- `color_animation` - 颜色变化
- `size_animation` - 大小变化
- `glow_effect` - 发光效果

#### 组合结构类 (9种)
- `node_network` - 节点网络
- `tree_structure` - 树状结构
- `flow_diagram` - 流程图
- `timeline` - 时间线
- `coordinate_system` - 坐标系
- `matrix_grid` - 矩阵网格
- `layered_structure` - 分层结构
- `comparison_layout` - 对比布局
- `annotation_system` - 标注系统

### 2. `color_systems.yaml` (450行)

**8套学科配色方案**：

| 学科 | 主色 | 次色 | 强调色 | 设计理念 |
|------|------|------|--------|----------|
| 物理 | #3B82F6 (蓝) | #F59E0B (橙) | #10B981 (绿) | 理性、精确、能量感 |
| 化学 | #DC2626 (红) | #2563EB (深蓝) | #10B981 (绿) | 反应、变化、活力 |
| 生物 | #22C55E (绿) | #EC4899 (粉) | #F59E0B (橙) | 生命、生长、自然 |
| 数学 | #1E40AF (深蓝) | #7C3AED (紫) | #0EA5E9 (青) | 严谨、逻辑、抽象 |
| 历史 | #92400E (棕) | #CA8A04 (金) | #78350F (深棕) | 厚重、经典、时间感 |
| 地理 | #0EA5E9 (蓝) | #10B981 (绿) | #F59E0B (黄) | 自然、地域、层次 |
| 计算机 | #06B6D4 (青) | #8B5CF6 (紫) | #10B981 (绿) | 科技、精确、数字化 |
| 医学 | #DC2626 (红) | #2563EB (蓝) | #10B981 (绿) | 生命、健康、专业 |

### 3. `interaction_types.yaml` (550行)

**12种交互类型**：

| ID | 名称 | 难度 | 使用场景 |
|----|------|------|---------|
| click | 点击 | simple | 按钮、开关、节点选择 |
| drag | 拖拽 | medium | 元素定位、拖拽排序 |
| hover | 悬停 | simple | 工具提示、高亮显示 |
| double_click | 双击 | simple | 快捷操作、缩放 |
| key_press | 键盘 | medium | 键盘控制、快捷键 |
| text_input | 文本输入 | medium | 参数输入、搜索 |
| dropdown_select | 下拉选择 | medium | 模式切换、选项选择 |
| play_pause | 播放/暂停 | simple | 动画控制、时间模拟 |
| timeline_scrub | 时间轴拖拽 | medium | 时间轴操作、进度控制 |
| pinch_zoom | 缩放 | simple | 缩放查看、地图缩放 |
| rotate | 旋转 | medium | 3D视角、分子结构 |
| swipe | 滑动 | medium | 卡片切换、翻页 |

### 4. `animation_easing.yaml` (580行)

**8个缓动函数**：

| ID | 公式 | 使用场景 |
|----|------|----------|
| linear | f(t) = t | 匀速运动、旋转 |
| easeIn | f(t) = t² | 加速进入 |
| easeOut | f(t) = 1-(1-t)² | 减速停止 |
| easeInOut | 分段函数 | 平滑过渡 |
| easeOutBack | 超过后返回 | 弹性效果 |
| easeOutBounce | 多次弹跳 | 弹跳球、掉落 |
| easeInOutElastic | 弹簧震荡 | 拉伸效果 |
| easeOutExpo | 1-2^(-10t) | 快速衰减 |

**4种物理动画**：
- 重力下落：y = y₀ + 0.5gt²
- 谐振动：x = A·sin(ωt)
- 阻尼振荡：x = A·e^(-bt)·sin(ωt)
- 摆锾运动：θ = θ₀·cos(√(g/L)·t)

---

## 性能优化

### 1. LRU缓存
StandardsLoader 使用 `@lru_cache(maxsize=32)` 缓存标准文档，减少磁盘I/O。

### 2. 单例模式
全局只有一个StandardsLoader实例，避免重复加载。

### 3. 懒加载
标准文档只在首次访问时加载，之后从缓存读取。

---

## 测试

```bash
# 运行所有测试
pytest backend/app/services/course_generation/tests/test_standards_loader.py -v

# 运行单个测试
pytest backend/app/services/course_generation/tests/test_standards_loader.py::TestStandardsLoader::test_load_simulator_standards -v

# 查看测试覆盖率
pytest --cov=app.services.course_generation.standards_loader backend/app/services/course_generation/tests/test_standards_loader.py
```

---

## API参考

### StandardsLoader 主要方法

```python
class StandardsLoader:
    # 基础加载
    def get_standard(self, standard_name: str) -> Dict[str, Any]
    def reload_standard(self, standard_name: str) -> Dict[str, Any]
    def reload_all_standards(self)
    
    # 快捷方法
    def get_simulator_standards() -> Dict[str, Any]
    def get_course_standards() -> Dict[str, Any]
    def get_canvas_config() -> Dict[str, Any]
    def get_visualization_elements() -> Dict[str, Any]
    def get_color_systems() -> Dict[str, Any]
    def get_visual_best_practices() -> Dict[str, Any]
    def get_interaction_types() -> Dict[str, Any]
    def get_api_reference() -> Dict[str, Any]
    def get_animation_easing() -> Dict[str, Any]
    
    # 查询辅助方法
    def get_subject_color_scheme(self, subject: str) -> Optional[Dict[str, Any]]
    def get_visualization_element(self, element_id: str) -> Optional[Dict[str, Any]]
    def get_interaction_type(self, type_id: str) -> Optional[Dict[str, Any]]
    def get_easing_function(self, easing_id: str) -> Optional[Dict[str, Any]]
    def get_recommended_elements_for_subject(self, subject: str) -> List[str]
    
    # 版本管理
    def get_standard_version(self, standard_name: str) -> str
    def get_all_versions() -> Dict[str, str]
    def check_version_consistency() -> bool
    
    # 诊断工具
    def get_load_info() -> Dict[str, Any]
    def validate_all_standards() -> Dict[str, Any]
```

### CourseGenerationService 新增方法

```python
class CourseGenerationService:
    def detect_course_subject(
        self,
        course_title: str,
        outline: Optional[CourseOutline] = None
    ) -> Dict[str, Any]
    
    async def auto_classify_and_update_course(
        self,
        course_id: str,
        course_title: str,
        outline: Optional[CourseOutline] = None
    ) -> Dict[str, Any]
```

---

## 待完成任务

### Phase 3: hercu-agent 增强 (0% 完成)

⏳ **任务 #11**: Agent标准同步系统  
⏳ **任务 #12**: Agent增强simulator生成  
⏳ **任务 #13**: 课程生成流程集成  

### Phase 4: 前端画布配置 (0% 完成)

⏳ **任务 #15**: 前端画布配置动态化  

### Phase 5: 交互API扩展 (0% 完成)

⏳ **任务 #18**: 扩展CustomRenderer交互API  
⏳ **任务 #19**: 监督者推荐交互方式  
⏳ **任务 #20**: 生成器生成交互代码  

### Phase 6: 美学代码生成 (0% 完成)

⏳ **任务 #25**: 监督者设计美学评估  
⏳ **任务 #26**: 生成器实现精致代码  
⏳ **任务 #27**: Agent美学评分系统  

---

## 更新记录

### v1.1.0 (2026-02-20)

**理文科分流系统**：
- ✅ 新增 `SCIENCE_SUBJECTS` 常量（physics/chemistry/biology/mathematics）
- ✅ 修复 `service.py` 中 `subject="physics"` 硬编码问题，改为动态传参
- ✅ 提前学科检测：在大纲生成前先识别学科，传递 `is_science` 给监督者
- ✅ `supervisor.py` 条件化模拟器步骤：非理科大纲不包含 simulator 步骤
- ✅ `enhancer.py`（Agent端）条件化 simulator 步骤和 JSON schema enum
- ✅ `_generate_simulator_codes_with_check` 非理科科目直接跳过模拟器生成

### v1.0.0 (2026-02-10)

**Phase 1 完成**：
- ✅ 创建9个YAML标准文档（3804行）
- ✅ 22种可视化元素定义
- ✅ 8套学科配色方案
- ✅ 12种交互类型
- ✅ 8个缓动函数 + 4种物理动画

**Phase 2 完成**：
- ✅ StandardsLoader类（单例 + LRU缓存）
- ✅ 监督者集成：自动推荐配色和元素
- ✅ 生成器集成：加载标准文档
- ✅ 学科自动分类系统
- ✅ 单元测试和文档

---

## 贡献指南

### 添加新学科

1. 在 `color_systems.yaml` 中添加新学科配色方案
2. 在 `visualization_elements.yaml` 的 `recommended_combinations` 中添加推荐元素组合
3. 在 `supervisor.py` 的 `_detect_subject()` 中添加关键词映射
4. 在 `service.py` 的 `detect_course_subject()` 中添加关键词映射

### 添加新可视化元素

1. 在 `visualization_elements.yaml` 的 `visualization_elements` 数组中添加新元素
2. 确保包含：`id`, `name`, `description`, `apis`, `use_cases`, `best_practices`
3. 更新 `api_reference.yaml` 如果需要新API

### 添加新交互类型

1. 在 `interaction_types.yaml` 的 `interaction_types` 数组中添加
2. 包含实现代码示例和最佳实践
3. 前端 CustomRenderer 需要同步实现

---

## 联系信息

**项目**: HERCU  
**模块**: 模拟器系统  
**版本**: 1.0.0  
**更新日期**: 2026-02-10  
