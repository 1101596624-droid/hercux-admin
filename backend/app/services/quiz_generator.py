"""
题库生成服务
用于在课程入库时预生成测验题目
支持三个难度级别：简单(easy)、中等(medium)、困难(hard)
采用分批生成策略，每批5道题，提高成功率
"""

import json
import re
import logging
from typing import List, Dict, Optional
import sqlite3
from pathlib import Path

from app.services.claude_service import get_claude_service, Message

logger = logging.getLogger(__name__)


class QuizItem:
    """单个测验题目"""
    def __init__(self, id: int, question: str, options: List[str], correct_option: str, difficulty: str = "easy"):
        self.id = id
        self.question = question
        self.options = options
        self.correct_option = correct_option
        self.difficulty = difficulty

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "question": self.question,
            "options": self.options,
            "correct_option": self.correct_option,
            "difficulty": self.difficulty
        }


class QuizGeneratorService:
    """题库生成服务"""

    def __init__(self):
        self.claude = get_claude_service()

    async def generate_quiz_bank_by_difficulty(
        self,
        node_title: str,
        learning_objectives: List[str],
        content: str,
        difficulty: str,
        num_questions: int = 13
    ) -> List[dict]:
        """
        为单个节点生成指定难度的题库（分批生成，每批5道题）

        Args:
            node_title: 节点标题
            learning_objectives: 学习目标列表
            content: 节点内容
            difficulty: 难度级别 (easy/medium/hard)
            num_questions: 生成题目数量

        Returns:
            题目列表
        """
        difficulty_cn = {"easy": "简单", "medium": "中等", "hard": "困难"}.get(difficulty, "简单")

        # 分批生成，每批5道题
        batch_size = 5
        all_questions = []
        batches_needed = (num_questions + batch_size - 1) // batch_size

        for batch_idx in range(batches_needed):
            remaining = num_questions - len(all_questions)
            current_batch_size = min(batch_size, remaining)

            if current_batch_size <= 0:
                break

            print(f"    生成第 {batch_idx + 1}/{batches_needed} 批 ({current_batch_size}道{difficulty_cn}题)...")

            batch_questions = await self._generate_single_batch(
                node_title=node_title,
                learning_objectives=learning_objectives,
                content=content,
                difficulty=difficulty,
                batch_size=current_batch_size,
                batch_num=batch_idx + 1
            )

            all_questions.extend(batch_questions)

        # 确保有足够的题目
        while len(all_questions) < num_questions:
            all_questions.extend(self._generate_default_questions(
                node_title,
                num_questions - len(all_questions),
                difficulty
            ))

        # 重新编号
        result = []
        for i, q in enumerate(all_questions[:num_questions]):
            result.append({
                "id": i + 1,
                "question": q.get("question", f"关于{node_title}的问题{i+1}"),
                "options": q.get("options", ["选项A", "选项B", "选项C", "选项D"]),
                "correct_option": q.get("correct_option", "A"),
                "difficulty": difficulty
            })

        logger.info(f"成功为节点 '{node_title}' 生成 {len(result)} 道{difficulty_cn}难度题目")
        return result

    async def _generate_single_batch(
        self,
        node_title: str,
        learning_objectives: List[str],
        content: str,
        difficulty: str,
        batch_size: int,
        batch_num: int
    ) -> List[dict]:
        """生成单批题目"""
        content_summary = content[:1200] if content else ""

        difficulty_cn = {"easy": "简单", "medium": "中等", "hard": "困难"}.get(difficulty, "简单")

        difficulty_hints = {
            "easy": "基础概念题，答案明显，考查定义和基本理解",
            "medium": "理解应用题，需要思考，考查概念联系",
            "hard": "综合分析题，有迷惑选项，���查深度理解和迁移"
        }

        # 简化的prompt，更容易生成正确的JSON
        prompt = f"""请为课程"{node_title}"生成{batch_size}道{difficulty_cn}难度的选择题。

课程内容：{content_summary}

难度要求：{difficulty_hints.get(difficulty, "基础概念题")}

请严格按以下JSON格式返回，不要有任何其他文字：
{{"questions":[
{{"id":1,"question":"题目内容","options":["A选项","B选项","C选项","D选项"],"correct_option":"A"}},
{{"id":2,"question":"题目内容","options":["A选项","B选项","C选项","D选项"],"correct_option":"B"}}
]}}

要求：
1. 生成{batch_size}道题
2. 每题4个选项
3. correct_option只能是A/B/C/D
4. 题目要与课程内容��关"""

        try:
            response = await self.claude.generate_raw_response(
                prompt,
                temperature=0.7,
                max_tokens=2000
            )

            # 尝试多种方式解析JSON
            questions = self._parse_quiz_response(response)

            if questions:
                # 添加difficulty字段
                for q in questions:
                    q["difficulty"] = difficulty
                return questions
            else:
                print(f"      批次{batch_num}解析失败，使用默认题目")
                return self._generate_default_questions(node_title, batch_size, difficulty)

        except Exception as e:
            print(f"      批次{batch_num}生成失败: {e}")
            return self._generate_default_questions(node_title, batch_size, difficulty)

    def _parse_quiz_response(self, response: str) -> List[dict]:
        """解析AI返回的题目JSON"""
        if not response:
            return []

        # 清理响应
        response = response.strip()

        # 方法1: 直接匹配完整JSON对象
        try:
            # 找到第一个{和最后一个}
            start = response.find('{')
            end = response.rfind('}')
            if start != -1 and end != -1 and end > start:
                json_str = response[start:end+1]
                data = json.loads(json_str)
                if "questions" in data:
                    return data["questions"]
        except json.JSONDecodeError:
            pass

        # 方法2: 使用正则匹配questions数组
        try:
            match = re.search(r'"questions"\s*:\s*(\[[\s\S]*?\])\s*\}', response)
            if match:
                array_str = match.group(1)
                return json.loads(array_str)
        except:
            pass

        # 方法3: 直接匹配数组
        try:
            match = re.search(r'\[[\s\S]*\]', response)
            if match:
                return json.loads(match.group())
        except:
            pass

        return []

    async def generate_full_quiz_bank(
        self,
        node_title: str,
        learning_objectives: List[str],
        content: str
    ) -> Dict[str, List[dict]]:
        """
        为单个节点生成完整的三难度题库

        Args:
            node_title: 节点标题
            learning_objectives: 学习目标列表
            content: 节点内容

        Returns:
            包含三个难度级别的题库字典
        """
        quiz_bank = {
            "easy": [],
            "medium": [],
            "hard": []
        }

        # 每个难度生成13道题，共39道
        for difficulty in ["easy", "medium", "hard"]:
            difficulty_cn = {"easy": "简单", "medium": "中等", "hard": "困难"}.get(difficulty, "简单")
            print(f"  开始生成{difficulty_cn}难度题目...")

            questions = await self.generate_quiz_bank_by_difficulty(
                node_title=node_title,
                learning_objectives=learning_objectives,
                content=content,
                difficulty=difficulty,
                num_questions=13
            )
            quiz_bank[difficulty] = questions
            print(f"  {difficulty_cn}���度完成: {len(questions)}道题")

        return quiz_bank

    def _generate_default_questions(self, title: str, count: int, difficulty: str = "easy") -> List[dict]:
        """生成默认问题"""
        default_questions = {
            "easy": [
                {"question": f"关于「{title}」，以下哪项是核心概念？", "options": ["基础理论", "应用实践", "案例分析", "总结归纳"], "correct_option": "A"},
                {"question": f"学习「{title}」的主要目的是什么？", "options": ["理解原理", "记忆公式", "完成作业", "应付考试"], "correct_option": "A"},
                {"question": f"「{title}」中最重要的知识点是？", "options": ["核心概念", "边缘知识", "历史背景", "未来展望"], "correct_option": "A"},
                {"question": f"「{title}」的基本定义是什么？", "options": ["专业术语解释", "日常用语", "随意理解", "不需要定义"], "correct_option": "A"},
                {"question": f"学习「{title}」需要注意什么？", "options": ["理解核心", "死记硬背", "跳过难点", "只看标题"], "correct_option": "A"},
            ],
            "medium": [
                {"question": f"如何更好地掌握「{title}」？", "options": ["理解+实践", "死记硬背", "只看不练", "临时抱佛脚"], "correct_option": "A"},
                {"question": f"「{title}」与其他知识的关系是？", "options": ["相互关联", "完全独立", "毫无关系", "相互矛盾"], "correct_option": "A"},
                {"question": f"在实际应用中，「{title}」的价值体现在？", "options": ["解决问题", "增加负担", "毫无用处", "制造困惑"], "correct_option": "A"},
                {"question": f"「{title}」的应用场景包括？", "options": ["多种实际情境", "仅限理论", "无法应用", "只在考试中"], "correct_option": "A"},
                {"question": f"理解「{title}」的关键是？", "options": ["把握核心逻辑", "记住所有细节", "忽略难点", "只看结论"], "correct_option": "A"},
            ],
            "hard": [
                {"question": f"深入理解「{title}」需要具备哪些前置知识？", "options": ["相关基础概念", "无需任何基础", "只需记忆", "随意学习"], "correct_option": "A"},
                {"question": f"「{title}」的核心原理可以如何迁移应���？", "options": ["举一反三", "死板套用", "完全照搬", "无法迁移"], "correct_option": "A"},
                {"question": f"批判性地看待「{title}」，其局限性可能是？", "options": ["适用范围有限", "完美无缺", "毫无价值", "全是错误"], "correct_option": "A"},
                {"question": f"「{title}」与相关领域的交叉点在哪里？", "options": ["多学科融合", "完全独立", "互不相关", "相互排斥"], "correct_option": "A"},
                {"question": f"如何评价「{title}」的理论价值？", "options": ["有重要指导意义", "纯粹学术游戏", "��无价值", "已经过时"], "correct_option": "A"},
            ]
        }

        questions = default_questions.get(difficulty, default_questions["easy"])
        result = []
        for i in range(count):
            q = questions[i % len(questions)].copy()
            q["id"] = i + 1
            q["difficulty"] = difficulty
            result.append(q)
        return result


