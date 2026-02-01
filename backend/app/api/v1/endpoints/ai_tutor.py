"""
AI 导师对话 API
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import sqlite3
import json
from pathlib import Path

from app.services.deepseek_service import get_deepseek_service, Message
from app.core.config import settings

router = APIRouter(tags=["AI Tutor"])


def get_sync_db():
    """获取同步 SQLite 连接"""
    # 使用相对于 backend 目录的路径
    db_path = Path(__file__).parent.parent.parent.parent.parent / "hercu_dev.db"
    if not db_path.exists():
        # 尝试另一个可能的位置
        db_path = Path(__file__).parent.parent.parent.parent / "hercu_dev.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


class ChatRequest(BaseModel):
    """聊天请求"""
    node_id: int
    message: str
    conversation_history: List[Dict[str, str]] = []  # [{"role": "user/assistant", "content": "..."}]
    current_layer: str = "L1"
    quiz_correct_count: int = 0  # 当前答对题数


class ChatResponse(BaseModel):
    """聊天响应"""
    message: str
    suggestions: Optional[List[str]] = None
    is_quiz_question: bool = False  # 是否是测验问题
    quiz_correct: Optional[bool] = None  # 用户回答是否正确
    new_correct_count: int = 0  # 更新后的答对题数
    unlock_next: bool = False  # 是否解锁下一节


class HintRequest(BaseModel):
    """提示请求"""
    question: str
    user_answer: str
    correct_answer: str
    node_id: int


@router.get("/test-simple")
async def test_simple():
    """简单测试端点"""
    return {"success": True, "message": "Test endpoint works"}


@router.get("/test-db")
async def test_db_connection():
    """测试数据库连接"""
    conn = None
    try:
        conn = get_sync_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title FROM course_nodes LIMIT 1")
        node = cursor.fetchone()
        return {"success": True, "node": dict(node) if node else None}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        if conn:
            conn.close()


@router.post("/chat", response_model=ChatResponse)
async def chat_with_tutor(request: ChatRequest):
    """
    与 AI 导师对话（含测验功能）

    AI 会在对话中随机提问，用户通过对话回答问题。
    答对3题后解锁下一节课程。

    Args:
        request: 聊天请求

    Returns:
        AI 导师回复
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
        ai_tutor_config = json.loads(node['ai_tutor_config']) if node['ai_tutor_config'] else {}
        content_l1 = node['content_l1'] or ""
        content_l2 = node['content_l2'] or ""

        # 构建上下文
        context = {
            "node": {
                "id": node['id'],
                "title": node['title'],
                "learning_objectives": learning_objectives
            },
            "ai_tutor_config": ai_tutor_config,
            "current_layer": request.current_layer,
            "progress": {}
        }

        # 转换对话历史
        conversation_history = [
            Message(role=msg["role"], content=msg["content"])
            for msg in request.conversation_history
        ]

        # 调用 DeepSeek 服务生成带测验的回复
        deepseek = get_deepseek_service()

        # 构建测验感知的系统提示
        quiz_correct_count = request.quiz_correct_count
        content_summary = content_l1[:1500] if content_l1 else content_l2[:1500] if content_l2 else ""
        objectives_text = "\n".join([f"- {obj}" for obj in learning_objectives]) if learning_objectives else ""

        # 计算当前是第几题
        current_question_num = quiz_correct_count + 1

        quiz_system_prompt = f"""你是测验机器人。课程：{node['title']}。已答对：{quiz_correct_count}/3题。

规则：收到"开始"直接出题，收到A/B/C/D判断对错。禁止问候、确认、解释。

标记：出题加[QUIZ_NONE]，答对加[QUIZ_CORRECT]，答错加[QUIZ_WRONG]"""

        # 检测是否是测验触发词
        quiz_trigger_words = ["开始测试", "测验", "考试", "出题", "做题", "答题", "开始答题", "开始测验", "开始考试", "开始"]
        is_quiz_trigger = any(word in request.message for word in quiz_trigger_words)

        # 检测是否是答案（A/B/C/D 或包含选项的回答）
        answer_patterns = ["a", "b", "c", "d", "A", "B", "C", "D"]
        user_msg_stripped = request.message.strip().upper()
        is_quiz_answer = user_msg_stripped in ["A", "B", "C", "D"] or (
            len(user_msg_stripped) <= 3 and any(p.upper() in user_msg_stripped for p in answer_patterns)
        )

        # 使用自定义系统提示生成回复
        messages = [
            Message(role="system", content=quiz_system_prompt)
        ]

        # 添加few-shot示例，教AI正确的行为
        # 示例1：用户说开始，AI直接出题
        messages.append(Message(role="user", content="开始"))
        messages.append(Message(role="assistant", content=f"📝第1题：什么是{node['title']}的核心概念？\nA.选项一 B.选项二 C.选项三 D.选项四\n请选择A/B/C/D[QUIZ_NONE]"))
        # 示例2：用户回答正确，AI判断并出下一题
        messages.append(Message(role="user", content="A"))
        messages.append(Message(role="assistant", content=f"✅正确！\n\n📝第2题：关于{node['title']}，以下哪项是正确的？\nA.选项一 B.选项二 C.选项三 D.选项四\n请选择A/B/C/D[QUIZ_CORRECT]"))

        # 如果是测验触发词，不传对话历史，强制出题
        if is_quiz_trigger:
            # 直接出题，不要任何对话历史干扰
            messages.append(Message(role="user", content="开始"))
        elif is_quiz_answer:
            # 是答案，只传最近的对话（包含上一题）以便AI判断对错
            # 只保留最近1条消息（上一个问题）
            if conversation_history:
                # 找到最后一条assistant消息（应该是题目）
                for msg in reversed(conversation_history):
                    if msg.role == "assistant":
                        messages.append(msg)
                        break
            messages.append(Message(role="user", content=request.message))
        else:
            messages.extend(conversation_history[-20:])
            messages.append(Message(role="user", content=request.message))

        response = await deepseek.chat_completion(messages, temperature=0.0)
        response_message = response["choices"][0]["message"]["content"]

        # DEBUG: 打印AI返回的原始内容
        print(f"[DEBUG] User message: {request.message}")
        print(f"[DEBUG] Is quiz trigger: {is_quiz_trigger}")
        print(f"[DEBUG] Is quiz answer: {is_quiz_answer}")
        print(f"[DEBUG] Quiz correct count: {quiz_correct_count}")
        print(f"[DEBUG] Messages sent to AI: {len(messages)} messages")
        print(f"[DEBUG] AI response: {response_message[:500]}...")

        # 解析测验状态
        is_quiz_question = False
        quiz_correct = None
        new_correct_count = quiz_correct_count
        unlock_next = False

        # 检查回复中的测验标记
        if "[QUIZ_CORRECT]" in response_message:
            quiz_correct = True
            new_correct_count = quiz_correct_count + 1
            response_message = response_message.replace("[QUIZ_CORRECT]", "").strip()
            is_quiz_question = True
        elif "[QUIZ_WRONG]" in response_message:
            quiz_correct = False
            response_message = response_message.replace("[QUIZ_WRONG]", "").strip()
            is_quiz_question = True
        elif "[QUIZ_NONE]" in response_message:
            response_message = response_message.replace("[QUIZ_NONE]", "").strip()

        # 检查是否解锁下一节
        if new_correct_count >= 3:
            unlock_next = True

        return ChatResponse(
            message=response_message,
            is_quiz_question=is_quiz_question,
            quiz_correct=quiz_correct,
            new_correct_count=new_correct_count,
            unlock_next=unlock_next
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)}")
    finally:
        if conn:
            conn.close()


