"""
AI 导师对话 API - 重构版本
使用同步数据库管理器解决异步冲突问题
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from typing import List, Dict, Optional
import sqlite3
import json
import re
import unicodedata
from pathlib import Path

from app.services.claude_service import get_claude_service, Message
from app.db.sync_manager import get_sync_db_manager

router = APIRouter(tags=["AI Tutor"])

# 输入限制
MAX_MESSAGE_LENGTH = 2000


def sanitize_text(text: str) -> str:
    """过滤特殊字符，防止 API 报错"""
    if not text:
        return text
    return (
        text
        # 移除控制字符 (ASCII 0-31, 127)，保留换行(\n)和制表符(\t)
        .replace('\r', '\n')
        .translate(str.maketrans('', '', ''.join(chr(i) for i in range(32) if i not in (9, 10)) + chr(127)))
        # 移除零宽字符
        .replace('\u200b', '').replace('\u200c', '').replace('\u200d', '')
        .replace('\ufeff', '').replace('\u2060', '').replace('\u00ad', '')
        # 规范化 Unicode
    )


def get_sync_db():
    """获取同步 SQLite 连接"""
    # 优先使用生产环境数据库
    possible_paths = [
        Path("/www/wwwroot/hercu-backend/hercu.db"),  # 服务器生产环境
        Path(__file__).parent.parent.parent.parent.parent / "hercu.db",
        Path(__file__).parent.parent.parent.parent.parent / "hercu_dev.db",
        Path(__file__).parent.parent.parent.parent / "hercu.db",
        Path(__file__).parent.parent.parent.parent / "hercu_dev.db",
    ]
    db_path = None
    for path in possible_paths:
        if path.exists():
            db_path = path
            break
    if db_path is None:
        raise FileNotFoundError("Database file not found")
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


class ChatRequest(BaseModel):
    """聊天请求"""
    node_id: int
    message: str
    conversation_history: List[Dict[str, str]] = []
    current_layer: str = "L1"
    ai_tone: str = "friendly"  # professional, friendly, concise
    # 前端可能发送的额外字段
    current_step_index: Optional[int] = None
    total_steps: Optional[int] = None
    current_step_content: Optional[Dict] = None

    model_config = {"extra": "ignore"}  # 忽略其他未定义的字段

    @field_validator('message')
    @classmethod
    def validate_message(cls, v: str) -> str:
        """验证并清理消息"""
        v = sanitize_text(v)
        if len(v) > MAX_MESSAGE_LENGTH:
            raise ValueError(f'消息过长，最多 {MAX_MESSAGE_LENGTH} 字符，请精简后重新输入')
        return v

    @field_validator('conversation_history')
    @classmethod
    def validate_history(cls, v: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """清理对话历史中的特殊字符"""
        for msg in v:
            if 'content' in msg:
                msg['content'] = sanitize_text(msg['content'])
        return v


class ChatResponse(BaseModel):
    """聊天响应"""
    message: str
    suggestions: Optional[List[str]] = None


class HintRequest(BaseModel):
    """提示请求"""
    question: str
    user_answer: str
    correct_answer: str
    node_id: int


@router.post("/chat", response_model=ChatResponse)
async def chat_with_tutor(request: ChatRequest):
    """
    与 AI 导师对话

    Args:
        request: 聊天请求

    Returns:
        AI 导师回复
    """
    try:
        # 尝试从数据库获取节点信息
        node_info = None
        if request.node_id and request.node_id > 0:
            try:
                db_manager = get_sync_db_manager()
                node_info = db_manager.get_node_info(request.node_id)
            except Exception:
                pass  # 数据库查询失败时继续使用前端提供的上下文

        # 构建上下文 - 优先使用数据库信息，否则使用前端提供的上下文
        if node_info:
            context = {
                "node": {
                    "id": node_info["id"],
                    "title": node_info["title"],
                    "learning_objectives": node_info["learning_objectives"]
                },
                "ai_tutor_config": node_info["ai_tutor_config"],
                "current_layer": request.current_layer,
                "progress": {},
                "ai_tone": request.ai_tone
            }
        else:
            # 使用前端提供的上下文
            step_content = request.current_step_content or {}
            context = {
                "node": {
                    "id": request.node_id,
                    "title": step_content.get("title", "学习内容"),
                    "learning_objectives": []
                },
                "ai_tutor_config": {
                    "diagnostic_focus": step_content.get("diagnostic_focus", []),
                    "probing_questions": [{
                        "question": step_content.get("question", ""),
                        "expected_elements": step_content.get("expected_elements", []),
                        "intent": step_content.get("intent", "")
                    }] if step_content.get("question") else []
                },
                "current_layer": request.current_layer,
                "progress": {},
                "ai_tone": request.ai_tone,
                "current_step_index": request.current_step_index,
                "total_steps": request.total_steps
            }

        # 转换对话历史
        conversation_history = [
            Message(role=msg["role"], content=msg["content"])
            for msg in request.conversation_history
        ]

        # 调用 Claude 服务
        claude = get_claude_service()
        response_message = await claude.generate_tutor_response(
            user_message=request.message,
            context=context,
            conversation_history=conversation_history
        )

        return ChatResponse(message=response_message)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)}")


@router.post("/hint", response_model=ChatResponse)
async def get_hint(request: HintRequest):
    """
    获取答题提示

    Args:
        request: 提示请求

    Returns:
        提示信息
    """
    try:
        # 使用同步数据库管理器
        db_manager = get_sync_db_manager()
        ai_tutor_config = db_manager.get_ai_tutor_config(request.node_id)

        # 构建上下文
        context = {
            "ai_tutor_config": ai_tutor_config
        }

        # 调用 Claude 服务
        claude = get_claude_service()
        hint_message = await claude.generate_hint(
            question=request.question,
            user_answer=request.user_answer,
            correct_answer=request.correct_answer,
            context=context
        )

        return ChatResponse(message=hint_message)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate hint: {str(e)}")


@router.get("/welcome/{node_id}")
async def get_welcome_message(node_id: int):
    """
    获取节点的欢迎消息

    Args:
        node_id: 节点 ID

    Returns:
        欢迎消息
    """
    try:
        print(f"[DEBUG] Welcome endpoint called with node_id={node_id}")
        db_manager = get_sync_db_manager()
        print(f"[DEBUG] Got db_manager: {type(db_manager)}")
        ai_tutor_config = db_manager.get_ai_tutor_config(node_id)
        print(f"[DEBUG] Got ai_tutor_config: {ai_tutor_config}")

        welcome_message = ai_tutor_config.get(
            "on_enter",
            "欢迎开始学习！有任何问题随时问我。"
        )
        print(f"[DEBUG] Returning message: {welcome_message}")

        return {"message": welcome_message}

    except Exception as e:
        print(f"[DEBUG] Exception occurred: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get welcome message: {str(e)}")


@router.get("/completion/{node_id}")
async def get_completion_message(node_id: int):
    """
    获取节点的完成消息

    Args:
        node_id: 节点 ID

    Returns:
        完成消息
    """
    try:
        db_manager = get_sync_db_manager()
        ai_tutor_config = db_manager.get_ai_tutor_config(node_id)

        completion_message = ai_tutor_config.get(
            "on_complete",
            "恭喜完成本节学习！"
        )

        return {"message": completion_message}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get completion message: {str(e)}")


@router.get("/debug")
async def debug_endpoint():
    """调试端点 - 确认重构版本已加载"""
    return {"status": "refactored_version_loaded", "version": "2.0"}


# === Quiz Generation Models ===

class QuizGenerateRequest(BaseModel):
    """测验生成请求"""
    node_id: int
    node_title: Optional[str] = None
    node_type: Optional[str] = None


class QuizItem(BaseModel):
    """单个测验题目"""
    id: int
    question: str
    options: List[str]
    correct_option: str


class BatchQuizGenerateResponse(BaseModel):
    """批量测验生成响应"""
    questions: List[QuizItem]
    total: int


def _generate_default_questions(title: str, count: int) -> List[dict]:
    """生成默认问题"""
    default_questions = [
        {"question": f"关于「{title}」，以下哪项是核心概念？", "options": ["基础理论", "应用实践", "案例分析", "总结归纳"], "correct_option": "A"},
        {"question": f"学习「{title}」的主要目的是什么？", "options": ["理解原理", "记忆公式", "完成作业", "应付考试"], "correct_option": "A"},
        {"question": f"「{title}」中最重要的知识点是？", "options": ["核心概念", "边缘知识", "历史背景", "未来展望"], "correct_option": "A"},
        {"question": f"如何更好地掌握「{title}」？", "options": ["理解+实践", "死记硬背", "只看不练", "临时抱佛脚"], "correct_option": "A"},
        {"question": f"「{title}」与其他知识的关系是？", "options": ["相互关联", "完全独立", "毫无关系", "相互矛盾"], "correct_option": "A"},
    ]
    result = []
    for i in range(count):
        q = default_questions[i % len(default_questions)].copy()
        result.append(q)
    return result


@router.post("/generate-batch-quiz", response_model=BatchQuizGenerateResponse)
async def generate_batch_quiz(request: QuizGenerateRequest):
    """
    批量生成13道测验题目

    Args:
        request: 测验生成请求

    Returns:
        13道测验题目列表
    """
    conn = None
    try:
        # 获取数据库连接
        conn = get_sync_db()
        cursor = conn.cursor()

        # 获取节点信息
        cursor.execute(
            """
            SELECT
                id,
                title,
                learning_objectives,
                content_l1,
                content_l2,
                content_l3,
                ai_tutor_config
            FROM course_nodes
            WHERE id = ?
            """,
            (request.node_id,)
        )

        node = cursor.fetchone()

        if not node:
            raise HTTPException(status_code=404, detail="Node not found")

        # 解析 JSON 字段
        learning_objectives = json.loads(node['learning_objectives']) if node['learning_objectives'] else []
        content_l1 = node['content_l1'] or ""
        content_l2 = node['content_l2'] or ""

        # 构建提示词
        content_summary = content_l1[:2000] if content_l1 else content_l2[:2000] if content_l2 else ""
        objectives_text = "\n".join([f"- {obj}" for obj in learning_objectives]) if learning_objectives else ""

        prompt = f"""基于以下课程内容，生成13道选择题来测试学生的理解。

