from dataclasses import dataclass, field
from typing import List, Dict, Any
from abc import ABC, abstractmethod
import re
from app.core.constants import QUALITY_BASELINE, QUALITY_SUPERVISOR_PASS

@dataclass
class BaseQualityScore:
    total_score: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)
    passed: bool = False
    threshold: float = QUALITY_BASELINE

    def calculate_total(self, *args):
        self.total_score = sum(args)
        self.passed = self.total_score >= self.threshold

class BaseQualityScorer(ABC):
    def evaluate(self, content): pass
    def extract_metadata(self, content): return {}

@dataclass
class TutorDialogueQualityScore(BaseQualityScore):
    coherence_score: float = 0.0
    guidance_score: float = 0.0
    knowledge_score: float = 0.0
    diagnosis_score: float = 0.0
    teaching_score: float = 0.0

    def calculate_total(self):
        super().calculate_total(self.coherence_score, self.guidance_score,
                                self.knowledge_score, self.diagnosis_score,
                                self.teaching_score)

@dataclass
class ChapterQualityScore(BaseQualityScore):
    depth_score: float = 0.0
    structure_score: float = 0.0
    visual_score: float = 0.0
    teaching_score: float = 0.0
    simulator_score: float = 0.0
    threshold: float = QUALITY_SUPERVISOR_PASS

    def calculate_total(self):
        super().calculate_total(self.depth_score, self.structure_score,
                                self.visual_score, self.teaching_score,
                                self.simulator_score)

@dataclass
class QuizQualityScore(BaseQualityScore):
    difficulty_score: float = 0.0
    option_score: float = 0.0
    explanation_score: float = 0.0
    knowledge_score: float = 0.0
    teaching_score: float = 0.0

    def calculate_total(self):
        super().calculate_total(self.difficulty_score, self.option_score,
                                self.explanation_score, self.knowledge_score,
                                self.teaching_score)


