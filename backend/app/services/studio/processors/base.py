# ============================================
# processors/base.py - 处理器基类和注册表（简化版）
# ============================================

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Type
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class ProcessorInfo:
    """处理器元信息"""
    id: str
    name: str
    description: str
    version: str = "1.0.0"
    author: str = ""
    tags: List[str] = field(default_factory=list)
    color: str = "#6366f1"
    icon: str = "sparkles"


class BaseProcessor(ABC):
    """课程处理器基类"""

    processor_info: ProcessorInfo

    def __init__(self):
        pass

    @abstractmethod
    def analyze_content(self, content: str, context: Dict[str, Any] = None) -> Any:
        """分析内容特性"""
        pass

    @abstractmethod
    def recommend_forms(self, analysis: Any) -> List[str]:
        """推荐教学形式"""
        pass

    @abstractmethod
    def build_structure_prompt(
        self,
        source_material: str,
        course_title: str,
        context: Dict[str, Any] = None
    ) -> str:
        """构建课程结构生成的 prompt"""
        pass

    @abstractmethod
    def build_lesson_prompt(
        self,
        source_material: str,
        course_title: str,
        lesson_info: Dict[str, Any],
        lesson_index: int,
        total_lessons: int,
        previous_summary: str = "",
        context: Dict[str, Any] = None
    ) -> str:
        """构建单个课时内容生成的 prompt"""
        pass

    def get_style_prompt(self) -> str:
        return f"使用 {self.processor_info.name} 风格进行讲解。"

    def process_structure(self, raw_structure: Dict[str, Any]) -> Dict[str, Any]:
        return raw_structure

    def process_lesson(self, raw_lesson: Dict[str, Any], lesson_info: Dict[str, Any]) -> Dict[str, Any]:
        return raw_lesson

    def assemble_package(
        self,
        meta: Dict[str, Any],
        lessons: List[Dict[str, Any]],
        source_info: str = ""
    ) -> Dict[str, Any]:
        """组装完整课程包"""
        date = datetime.now().strftime("%Y%m%d")
        rand = uuid.uuid4().hex[:4].upper()
        pkg_id = f"PKG-{date}-{rand}"

        processed_lessons = []
        edges = []
        lesson_id_map = {}

        for i, lesson_data in enumerate(lessons):
            lesson_id = f"{pkg_id}_L{i+1:03d}"
            lesson_id_map[i] = lesson_id

            steps = lesson_data.get("script", [])
            for j, step in enumerate(steps):
                step["step_id"] = f"{lesson_id}_S{j+1:03d}"

            processed_lesson = {
                "lesson_id": lesson_id,
                "title": lesson_data.get("title", f"课时 {i+1}"),
                "total_steps": len(steps),
                "rationale": lesson_data.get("rationale", ""),
                "script": steps,
                "estimated_minutes": lesson_data.get("estimated_minutes", 30),
                "prerequisites": [],
                "learning_objectives": lesson_data.get("learning_objectives", []),
                "complexity_level": lesson_data.get("complexity_level", "standard"),
            }
            processed_lessons.append(processed_lesson)

        edge_idx = 1
        for i, lesson_data in enumerate(lessons):
            prereqs = []
            for prereq_idx in lesson_data.get("prerequisites", []):
                if prereq_idx in lesson_id_map:
                    prereq_id = lesson_id_map[prereq_idx]
                    prereqs.append(prereq_id)
                    edges.append({
                        "id": f"{pkg_id}_E{edge_idx:03d}",
                        "from": prereq_id,
                        "to": lesson_id_map[i],
                        "type": "prerequisite"
                    })
                    edge_idx += 1
            processed_lessons[i]["prerequisites"] = prereqs

        package = {
            "id": pkg_id,
            "version": "2.0.0",
            "meta": {
                "title": meta.get("title", "未命名课程"),
                "description": meta.get("description", ""),
                "source_info": source_info,
                "total_lessons": len(processed_lessons),
                "estimated_hours": meta.get("estimated_hours", len(processed_lessons) * 0.5),
                "style": self.processor_info.id,
                "created_at": datetime.now().isoformat(),
            },
            "lessons": processed_lessons,
            "edges": edges,
            "global_ai_config": {
                "tutor_persona": "专业友好的AI导师",
                "fallback_responses": ["让我换个方式解释...", "我们再看一遍..."]
            }
        }

        return package

    def get_info(self) -> Dict[str, Any]:
        """获取处理器信息"""
        return {
            "id": self.processor_info.id,
            "name": self.processor_info.name,
            "description": self.processor_info.description,
            "version": self.processor_info.version,
            "author": self.processor_info.author,
            "tags": self.processor_info.tags,
            "color": self.processor_info.color,
            "icon": self.processor_info.icon,
        }


class ProcessorRegistry:
    """处理器注册表"""

    _processors: Dict[str, Type[BaseProcessor]] = {}
    _instances: Dict[str, BaseProcessor] = {}
    _default_processor: str = "intelligent"

    @classmethod
    def register(cls, processor_class: Type[BaseProcessor]) -> Type[BaseProcessor]:
        processor_id = processor_class.processor_info.id
        cls._processors[processor_id] = processor_class
        return processor_class

    @classmethod
    def get(cls, processor_id: str) -> Optional[BaseProcessor]:
        if processor_id not in cls._processors:
            return None
        if processor_id not in cls._instances:
            cls._instances[processor_id] = cls._processors[processor_id]()
        return cls._instances[processor_id]

    @classmethod
    def get_default(cls) -> BaseProcessor:
        processor = cls.get(cls._default_processor)
        if processor is None:
            if cls._processors:
                first_id = next(iter(cls._processors))
                return cls.get(first_id)
            raise RuntimeError("没有可用的处理器")
        return processor

    @classmethod
    def set_default(cls, processor_id: str):
        if processor_id not in cls._processors:
            raise ValueError(f"处理器 '{processor_id}' 不存在")
        cls._default_processor = processor_id

    @classmethod
    def list_all(cls) -> List[Dict[str, Any]]:
        result = []
        for processor_id, processor_class in cls._processors.items():
            info = processor_class.processor_info
            result.append({
                "id": info.id,
                "name": info.name,
                "description": info.description,
                "version": info.version,
                "tags": info.tags,
                "color": info.color,
                "icon": info.icon,
            })
        return result

    @classmethod
    def exists(cls, processor_id: str) -> bool:
        return processor_id in cls._processors

    @classmethod
    def clear(cls):
        cls._processors.clear()
        cls._instances.clear()

    @classmethod
    def reload(cls):
        cls._instances.clear()
