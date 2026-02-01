# ============================================
# generation/output_processor.py - 输出处理器
# ============================================

from datetime import datetime
import uuid


class IDGenerator:
    """简单的 ID 生成器"""

    @staticmethod
    def _short_uuid():
        return uuid.uuid4().hex[:8]

    @classmethod
    def package_id(cls):
        return f"pkg_{cls._short_uuid()}"

    @classmethod
    def node_id(cls, pkg_id: str, index: int):
        return f"node_{cls._short_uuid()}"

    @classmethod
    def lesson_id(cls, pkg_id: str, index: int):
        return f"lesson_{cls._short_uuid()}"

    @classmethod
    def step_id(cls, lesson_id: str, index: int):
        return f"step_{cls._short_uuid()}"

    @classmethod
    def timeline_id(cls, node_id: str, at_percent: int):
        return f"tl_{cls._short_uuid()}"

    @classmethod
    def quiz_id(cls, node_id: str):
        return f"quiz_{cls._short_uuid()}"

    @classmethod
    def question_id(cls, quiz_id: str, index: int):
        return f"q_{cls._short_uuid()}"

    @classmethod
    def edge_id(cls, pkg_id: str, index: int):
        return f"edge_{cls._short_uuid()}"


def process_output(raw: dict, style: str, source_info: str) -> dict:
    """后处理：分配 ID"""
    pkg_id = IDGenerator.package_id()
    node_id_map = {}

    nodes = []
    for i, node in enumerate(raw.get("nodes", [])):
        node_id = IDGenerator.node_id(pkg_id, i + 1)
        node_id_map[i] = node_id

        # 时间轴 ID
        timeline = []
        for event in node.get("timeline", []):
            event["id"] = IDGenerator.timeline_id(node_id, event["at_percent"])
            timeline.append(event)

        # 测验 ID
        quiz = node.get("quiz", {})
        if quiz:
            quiz_id = IDGenerator.quiz_id(node_id)
            quiz["id"] = quiz_id
            for j, q in enumerate(quiz.get("questions", [])):
                q["id"] = IDGenerator.question_id(quiz_id, j + 1)

        nodes.append({
            "id": node_id,
            "title": node["title"],
            "order": i + 1,
            "estimated_minutes": node.get("estimated_minutes", 30),
            "prerequisites": [],
            "learning_objectives": node.get("learning_objectives", []),
            "content": node.get("content", {}),
            "timeline": timeline,
            "quiz": quiz,
            "ai_tutor": node.get("ai_tutor", {})
        })

    # 转换依赖
    edges = []
    edge_idx = 1
    for i, node in enumerate(raw.get("nodes", [])):
        prereqs = []
        for prereq_idx in node.get("prerequisites", []):
            if prereq_idx in node_id_map:
                prereq_id = node_id_map[prereq_idx]
                prereqs.append(prereq_id)
                edges.append({
                    "id": IDGenerator.edge_id(pkg_id, edge_idx),
                    "from": prereq_id,
                    "to": node_id_map[i],
                    "type": "prerequisite"
                })
                edge_idx += 1
        nodes[i]["prerequisites"] = prereqs

    meta = raw.get("meta", {})

    return {
        "id": pkg_id,
        "version": "1.0.0",
        "meta": {
            "title": meta.get("title", "未命名课程"),
            "description": meta.get("description", ""),
            "source_info": source_info,
            "total_nodes": len(nodes),
            "estimated_hours": meta.get("estimated_hours", len(nodes) * 0.5),
            "style": style,
            "created_at": datetime.now().isoformat()
        },
        "nodes": nodes,
        "edges": edges,
        "global_ai_config": {
            "tutor_persona": "专业友好的AI导师",
            "fallback_responses": ["让我换个方式解释...", "我们再看一遍..."]
        }
    }


def process_output_v2(raw: dict, style: str, source_info: str) -> dict:
    """后处理 v2：处理新的 lesson-based 结构"""
    pkg_id = IDGenerator.package_id()
    lesson_id_map = {}

    lessons = []
    for i, lesson in enumerate(raw.get("lessons", [])):
        lesson_id = IDGenerator.lesson_id(pkg_id, i + 1)
        lesson_id_map[i] = lesson_id

        # 处理 steps
        script = lesson.get("script", [])
        for j, step in enumerate(script):
            step["step_id"] = IDGenerator.step_id(lesson_id, j + 1)

        lessons.append({
            "lesson_id": lesson_id,
            "title": lesson.get("title", f"课时 {i + 1}"),
            "order": i + 1,
            "total_steps": len(script),
            "rationale": lesson.get("rationale", ""),
            "script": script,
            "estimated_minutes": lesson.get("estimated_minutes", 30),
            "prerequisites": [],
            "learning_objectives": lesson.get("learning_objectives", []),
            "complexity_level": lesson.get("complexity_level", "standard"),
        })

    # 转换依赖
    edges = []
    edge_idx = 1
    for i, lesson in enumerate(raw.get("lessons", [])):
        prereqs = []
        for prereq_idx in lesson.get("prerequisites", []):
            if prereq_idx in lesson_id_map:
                prereq_id = lesson_id_map[prereq_idx]
                prereqs.append(prereq_id)
                edges.append({
                    "id": IDGenerator.edge_id(pkg_id, edge_idx),
                    "from": prereq_id,
                    "to": lesson_id_map[i],
                    "type": "prerequisite"
                })
                edge_idx += 1
        lessons[i]["prerequisites"] = prereqs

    meta = raw.get("meta", {})

    return {
        "id": pkg_id,
        "version": "2.0.0",
        "meta": {
            "title": meta.get("title", "未命名课程"),
            "description": meta.get("description", ""),
            "source_info": source_info,
            "total_lessons": len(lessons),
            "estimated_hours": meta.get("estimated_hours", len(lessons) * 0.5),
            "style": style,
            "created_at": datetime.now().isoformat()
        },
        "lessons": lessons,
        "edges": edges,
        "global_ai_config": {
            "tutor_persona": "专业友好的AI导师",
            "fallback_responses": ["让我换个方式解释...", "我们再看一遍..."]
        }
    }