class TutorDialogueScorer(BaseQualityScorer):
    """AI导师对话质量评分器 - 基于规则的对话质量评估

    评分维度 (满分100):
    - coherence_score (0-20): 对话连贯性 — 轮次数、上下文关联
    - guidance_score (0-20): 引导质量 — 提问引导、非直接给答案
    - knowledge_score (0-20): 知识密度 — 学科术语、概念覆盖
    - diagnosis_score (0-20): 诊断能力 — 识别错误、针对性纠正
    - teaching_score (0-20): 教学策略 — 总结、鼓励、下一步建议
    """

    MAX_COHERENCE = 20.0
    MAX_GUIDANCE = 20.0
    MAX_KNOWLEDGE = 20.0
    MAX_DIAGNOSIS = 20.0
    MAX_TEACHING = 20.0

    def evaluate(self, dialogue: Dict[str, Any]) -> TutorDialogueQualityScore:
        score = TutorDialogueQualityScore()

        # 提取对话数据
        messages = dialogue.get("messages", dialogue.get("turns", []))
        ai_spec = dialogue.get("ai_spec", {})
        if not messages and not ai_spec:
            score.issues.append("No dialogue data found")
            score.calculate_total()
            return score

        score.coherence_score = self._score_coherence(messages, ai_spec)
        score.guidance_score = self._score_guidance(messages, ai_spec)
        score.knowledge_score = self._score_knowledge(messages, ai_spec)
        score.diagnosis_score = self._score_diagnosis(messages, ai_spec)
        score.teaching_score = self._score_teaching(messages, ai_spec)
        score.calculate_total()
        return score

    def _score_coherence(self, messages: list, ai_spec: dict) -> float:
        pts = 0.0
        # 对话轮次
        turn_count = len(messages)
        if turn_count >= 6:
            pts += 8.0
        elif turn_count >= 4:
            pts += 6.0
        elif turn_count >= 2:
            pts += 4.0
        elif turn_count >= 1:
            pts += 2.0

        # 开场白质量
        opening = ai_spec.get("opening_message", "")
        if opening and len(opening) >= 30:
            pts += 5.0
        elif opening:
            pts += 2.0

        # 探究性问题（上下文引导）
        probing = ai_spec.get("probing_questions", [])
        if isinstance(probing, list) and len(probing) >= 3:
            pts += 7.0
        elif isinstance(probing, list) and len(probing) >= 2:
            pts += 5.0
        elif isinstance(probing, list) and len(probing) >= 1:
            pts += 3.0

        return min(pts, self.MAX_COHERENCE)

    def _score_guidance(self, messages: list, ai_spec: dict) -> float:
        pts = 0.0
        # 引导性提问（非直接给答案）
        guidance_patterns = ["你觉得", "为什么", "如何", "试试", "想一想",
                            "what do you think", "why", "how", "try", "consider"]
        probing = ai_spec.get("probing_questions", [])
        if isinstance(probing, list):
            guidance_count = 0
            for q in probing:
                q_lower = (q if isinstance(q, str) else str(q)).lower()
                if any(p in q_lower for p in guidance_patterns):
                    guidance_count += 1
            pts += min(guidance_count * 4.0, 10.0)

        # 提示策略（hints）
        hints = ai_spec.get("hints", ai_spec.get("scaffolding", []))
        if isinstance(hints, list) and len(hints) >= 2:
            pts += 5.0
        elif isinstance(hints, list) and len(hints) >= 1:
            pts += 3.0

        # 开场白是否有引导性
        opening = ai_spec.get("opening_message", "")
        if opening:
            opening_lower = opening.lower()
            if any(p in opening_lower for p in guidance_patterns):
                pts += 5.0
            elif len(opening) >= 20:
                pts += 2.0

        return min(pts, self.MAX_GUIDANCE)

    def _score_knowledge(self, messages: list, ai_spec: dict) -> float:
        pts = 0.0
        # 诊断焦点中的关键概念
        diag = ai_spec.get("diagnostic_focus", {})
        key_concepts = diag.get("key_concepts", [])
        if isinstance(key_concepts, list):
            if len(key_concepts) >= 4:
                pts += 10.0
            elif len(key_concepts) >= 2:
                pts += 7.0
            elif len(key_concepts) >= 1:
                pts += 4.0

        # 常见误解覆盖
        misconceptions = diag.get("common_misconceptions", [])
        if isinstance(misconceptions, list):
            if len(misconceptions) >= 3:
                pts += 6.0
            elif len(misconceptions) >= 1:
                pts += 3.0

        # 消息中的知识密度（术语/概念出现频率）
        all_text = ""
        for m in messages:
            content = m.get("content", "") if isinstance(m, dict) else str(m)
            all_text += content + " "
        if len(all_text) >= 500:
            pts += 4.0
        elif len(all_text) >= 200:
            pts += 2.0

        return min(pts, self.MAX_KNOWLEDGE)

    def _score_diagnosis(self, messages: list, ai_spec: dict) -> float:
        pts = 0.0
        diag = ai_spec.get("diagnostic_focus", {})

        # 诊断焦点完整性
        if diag.get("key_concepts"):
            pts += 5.0
        if diag.get("common_misconceptions"):
            pts += 5.0
        if diag.get("difficulty_areas") or diag.get("prerequisites"):
            pts += 4.0

        # 反馈模板/纠正策略
        feedback = ai_spec.get("feedback_templates", ai_spec.get("correction_strategies", []))
        if isinstance(feedback, list) and len(feedback) >= 2:
            pts += 6.0
        elif isinstance(feedback, list) and len(feedback) >= 1:
            pts += 3.0

        return min(pts, self.MAX_DIAGNOSIS)

    def _score_teaching(self, messages: list, ai_spec: dict) -> float:
        pts = 0.0
        # 总结/回顾
        summary = ai_spec.get("summary", ai_spec.get("wrap_up", ""))
        if summary and len(str(summary)) >= 30:
            pts += 6.0
        elif summary:
            pts += 3.0

        # 鼓励性语言
        encourage_patterns = ["很好", "不错", "正确", "good", "great", "well done",
                             "excellent", "加油", "继续"]
        opening = ai_spec.get("opening_message", "")
        all_text = opening
        for m in messages:
            content = m.get("content", "") if isinstance(m, dict) else str(m)
            all_text += " " + content
        all_lower = all_text.lower()
        encourage_count = sum(1 for p in encourage_patterns if p in all_lower)
        pts += min(encourage_count * 2.0, 6.0)

        # 学习目标对齐
        objectives = ai_spec.get("learning_objectives", [])
        if isinstance(objectives, list) and len(objectives) >= 2:
            pts += 5.0
        elif isinstance(objectives, list) and len(objectives) >= 1:
            pts += 3.0

        # 下一步建议
        next_steps = ai_spec.get("next_steps", ai_spec.get("follow_up", ""))
        if next_steps:
            pts += 3.0

        return min(pts, self.MAX_TEACHING)

    def extract_metadata(self, dialogue: Dict[str, Any]) -> dict:
        ai_spec = dialogue.get("ai_spec", {})
        messages = dialogue.get("messages", dialogue.get("turns", []))
        diag = ai_spec.get("diagnostic_focus", {})
        return {
            "turn_count": len(messages),
            "has_opening": bool(ai_spec.get("opening_message")),
            "probing_question_count": len(ai_spec.get("probing_questions", [])),
            "has_diagnostic_focus": bool(diag),
            "key_concept_count": len(diag.get("key_concepts", [])),
        }


