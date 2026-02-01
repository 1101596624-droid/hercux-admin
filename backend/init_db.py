from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, Float, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()

# Enums
class DifficultyLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class NodeType(str, enum.Enum):
    CHAPTER = "chapter"
    SECTION = "section"
    LESSON = "lesson"

class NodeStatus(str, enum.Enum):
    LOCKED = "locked"
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class StudioPackageStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    avatar_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    total_usage_seconds = Column(Integer, default=0)
    total_tokens_used = Column(Integer, default=0)
    total_input_tokens = Column(Integer, default=0)
    total_output_tokens = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    difficulty = Column(Enum(DifficultyLevel), default=DifficultyLevel.BEGINNER)
    instructor = Column(String(255))
    duration_hours = Column(Float, default=0)
    thumbnail_url = Column(String(500))
    is_published = Column(Boolean, default=False)
    tags = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class CourseNode(Base):
    __tablename__ = "course_nodes"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("course_nodes.id"), nullable=True)
    node_id = Column(String(100), unique=True, nullable=False)
    type = Column(Enum(NodeType), nullable=False)
    component_id = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    sequence = Column(Integer, default=0)
    content = Column(JSON)
    config = Column(JSON)
    timeline_config = Column(JSON)
    unlock_condition = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class LearningProgress(Base):
    __tablename__ = "learning_progress"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    node_id = Column(Integer, ForeignKey("course_nodes.id"), nullable=False, index=True)
    status = Column(Enum(NodeStatus), default=NodeStatus.LOCKED)
    current_step = Column(Integer, default=0)
    score = Column(Float)
    time_spent_seconds = Column(Integer, default=0)
    attempts = Column(Integer, default=0)
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class UserCourse(Base):
    __tablename__ = "user_courses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    progress_percentage = Column(Float, default=0)

class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    node_id = Column(Integer, ForeignKey("course_nodes.id"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class LearningStatistics(Base):
    __tablename__ = "learning_statistics"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    total_time_seconds = Column(Integer, default=0)
    nodes_completed = Column(Integer, default=0)
    streak_days = Column(Integer, default=0)

class SimulatorResult(Base):
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

class StudioProcessor(Base):
    __tablename__ = "studio_processors"
    id = Column(String(100), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    version = Column(String(50), default="1.0.0")
    author = Column(String(255))
    tags = Column(JSON)
    color = Column(String(50), default="#3B82F6")
    icon = Column(String(50), default="Sparkles")
    system_prompt = Column(Text)
    enabled = Column(Integer, default=1)
    display_order = Column(Integer, default=0)
    is_official = Column(Integer, default=0)
    is_custom = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class StudioPackage(Base):
    __tablename__ = "studio_packages"
    id = Column(String(100), primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    source_info = Column(Text)
    style = Column(String(100))
    status = Column(Enum(StudioPackageStatus), default=StudioPackageStatus.DRAFT)
    meta = Column(JSON)
    lessons = Column(JSON)
    edges = Column(JSON)
    global_ai_config = Column(JSON)
    total_lessons = Column(Integer, default=0)
    estimated_hours = Column(Float, default=0)
    processor_id = Column(String(100), ForeignKey("studio_processors.id"), nullable=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Create tables
# Use absolute path for Linux server
import os
db_path = os.environ.get('DB_PATH', '/www/wwwroot/hercu-backend/hercu.db')
engine = create_engine(f'sqlite:///{db_path}')
Base.metadata.create_all(bind=engine)
print(f'All tables created successfully in {db_path}!')
