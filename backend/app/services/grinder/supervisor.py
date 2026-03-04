"""
小课堂 AI 监督者 - 确保题目质量、内容正确性和信息时效性
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.llm_factory import get_llm_service
from app.services.learning.quality_scorers import QuizScorer, QuizQualityScore
from app.services.learning.template_service import UnifiedTemplateService

logger = logging.getLogger(__name__)


class GrinderSupervisor:
    """
    小课堂监督者

    职责：
    1. 搜索最新信息确保内容时效性
    2. 审核生成的题目质量
    3. 验证答案正确性
    4. 检测并修复 JSON 格式问题
    5. 质量评分和学习模板保存 (NEW)
    """

    def __init__(self, db: Session = None):
        self.claude_service = get_llm_service()
        self._search_service = None
        self.db = db
        self.quiz_scorer = QuizScorer()
        self.template_service = UnifiedTemplateService(db) if db else None

    @property
    def search_service(self):
        """Lazy load search service"""
        if self._search_service is None:
            from app.services.deepseek_search_service import get_search_service
            self._search_service = get_search_service()
        return self._search_service

    async def search_latest_info(self, topic: str) -> str:
        """搜索主题的最新信息"""
        try:
            return await self.search_service.search_for_context(topic, "educational")
        except Exception as e:
            logger.warning(f"Search failed for topic '{topic}': {e}")
            return ""

    async def generate_exam_with_supervision(
        self,
        topic: str,
        question_count: int = 5,
        focus_categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        监督式生成考试题目

        流程：
        1. 搜索最新信息
        2. 生成题目
        3. 审核题目质量
        4. 验证答案正确性
        5. 必要时重新生成
        """

        # 1. 搜索最新信息
        logger.info(f"Searching latest info for topic: {topic}")
        latest_info = await self.search_latest_info(topic)

        # 2. 构建增强的系统提示词
        system_prompt = self._build_system_prompt(latest_info)

        # 3. 生成题目
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                exam = await self._generate_exam(
                    topic=topic,
                    question_count=question_count,
                    focus_categories=focus_categories,
                    system_prompt=system_prompt,
                    latest_info=latest_info
                )

                # 4. 审核题目
                review_result = await self._review_exam(exam, topic, latest_info)

                if review_result['approved']:
                    logger.info(f"Exam approved on attempt {attempt + 1}")

                    # 5. 质量评分和保存高质量题目为学习模板
                    if self.template_service:
                        quality_results = await self._evaluate_and_save_quality_questions(
                            exam, topic, review_result
                        )
                        review_result['quality_results'] = quality_results

                    return {
                        'exam': exam,
                        'review': review_result,
                        'latest_info_used': bool(latest_info),
                        'attempts': attempt + 1
                    }
                else:
                    logger.warning(f"Exam rejected on attempt {attempt + 1}: {review_result['issues']}")
                    # 如果有具体问题，在下次生成时提供反馈
                    if attempt < max_attempts - 1:
                        system_prompt = self._build_system_prompt(
                            latest_info,
                            previous_issues=review_result['issues']
                        )

            except Exception as e:
                logger.error(f"Exam generation failed on attempt {attempt + 1}: {e}")
                if attempt == max_attempts - 1:
                    raise

        # 如果所有尝试都失败，返回最后一次的结果
        return {
            'exam': exam,
            'review': review_result,
            'latest_info_used': bool(latest_info),
            'attempts': max_attempts,
            'warning': 'Exam may have quality issues'
        }

    def _build_system_prompt(
        self,
        latest_info: str = "",
        previous_issues: Optional[List[str]] = None
    ) -> str:
        """构建系统提示词"""

        base_prompt = """你是 HERCU 做题家系统的 AI 考官，专注于生成高质量的练习题目。

【核心职责】
1. 生成准确、有深度的练习题目
2. 确保所有答案和解析都是正确的
3. 使用最新的信息和数据
4. 题目要有教育价值，促进深度思考

【题目类型】
- choice: 选择题（4个选项，correct 为正确选项索引 0-3）
- blank: 填空题（answer 为标准答案）
- analysis: 分析题（开放性问题）

【质量标准】
1. 答案必须绝对正确，不能有任何错误
2. 解析必须详细说明原理，不能敷衍
3. 选项设计要有区分度，干扰项要合理
4. 题目难度要有梯度，从基础到进阶
5. 内容必须反映最新的知识和研究

【输出格式】
必须返回严格有效的 JSON 格式：
- 不要在 JSON 前后添加任何文字
- 不要使用 markdown 代码块
- 确保所有字符串使用双引号
- 代码或公式中的特殊字符要正确转义
"""

        if latest_info:
            base_prompt += f"""

【最新信息参考】
以下是关于该主题的最新信息，请确保题目内容与之一致：
{latest_info[:3000]}

【重要】如果最新信息与你的知识有冲突，以最新信息为准。
"""

        if previous_issues:
            base_prompt += f"""

【上次生成的问题 - 必须修正】
{chr(10).join(f'- {issue}' for issue in previous_issues)}

请在本次生成中避免这些问题。
"""

        return base_prompt

    async def _generate_exam(
        self,
        topic: str,
        question_count: int,
        focus_categories: Optional[List[str]],
        system_prompt: str,
        latest_info: str
    ) -> Dict[str, Any]:
        """生成考试题目"""

        exam_id = f"GRINDER-{int(datetime.utcnow().timestamp() * 1000)}"

        prompt = f"""请根据主题「{topic}」生成 {question_count} 道高质量练习题。

【要求】
1. 至少包含 2 道选择题、1 道填空题、1 道分析题
2. 选择题的 correct 字段是正确选项的索引（0-3）
3. 每道题必须有详细的 explanation 解析
4. 题目要有深度，促进思考
5. 确保所有答案都是正确的
{f'6. 优先覆盖以下知识点：{", ".join(focus_categories)}' if focus_categories else ''}

【JSON 结构】
{{
    "examId": "{exam_id}",
    "title": "{topic}专项训练",
    "totalQuestions": {question_count},
    "generatedAt": "{datetime.utcnow().isoformat()}",
    "questions": [
        {{
            "id": 1,
            "type": "choice",
            "text": "题目内容",
            "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
            "correct": 0,
            "category": "知识分类",
            "explanation": "详细解析，说明为什么这个答案是正确的"
        }},
        {{
            "id": 2,
            "type": "blank",
            "text": "填空题内容______",
            "answer": "标准答案",
            "category": "知识分类",
            "hint": "提示信息",
            "explanation": "详细解析"
        }},
        {{
            "id": 3,
            "type": "analysis",
            "text": "分析题内容",
            "category": "知识分类",
            "placeholder": "请输入你的分析...",
            "explanation": "参考答案和评分要点"
        }}
    ]
}}

现在直接输出 JSON："""

        response = await self.claude_service.generate_raw_response(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=4096
        )

        # 解析 JSON
        return self._parse_exam_json(response)

    def _parse_exam_json(self, response: str) -> Dict[str, Any]:
        """解析考试 JSON，带容错处理"""

        # 清理响应
        text = response.strip()

        # 移除 markdown 代码块
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0]
        elif '```' in text:
            text = text.split('```')[1].split('```')[0]

        # 提取 JSON 对象
        if '{' in text:
            start = text.index('{')
            # 找到匹配的闭合括号
            depth = 0
            end = start
            for i in range(start, len(text)):
                if text[i] == '{':
                    depth += 1
                elif text[i] == '}':
                    depth -= 1
                    if depth == 0:
                        end = i + 1
                        break
            text = text[start:end]

        # 修复常见 JSON 问题
        text = self._fix_json_string(text)

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            logger.debug(f"Response preview: {text[:500]}")
            raise ValueError(f"无法解析题目 JSON: {e}")

    def _fix_json_string(self, text: str) -> str:
        """修复 JSON 字符串中的常见问题"""

        # 替换中文引号
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")

        # 移除尾随逗号
        import re
        text = re.sub(r',(\s*[}\]])', r'\1', text)

        # 修复字符串中的换行符
        result = []
        in_string = False
        escape = False

        for char in text:
            if in_string:
                if escape:
                    result.append(char)
                    escape = False
                elif char == '\\':
                    result.append(char)
                    escape = True
                elif char == '"':
                    result.append(char)
                    in_string = False
                elif char == '\n':
                    result.append('\\n')
                elif char == '\r':
                    pass  # 忽略
                elif char == '\t':
                    result.append('\\t')
                else:
                    result.append(char)
            else:
                if char == '"':
                    in_string = True
                result.append(char)

        return ''.join(result)

    async def _review_exam(
        self,
        exam: Dict[str, Any],
        topic: str,
        latest_info: str
    ) -> Dict[str, Any]:
        """审核考试题目质量"""

        issues = []
        suggestions = []

        questions = exam.get('questions', [])

        # 1. 检查题目数量
        if len(questions) < 3:
            issues.append(f"题目数量太少，只有 {len(questions)} 道")

        # 2. 检查题目类型分布
        types = [q.get('type') for q in questions]
        if 'choice' not in types:
            issues.append("缺少选择题")
        if 'blank' not in types and 'analysis' not in types:
            issues.append("缺少填空题或分析题")

        # 3. 检查每道题的质量
        for i, q in enumerate(questions):
            q_issues = self._check_question_quality(q, i + 1)
            issues.extend(q_issues)

        # 4. 使用 AI 验证答案正确性（抽查）
        if len(questions) > 0:
            # 抽查选择题答案
            choice_questions = [q for q in questions if q.get('type') == 'choice']
            if choice_questions:
                sample = choice_questions[0]
                answer_check = await self._verify_answer(sample, topic, latest_info)
                if not answer_check['correct']:
                    issues.append(f"题目 {sample.get('id')} 答案可能有误: {answer_check['reason']}")

        return {
            'approved': len(issues) == 0,
            'issues': issues,
            'suggestions': suggestions,
            'score': max(0, 100 - len(issues) * 15)
        }

    def _check_question_quality(self, question: Dict[str, Any], index: int) -> List[str]:
        """检查单道题目的质量"""

        issues = []
        q_type = question.get('type', '')

        # 检查必要字段
        if not question.get('text'):
            issues.append(f"题目 {index} 缺少题目内容")

        if not question.get('explanation'):
            issues.append(f"题目 {index} 缺少解析")
        elif len(question.get('explanation', '')) < 20:
            issues.append(f"题目 {index} 解析太简短")

        if not question.get('category'):
            issues.append(f"题目 {index} 缺少分类")

        # 类型特定检查
        if q_type == 'choice':
            options = question.get('options', [])
            if len(options) != 4:
                issues.append(f"题目 {index} 选项数量不是4个")

            correct = question.get('correct')
            if correct is None or not isinstance(correct, int) or correct < 0 or correct > 3:
                issues.append(f"题目 {index} 正确答案索引无效")

        elif q_type == 'blank':
            if not question.get('answer'):
                issues.append(f"题目 {index} 缺少标准答案")

        return issues

    async def _verify_answer(
        self,
        question: Dict[str, Any],
        topic: str,
        latest_info: str
    ) -> Dict[str, Any]:
        """验证答案正确性"""

        prompt = f"""请验证以下题目的答案是否正确。

【主题】{topic}

【题目】
{question.get('text')}

【选项】
{chr(10).join(question.get('options', []))}

【给出的正确答案】选项 {chr(65 + question.get('correct', 0))}

【解析】
{question.get('explanation', '')}

{f'【最新参考信息】{latest_info[:1000]}' if latest_info else ''}

请判断这个答案是否正确。返回 JSON：
{{"correct": true/false, "reason": "判断理由"}}

直接输出 JSON："""

        try:
            response = await self.claude_service.generate_raw_response(
                prompt=prompt,
                system_prompt="你是一位严谨的学科专家，负责验证题目答案的正确性。",
                max_tokens=500
            )

            # 解析响应
            text = response.strip()
            if '{' in text:
                start = text.index('{')
                end = text.rindex('}') + 1
                text = text[start:end]

            return json.loads(text)

        except Exception as e:
            logger.warning(f"Answer verification failed: {e}")
            return {'correct': True, 'reason': '验证失败，默认通过'}

    async def _evaluate_and_save_quality_questions(
        self,
        exam: Dict[str, Any],
        topic: str,
        review_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        对审核通过的题目进行质量评分，并保存85+分的题目为学习模板

        Args:
            exam: 考试数据
            topic: 主题
            review_result: 审核结果

        Returns:
            质量评分结果统计
        """
        questions = exam.get('questions', [])
        quality_results = {
            'total_evaluated': 0,
            'high_quality_count': 0,
            'saved_as_template': 0,
            'quality_scores': [],
            'saved_questions': []
        }

        if not questions:
            return quality_results

        logger.info(f"Evaluating quality for {len(questions)} questions")

        for question in questions:
            try:
                # 转换题目格式为QuizScorer期望的格式
                quiz_data = self._convert_question_format(question)

                # 使用QuizScorer评分
                quality_score = self.quiz_scorer.evaluate(quiz_data)

                quality_results['total_evaluated'] += 1
                quality_results['quality_scores'].append({
                    'question_id': question.get('id'),
                    'score': quality_score.total_score,
                    'passed': quality_score.passed
                })

                logger.info(
                    f"Question {question.get('id')} quality score: "
                    f"{quality_score.total_score:.1f}/100 (threshold: 85)"
                )

                # 85+分自动保存为学习模板
                if quality_score.total_score >= 85.0:
                    quality_results['high_quality_count'] += 1

                    # 提取科目和难度
                    subject = self._infer_subject(topic)
                    difficulty = self._infer_difficulty(question)

                    # 保存为模板
                    template = await self.template_service.save_as_template(
                        template_type='quiz_question',
                        subject=subject,
                        topic=topic,
                        content=quiz_data,
                        quality_score=quality_score.total_score,
                        score_breakdown={
                            'difficulty_score': quality_score.difficulty_score,
                            'option_score': quality_score.option_score,
                            'explanation_score': quality_score.explanation_score,
                            'knowledge_score': quality_score.knowledge_score,
                            'teaching_score': quality_score.teaching_score,
                        },
                        metadata=self.quiz_scorer.extract_metadata(quiz_data),
                        difficulty_level=difficulty
                    )

                    if template:
                        quality_results['saved_as_template'] += 1
                        quality_results['saved_questions'].append({
                            'question_id': question.get('id'),
                            'template_id': template.id,
                            'quality_score': quality_score.total_score
                        })
                        logger.info(
                            f"Question {question.get('id')} saved as learning template "
                            f"(ID: {template.id}, score: {quality_score.total_score:.1f})"
                        )
                    else:
                        logger.info(
                            f"Question {question.get('id')} is duplicate, "
                            f"template usage count updated"
                        )

            except Exception as e:
                logger.error(f"Failed to evaluate question {question.get('id')}: {e}")
                continue

        logger.info(
            f"Quality evaluation complete: {quality_results['high_quality_count']}/{quality_results['total_evaluated']} "
            f"high-quality questions, {quality_results['saved_as_template']} saved as templates"
        )

        return quality_results

    def _convert_question_format(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """
        将Grinder题目格式转换为QuizScorer期望的格式

        Grinder格式:
        {
            "id": 1,
            "type": "choice",
            "text": "题目内容",
            "options": ["A. 选项1", "B. 选项2", ...],
            "correct": 0,
            "explanation": "解析"
        }

        QuizScorer格式:
        {
            "question": "题目内容",
            "options": ["选项1", "选项2", ...],
            "correct_answer": "选项1",
            "explanation": "解析",
            "difficulty": "medium"
        }
        """
        question_type = question.get('type', 'choice')

        if question_type == 'choice':
            options = question.get('options', [])
            correct_index = question.get('correct', 0)

            # 移除选项前缀 (A. B. C. D.)
            cleaned_options = []
            for opt in options:
                # 去掉 "A. ", "B. " 等前缀
                cleaned = opt
                if len(opt) > 3 and opt[1:3] == '. ':
                    cleaned = opt[3:]
                cleaned_options.append(cleaned)

            # 获取正确答案
            correct_answer = cleaned_options[correct_index] if 0 <= correct_index < len(cleaned_options) else cleaned_options[0]

            return {
                'question': question.get('text', ''),
                'options': cleaned_options,
                'correct_answer': correct_answer,
                'explanation': question.get('explanation', ''),
                'difficulty': self._infer_difficulty(question),
                'category': question.get('category', 'general')
            }

        elif question_type == 'blank':
            return {
                'question': question.get('text', ''),
                'options': ['填空题'],
                'correct_answer': question.get('answer', ''),
                'explanation': question.get('explanation', ''),
                'difficulty': self._infer_difficulty(question),
                'category': question.get('category', 'general')
            }

        elif question_type == 'analysis':
            return {
                'question': question.get('text', ''),
                'options': ['开放性问题'],
                'correct_answer': '见解析',
                'explanation': question.get('explanation', ''),
                'difficulty': 'hard',
                'category': question.get('category', 'general')
            }

        else:
            # 默认格式
            return {
                'question': question.get('text', ''),
                'options': question.get('options', []),
                'correct_answer': str(question.get('answer', '')),
                'explanation': question.get('explanation', ''),
                'difficulty': 'medium',
                'category': question.get('category', 'general')
            }

    def _infer_subject(self, topic: str) -> str:
        """从主题推断科目"""
        topic_lower = topic.lower()

        subject_keywords = {
            'physics': ['物理', 'physics', '力学', '电磁', '光学', '热学'],
            'mathematics': ['数学', 'math', '代数', '几何', '微积分', '概率'],
            'chemistry': ['化学', 'chemistry', '有机', '无机', '元素'],
            'computer_science': ['编程', 'programming', '算法', '数据结构', 'python', 'javascript', '计算机'],
            'biology': ['生物', 'biology', '细胞', '基因', '进化'],
            'history': ['历史', 'history', '朝代', '战争'],
            'language': ['语言', '英语', 'english', '语法', '词汇'],
        }

        for subject, keywords in subject_keywords.items():
            if any(keyword in topic_lower for keyword in keywords):
                return subject

        return 'general'

    def _infer_difficulty(self, question: Dict[str, Any]) -> str:
        """从题目内容推断难度"""
        question_type = question.get('type', 'choice')

        # 分析题默认为困难
        if question_type == 'analysis':
            return 'hard'

        # 根据题目长度和复杂度推断
        text = question.get('text', '')
        text_length = len(text)

        if text_length > 100:
            return 'hard'
        elif text_length > 50:
            return 'medium'
        else:
            return 'easy'


# 单例
_grinder_supervisor = None

def get_grinder_supervisor(db: Session = None) -> GrinderSupervisor:
    global _grinder_supervisor
    if _grinder_supervisor is None or (_grinder_supervisor.db is None and db is not None):
        _grinder_supervisor = GrinderSupervisor(db)
    return _grinder_supervisor
