from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import enum


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
    content = Column(JSON)  # Lesson content with steps
    config = Column(JSON)  # Lesson configuration

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


class LearningProgress(Base):
    """User learning progress tracking"""
    __tablename__ = "learning_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    node_id = Column(Integer, ForeignKey("course_nodes.id"), nullable=False, index=True)
    status = Column(Enum(NodeStatus, values_callable=lambda x: [e.value for e in x]), default=NodeStatus.LOCKED, index=True)
    completion_percentage = Column(Float, default=0.0)
    time_spent_seconds = Column(Integer, default=0)
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