class ChapterScorer(BaseQualityScorer):
    """章节质量评分器 - 基于规则的内容质量评估

    评分维度 (满分100):
    - depth_score (0-25): 内容深度 — 学习目标、文本长度、要点覆盖、设计理念
    - structure_score (0-25): 结构质量 — 步骤数量、类型多样性、必要类型覆盖
    - visual_score (0-20): 可视化质量 — 图文内容、模拟器描述
    - teaching_score (0-20): 教学设计 — AI导师、评估题目、解释质量
    - simulator_score (0-10): 模拟器质量 — HTML代码、Canvas API、动画
    """

    MAX_DEPTH = 25.0
    MAX_STRUCTURE = 25.0
    MAX_VISUAL = 20.0
    MAX_TEACHING = 20.0
    MAX_SIMULATOR = 10.0

    def evaluate(self, chapter: Dict[str, Any]) -> ChapterQualityScore:
        score = ChapterQualityScore()
        steps = chapter.get("steps", chapter.get("script", []))
        if not steps:
            score.issues.append("No steps found")
            score.calculate_total()
            return score

        score.depth_score = self._score_depth(chapter, steps)
        score.structure_score = self._score_structure(chapter, steps)
        score.visual_score = self._score_visual(steps)
        score.teaching_score = self._score_teaching(steps)
        score.simulator_score = self._score_simulator(steps)
        score.calculate_total()
        return score

    def _score_depth(self, chapter: dict, steps: list) -> float:
        pts = 0.0
        objectives = chapter.get("learning_objectives", [])
        pts += min(len(objectives) * 1.5, 5.0)

        total_text = 0
        for s in steps:
            if s.get("type") in ("text_content", "illustrated_content"):
                body = (s.get("content") or {}).get("body", "") or ""
                total_text += len(body)
        if total_text >= 2000:
            pts += 10.0
        elif total_text >= 1000:
            pts += 7.0
        elif total_text >= 500:
            pts += 4.0
        elif total_text > 0:
            pts += 2.0

        kp_count = 0
        for s in steps:
            kps = (s.get("content") or {}).get("key_points", [])
            kp_count += len(kps) if isinstance(kps, list) else 0
        pts += min(kp_count * 1.0, 5.0)

        rationale = chapter.get("rationale", "") or ""
        if len(rationale) >= 30:
            pts += 5.0
        elif rationale:
            pts += 2.0

        return min(pts, self.MAX_DEPTH)

    def _score_structure(self, chapter: dict, steps: list) -> float:
        pts = 0.0
        n = len(steps)
        if 7 <= n <= 12:
            pts += 8.0
        elif 5 <= n <= 14:
            pts += 5.0
        elif n >= 3:
            pts += 3.0

        types = set(s.get("type", "") for s in steps)
        if len(types) >= 4:
            pts += 8.0
        elif len(types) >= 3:
            pts += 6.0
        elif len(types) >= 2:
            pts += 3.0

        if "text_content" in types or "illustrated_content" in types:
            pts += 3.0
        if "ai_tutor" in types:
            pts += 3.0
        if "assessment" in types:
            pts += 3.0

        return min(pts, self.MAX_STRUCTURE)

    def _score_visual(self, steps: list) -> float:
        pts = 0.0
        for s in steps:
            t = s.get("type", "")
            if t == "illustrated_content":
                pts += 5.0
                ds = s.get("diagram_spec") or (s.get("content") or {}).get("diagram_spec")
                if ds and (ds.get("description") or ds.get("image_url")):
                    pts += 3.0
            elif t == "simulator":
                spec = s.get("simulator_spec") or {}
                html = spec.get("html_content", "") or ""
                if html and len(html) > 100:
                    pts += 8.0
                elif spec.get("description"):
                    pts += 3.0
        return min(pts, self.MAX_VISUAL)

    def _score_teaching(self, steps: list) -> float:
        pts = 0.0
        for s in steps:
            t = s.get("type", "")
            if t == "ai_tutor":
                ai = s.get("ai_spec") or {}
                if ai.get("opening_message"):
                    pts += 3.0
                pqs = ai.get("probing_questions", [])
                if isinstance(pqs, list) and len(pqs) >= 2:
                    pts += 5.0
                elif isinstance(pqs, list) and len(pqs) >= 1:
                    pts += 2.0
                diag = ai.get("diagnostic_focus") or {}
                if diag.get("key_concepts") or diag.get("common_misconceptions"):
                    pts += 4.0
            elif t == "assessment":
                aspec = s.get("assessment_spec") or {}
                qs = aspec.get("questions", [])
                if isinstance(qs, list) and len(qs) >= 3:
                    pts += 5.0
                elif isinstance(qs, list) and len(qs) >= 1:
                    pts += 3.0
                has_expl = any(q.get("explanation") for q in qs if isinstance(q, dict))
                if has_expl:
                    pts += 3.0
        return min(pts, self.MAX_TEACHING)

    def _score_simulator(self, steps: list) -> float:
        pts = 0.0
        for s in steps:
            if s.get("type") != "simulator":
                continue
            spec = s.get("simulator_spec") or {}
            html = spec.get("html_content", "") or ""
            if html and len(html) >= 100:
                pts += 5.0
                canvas_calls = len(re.findall(r'ctx\.\w+', html))
                if canvas_calls >= 20:
                    pts += 3.0
                elif canvas_calls >= 10:
                    pts += 2.0
                if "requestAnimationFrame" in html:
                    pts += 2.0
        return min(pts, self.MAX_SIMULATOR)

    def extract_metadata(self, chapter):
        steps = chapter.get("steps", chapter.get("script", []))
        types = [s.get("type", "") for s in steps]
        return {
            "step_count": len(steps),
            "step_types": list(set(types)),
            "has_simulator": "simulator" in types,
            "has_ai_tutor": "ai_tutor" in types,
            "has_assessment": "assessment" in types,
        }