async def generate_quiz_for_node(node_id: int, db_path: str = None) -> bool:
    """
    为指定节点生成完整的三难度题库并保存到数据库

    Args:
        node_id: 节点数据库ID
        db_path: 数据库路径

    Returns:
        是否成功
    """
    if db_path is None:
        db_path = Path(__file__).parent.parent.parent / "hercu_dev.db"

    conn = None
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, title, learning_objectives, content_l1, content_l2
            FROM course_nodes
            WHERE id = ?
        """, (node_id,))

        node = cursor.fetchone()
        if not node:
            logger.error(f"节点不存在: {node_id}")
            return False

        learning_objectives = []
        if node['learning_objectives']:
            try:
                learning_objectives = json.loads(node['learning_objectives'])
            except:
                pass

        content = node['content_l1'] or node['content_l2'] or ""

        generator = QuizGeneratorService()
        quiz_bank = await generator.generate_full_quiz_bank(
            node_title=node['title'],
            learning_objectives=learning_objectives,
            content=content
        )

        # 保存到数据库（JSON格式包含三个难度级别）
        cursor.execute("""
            UPDATE course_nodes
            SET quiz_data = ?
            WHERE id = ?
        """, (json.dumps(quiz_bank, ensure_ascii=False), node_id))

        conn.commit()
        logger.info(f"节点 {node_id} 三难度题库已保存")
        return True

    except Exception as e:
        logger.error(f"生成题库失败: {e}")
        return False
    finally:
        if conn:
            conn.close()


async def generate_quiz_for_course(course_id: int, db_path: str = None) -> Dict[str, any]:
    """
    为整个课程的所有节点生成三难度题库

    Args:
        course_id: 课程ID
        db_path: 数据库路径

    Returns:
        生成结果统计
    """
    if db_path is None:
        db_path = Path(__file__).parent.parent.parent / "hercu_dev.db"

    conn = None
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, title
            FROM course_nodes
            WHERE course_id = ?
        """, (course_id,))

        nodes = cursor.fetchall()
        conn.close()
        conn = None

        if not nodes:
            return {"success": False, "message": "课程没有节点", "generated": 0, "failed": 0}

        print(f"\n找到 {len(nodes)} 个节点，开始生成题库...\n")

        generated = 0
        failed = 0

        for idx, node in enumerate(nodes):
            print(f"\n[{idx+1}/{len(nodes)}] 节点: {node['title']} (ID: {node['id']})")
            success = await generate_quiz_for_node(node['id'], db_path)
            if success:
                generated += 1
                print(f"  ✓ 完成")
            else:
                failed += 1
                print(f"  ✗ 失败")

        return {
            "success": True,
            "message": f"三难度题库生成完成: {generated} 成功, {failed} 失败",
            "generated": generated,
            "failed": failed,
            "total": len(nodes)
        }

    except Exception as e:
        logger.error(f"批量生成题库失败: {e}")
        return {"success": False, "message": str(e), "generated": 0, "failed": 0}
    finally:
        if conn:
            conn.close()
