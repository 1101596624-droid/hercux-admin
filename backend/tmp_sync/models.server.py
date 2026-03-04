import os
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON, Float, Boolean, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import enum

# Conditionally import Vector type for PostgreSQL
# In test environment (SQLite), use Text type instead
try:
    from pgvector.sqlalchemy import Vector
    USE_VECTOR = True
except ImportError:
    USE_VECTOR = False

# Detect database type from environment
db_url = os.getenv('DATABASE_URL', '')
IS_POSTGRESQL = 'postgresql' in db_url or 'postgres' in db_url

# Choose appropriate types
if IS_POSTGRESQL:
    JSONType = JSONB
else:
    JSONType = JSON

def get_vector_type(dim):
    """Return Vector for PostgreSQL, Text for SQLite"""
    if USE_VECTOR and IS_POSTGRESQL:
        return Vector(dim)
    return Text  # Fallback to Text for testing/SQLite


class DifficultyLevel(str, enum.Enum):
    """Course difficulty levels"""
    ENTRY = "entry"           # 入门
    BEGINNER = "beginner"     # 基础
    INTERMEDIATE = "intermediate"  # 进阶
    ADVANCED = "advanced"     # 高级
    EXPERT = "expert"         # 专家


class NodeType(str, enum.Enum):
    """Course node types"""
    VIDEO = "video"
    QUIZ = "quiz"
    READING = "reading"
    PRACTICE = "practice"
    LESSON = "lesson"


class NodeStatus(str, enum.Enum):
    """Learning progress status"""
    LOCKED = "locked"
    UNLOCKED = "unlocked"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    avatar_url = Column(String(500))
    is_active = Column(Integer, default=1)
    is_premium = Column(Integer, default=0)
    is_admin = Column(Integer, default=0)  # Admin role flag
    admin_level = Column(Integer, default=0)  # 管理员等级: 0=非管理员, 1=超级管理员, 2=高级管理员, 3=普通管理员

    # 使用统计汇总字段
    total_usage_seconds = Column(Integer, default=0)  # 累计使用时长（秒）
    total_tokens_used = Column(Integer, default=0)    # 累计消耗 token 数
    total_input_tokens = Column(Integer, default=0)   # 累计输入 token
    total_output_tokens = Column(Integer, default=0)  # 累计输出 token

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    progress = relationship("LearningProgress", back_populates="user")
    training_plans = relationship("TrainingPlan", back_populates="user")


class Course(Base):
    """Course model"""
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    difficulty = Column(Enum(DifficultyLevel, values_callable=lambda x: [e.value for e in x]), nullable=False)
    tags = Column(JSON)  # Array of tags like ["biomechanics", "strength"]
    instructor = Column(String(255))
    duration_hours = Column(Float)
    thumbnail_url = Column(String(500))
    is_published = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    nodes = relationship("CourseNode", back_populates="course")


class CourseNode(Base):
    """Course node model - Core table for content distribution"""
    __tablename__ = "course_nodes"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("course_nodes.id"), nullable=True)  # Tree structure support
    node_id = Column(String(100), unique=True, index=True, nullable=False)  # e.g., "node_biomech_01"
    type = Column(Enum(NodeType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    component_id = Column(String(100), nullable=False)  # e.g., "force-balance-sim"
    title = Column(String(255), nullable=False)
    description = Column(Text)
    sequence = Column(Integer, default=0)  # Order within same parent

    # Content and config for V2 course packages
    content = Column(JSONType)  # Lesson content with steps (统一使用jsonb)
    config = Column(JSONType)  # Lesson configuration

    # Timeline configuration - stores steps for video/simulator/quiz sequence
    timeline_config = Column(JSON)  # {"steps": [...]}

    # Unlock conditions
    unlock_condition = Column(JSON)  # {"type": "previous_complete"} or {"type": "manual"}

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    course = relationship("Course", back_populates="nodes")
    progress = relationship("LearningProgress", back_populates="node")
    children = relationship("CourseNode", backref="parent", remote_side=[id])


class SimulatorTemplate(Base):
    """HTML simulator template for agent learning (2026-02-11)

    Stores high-quality HTML simulator templates (75+ points) for the AI agent to learn from.
    Templates serve as reference examples for code structure, Canvas API usage, and interaction patterns.
    """
    __tablename__ = "simulator_templates"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(100), nullable=False, index=True)  # e.g., "physics", "mathematics"
    topic = Column(String(255), nullable=False, index=True)    # e.g., "projectile_motion", "matrix_operations"

    # Core content
    code = Column(Text, nullable=False)  # Full HTML code
    quality_score = Column(Float, nullable=False, index=True)  # 0-100, baseline 75

    # Code metrics (for quick filtering)
    line_count = Column(Integer, nullable=False)
    variable_count = Column(Integer, default=0)
    has_setup_update = Column(Boolean, default=False)  # setup() and update() pattern

    # Visual and interaction features
    visual_elements = Column(JSON)  # ["grid", "vectors", "particles", "labels"]

    # Legacy metadata column (DB has NOT NULL constraint, 'metadata' is reserved in SQLAlchemy)
    template_meta = Column('metadata', JSON, nullable=False, default=dict, server_default='{}')

    # Template metadata for learning
    template_metadata = Column(JSON)  # {
        # "common_apis": ["fillRect", "arc", "beginPath", "stroke"],
        # "color_scheme": ["#FF6B6B", "#4ECDC4", "#45B7D1"],
        # "animation_patterns": ["requestAnimationFrame", "physics_update"],
        # "interaction_types": ["mouse_drag", "slider_control"],
        # "structure_insights": "Uses modular state management with clear separation"
    # }

    status = Column(String(20), nullable=False, default='pending', server_default='pending', index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class LearningProgress(Base):
    """User learning progress tracking"""
    __tablename__ = "learning_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    node_id = Column(Integer, ForeignKey("course_nodes.id"), nullable=False, index=True)
    status = Column(Enum(NodeStatus, values_callable=lambda x: [e.value for e in x]), default=NodeStatus.LOCKED, index=True)
    completion_percentage = Column(Float, default=0.0)
    time_spent_seconds = Column(Integer, default=0)
    current_step_index = Column(Integer, default=0)
    last_accessed = Column(DateTime(timezone=True), index=True)
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="progress")
    node = relationship("CourseNode", back_populates="progress")


class TrainingPlan(Base):
    """AI-generated training plans"""
    __tablename__ = "training_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    plan_data = Column(JSON, nullable=False)  # Structured plan with periods, weeks, sessions
    status = Column(String(50), default="active")  # active, completed, archived
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="training_plans")


