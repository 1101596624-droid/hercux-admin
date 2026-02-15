"""
Enhanced Quiz Generator with Learning Integration

Generates quiz questions by learning from high-quality examples.
Integrates with the unified learning framework to continuously
improve question quality over time.

Quality Scoring:
- 75: Baseline acceptable question
- 85+: High-quality template-worthy question

Learning Process:
1. Retrieve similar high-quality questions (85+ score) for the same difficulty
2. Analyze patterns in question structure, distractor design, explanation style
3. Inject learning context into generation prompt
4. Generate new question
5. Evaluate quality using QuizScorer
6. Save 85+ score questions as templates for future learning
"""

import json
import re
import logging
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session

from app.services.llm_factory import get_llm_service
from app.services.learning.template_service import UnifiedTemplateService
from app.services.learning.quality_scorers import QuizScorer, QuizQualityScore

logger = logging.getLogger(__name__)


class EnhancedQuizGenerator:
    """Quiz generator with learning capabilities"""

    def __init__(self, db: Session):
        """
        Initialize generator with database session

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.claude = get_llm_service()
        self.template_service = UnifiedTemplateService(db)
        self.scorer = QuizScorer()

        # Quality thresholds
        self.BASELINE_QUALITY = 75.0
        self.TEMPLATE_QUALITY = 85.0

    async def generate_quiz_with_learning(
        self,
        node_title: str,
        learning_objectives: List[str],
        content: str,
        difficulty: str,
        subject: str = "general",
        topic: str = None,
        num_questions: int = 13
    ) -> List[Dict[str, Any]]:
        """
        Generate quiz questions with learning from high-quality examples

        Args:
            node_title: Node title
            learning_objectives: Learning objectives
            content: Course content
            difficulty: Difficulty level (easy/medium/hard)
            subject: Subject area (e.g., 'physics', 'mathematics')
            topic: Specific topic for more targeted learning
            num_questions: Number of questions to generate

        Returns:
            List of quiz questions with quality scores
        """
        logger.info(f"Generating {num_questions} {difficulty} questions for '{node_title}' with learning")

        # Step 1: Retrieve similar high-quality templates
        templates = await self.template_service.get_similar_templates(
            template_type="quiz_question",
            subject=subject,
            topic=topic or node_title,
            min_quality=self.TEMPLATE_QUALITY,
            limit=3,
            difficulty_level=difficulty
        )

        # Step 2: Analyze patterns if templates exist
        learning_context = ""
        if templates:
            patterns = self.template_service.analyze_patterns(templates)
            learning_context = self.template_service.format_learning_context(
                patterns, templates, "quiz_question"
            )
            logger.info(f"Learning from {len(templates)} high-quality templates (avg: {patterns['avg_quality_score']:.1f})")
        else:
            logger.info("No templates found, generating without learning context")

        # Step 3: Generate questions in batches
        batch_size = 5
        all_questions = []
        batches_needed = (num_questions + batch_size - 1) // batch_size

        for batch_idx in range(batches_needed):
            remaining = num_questions - len(all_questions)
            current_batch_size = min(batch_size, remaining)

            if current_batch_size <= 0:
                break

            logger.info(f"Generating batch {batch_idx + 1}/{batches_needed} ({current_batch_size} questions)")

            batch_questions = await self._generate_batch_with_learning(
                node_title=node_title,
                learning_objectives=learning_objectives,
                content=content,
                difficulty=difficulty,
                subject=subject,
                topic=topic,
                batch_size=current_batch_size,
                learning_context=learning_context
            )

            all_questions.extend(batch_questions)

        # Re-number questions
        for i, q in enumerate(all_questions):
            q["id"] = i + 1

        logger.info(f"Generated {len(all_questions)} questions for '{node_title}'")
        return all_questions[:num_questions]

    async def _generate_batch_with_learning(
        self,
        node_title: str,
        learning_objectives: List[str],
        content: str,
        difficulty: str,
        subject: str,
        topic: Optional[str],
        batch_size: int,
        learning_context: str
    ) -> List[Dict[str, Any]]:
        """Generate a batch of questions with learning context"""

        content_summary = content[:1200] if content else ""

        difficulty_cn = {"easy": "简单", "medium": "中等", "hard": "困难"}.get(difficulty, "简单")

        difficulty_hints = {
            "easy": "基础概念题，答案明显，考查定义和基本理解",
            "medium": "理解应用题，需要思考，考查概念联系和应用能力",
            "hard": "综合分析题，有迷惑选项，考查深度理解和知识迁移"
        }

        # Build enhanced prompt with learning context
        prompt = self._build_generation_prompt(
            node_title=node_title,
            content_summary=content_summary,
            difficulty=difficulty,
            difficulty_cn=difficulty_cn,
            difficulty_hint=difficulty_hints.get(difficulty, ""),
            batch_size=batch_size,
            learning_context=learning_context
        )

        try:
            response = await self.claude.generate_raw_response(
                prompt,
                temperature=0.7,
                max_tokens=3000
            )

            # Parse response
            questions = self._parse_quiz_response(response)

            if not questions:
                logger.warning(f"Failed to parse questions, using fallback")
                return self._generate_fallback_questions(node_title, batch_size, difficulty)

            # Step 4: Evaluate and save high-quality questions
            evaluated_questions = []
            for question_data in questions:
                # Add difficulty field
                question_data["difficulty"] = difficulty

                # Evaluate quality
                quality_score = self.scorer.evaluate(question_data)

                # Add quality info to question
                question_data["quality_score"] = quality_score.total_score
                question_data["quality_passed"] = quality_score.passed

                # Record evaluation
                await self.template_service.record_quality_evaluation(
                    content_type="quiz_question",
                    content_id=f"{node_title}_{difficulty}_{question_data.get('question', '')[:50]}",
                    quality_score=quality_score.total_score,
                    score_breakdown={
                        "difficulty_score": quality_score.difficulty_score,
                        "option_score": quality_score.option_score,
                        "explanation_score": quality_score.explanation_score,
                        "knowledge_score": quality_score.knowledge_score,
                        "teaching_score": quality_score.teaching_score,
                    },
                    saved_as_template=False
                )

                # Save as template if high quality (85+)
                if quality_score.total_score >= self.TEMPLATE_QUALITY:
                    metadata = self.scorer.extract_metadata(question_data)

                    await self.template_service.save_as_template(
                        template_type="quiz_question",
                        subject=subject,
                        topic=topic or node_title,
                        content=question_data,
                        quality_score=quality_score.total_score,
                        score_breakdown={
                            "difficulty_score": quality_score.difficulty_score,
                            "option_score": quality_score.option_score,
                            "explanation_score": quality_score.explanation_score,
                            "knowledge_score": quality_score.knowledge_score,
                            "teaching_score": quality_score.teaching_score,
                        },
                        metadata=metadata,
                        difficulty_level=difficulty
                    )

                    logger.info(f"Saved high-quality question as template (score: {quality_score.total_score:.1f})")

                evaluated_questions.append(question_data)

            return evaluated_questions

        except Exception as e:
            logger.error(f"Failed to generate batch: {e}", exc_info=True)
            return self._generate_fallback_questions(node_title, batch_size, difficulty)

    def _build_generation_prompt(
        self,
        node_title: str,
        content_summary: str,
        difficulty: str,
        difficulty_cn: str,
        difficulty_hint: str,
        batch_size: int,
        learning_context: str
    ) -> str:
        """Build generation prompt with optional learning context"""

        # Base prompt
        prompt_parts = []

        # Add learning context if available
        if learning_context:
            prompt_parts.append(learning_context)
            prompt_parts.append("\n" + "="*60 + "\n")

        # Main generation instructions
        prompt_parts.append(f"""请为课程"{node_title}"生成{batch_size}道{difficulty_cn}难度的选择题。