课程标题: {node['title']}

学习目标:
{objectives_text}

课程内容摘要:
{content_summary}

请生成13道选择题，要求：
1. 问题要与课程内容直接相关
2. 每题提供4个选项（A、B、C、D）
3. 只有一个正确答案
4. 选项要有一定的迷惑性但不能太难
5. 题目难度要有层次，从简单到中等

请严格按照以下JSON格式返回（不要包含其他文字）：
{{"questions": [
  {{"id": 1, "question": "问题1", "options": ["选项A", "选项B", "选项C", "选项D"], "correct_option": "A"}},
  {{"id": 2, "question": "问题2", "options": ["选项A", "选项B", "选项C", "选项D"], "correct_option": "B"}},
  ...
]}}

注意：correct_option 只能是 A、B、C、D 中的一个字母。"""

        # 调用 Claude 服务
        claude = get_claude_service()
        response = await claude.generate_raw_response(prompt, temperature=0.7, max_tokens=4000)

        # 解析响应
        # 尝试提取 JSON
        json_match = re.search(r'\{[\s\S]*"questions"[\s\S]*\}', response)
        if json_match:
            quiz_data = json.loads(json_match.group())
            questions = quiz_data.get("questions", [])
        else:
            # 如果无法解析，返回默认问题
            questions = _generate_default_questions(node['title'], 13)

        # 确保有13道题
        while len(questions) < 13:
            questions.extend(_generate_default_questions(node['title'], 13 - len(questions)))

        # 转换为响应格式
        quiz_items = []
        for i, q in enumerate(questions[:13]):
            quiz_items.append(QuizItem(
                id=i + 1,
                question=q.get("question", f"关于{node['title']}的问题{i+1}"),
                options=q.get("options", ["选项A", "选项B", "选项C", "选项D"]),
                correct_option=q.get("correct_option", "A")
            ))

        return BatchQuizGenerateResponse(
            questions=quiz_items,
            total=len(quiz_items)
        )

    except json.JSONDecodeError as e:
        # JSON 解析失败，返回默认问题
        questions = _generate_default_questions(request.node_title or "本节课程", 20)
        quiz_items = [QuizItem(
            id=i + 1,
            question=q["question"],
            options=q["options"],
            correct_option=q["correct_option"]
        ) for i, q in enumerate(questions)]
        return BatchQuizGenerateResponse(questions=quiz_items, total=20)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate batch quiz: {str(e)}")
    finally:
        if conn:
            conn.close()


# === Answer Evaluation ===

class AnswerItem(BaseModel):
    """单个答案"""
    question_index: int
    question: str
    options: List[str]
    user_answer: str
    correct_answer: str


class EvaluateRequest(BaseModel):
    """评估请求"""
    node_id: int
    answers: List[AnswerItem]


@router.post("/evaluate-answers")
async def evaluate_answers(request: EvaluateRequest):
    """评估用户答案"""
    results = []
    correct_count = 0

    for ans in request.answers:
        # 处理空值情况
        correct_answer = ans.correct_answer or ""
        user_answer = ans.user_answer or ""

        is_correct = user_answer.upper() == correct_answer.upper() if correct_answer else False
        if is_correct:
            correct_count += 1

        # 获取正确答案的完整内容
        if correct_answer and len(correct_answer) == 1:
            correct_index = ord(correct_answer.upper()) - ord('A')
            correct_option_text = ans.options[correct_index] if 0 <= correct_index < len(ans.options) else correct_answer
        else:
            correct_option_text = correct_answer or "未知"

        # 生成解析
        if is_correct:
            explanation = f"正确！答案是 {correct_answer}：{correct_option_text}"
        else:
            if user_answer and len(user_answer) == 1:
                user_index = ord(user_answer.upper()) - ord('A')
                user_option_text = ans.options[user_index] if 0 <= user_index < len(ans.options) else user_answer
            else:
                user_option_text = user_answer or "未选择"
            explanation = f"正确答案是 {correct_answer or '未设置'}：{correct_option_text}。你选择的「{user_option_text}」不正确。"

        results.append({
            "question_index": ans.question_index,
            "is_correct": is_correct,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "explanation": explanation
        })

    total = len(request.answers)
    score = (correct_count / total * 100) if total > 0 else 0

    return {
        "results": results,
        "total_questions": total,
        "correct_count": correct_count,
        "score": round(score, 1),
        "overall_feedback": "做得很好！" if score >= 80 else "继续努力！" if score >= 60 else "需要复习一下"
    }