class Achievement(Base):
    """User achievements and badges"""
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    badge_id = Column(String(100), nullable=False)
    badge_name = Column(String(255), nullable=False)
    badge_description = Column(Text)
    rarity = Column(String(50))  # common, rare, epic, legendary
    icon_url = Column(String(500))
    unlocked_at = Column(DateTime(timezone=True), server_default=func.now())


class UserCourse(Base):
    """User course enrollment tracking"""
    __tablename__ = "user_courses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    last_accessed = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True), nullable=True)  # 课程完成时间
    is_favorite = Column(Integer, default=0)


class ChatHistory(Base):
    """AI chat history for each node"""
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    node_id = Column(Integer, ForeignKey("course_nodes.id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SimulatorResult(Base):
    """Simulator results for tracking user interactions"""
    __tablename__ = "simulator_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    node_id = Column(Integer, ForeignKey("course_nodes.id"), nullable=False)
    session_id = Column(String(100), nullable=False, index=True)
    result_data = Column(JSON, nullable=False)
    score = Column(Float, nullable=True)
    time_spent_seconds = Column(Integer, default=0)
    completed = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class LearningStatistics(Base):
    """Daily learning statistics for users"""
    __tablename__ = "learning_statistics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    total_time_seconds = Column(Integer, default=0)
    nodes_completed = Column(Integer, default=0)
    streak_days = Column(Integer, default=0)


# ============================================
# Studio Models
# ============================================

class StudioProcessor(Base):
    """Studio processor (plugin) for course generation"""
    __tablename__ = "studio_processors"

    id = Column(String(100), primary_key=True)  # e.g., "default", "academic", "custom_xxx"
    name = Column(String(255), nullable=False)
    description = Column(Text)
    version = Column(String(50), default="1.0.0")
    author = Column(String(255))
    tags = Column(JSON)  # ["official", "academic", etc.]
    color = Column(String(50), default="#3B82F6")
    icon = Column(String(50), default="Sparkles")
    system_prompt = Column(Text)  # AI system prompt for generation

    # 【新增】课程结构约束 - 优先级最高,覆盖默认标准
    structure_constraints = Column(JSON)  # {
    #   "min_chapters": 4,
    #   "max_chapters": 8,
    #   "min_steps_per_chapter": 7,
    #   "max_steps_per_chapter": 12,
    #   "required_step_types": ["text_content", "simulator", "assessment"],
    #   "min_simulators_per_chapter": 1,
    #   "min_assessments_per_chapter": 1
    # }

    enabled = Column(Integer, default=1)
    display_order = Column(Integer, default=0)
    is_official = Column(Integer, default=0)
    is_custom = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class StudioPackageStatus(str, enum.Enum):
    """Course package status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class StudioPackage(Base):
    """Generated course package from Studio"""
    __tablename__ = "studio_packages"

    id = Column(String(100), primary_key=True)  # UUID
    title = Column(String(255), nullable=False)
    description = Column(Text)
    source_info = Column(Text)  # Source material info
    style = Column(String(100))  # Generation style
    status = Column(Enum(StudioPackageStatus, values_callable=lambda x: [e.value for e in x]), default=StudioPackageStatus.DRAFT)

    # Package data (V2 format)
    meta = Column(JSON)  # PackageMetaV2
    lessons = Column(JSON)  # Array of Lesson objects
    edges = Column(JSON)  # Array of Edge objects
    global_ai_config = Column(JSON)  # AI tutor config

    # Statistics
    total_lessons = Column(Integer, default=0)
    estimated_hours = Column(Float, default=0)

    # Processor used
    processor_id = Column(String(100), ForeignKey("studio_processors.id"), nullable=True)

    # Linked course (after import)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TokenUsage(Base):
    """AI Token usage tracking for analytics"""
    __tablename__ = "token_usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 可选，未登录用户为空
    feature = Column(String(100), nullable=False, index=True)  # 功能名称：ai_training_plan, ai_tutor, etc.
    model = Column(String(100), nullable=False)  # 模型名称：claude-sonnet-4-20250514
    input_tokens = Column(Integer, nullable=False, default=0)
    output_tokens = Column(Integer, nullable=False, default=0)
    total_tokens = Column(Integer, nullable=False, default=0)
    plan_id = Column(String(100), nullable=True)  # 关联的计划ID（如果有）
    extra_data = Column(JSON, nullable=True)  # 额外元数据
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


# ============================================
# Achievement Center Models (勋章中心)
# ============================================

class BadgeCategory(str, enum.Enum):
    """勋章分类"""
    LEARNING = "learning"
    PERSISTENCE = "persistence"
    PRACTICE = "practice"
    QUIZ = "quiz"
    SPECIAL = "special"


class BadgeRarity(str, enum.Enum):
    """勋章稀有度"""
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class BadgeConfig(Base):
    """勋章配置表"""
    __tablename__ = "badge_configs"

    id = Column(String(50), primary_key=True)  # snake_case 唯一标识
    name = Column(String(100), nullable=False)
    name_en = Column(String(100))
    icon = Column(String(10), nullable=False)  # emoji
    icon_url = Column(String(500))  # 自定义图标URL
    description = Column(Text)

    category = Column(Enum(BadgeCategory, values_callable=lambda x: [e.value for e in x]), nullable=False)
    rarity = Column(Enum(BadgeRarity, values_callable=lambda x: [e.value for e in x]), default=BadgeRarity.COMMON)
    points = Column(Integer, nullable=False, default=10)

    # 解锁条件 JSON: {"type": "counter", "metric": "nodes_completed", "target": 10}
    condition = Column(JSON, nullable=False)

    # 解锁动画代码 (JavaScript/CSS)
    unlock_animation = Column(Text)

    is_active = Column(Integer, default=1)
    sort_order = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(50))


class SkillTreeConfig(Base):
    """技能树配置表"""
    __tablename__ = "skill_tree_configs"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    name_en = Column(String(100))
    icon = Column(String(10), nullable=False)
    color = Column(String(20), nullable=False)  # hex color
    description = Column(Text)

    # 匹配规则 JSON: {"domains": ["biomechanics"], "subdomains": ["joint", "muscle"]}
    match_rules = Column(JSON, nullable=False)

    # 等级阈值 [0, 50, 150, 300, 500]
    level_thresholds = Column(JSON, default=[0, 50, 150, 300, 500])

    # 前置依赖 JSON: [{"treeId": "biomechanics", "requiredLevel": 2}]
    prerequisites = Column(JSON, default=[])

    # 解锁哪些技能树
    unlocks = Column(JSON, default=[])

    is_advanced = Column(Integer, default=0)
    is_active = Column(Integer, default=1)
    sort_order = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SkillAchievementConfig(Base):
    """技能成就配置表"""
    __tablename__ = "skill_achievement_configs"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    name_en = Column(String(100))
    icon = Column(String(10), nullable=False)
    description = Column(Text)
    points = Column(Integer, nullable=False, default=50)

    # 解锁条件 JSON
    condition = Column(JSON, nullable=False)

    is_active = Column(Integer, default=1)
    sort_order = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TagDictionary(Base):
    """标签字典表"""
    __tablename__ = "tag_dictionary"

    id = Column(String(50), primary_key=True)
    type = Column(String(20), nullable=False)  # 'domain' | 'subdomain'
    name = Column(String(100), nullable=False)
    name_en = Column(String(100))
    icon = Column(String(10))  # 仅 domain
    color = Column(String(20))  # 仅 domain
    parent_id = Column(String(50), ForeignKey("tag_dictionary.id"))
    description = Column(Text)

    is_registered = Column(Integer, default=0)  # 是否已关联技能树
    is_active = Column(Integer, default=1)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PendingDomain(Base):
    """待审核领域表"""
    __tablename__ = "pending_domains"

    domain = Column(String(50), primary_key=True)
    node_count = Column(Integer, default=0)
    completed_users = Column(Integer, default=0)
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(20), default="pending")  # pending | approved | rejected

    reviewed_at = Column(DateTime(timezone=True))
    reviewed_by = Column(String(50))
    reject_reason = Column(Text)


class UserBadge(Base):
    """用户勋章解锁记录"""
    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    badge_id = Column(String(50), ForeignKey("badge_configs.id"), nullable=False)
    unlocked_at = Column(DateTime(timezone=True), server_default=func.now())


class UserSkillProgress(Base):
    """用户技能进度"""
    __tablename__ = "user_skill_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    skill_tree_id = Column(String(50), ForeignKey("skill_tree_configs.id"), nullable=False)
    current_points = Column(Integer, default=0)
    current_level = Column(Integer, default=0)
    sub_skills = Column(JSON, default={})  # 子技能进度
    last_updated = Column(DateTime(timezone=True), server_default=func.now())


class UserSkillAchievement(Base):
    """用户技能成就解锁记录"""
    __tablename__ = "user_skill_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    achievement_id = Column(String(50), ForeignKey("skill_achievement_configs.id"), nullable=False)
    unlocked_at = Column(DateTime(timezone=True), server_default=func.now())


class UserProfile(Base):
    """用户特征画像 - 基于AI对话分析"""
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # 学习特征
    learning_style = Column(JSON)  # {"visual": 0.3, "auditory": 0.2, "reading": 0.3, "kinesthetic": 0.2}
    knowledge_levels = Column(JSON)  # {"biomechanics": "intermediate", "nutrition": "beginner", ...}
    interests = Column(JSON)  # ["strength_training", "injury_prevention", ...]
    strengths = Column(JSON)  # ["analytical_thinking", "quick_learner", ...]
    weaknesses = Column(JSON)  # ["time_management", "consistency", ...]

    # 沟通特征
    communication_style = Column(String(50))  # "detailed", "concise", "questioning", "passive"
    engagement_level = Column(String(50))  # "high", "medium", "low"
    question_patterns = Column(JSON)  # {"clarification": 5, "deep_dive": 3, "practical": 8}
    learning_pace = Column(String(50))  # "fast", "moderate", "slow"

    # AI分析结果
    personality_traits = Column(JSON)  # ["curious", "methodical", "goal-oriented"]
    recommended_approach = Column(Text)  # AI建议的教学方式
    analysis_summary = Column(Text)  # AI分析总结

    # 元数据
    messages_analyzed = Column(Integer, default=0)  # 已分析的消息数量
    last_analyzed_at = Column(DateTime(timezone=True))
    analysis_version = Column(String(20), default="1.0")  # 分析算法版本

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ============================================
# Simulator Icon Library (模拟器图标库)
# ============================================

class IconCategory(str, enum.Enum):
    """图标分类"""
    BASIC = "basic"                    # 基础形状
    EDUCATION = "education"            # 教育学习
    SCIENCE = "science"                # 科学实验
    COGNITION = "cognition"            # 思维认知
    NATURE = "nature"                  # 自然生物
    ANATOMY = "anatomy"                # 人体解剖
    SPORTS = "sports"                  # 体育运动
    SPORTS_EQUIPMENT = "sports_equipment"  # 体育器材
    SPORTS_ACTION = "sports_action"    # 运动动作
    SPORTS_BALL = "sports_ball"        # 球类运动
    MECHANICAL = "mechanical"          # 机械工程
    ELECTRONIC = "electronic"          # 电子电气
    CONSTRUCTION = "construction"      # 建筑工程
    TRANSPORT = "transport"            # 交通运输
    MEDICAL = "medical"                # 医疗健康
    ART = "art"                        # 音乐艺术
    BUSINESS = "business"              # 商业金融
    FOOD = "food"                      # 食物饮品
    ANIMAL = "animal"                  # 动物
    GEOGRAPHY = "geography"            # 天文地理
    FURNITURE = "furniture"            # 家具家电
    DAILY = "daily"                    # 日常用品
    KITCHEN = "kitchen"                # 厨房用品
    CLASSROOM = "classroom"            # 教室用品
    MATH = "math"                      # 数学工具
    OUTDOOR = "outdoor"                # 户外场景
    WEATHER = "weather"                # 天气场景
    TIME = "time"                      # 时间场景
    EMOTION = "emotion"                # 情绪表情
    SOCIAL = "social"                  # 社交场景
    OFFICE = "office"                  # 工作场景
    SAFETY = "safety"                  # 安全场景


class SimulatorIcon(Base):
    """模拟器图标配置表"""
    __tablename__ = "simulator_icons"

    id = Column(String(50), primary_key=True)  # 图标ID，如 'book', 'running'
    name = Column(String(100), nullable=False)  # 显示名称
    name_en = Column(String(100))  # 英文名称
    category = Column(String(30), nullable=False)  # 使用字符串存储分类
    description = Column(Text)  # 图标描述
    keywords = Column(JSON)  # 搜索关键词 ["书", "阅读", "学习"]

    # 默认样式
    default_color = Column(String(20), default="#3B82F6")  # 默认颜色
    default_scale = Column(Float, default=1.0)  # 默认缩放

    # 推荐使用场景
    recommended_scenes = Column(JSON)  # ["education", "reading", "library"]

    # 元数据
    is_active = Column(Integer, default=1)
    sort_order = Column(Integer, default=0)
    usage_count = Column(Integer, default=0)  # 使用次数统计

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SimulatorIconPreset(Base):
    """模拟器图标预设组合"""
    __tablename__ = "simulator_icon_presets"

    id = Column(String(50), primary_key=True)  # 预设ID
    name = Column(String(100), nullable=False)
    name_en = Column(String(100))
    description = Column(Text)

    # 预设包含的图标配置
    icons = Column(JSON, nullable=False)  # [{"id": "book", "x": 100, "y": 100, "scale": 1.2, "tint": "#EF4444"}, ...]

    # 画布配置
    canvas_config = Column(JSON)  # {"width": 800, "height": 500, "background": {...}}

    # 分类和标签
    category = Column(String(50))  # 预设分类
    tags = Column(JSON)  # 标签

    # 元数据
    is_official = Column(Integer, default=0)  # 是否官方预设
    is_active = Column(Integer, default=1)
    usage_count = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ============================================
# User Notes (用户笔记)
# ============================================

class UserNote(Base):
    """用户学习笔记"""
    __tablename__ = "user_notes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    node_id = Column(Integer, ForeignKey("course_nodes.id"), nullable=True, index=True)  # 可选，关联到具体节点

    title = Column(String(255))  # 笔记标题（可选）
    content = Column(Text, nullable=False)  # 笔记内容（Markdown）

    # 元数据
    is_pinned = Column(Integer, default=0)  # 是否置顶
    is_archived = Column(Integer, default=0)  # 是否归档

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ============================================
# User Settings (用户学习设置)
# ============================================

class UserLearningSettings(Base):
    """用户学习偏好设置"""
    __tablename__ = "user_learning_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # 显示设置
    font_size = Column(String(20), default="medium")  # small, medium, large

    # 学习设置
    auto_play_next = Column(Integer, default=1)  # 自动播放下一节点
    show_learning_time = Column(Integer, default=1)  # 显示学习时长

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ============================================
# Unified Learning System (统一Agent学习系统)
# ============================================

class ContentTemplate(Base):
    """Unified content template for agent learning (2026-02-11)

    Stores high-quality content templates for 4 core features:
    - simulator: HTML simulator code
    - tutor_dialogue: AI tutor dialogue patterns
    - chapter_content: Course chapter content
    - quiz_question: Quiz questions

    Templates serve as reference examples for the AI agent to learn from
    and improve content generation quality over time.
    """
    __tablename__ = "content_templates"

    id = Column(Integer, primary_key=True, index=True)
    template_type = Column(String(50), nullable=False, index=True)  # 'simulator', 'tutor_dialogue', 'chapter_content', 'quiz_question'
    subject = Column(String(100), nullable=False, index=True)  # e.g., "physics", "mathematics"
    topic = Column(String(255), nullable=False, index=True)    # e.g., "projectile_motion", "linear_algebra"

    # Core content (JSON format)
    content = Column(Text, nullable=False)  # JSON string containing the template content
    quality_score = Column(Float, nullable=False, index=True)  # 0-100 quality score

    # Quality breakdown
    score_breakdown = Column(JSON)  # Detailed scoring per dimension

    # Learning metadata
    template_metadata = Column(JSON)  # {
        # Template-specific patterns and insights extracted for learning
        # e.g., "dialogue_strategies", "code_patterns", "content_structure"
    # }

    # Type-specific fields
    difficulty_level = Column(String(50))  # For quiz/chapter: "entry", "beginner", etc.
    content_hash = Column(String(64), index=True)  # For deduplication

    # Vector embedding for similarity search (384-dimensional)
    embedding = Column(get_vector_type(384))  # Sentence-transformers embedding

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    usage_count = Column(Integer, default=0)  # Track how many times this template was used


class QualityEvaluation(Base):
    """Quality evaluation records for all content types (2026-02-11)

    Tracks quality assessments of generated content to monitor
    learning progress and decide which content to save as templates.
    """
    __tablename__ = "quality_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(String(50), nullable=False, index=True)  # 'simulator', 'tutor_dialogue', 'chapter_content', 'quiz_question'
    content_id = Column(String(255), nullable=False, index=True)  # Unique identifier for the content
    quality_score = Column(Float, nullable=False)
    score_breakdown = Column(JSON)  # Detailed scoring per dimension
    saved_as_template = Column(Integer, default=0)  # Whether this was saved as a template
    evaluated_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


# ============================================
# Learning Patterns System (经验蒸馏系统)
# ============================================

class GenerationPattern(Base):
    """Generation pattern model for experience distillation (2026-02-13)

    Stores distilled patterns from successful content generations to guide
    future generation strategies and improve quality over time.
    """
    __tablename__ = "generation_patterns"

    id = Column(Integer, primary_key=True, index=True)
    pattern_type = Column(String(50), nullable=False, index=True)  # 'failure_recovery', 'optimization', 'best_practice'
    step_type = Column(String(50), nullable=False, index=True)  # 'text_content', 'illustrated_content', 'assessment', 'ai_tutor'
    subject = Column(String(100), nullable=False, index=True)  # e.g., "physics", "mathematics"

    # Pattern details
    pattern_name = Column(String(255), nullable=False)  # Human-readable pattern name
    pattern_description = Column(Text, nullable=False)  # Detailed description of the pattern
    trigger_conditions = Column(JSONType, nullable=False)  # Conditions that trigger this pattern
    solution_strategy = Column(Text, nullable=False)  # Strategy to apply when pattern is triggered

    # Pattern metrics
    confidence = Column(Float, nullable=False, default=0.8)  # Confidence score (0-1)
    use_count = Column(Integer, nullable=False, default=0)  # Number of times pattern was applied
    success_count = Column(Integer, nullable=False, default=0)  # Number of successful applications

    # Vector embedding for similarity search (384-dimensional)
    embedding = Column(get_vector_type(384), nullable=False)  # Sentence-transformers embedding

    # Source tracking
    source_templates = Column(JSONType)  # List of template IDs this pattern was distilled from
    created_from_count = Column(Integer, nullable=False, default=1)  # Number of templates used in distillation

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PatternApplication(Base):
    """Pattern application record (2026-02-13)

    Tracks when and how patterns are applied during content generation,
    including success metrics for continuous learning.
    """
    __tablename__ = "pattern_applications"

    id = Column(Integer, primary_key=True, index=True)
    pattern_id = Column(Integer, ForeignKey("generation_patterns.id", ondelete="CASCADE"), nullable=False, index=True)
    step_type = Column(String(50), nullable=False, index=True)  # 'text_content', 'illustrated_content', 'assessment', 'ai_tutor'
    subject = Column(String(100), nullable=False, index=True)
    topic = Column(String(255), nullable=False, index=True)

    # Application details
    original_input = Column(JSONType, nullable=False)  # Original generation request
    applied_strategy = Column(Text, nullable=False)  # Strategy text that was applied
    result_quality = Column(Float)  # Quality score of the result (if evaluated)
    success = Column(Boolean, nullable=False, default=True)  # Whether application was successful

    applied_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


# ============================================
# Generation Task Queue (并发课程生成任务队列)
# ============================================

class GenerationTaskStatus(str, enum.Enum):
    """课程生成任务状态"""
    PENDING = "pending"          # 排队中
    RUNNING = "running"          # 生成中
    COMPLETED = "completed"      # 已完成
    FAILED = "failed"            # 失败
    CANCELLED = "cancelled"      # 已取消


class GenerationTask(Base):
    """课程生成任务 (2026-02-23)

    支持多管理员并发生成课程，任务队列化管理。
    """
    __tablename__ = "generation_tasks"

    id = Column(String(36), primary_key=True)  # UUID
    admin_id = Column(Integer, nullable=False, index=True)
    status = Column(String(20), nullable=False, default="pending", index=True)

    # 生成参数
    course_title = Column(String(500), nullable=False)
    source_material = Column(Text)
    source_info = Column(Text)
    processor_id = Column(String(100))
    processor_prompt = Column(Text)

    # 进度信息
    progress_pct = Column(Integer, default=0)          # 0-100
    current_phase = Column(String(100))                 # 当前阶段描述
    chapters_completed = Column(Integer, default=0)     # 已完成章节数
    chapters_total = Column(Integer, default=0)         # 总章节数

    # 结果
    package_id = Column(String(36))                     # 生成完成后的课程包ID
    error_message = Column(Text)                        # 失败原因

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))


# ============================================
# BKT Knowledge Tracking Models (知识追踪)
# ============================================

class Subject(Base):
    """学科表"""
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    knowledge_nodes = relationship("KnowledgeNode", back_populates="subject")


class KnowledgeNode(Base):
    """知识节点"""
    __tablename__ = "knowledge_nodes"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False, index=True)
    course_node_id = Column(Integer, ForeignKey("course_nodes.id"), nullable=True)
    code = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    difficulty = Column(Float, default=0.5)
    parent_code = Column(String(100))
    prerequisites = Column(JSON, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    subject = relationship("Subject", back_populates="knowledge_nodes")
    course_node = relationship("CourseNode", foreign_keys=[course_node_id])


class StudentKnowledgeState(Base):
    """学生知识状态"""
    __tablename__ = "student_knowledge_state"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    knowledge_node_id = Column(Integer, ForeignKey("knowledge_nodes.id"), nullable=False, index=True)
    mastery = Column(Float, default=0.1)
    stability = Column(Float, default=0.5)
    last_practice_at = Column(DateTime(timezone=True))
    practice_count = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    streak = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class StudentEvent(Base):
    """学生行为事件"""
    __tablename__ = "student_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    knowledge_node_id = Column(Integer, ForeignKey("knowledge_nodes.id"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)
    is_correct = Column(Integer)
    response_time_ms = Column(Integer)
    event_data = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class StudentMisconception(Base):
    """学生错误概念"""
    __tablename__ = "student_misconceptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    knowledge_node_id = Column(Integer, ForeignKey("knowledge_nodes.id"), nullable=False, index=True)
    misconception = Column(Text, nullable=False)
    frequency = Column(Integer, default=1)
    last_seen_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class StudentEmotionState(Base):
    """学生情感状态（Phase 2 情感感知）"""
    __tablename__ = "student_emotion_states"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    emotion_type = Column(String(50), nullable=False)  # frustration, anxiety, boredom, focus, excitement
    intensity = Column(Float, default=0.0)  # 0~1 情感强度
    confidence = Column(Float, default=0.5)  # 检测置信度
    trigger_event_id = Column(Integer, ForeignKey("student_events.id"))
    trigger_type = Column(String(50))  # streak_fail, low_mastery, fast_correct, long_pause
    context = Column(JSON, default={})  # 附加上下文
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class StudentLearningPath(Base):
    """学生学习路径（Phase 2 自适应路径规划）"""
    __tablename__ = "student_learning_paths"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False, index=True)
    status = Column(String(20), default="active")  # active, completed, expired
    session_duration = Column(Integer, default=30)  # 计划学习时长（分钟）
    path_items = Column(JSON, default=[])  # 路径项列表
    emotion_snapshot = Column(String(50))  # 生成时的情感状态快照
    total_nodes = Column(Integer, default=0)
    completed_nodes = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))


class ReviewSchedule(Base):
    """间隔复习调度表（Phase 4 FSRS）"""
    __tablename__ = "review_schedule"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    knowledge_node_id = Column(Integer, ForeignKey("knowledge_nodes.id"), nullable=False)
    fsrs_stability = Column(Float, default=1.0)       # FSRS 稳定性
    fsrs_difficulty = Column(Float, default=5.0)       # FSRS 难度 (1~10)
    next_review_at = Column(DateTime(timezone=True), nullable=False)
    last_review_at = Column(DateTime(timezone=True))
    last_review_type = Column(String(30))              # flashcard, mini_quiz, simulator_replay, explain_to_ai
    last_rating = Column(Integer)                      # 1=Again, 2=Hard, 3=Good, 4=Easy
    review_count = Column(Integer, default=0)
    interval_days = Column(Float, default=1.0)         # 当前复习间隔（天）
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_review_user_due", "user_id", "next_review_at"),
        UniqueConstraint("user_id", "knowledge_node_id", name="uq_review_user_node"),
    )


class LearningReport(Base):
    """学习报告（Phase 5 元认知）"""
    __tablename__ = "learning_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    report_type = Column(String(20), nullable=False)  # session, weekly, monthly
    period_start = Column(DateTime(timezone=True))
    period_end = Column(DateTime(timezone=True))
    summary = Column(JSON, default={})       # 报告摘要数据
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MetacognitiveLog(Base):
    """元认知日志（Phase 5）"""
    __tablename__ = "metacognitive_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    trigger = Column(String(50), nullable=False)  # after_practice_set, session_end, etc.
    prompt_text = Column(Text, nullable=False)
    student_response = Column(Text)
    knowledge_node_id = Column(Integer, ForeignKey("knowledge_nodes.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class StudentConversation(Base):
    """学生对话记录（Phase 3 诊断式Tutor）"""
    __tablename__ = "student_conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    knowledge_node_id = Column(Integer, ForeignKey("knowledge_nodes.id"), nullable=False)
    session_id = Column(String(64), nullable=False, index=True)  # 对话会话ID
    tutor_phase = Column(String(20), default="understand")  # understand/diagnose/scaffold/explain/verify/extend
    messages = Column(JSON, default=[])  # [{role, content, timestamp}]
    diagnosis = Column(JSON, default={})  # 诊断结果
    emotion_snapshot = Column(String(50))  # 对话时的情感状态
    mastery_before = Column(Float)  # 对话前mastery
    mastery_after = Column(Float)  # 对话后mastery
    mode = Column(String(20), default="adaptive")  # adaptive/diagnostic/remedial/challenge
    turn_count = Column(Integer, default=0)
    resolved = Column(Boolean, default=False)  # 问题是否解决
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("idx_conv_user_session", "user_id", "session_id"),
        Index("idx_conv_user_node", "user_id", "knowledge_node_id"),
    )


class CourseRecommendation(Base):
    """课程推荐关联表（Phase 6 推荐系统）"""
    __tablename__ = "course_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    source_course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    target_course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    relation_type = Column(String(30), nullable=False)  # prerequisite/complementary/advanced/cross_discipline
    weight = Column(Float, default=1.0)  # 关联强度 0~1
    reason = Column(String(500))  # 推荐理由
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_rec_source", "source_course_id"),
        Index("idx_rec_target", "target_course_id"),
        UniqueConstraint("source_course_id", "target_course_id", "relation_type", name="uq_course_rec"),
    )


class RecommendedLesson(Base):
    """推荐小课堂记录（Phase 6）"""
    __tablename__ = "recommended_lessons"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    knowledge_node_id = Column(Integer, ForeignKey("knowledge_nodes.id"), nullable=False)
    course_node_id = Column(Integer, ForeignKey("course_nodes.id"))
    reason = Column(String(500))  # 推荐理由
    priority = Column(Integer, default=1)  # 1=最高
    mastery_at_recommend = Column(Float)  # 推荐时的掌握度
    emotion_at_recommend = Column(String(50))  # 推荐时的情感状态
    is_viewed = Column(Boolean, default=False)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    viewed_at = Column(DateTime(timezone=True))

    __table_args__ = (
        Index("idx_rec_lesson_user", "user_id", "created_at"),
    )


class RecommendedGrinder(Base):
    """推荐做题家题目记录（Phase 6）"""
    __tablename__ = "recommended_grinders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    knowledge_node_id = Column(Integer, ForeignKey("knowledge_nodes.id"), nullable=False)
    reason = Column(String(500))  # 推荐理由
    priority = Column(Integer, default=1)
    suggested_difficulty = Column(Float, default=0.5)
    mastery_at_recommend = Column(Float)
    emotion_at_recommend = Column(String(50))
    misconception_id = Column(Integer, ForeignKey("student_misconceptions.id"))
    is_viewed = Column(Boolean, default=False)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    viewed_at = Column(DateTime(timezone=True))

    __table_args__ = (
        Index("idx_rec_grinder_user", "user_id", "created_at"),
    )


class StudentAssessment(Base):
    """学生评估记录（Phase 7 智能评估与自适应反馈）"""
    __tablename__ = "student_assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    knowledge_node_id = Column(Integer, ForeignKey("knowledge_nodes.id"))
    mastery = Column(Float)  # 综合掌握度
    stability = Column(Float)  # 记忆稳定性
    frustration_level = Column(Float, default=0.0)  # 挫败感 0~1
    anxiety_level = Column(Float, default=0.0)  # 焦虑度 0~1
    focus_level = Column(Float, default=0.5)  # 专注度 0~1
    assessment_type = Column(String(30), default="auto")  # auto/manual/session_end
    feedback = Column(Text)  # 自适应反馈文本
    strategy_suggestions = Column(JSON, default=[])  # 学习策略建议列表
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_assess_user", "user_id", "created_at"),
    )


class StudentMultiTaskPlan(Base):
    """多任务学习计划（Phase 8 多任务学习与多目标优化）"""
    __tablename__ = "student_multi_task_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    objective_weights = Column(JSON, default={"mastery": 0.35, "retention": 0.25, "emotion": 0.2, "efficiency": 0.2})
    student_snapshot = Column(JSON, default={})
    tasks = Column(JSON, default=[])
    optimization_summary = Column(JSON, default={})
    status = Column(String(20), default="active")
    total_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    session_minutes = Column(Integer, default=30)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    __table_args__ = (
        Index("idx_mtp_user", "user_id", "created_at"),
        Index("idx_mtp_status", "user_id", "status"),
    )


class SubjectRelation(Base):
    """学科间关系（Phase 9 学科知识图谱）"""
    __tablename__ = "subject_relations"

    id = Column(Integer, primary_key=True, index=True)
    source_subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    target_subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    relation_type = Column(String(30), nullable=False)  # prerequisite/extension/cross_discipline/complementary
    weight = Column(Float, default=1.0)
    transfer_coefficient = Column(Float, default=0.3)  # 学习迁移系数 0~1
    description = Column(Text)
    shared_concepts = Column(JSON, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    source_subject = relationship("Subject", foreign_keys=[source_subject_id])
    target_subject = relationship("Subject", foreign_keys=[target_subject_id])

    __table_args__ = (
        Index("idx_sr_source", "source_subject_id"),
        Index("idx_sr_target", "target_subject_id"),
        UniqueConstraint("source_subject_id", "target_subject_id", "relation_type", name="uq_subject_rel"),
    )


class ConceptBridge(Base):
    """知识节点级跨学科概念桥接（Phase 10）"""
    __tablename__ = "concept_bridges"

    id = Column(Integer, primary_key=True, index=True)
    source_node_id = Column(Integer, ForeignKey("knowledge_nodes.id"), nullable=False)
    target_node_id = Column(Integer, ForeignKey("knowledge_nodes.id"), nullable=False)
    concept_name = Column(String(200), nullable=False)
    transfer_weight = Column(Float, default=0.5)  # 概念迁移权重
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    source_node = relationship("KnowledgeNode", foreign_keys=[source_node_id])
    target_node = relationship("KnowledgeNode", foreign_keys=[target_node_id])

    __table_args__ = (
        Index("idx_cb_source", "source_node_id"),
        Index("idx_cb_target", "target_node_id"),
        Index("idx_cb_concept", "concept_name"),
        UniqueConstraint("source_node_id", "target_node_id", "concept_name", name="uq_concept_bridge"),
    )


class CourseRelation(Base):
    """课程间结构关系（Phase 11）"""
    __tablename__ = "course_relations"

    id = Column(Integer, primary_key=True, index=True)
    source_course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    target_course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    relation_type = Column(String(30), nullable=False)  # prerequisite/advanced/parallel/supplementary
    weight = Column(Float, default=1.0)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_cr_source", "source_course_id"),
        Index("idx_cr_target", "target_course_id"),
        UniqueConstraint("source_course_id", "target_course_id", "relation_type", name="uq_course_rel"),
    )


class StudentCourseProgress(Base):
    """学生课程级进度聚合（Phase 11）"""
    __tablename__ = "student_course_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    total_nodes = Column(Integer, default=0)
    completed_nodes = Column(Integer, default=0)
    completion_pct = Column(Float, default=0.0)
    avg_mastery = Column(Float, default=0.0)
    total_time_seconds = Column(Integer, default=0)
    last_activity_at = Column(DateTime(timezone=True))
    status = Column(String(20), default="in_progress")  # in_progress/completed/paused
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_scp_user_course"),
        Index("idx_scp_user", "user_id", "status"),
    )


class StudentFeedback(Base):
    """综合学习反馈（Phase 12 学习反馈与智能报告）"""
    __tablename__ = "student_feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    feedback_type = Column(String(30), nullable=False)  # progress/emotion/smart_report
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    progress_summary = Column(JSON, default={})    # 学习进度摘要
    emotion_summary = Column(JSON, default={})     # 情感状态摘要
    suggestions = Column(JSON, default=[])         # 个性化建议列表
    difficulty_adjustment = Column(JSON, default={})  # 难度调整建议
    encouragement = Column(Text)                   # 鼓励语
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_sf_user", "user_id", "created_at"),
        Index("idx_sf_type", "user_id", "feedback_type"),
    )


class AgentStrategyReward(Base):
    """Agent策略奖惩记录（Phase 13 强化学习）"""
    __tablename__ = "agent_strategy_rewards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    strategy_type = Column(String(50), nullable=False)  # task_generation/difficulty_selection/content_type
    action_taken = Column(JSON, default={})        # 执行的动作
    student_state_before = Column(JSON, default={})  # 动作前学生状态
    student_state_after = Column(JSON, default={})   # 动作后学生状态
    reward_signal = Column(Float, default=0.0)       # 奖励信号 (-1 ~ +1)
    reward_components = Column(JSON, default={})     # 奖励分量明细
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_asr_user", "user_id", "created_at"),
        Index("idx_asr_strategy", "strategy_type", "reward_signal"),
    )


class AgentStrategyWeight(Base):
    """Agent策略权重（Phase 13 自我优化）"""
    __tablename__ = "agent_strategy_weights"

    id = Column(Integer, primary_key=True, index=True)
    strategy_type = Column(String(50), nullable=False, unique=True)
    weights = Column(JSON, default={})
    total_episodes = Column(Integer, default=0)
    avg_reward = Column(Float, default=0.0)
    last_updated_at = Column(DateTime(timezone=True), server_default=func.now())


class StudentGoal(Base):
    """学习目标（Phase 15 目标管理）"""
    __tablename__ = "student_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal_type = Column(String(20), nullable=False)  # mastery/streak/completion/custom
    title = Column(String(200), nullable=False)
    description = Column(Text)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    node_id = Column(Integer, ForeignKey("knowledge_nodes.id"))
    target_value = Column(Float, nullable=False)
    current_value = Column(Float, default=0)
    deadline = Column(DateTime(timezone=True))
    status = Column(String(20), default="active")  # active/completed/abandoned/expired
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_sg_user_status", "user_id", "status"),
        Index("idx_sg_user_deadline", "user_id", "deadline"),
    )


class LearningHabit(Base):
    """每日学习习惯快照（Phase 15 习惯追踪）"""
    __tablename__ = "learning_habits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime(timezone=False), nullable=False)  # DATE type
    events_count = Column(Integer, default=0)
    study_minutes = Column(Integer, default=0)
    subjects_touched = Column(Integer, default=0)
    accuracy = Column(Float)
    dominant_emotion = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_lh_user_date"),
        Index("idx_lh_user_date", "user_id", "date"),
    )


class StudentSubjectTransfer(Base):
    """个性化跨学科迁移系数（Phase 16 动态贝叶斯更新）"""
    __tablename__ = "student_subject_transfers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    source_subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    target_subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    observed_transfer = Column(Float, default=0.5)
    confidence = Column(Float, default=0.1)
    sample_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "source_subject_id", "target_subject_id", name="uq_sst_user_src_tgt"),
        Index("idx_sst_user", "user_id"),
        Index("idx_sst_user_source", "user_id", "source_subject_id"),
    )