课程内容：{content_summary}

难度要求：{difficulty_hint}

请严格按以下JSON格式返回，不要有任何其他文字：
{{"questions":[
{{"id":1,"question":"题目内容","options":["A选项","B选项","C选项","D选项"],"correct_option":"A","explanation":"解析内容"}},
{{"id":2,"question":"题目内容","options":["A选项","B选项","C选项","D选项"],"correct_option":"B","explanation":"解析内容"}}
]}}

质量要求：
1. 生成{batch_size}道题
2. 每题4个选项，选项长度相近
3. correct_option只能是A/B/C/D
4. 必须包含详细的explanation解析（至少50字）
5. 题目要与课程内容紧密相关
6. 干扰项要有迷惑性，避免明显错误
7. 解析要说明正确答案的原因
8. 题目长度至少30字，体现{difficulty_cn}难度特点""")

        if learning_context:
            prompt_parts.append("\n\n请参考上述学习上下文中的高质量模式，生成达到相同质量标准的题目。")

        return "\n".join(prompt_parts)

    def _parse_quiz_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse quiz questions from AI response"""
        if not response:
            return []

        response = response.strip()

        # Method 1: Direct JSON parsing
        try:
            start = response.find('{')
            end = response.rfind('}')
            if start != -1 and end != -1 and end > start:
                json_str = response[start:end+1]
                data = json.loads(json_str)
                if "questions" in data:
                    return data["questions"]
        except json.JSONDecodeError:
            pass

        # Method 2: Regex match questions array
        try:
            match = re.search(r'"questions"\s*:\s*(\[[\s\S]*?\])\s*\}', response)
            if match:
                array_str = match.group(1)
                return json.loads(array_str)
        except:
            pass

        # Method 3: Direct array match
        try:
            match = re.search(r'\[[\s\S]*\]', response)
            if match:
                return json.loads(match.group())
        except:
            pass

        return []

    def _generate_fallback_questions(
        self,
        title: str,
        count: int,
        difficulty: str
    ) -> List[Dict[str, Any]]:
        """Generate fallback questions when AI generation fails"""

        templates = {
            "easy": [
                {
                    "question": f"关于「{title}」，以下哪项是核心概念？",
                    "options": ["基础理论", "应用实践", "案例分析", "总结归纳"],
                    "correct_option": "A",
                    "explanation": "基础理论是学习的核心概念，掌握理论基础是后续学习的关键。",
                    "difficulty": difficulty
                },
                {
                    "question": f"学习「{title}」的主要目的是什么？",
                    "options": ["理解原理", "记忆公式", "完成作业", "应付考试"],
                    "correct_option": "A",
                    "explanation": "学习的主要目的是理解原理，只有真正理解才能灵活应用。",
                    "difficulty": difficulty
                },
            ],
            "medium": [
                {
                    "question": f"如何更好地掌握「{title}」？",
                    "options": ["理解+实践", "死记硬背", "只看不练", "临时抱佛脚"],
                    "correct_option": "A",
                    "explanation": "理解与实践相结合是最有效的学习方式，理论需要通过实践来巩固。",
                    "difficulty": difficulty
                },
            ],
            "hard": [
                {
                    "question": f"深入理解「{title}」需要具备哪些前置知识？",
                    "options": ["相关基础概念", "无需任何基础", "只需记忆", "随意学习"],
                    "correct_option": "A",
                    "explanation": "深入理解需要扎实的基础概念作为支撑，前置知识是深度学习的必要条件。",
                    "difficulty": difficulty
                },
            ]
        }

        question_templates = templates.get(difficulty, templates["easy"])
        result = []

        for i in range(count):
            template = question_templates[i % len(question_templates)].copy()
            template["id"] = i + 1
            result.append(template)

        return result

    async def generate_full_quiz_bank(
        self,
        node_title: str,
        learning_objectives: List[str],
        content: str,
        subject: str = "general",
        topic: str = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate complete quiz bank for all three difficulty levels

        Args:
            node_title: Node title
            learning_objectives: Learning objectives
            content: Course content
            subject: Subject area
            topic: Specific topic

        Returns:
            Quiz bank with easy, medium, hard questions
        """
        quiz_bank = {
            "easy": [],
            "medium": [],
            "hard": []
        }

        for difficulty in ["easy", "medium", "hard"]:
            difficulty_cn = {"easy": "简单", "medium": "中等", "hard": "困难"}.get(difficulty)
            logger.info(f"Generating {difficulty_cn} questions...")

            questions = await self.generate_quiz_with_learning(
                node_title=node_title,
                learning_objectives=learning_objectives,
                content=content,
                difficulty=difficulty,
                subject=subject,
                topic=topic,
                num_questions=13
            )

            quiz_bank[difficulty] = questions
            logger.info(f"{difficulty_cn} completed: {len(questions)} questions")

        return quiz_bank