class QuizScorer(BaseQualityScorer):
    """测验质量评分器 - 基于规则的测验质量评估

    评分维度 (满分100):
    - difficulty_score (0-20): 难度设计 — 题目数量、难度梯度
    - option_score (0-25): 选项质量 — 选项数量、干扰项质量
    - explanation_score (0-20): 解析质量 — 解析覆盖率、解析长度
    - knowledge_score (0-20): 知识覆盖 — 学习目标覆盖、知识点标签
    - teaching_score (0-15): 教学价值 — 难度标注、题目排序
    """

    MAX_DIFFICULTY = 20.0
    MAX_OPTION = 25.0
    MAX_EXPLANATION = 20.0
    MAX_KNOWLEDGE = 20.0
    MAX_TEACHING = 15.0

    def evaluate(self, quiz: Dict[str, Any]) -> QuizQualityScore:
        score = QuizQualityScore()

        questions = quiz.get("questions", [])
        if isinstance(quiz, list):
            questions = quiz
        if not questions:
            score.issues.append("No questions found")
            score.calculate_total()
            return score

        score.difficulty_score = self._score_difficulty(questions)
        score.option_score = self._score_options(questions)
        score.explanation_score = self._score_explanations(questions)
        score.knowledge_score = self._score_knowledge(questions, quiz)
        score.teaching_score = self._score_teaching(questions)
        score.calculate_total()
        return score

    def _score_difficulty(self, questions: list) -> float:
        pts = 0.0
        n = len(questions)
        # 题目数量
        if n >= 5:
            pts += 8.0
        elif n >= 3:
            pts += 5.0
        elif n >= 1:
            pts += 2.0

        # 难度梯度（是否有不同难度级别）
        difficulties = set()
        for q in questions:
            if isinstance(q, dict):
                d = q.get("difficulty", q.get("level", ""))
                if d:
                    difficulties.add(str(d).lower())
        if len(difficulties) >= 3:
            pts += 8.0
        elif len(difficulties) >= 2:
            pts += 5.0
        elif len(difficulties) >= 1:
            pts += 3.0

        # 题目文本长度（非过于简短）
        avg_len = 0
        for q in questions:
            if isinstance(q, dict):
                avg_len += len(q.get("question", q.get("stem", "")))
        avg_len = avg_len / max(n, 1)
        if avg_len >= 30:
            pts += 4.0
        elif avg_len >= 15:
            pts += 2.0

        return min(pts, self.MAX_DIFFICULTY)

    def _score_options(self, questions: list) -> float:
        pts = 0.0
        valid_count = 0
        good_option_count = 0

        for q in questions:
            if not isinstance(q, dict):
                continue
            options = q.get("options", q.get("choices", []))
            if not isinstance(options, list):
                continue
            valid_count += 1

            # 选项数量 >= 4
            if len(options) >= 4:
                good_option_count += 1

            # 选项长度相近（干扰项质量）
            if len(options) >= 2:
                lengths = []
                for opt in options:
                    if isinstance(opt, dict):
                        lengths.append(len(opt.get("text", opt.get("label", str(opt)))))
                    else:
                        lengths.append(len(str(opt)))
                if lengths:
                    avg = sum(lengths) / len(lengths)
                    # 长度标准差小说明选项质量好
                    variance = sum((l - avg) ** 2 for l in lengths) / len(lengths)
                    if variance < avg * avg * 0.5:  # 变异系数较小
                        pts += 2.0

        # 每题4选项的比例
        if valid_count > 0:
            ratio = good_option_count / valid_count
            if ratio >= 0.8:
                pts += 10.0
            elif ratio >= 0.5:
                pts += 6.0
            elif ratio > 0:
                pts += 3.0

        # 有正确答案标注
        has_answer = sum(1 for q in questions if isinstance(q, dict) and
                        (q.get("correct_option") or q.get("answer") or q.get("correct_answer")))
        if has_answer == len(questions):
            pts += 8.0
        elif has_answer > 0:
            pts += 4.0

        return min(pts, self.MAX_OPTION)

    def _score_explanations(self, questions: list) -> float:
        pts = 0.0
        n = len(questions)
        if n == 0:
            return 0.0

        has_explanation = 0
        good_explanation = 0
        for q in questions:
            if not isinstance(q, dict):
                continue
            expl = q.get("explanation", q.get("解析", q.get("analysis", "")))
            if expl and len(str(expl)) > 0:
                has_explanation += 1
                if len(str(expl)) >= 50:
                    good_explanation += 1

        # 解析覆盖率
        coverage = has_explanation / n
        if coverage >= 0.9:
            pts += 10.0
        elif coverage >= 0.6:
            pts += 7.0
        elif coverage > 0:
            pts += 3.0

        # 解析质量（长度充分）
        if good_explanation > 0:
            quality_ratio = good_explanation / n
            if quality_ratio >= 0.8:
                pts += 10.0
            elif quality_ratio >= 0.5:
                pts += 6.0
            else:
                pts += 3.0

        return min(pts, self.MAX_EXPLANATION)

    def _score_knowledge(self, questions: list, quiz: dict) -> float:
        pts = 0.0
        # 知识点标签
        tagged_count = 0
        for q in questions:
            if not isinstance(q, dict):
                continue
            if q.get("knowledge_point") or q.get("tag") or q.get("topic"):
                tagged_count += 1

        n = len(questions)
        if n > 0 and tagged_count / n >= 0.8:
            pts += 8.0
        elif tagged_count > 0:
            pts += 4.0

        # 学习目标覆盖
        objectives = quiz.get("learning_objectives", []) if isinstance(quiz, dict) else []
        if isinstance(objectives, list) and len(objectives) >= 2:
            pts += 6.0
        elif isinstance(objectives, list) and len(objectives) >= 1:
            pts += 3.0

        # 题目内容多样性（不重复）
        stems = set()
        for q in questions:
            if isinstance(q, dict):
                stem = q.get("question", q.get("stem", ""))
                if stem:
                    stems.add(stem[:30])  # 前30字去重
        if n > 0:
            uniqueness = len(stems) / n
            if uniqueness >= 0.9:
                pts += 6.0
            elif uniqueness >= 0.7:
                pts += 4.0
            elif uniqueness > 0.5:
                pts += 2.0

        return min(pts, self.MAX_KNOWLEDGE)

    def _score_teaching(self, questions: list) -> float:
        pts = 0.0
        # 难度标注
        has_difficulty = sum(1 for q in questions if isinstance(q, dict) and
                           q.get("difficulty", q.get("level")))
        n = len(questions)
        if n > 0 and has_difficulty / n >= 0.8:
            pts += 5.0
        elif has_difficulty > 0:
            pts += 2.0

        # 题型多样性
        types = set()
        for q in questions:
            if isinstance(q, dict):
                t = q.get("type", q.get("question_type", ""))
                if t:
                    types.add(str(t))
        if len(types) >= 3:
            pts += 5.0
        elif len(types) >= 2:
            pts += 3.0

        # 题目有序号/编号
        has_id = sum(1 for q in questions if isinstance(q, dict) and
                    (q.get("id") or q.get("number") or q.get("order")))
        if n > 0 and has_id / n >= 0.8:
            pts += 3.0

        # 有知识点关联
        has_link = sum(1 for q in questions if isinstance(q, dict) and
                      (q.get("knowledge_point") or q.get("related_concept")))
        if has_link > 0:
            pts += 2.0

        return min(pts, self.MAX_TEACHING)

    def extract_metadata(self, quiz: Dict[str, Any]) -> dict:
        questions = quiz.get("questions", [])
        if isinstance(quiz, list):
            questions = quiz
        difficulties = set()
        types = set()
        for q in questions:
            if isinstance(q, dict):
                d = q.get("difficulty", q.get("level", ""))
                if d:
                    difficulties.add(str(d))
                t = q.get("type", q.get("question_type", ""))
                if t:
                    types.add(str(t))
        return {
            "question_count": len(questions),
            "difficulty_levels": list(difficulties),
            "question_types": list(types),
            "has_explanations": any(
                isinstance(q, dict) and q.get("explanation")
                for q in questions
            ),
        }