@router.post("/hint", response_model=ChatResponse)
async def get_hint(request: HintRequest):
    """
    获取答题提示

    Args:
        request: 提示请求

    Returns:
        提示信息
    """
    conn = None
    try:
        # 获取数据库连接
        conn = get_sync_db()
        cursor = conn.cursor()

        # 获取节点信息
        cursor.execute(
            """
            SELECT ai_tutor_config
            FROM course_nodes
            WHERE id = ?
            """,
            (request.node_id,)
        )

        node = cursor.fetchone()

        if not node:
            raise HTTPException(status_code=404, detail="Node not found")

        # 解析 JSON 字段
        ai_tutor_config = json.loads(node['ai_tutor_config']) if node['ai_tutor_config'] else {}

        # 构建上下文
        context = {
            "ai_tutor_config": ai_tutor_config
        }

        # 调用 DeepSeek 服务
        deepseek = get_deepseek_service()
        hint_message = await deepseek.generate_hint(
            question=request.question,
            user_answer=request.user_answer,
            correct_answer=request.correct_answer,
            context=context
        )

        return ChatResponse(message=hint_message)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate hint: {str(e)}")
    finally:
        if conn:
            conn.close()


@router.get("/welcome/{node_id}")
async def get_welcome_message(node_id: int):
    """
    获取节点的欢迎消息

    Args:
        node_id: 节点 ID

    Returns:
        欢迎消息
    """
    conn = None
    try:
        print(f"[DEBUG] Getting DB connection...")
        conn = get_sync_db()
        print(f"[DEBUG] Connection type: {type(conn)}")
        cursor = conn.cursor()
        print(f"[DEBUG] Cursor type: {type(cursor)}")

        cursor.execute(
            """
            SELECT ai_tutor_config
            FROM course_nodes
            WHERE id = ?
            """,
            (node_id,)
        )

        print(f"[DEBUG] About to fetchone...")
        node = cursor.fetchone()
        print(f"[DEBUG] Node fetched: {node}")

        if not node:
            raise HTTPException(status_code=404, detail="Node not found")

        ai_tutor_config = json.loads(node['ai_tutor_config']) if node['ai_tutor_config'] else {}
        welcome_message = ai_tutor_config.get("on_enter", "欢迎开始学习！有任何问题随时问我。")

        return {"message": welcome_message}

    except Exception as e:
        print(f"[DEBUG] Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get welcome message: {str(e)}")
    finally:
        if conn:
            conn.close()


