"""
HERCU Studio 课程包导入服务
支持 V2 格式 (CoursePackageV2 - lessons/script 结构)
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import uuid
import logging
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ==================== V2 数据模型 ====================

class TextContent(BaseModel):
    """文本内容"""
    body: str = ""
    key_points: List[str] = Field(default_factory=list)


class IllustratedContent(BaseModel):
    """图文内容"""
    text: str = ""


class DiagramSpec(BaseModel):
    """图表规格"""
    diagram_id: str = ""
    type: str = "static_diagram"
    description: str = ""
    annotations: List[Dict] = Field(default_factory=list)
    design_notes: str = ""


class VideoSpec(BaseModel):
    """视频规格"""
    video_id: str = ""
    duration: str = ""
    script: Optional[Dict] = None
    production_notes: str = ""


class EmbeddedInteraction(BaseModel):
    """嵌入式交互"""
    timestamp: str = ""
    type: str = "pause_and_ask"
    question: str = ""
    options: List[str] = Field(default_factory=list)
    correct: str = ""


class SimulatorSpec(BaseModel):
    """模拟器规格"""
    simulator_id: str = ""
    type: str = ""
    scenario: Dict = Field(default_factory=dict)
    interface_spec: Optional[Dict] = None
    evaluation_logic: Optional[Dict] = None


class AITutorSpec(BaseModel):
    """AI 导师规格"""
    opening_message: str = ""
    conversation_goals: List[Dict] = Field(default_factory=list)
    max_turns: int = 5


class AssessmentQuestion(BaseModel):
    """评估问题"""
    question: str = ""
    scenario: str = ""
    options: List[str] = Field(default_factory=list)
    correct: str = ""
    explanation: str = ""


class AssessmentSpec(BaseModel):
    """评估规格"""
    type: str = "multiple_choice"
    questions: List[AssessmentQuestion] = Field(default_factory=list)
    pass_required: bool = False


class PracticeContent(BaseModel):
    """练习内容"""
    instructions: str = ""
    tasks: List[str] = Field(default_factory=list)


class LessonStep(BaseModel):
    """课时步骤"""
    step_id: str
    type: str  # text_content, illustrated_content, video, simulator, ai_tutor, assessment, quick_check, practice
    title: str = ""
    content: Optional[Dict] = None
    diagram_spec: Optional[Dict] = None
    video_spec: Optional[Dict] = None
    embedded_interactions: List[Dict] = Field(default_factory=list)
    simulator_spec: Optional[Dict] = None
    trigger: str = ""
    ai_spec: Optional[Dict] = None
    assessment_spec: Optional[Dict] = None


class Lesson(BaseModel):
    """课时"""
    lesson_id: str
    title: str
    order: int = 0
    total_steps: int = 0
    rationale: str = ""
    steps: List[LessonStep] = Field(default_factory=list)
    estimated_minutes: int = 30
    prerequisites: List[str] = Field(default_factory=list)
    learning_objectives: List[str] = Field(default_factory=list)
    complexity_level: str = "standard"


class PackageMetaV2(BaseModel):
    """V2 课程包元数据"""
    title: str
    description: str = ""
    cover_url: str = ""
    source_info: str = ""
    total_lessons: int = 0
    estimated_hours: float = 0
    style: str = "rcs"
    difficulty: str = "intermediate"  # 难度等级: entry, beginner, intermediate, advanced, expert
    created_at: str = ""


class Edge(BaseModel):
    """边"""
    id: str
    from_: str = Field(alias="from", default="")
    to: str = ""
    type: str = "prerequisite"

    class Config:
        populate_by_name = True


class GlobalAIConfig(BaseModel):
    """全局 AI 配置"""
    tutor_persona: str = ""
    fallback_responses: List[str] = Field(default_factory=list)


class CoursePackageV2(BaseModel):
    """V2 课程包"""
    id: str
    version: str = "2.0.0"
    meta: PackageMetaV2
    lessons: List[Lesson] = Field(default_factory=list)
    edges: List[Edge] = Field(default_factory=list)
    global_ai_config: GlobalAIConfig = Field(default_factory=GlobalAIConfig)


# ==================== 导入服务 ====================

class PackageImporterV2:
    """V2 课程包导入器 (异步版本)"""

    def __init__(self, db_session):
        self.db = db_session

    async def import_package(
        self,
        package: CoursePackageV2,
        user_id: Optional[int] = None,
        instructor_name: Optional[str] = None
    ) -> Dict:
        """
        导入 V2 课程包

        Args:
            package: V2 课程包
            user_id: 导入用户 ID
            instructor_name: 导入用户名称 (作为课程负责人)

        Returns:
            导入结果 {course_id, nodes_created, edges_created}
        """
        try:
            # 1. 检查是否已导入
            existing = await self._check_existing(package.id)
            if existing:
                raise ValueError(f"课程包 {package.id} 已存在")

            # 2. 创建课程 (传入负责人名称)
            course_id = await self._create_course(package, instructor_name)

            # 3. 创建节点 (从 lessons 转换)
            node_id_map = await self._create_nodes_from_lessons(package, course_id)

            # 4. 创建依赖关系
            edges_created = await self._create_edges(package, node_id_map)

            # 5. 保存课程包记录
            await self._save_package_record(package, course_id, user_id)

            await self.db.commit()

            return {
                "success": True,
                "course_id": course_id,
                "nodes_created": len(node_id_map),
                "edges_created": edges_created,
                "message": "课程包导入成功"
            }

        except Exception as e:
            await self.db.rollback()
            raise Exception(f"导入失败: {str(e)}")

    async def _check_existing(self, studio_package_id: str) -> bool:
        """检查课程包是否已存在"""
        from sqlalchemy import text
        result = await self.db.execute(
            text("SELECT id FROM course_packages WHERE studio_package_id = :pkg_id"),
            {"pkg_id": studio_package_id}
        )
        return result.fetchone() is not None

    async def _create_course(self, package: CoursePackageV2, instructor_name: Optional[str] = None) -> int:
        """创建课程记录"""
        from sqlalchemy import text

        # 获取难度等级，默认为 intermediate
        difficulty = package.meta.difficulty or "intermediate"
        # 验证难度等级
        valid_difficulties = ["entry", "beginner", "intermediate", "advanced", "expert"]
        if difficulty not in valid_difficulties:
            difficulty = "intermediate"

        result = await self.db.execute(
            text("""
                INSERT INTO courses (
                    name, description, difficulty, duration_hours,
                    instructor, thumbnail_url, is_published, created_at
                )
                VALUES (:name, :description, :difficulty, :duration_hours, :instructor, :thumbnail_url, :is_published, :created_at)
                RETURNING id
            """),
            {
                "name": package.meta.title,
                "description": package.meta.description,
                "difficulty": difficulty,
                "duration_hours": package.meta.estimated_hours,
                "instructor": instructor_name,
                "thumbnail_url": package.meta.cover_url or None,
                "is_published": 0,
                "created_at": datetime.now()
            }
        )

        # 获取最后插入的 ID
        course_id = result.fetchone()[0]

        return course_id

    async def _create_nodes_from_lessons(
        self,
        package: CoursePackageV2,
        course_id: int
    ) -> Dict[str, int]:
        """
        从 lessons 创建节点记录

        Returns:
            Lesson ID -> Node ID 映射
        """
        from sqlalchemy import text
        node_id_map = {}

        for index, lesson in enumerate(package.lessons):
            # 将 lesson 的 script 转换为节点内容
            node_content = self._convert_lesson_to_node_content(lesson)

            # 生成唯一的 node_id
            node_id = f"{package.id}_{lesson.lesson_id}"

            await self.db.execute(
                text("""
                    INSERT INTO course_nodes (
                        course_id, node_id, type, component_id, title, description,
                        sequence, content, config, created_at
                    )
                    VALUES (
                        :course_id, :node_id, :type, :component_id, :title, :description,
                        :sequence, :content, :config, :created_at
                    )
                    RETURNING id
                """),
                {
                    "course_id": course_id,
                    "node_id": node_id,
                    "type": "lesson",
                    "component_id": lesson.lesson_id,
                    "title": lesson.title,
                    "description": lesson.rationale or "",
                    "sequence": index + 1,
                    "content": json.dumps(node_content, ensure_ascii=False),
                    "config": json.dumps({
                        "estimated_minutes": lesson.estimated_minutes,
                        "learning_objectives": lesson.learning_objectives,
                        "complexity_level": lesson.complexity_level,
                        "prerequisites": lesson.prerequisites
                    }, ensure_ascii=False),
                    "created_at": datetime.now()
                }
            )

            # 获取最后插入的 ID
            result = await self.db.execute(text("SELECT currval('course_nodes_id_seq')"))
            hercu_node_id = result.fetchone()[0]
            node_id_map[lesson.lesson_id] = hercu_node_id

        return node_id_map

    def _convert_lesson_to_node_content(self, lesson: Lesson) -> Dict:
        """
        将 lesson 的 script 转换为节点内容格式
        """
        steps = []

        for step in lesson.steps:
            step_data = {
                "step_id": step.step_id,
                "type": step.type,
                "title": step.title,
            }

            # 根据类型添加对应内容 (确保 Pydantic 模型转换为字典)
            if step.content:
                step_data["content"] = step.content if isinstance(step.content, dict) else step.content
            if step.diagram_spec:
                step_data["diagram_spec"] = step.diagram_spec.model_dump() if hasattr(step.diagram_spec, 'model_dump') else step.diagram_spec
            if step.video_spec:
                step_data["video_spec"] = step.video_spec.model_dump() if hasattr(step.video_spec, 'model_dump') else step.video_spec
            if step.embedded_interactions:
                step_data["embedded_interactions"] = [
                    ei.model_dump() if hasattr(ei, 'model_dump') else ei
                    for ei in step.embedded_interactions
                ]
            if step.simulator_spec:
                # 确保 simulator_spec 被正确转换为字典，保留所有字段
                logger.info(f"[PackageImporter] Processing simulator_spec for step: {step.title}")
                logger.info(f"[PackageImporter] simulator_spec type: {type(step.simulator_spec)}")
                logger.info(f"[PackageImporter] simulator_spec content: {step.simulator_spec}")

                if hasattr(step.simulator_spec, 'model_dump'):
                    spec_dict = step.simulator_spec.model_dump(exclude_none=True)
                elif isinstance(step.simulator_spec, dict):
                    spec_dict = step.simulator_spec
                else:
                    spec_dict = dict(step.simulator_spec)

                logger.info(f"[PackageImporter] spec_dict keys: {list(spec_dict.keys())}")
                logger.info(f"[PackageImporter] spec_dict mode: {spec_dict.get('mode')}")
                logger.info(f"[PackageImporter] spec_dict custom_code exists: {bool(spec_dict.get('custom_code'))}")

                step_data["simulator_spec"] = spec_dict
            if step.ai_spec:
                step_data["ai_spec"] = step.ai_spec.model_dump() if hasattr(step.ai_spec, 'model_dump') else step.ai_spec
            if step.assessment_spec:
                step_data["assessment_spec"] = step.assessment_spec.model_dump() if hasattr(step.assessment_spec, 'model_dump') else step.assessment_spec
            if step.trigger:
                step_data["trigger"] = step.trigger

            steps.append(step_data)

        return {
            "version": "2.0",
            "lesson_id": lesson.lesson_id,
            "title": lesson.title,
            "rationale": lesson.rationale,
            "estimated_minutes": lesson.estimated_minutes,
            "learning_objectives": lesson.learning_objectives,
            "complexity_level": lesson.complexity_level,
            "steps": steps
        }

    async def _create_edges(
        self,
        package: CoursePackageV2,
        node_id_map: Dict[str, int]
    ) -> int:
        """创建节点依赖关系"""
        edges_created = 0

        for edge in package.edges:
            from_id = node_id_map.get(edge.from_)
            to_id = node_id_map.get(edge.to)

            if not from_id or not to_id:
                continue

            edges_created += 1

        return edges_created

    async def _save_package_record(
        self,
        package: CoursePackageV2,
        course_id: int,
        user_id: Optional[int]
    ):
        """保存课程包记录"""
        from sqlalchemy import text

        await self.db.execute(
            text("""
                INSERT INTO course_packages (
                    studio_package_id, course_id, version, style,
                    package_data, imported_by, imported_at
                )
                VALUES (:studio_package_id, :course_id, :version, :style, :package_data, :imported_by, :imported_at)
            """),
            {
                "studio_package_id": package.id,
                "course_id": course_id,
                "version": package.version,
                "style": package.meta.style,
                "package_data": json.dumps(package.model_dump(), ensure_ascii=False),
                "imported_by": user_id,
                "imported_at": datetime.now()
            }
        )


# 别名导出
PackageImporter = PackageImporterV2
StudioPackage = CoursePackageV2