@router.get("/completion/{node_id}")
async def get_completion_message(node_id: int):
    """
    获取节点的完成消息

    Args:
        node_id: 节点 ID

    Returns:
        完成消息
    """
    conn = None
    try:
        conn = get_sync_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT ai_tutor_config
            FROM course_nodes
            WHERE id = ?
            """,
            (node_id,)
        )

        node = cursor.fetchone()

        if not node:
            raise HTTPException(status_code=404, detail="Node not found")

        ai_tutor_config = json.loads(node['ai_tutor_config']) if node['ai_tutor_config'] else {}
        completion_message = ai_tutor_config.get("on_complete", "恭喜完成本节学习！")

        return {"message": completion_message}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get completion message: {str(e)}")
    finally:
        if conn:
            conn.close()


class QuizGenerateRequest(BaseModel):
    """测验生成请求"""
    node_id: int
    node_title: Optional[str] = None
    node_type: Optional[str] = None
    difficulty: str = "easy"  # easy, medium, hard


class QuizGenerateResponse(BaseModel):
    """测验生成响应"""
    question: str
    answer: str
    options: List[str]


class QuizItem(BaseModel):
    """单个测验题目"""
    id: int
    question: str
    options: List[str]
    correct_option: str  # A, B, C, or D
    difficulty: str = "easy"  # easy, medium, hard


class BatchQuizGenerateResponse(BaseModel):
    """批量测验生成响应"""
    questions: List[QuizItem]
    total: int
    difficulty: str = "easy"  # 当前返回的难度级别


@router.post("/generate-quiz", response_model=QuizGenerateResponse)
async def generate_quiz_question(request: QuizGenerateRequest):
    """
    根据节点内容生成测验问题

    Args:
        request: 测验生成请求

    Returns:
        测验问题、选项和正确答案
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
        content_summary = content_l1[:1000] if content_l1 else content_l2[:1000] if content_l2 else ""
        objectives_text = "\n".join([f"- {obj}" for obj in learning_objectives]) if learning_objectives else ""

        prompt = f"""基于以下课程内容，生成一道选择题来测试学生的理解。

课程标题: {node['title']}

学习目标:
{objectives_text}

课程内容摘要:
{content_summary}

请生成一道选择题，要求：
1. 问题要与课程内容直接相关
2. 提供4个选项（A、B、C、D）
3. 只有一个正确答案
4. 选项要有一定的迷惑性但不能太难

请严格按照以下JSON格式返回（不要包含其他文字）：
{{"question": "问题内容", "options": ["选项A", "选项B", "选项C", "选项D"], "answer": "正确答案的完整文本"}}"""

        # 调用 DeepSeek 服务
        deepseek = get_deepseek_service()
        response = await deepseek.generate_raw_response(prompt)

        # 解析响应
        import re
        # 尝试提取 JSON
        json_match = re.search(r'\{[^{}]*"question"[^{}]*\}', response, re.DOTALL)
        if json_match:
            quiz_data = json.loads(json_match.group())
        else:
            # 如果无法解析，返回默认问题
            quiz_data = {
                "question": f"关于「{node['title']}」，以下哪项描述是正确的？",
                "options": [
                    "这是一个关于基础概念的问题",
                    "这是一个关于应用实践的问题",
                    "这是一个关于理论分析的问题",
                    "以上都不正确"
                ],
                "answer": "这是一个关于基础概念的问题"
            }

        return QuizGenerateResponse(
            question=quiz_data["question"],
            options=quiz_data["options"],
            answer=quiz_data["answer"]
        )

    except json.JSONDecodeError as e:
        # JSON 解析失败，返回默认问题
        return QuizGenerateResponse(
            question=f"关于「{request.node_title or '本节课程'}」的内容，你学到了什么？",
            options=[
                "掌握了核心概念",
                "了解了基本原理",
                "学会了实际应用",
                "以上都有"
            ],
            answer="以上都有"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")
    finally:
        if conn:
            conn.close()


@router.post("/generate-batch-quiz", response_model=BatchQuizGenerateResponse)
async def generate_batch_quiz(request: QuizGenerateRequest):
    """
    获取预生成的测验题库

    只使用后台管理系统预生成的题库，不再实时生成。
    支持三个难度级别：easy（简单）、medium（中等）、hard（困难）

    Args:
        request: 测验生成请求（包含 difficulty 参数）

    Returns:
        指定难度的测验题目列表
    """
    conn = None
    try:
        # 获取数据库连接
        conn = get_sync_db()
        cursor = conn.cursor()

        # 获取节点信息（包含预生成的题库）
        cursor.execute(
            """
            SELECT
                id,
                title,
                quiz_data
            FROM course_nodes
            WHERE id = ?
            """,
            (request.node_id,)
        )

        node = cursor.fetchone()

        if not node:
            raise HTTPException(status_code=404, detail="Node not found")

        # 验证难度参数
        difficulty = request.difficulty if request.difficulty in ["easy", "medium", "hard"] else "easy"

        # 检查是否有预生成的题库
        if node['quiz_data']:
            try:
                quiz_data = json.loads(node['quiz_data'])

                # 新格式：包含 easy/medium/hard 三个难度级别
                if isinstance(quiz_data, dict) and difficulty in quiz_data:
                    questions = quiz_data[difficulty]
                    if questions and len(questions) > 0:
                        quiz_items = []
                        for i, q in enumerate(questions):
                            quiz_items.append(QuizItem(
                                id=i + 1,
                                question=q.get("question", f"关于{node['title']}的问题{i+1}"),
                                options=q.get("options", ["选项A", "选项B", "选项C", "选项D"]),
                                correct_option=q.get("correct_option", "A"),
                                difficulty=difficulty
                            ))
                        print(f"[INFO] 使用预生成题库: 节点 {node['title']}, 难度 {difficulty}, {len(quiz_items)} 道题")
                        return BatchQuizGenerateResponse(
                            questions=quiz_items,
                            total=len(quiz_items),
                            difficulty=difficulty
                        )

                # 旧格式：直接是题目列表（兼容处理）
                elif isinstance(quiz_data, list) and len(quiz_data) > 0:
                    quiz_items = []
                    for i, q in enumerate(quiz_data[:20]):
                        quiz_items.append(QuizItem(
                            id=i + 1,
                            question=q.get("question", f"关于{node['title']}的问题{i+1}"),
                            options=q.get("options", ["选项A", "选项B", "选项C", "选项D"]),
                            correct_option=q.get("correct_option", "A"),
                            difficulty="easy"
                        ))
                    print(f"[INFO] 使用旧格式题库: 节点 {node['title']}, {len(quiz_items)} 道题")
                    return BatchQuizGenerateResponse(
                        questions=quiz_items,
                        total=len(quiz_items),
                        difficulty="easy"
                    )

            except json.JSONDecodeError:
                print(f"[WARN] 预生成题库解析失败: 节点 {node['title']}")

        # 没有预生成题库，返回默认问题（提示用户需要在后台生成题库）
        print(f"[WARN] 节点 {node['title']} 没有预生成题库，请在后台管理系统生成")
        questions = _generate_default_questions(node['title'], 7, difficulty)
        quiz_items = [QuizItem(
            id=i + 1,
            question=q["question"],
            options=q["options"],
            correct_option=q["correct_option"],
            difficulty=difficulty
        ) for i, q in enumerate(questions)]
        return BatchQuizGenerateResponse(questions=quiz_items, total=len(quiz_items), difficulty=difficulty)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get quiz: {str(e)}")
    finally:
        if conn:
            conn.close()


def _generate_default_questions(title: str, count: int, difficulty: str = "easy") -> List[dict]:
    """生成默认问题"""
    difficulty_cn = {"easy": "简单", "medium": "中等", "hard": "困难"}.get(difficulty, "简单")

    default_questions = {
        "easy": [
            {"question": f"关于「{title}」，以下哪项是核心概念？", "options": ["基础理论", "应用实践", "案例分析", "总结归纳"], "correct_option": "A"},
            {"question": f"学习「{title}」的主要目的是什么？", "options": ["理解原理", "记忆公式", "完成作业", "应付考试"], "correct_option": "A"},
            {"question": f"「{title}」中最重要的知识点是？", "options": ["核心概念", "边缘知识", "历史背景", "未来展望"], "correct_option": "A"},
        ],
        "medium": [
            {"question": f"如何更好地掌握「{title}」？", "options": ["理解+实践", "死记硬背", "只看不练", "临时抱佛脚"], "correct_option": "A"},
            {"question": f"「{title}」与其他知识的关系是？", "options": ["相互关联", "完全独立", "毫无关系", "相互矛盾"], "correct_option": "A"},
            {"question": f"在实际应用中，「{title}」的价值体现在？", "options": ["解决问题", "增加负担", "毫无用处", "制造困惑"], "correct_option": "A"},
        ],
        "hard": [
            {"question": f"深入理解「{title}」需要具备哪些前置知识？", "options": ["相关基础概念", "无需任何基础", "只需记忆", "随意学习"], "correct_option": "A"},
            {"question": f"「{title}」的核心原理可以如何迁移应用？", "options": ["举一反三", "死板套用", "完全照搬", "无法迁移"], "correct_option": "A"},
            {"question": f"批判性地看待「{title}」，其局限性可能是？", "options": ["适用范围有限", "完美无缺", "毫无价值", "全是错误"], "correct_option": "A"},
        ]
    }

    questions = default_questions.get(difficulty, default_questions["easy"])
    result = []
    for i in range(count):
        q = questions[i % len(questions)].copy()
        result.append(q)
    return result
