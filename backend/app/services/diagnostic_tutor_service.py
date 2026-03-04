"""
Diagnostic Tutor Service - Phase 3 诊断式AI Tutor
多轮对话状态机 + 情感感知 + BKT知识状态 + 苏格拉底式引导
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from app.models.models import (
    StudentConversation, StudentKnowledgeState,
    StudentEmotionState, StudentMisconception, KnowledgeNode
)
from app.services.emotion_service import EmotionService
from app.services.llm_factory import get_llm_service, Message


class TutorPhase(str, Enum):
    UNDERSTAND = "understand"
    DIAGNOSE = "diagnose"
    SCAFFOLD = "scaffold"
    EXPLAIN = "explain"
    VERIFY = "verify"
    EXTEND = "extend"


# 各阶段系统提示模板
PHASE_PROMPTS = {
    TutorPhase.UNDERSTAND: """你是一位顶级私教。学生刚提出问题。
你的任务：
1. 准确理解学生的困惑点（不是表面问题，而是深层卡点）
2. 用一个精准的追问来确认你的理解
3. 不要急于给答案

学生当前知识状态：{state_summary}
当前情感状态：{emotion_summary}
{emotion_guidance}""",

    TutorPhase.DIAGNOSE: """基于学生的回答，你需要诊断：
1. 学生缺少哪个前置知识？
2. 是概念理解错误还是应用方法错误？
3. 是否存在常见误解（misconception）？

已知误解模式：{known_misconceptions}
学生知识掌握度：{mastery:.0%}

用一个针对性的问题来验证你的诊断。""",

    TutorPhase.SCAFFOLD: """诊断结果：{diagnosis}
现在用苏格拉底式引导帮助学生自己发现答案：
1. 从学生已掌握的知识出发
2. 搭建一个思维阶梯，每步只跨越一个小概念
3. 用具体例子而非抽象定义
4. 如果学生的误解是「{misconception}」，设计一个反例让学生自己发现矛盾

学生掌握度：{mastery:.0%}
{emotion_guidance}""",

    TutorPhase.EXPLAIN: """学生经过引导仍有困难，现在需要直接讲解。
要求：
1. 用最简单的语言解释核心概念
2. 结合学生之前的回答，针对性地讲解
3. 给出一个具体的例子帮助理解
4. 讲解后用一个简单的问题确认理解

诊断结果：{diagnosis}
{emotion_guidance}""",

    TutorPhase.VERIFY: """学生似乎理解了。用以下方式验证：
1. 给一个变式问题（改变表面特征，保留深层结构）
2. 或者让学生用自己的话解释
3. 如果学生能正确回答变式题，确认掌握

当前知识点：{node_title}
学生掌握度：{mastery:.0%}""",

    TutorPhase.EXTEND: """学生已掌握当前知识点。
根据知识图谱，推荐一个自然的延伸方向。
用一个有趣的问题引导学生思考更深层的联系。

当前知识点：{node_title}
学生掌握度：{mastery:.0%}""",
}

# 情感引导策略
EMOTION_GUIDANCE = {
    "frustration": "学生正在感到挫败，请用温和鼓励的语气，降低问题难度，先从学生能回答的问题开始建立信心。",
    "anxiety": "学生有些焦虑，请放慢节奏，给予更多正面反馈，避免连续追问。",
    "boredom": "学生感到无聊，请提高挑战性，用更有趣的例子或反直觉的问题激发兴趣。",
    "focus": "学生状态良好，保持当前节奏。",
    "excitement": "学生很兴奋，可以适当提高难度，引导更深入的思考。",
}


class DiagnosticTutorService:

    @staticmethod
    def _determine_phase(conversation: StudentConversation) -> TutorPhase:
        """根据对话状态确定当前阶段"""
        msgs = conversation.messages or []
        student_turns = [m for m in msgs if m.get("role") == "user"]
        turn_count = len(student_turns)
        diagnosis = conversation.diagnosis or {}

        if turn_count == 0:
            return TutorPhase.UNDERSTAND
        elif turn_count <= 1 and not diagnosis.get("identified"):
            return TutorPhase.DIAGNOSE
        elif diagnosis.get("identified") and not diagnosis.get("scaffolded"):
            return TutorPhase.SCAFFOLD
        elif diagnosis.get("scaffolded") and not diagnosis.get("understood"):
            return TutorPhase.EXPLAIN
        elif not diagnosis.get("verified"):
            return TutorPhase.VERIFY
        else:
            return TutorPhase.EXTEND

    @staticmethod
    async def _get_context(
        db: AsyncSession, user_id: int, knowledge_node_id: int
    ) -> Dict[str, Any]:
        """获取学生知识状态、情感、误解等上下文"""
        # 知识状态
        ks_result = await db.execute(
            select(StudentKnowledgeState).where(
                and_(
                    StudentKnowledgeState.user_id == user_id,
                    StudentKnowledgeState.knowledge_node_id == knowledge_node_id,
                )
            )
        )
        ks = ks_result.scalar_one_or_none()
        mastery = ks.mastery if ks else 0.0

        # 情感状态
        emotion = await EmotionService.get_current_emotion(db, user_id)
        emotion_type = emotion["emotion_type"] if emotion else "focus"
        emotion_intensity = emotion["intensity"] if emotion else 0.3

        # 已知误解
        misc_result = await db.execute(
            select(StudentMisconception).where(
                and_(
                    StudentMisconception.user_id == user_id,
                    StudentMisconception.knowledge_node_id == knowledge_node_id,
                    StudentMisconception.resolved == 0,
                )
            ).limit(5)
        )
        misconceptions = [m.misconception for m in misc_result.scalars().all()]

        # 知识节点信息
        node_result = await db.execute(
            select(KnowledgeNode).where(KnowledgeNode.id == knowledge_node_id)
        )
        node = node_result.scalar_one_or_none()
        node_title = node.name if node else "未知知识点"

        return {
            "mastery": mastery,
            "emotion_type": emotion_type,
            "emotion_intensity": emotion_intensity,
            "misconceptions": misconceptions,
            "node_title": node_title,
            "state_summary": f"掌握度 {mastery:.0%}, 练习 {ks.practice_count if ks else 0} 次, 连续正确 {ks.streak if ks else 0}",
            "emotion_summary": f"{emotion_type} (强度 {emotion_intensity:.1f})",
        }

    @staticmethod
    def _build_system_prompt(phase: TutorPhase, ctx: Dict[str, Any], conversation: StudentConversation) -> str:
        """根据阶段和上下文构建系统提示"""
        template = PHASE_PROMPTS[phase]
        emotion_guidance = EMOTION_GUIDANCE.get(ctx["emotion_type"], "")

        format_args = {
            "state_summary": ctx["state_summary"],
            "emotion_summary": ctx["emotion_summary"],
            "emotion_guidance": f"\n情感引导：{emotion_guidance}" if emotion_guidance else "",
            "mastery": ctx["mastery"],
            "known_misconceptions": "\n".join(f"- {m}" for m in ctx["misconceptions"]) if ctx["misconceptions"] else "暂无已知误解",
            "diagnosis": str(conversation.diagnosis) if conversation.diagnosis else "尚未诊断",
            "misconception": ctx["misconceptions"][0] if ctx["misconceptions"] else "未知",
            "node_title": ctx["node_title"],
        }

        base_prompt = "你是HERCU深度认知学习系统的诊断式AI私教。你的目标是通过苏格拉底式对话帮助学生真正理解知识，而不是直接给答案。\n\n"
        base_prompt += f"当前知识点：{ctx['node_title']}\n"
        base_prompt += f"对话阶段：{phase.value}\n\n"

        try:
            base_prompt += template.format(**format_args)
        except KeyError:
            base_prompt += template

        base_prompt += "\n\n回复要求：简洁、有针对性、用中文回答。每次回复控制在200字以内。"
        return base_prompt

    @staticmethod
    async def start_conversation(
        db: AsyncSession,
        user_id: int,
        knowledge_node_id: int,
        mode: str = "adaptive",
        initial_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """开始新的诊断式对话"""
        session_id = uuid.uuid4().hex[:16]
        ctx = await DiagnosticTutorService._get_context(db, user_id, knowledge_node_id)

        # 创建对话记录
        conv = StudentConversation(
            user_id=user_id,
            knowledge_node_id=knowledge_node_id,
            session_id=session_id,
            tutor_phase=TutorPhase.UNDERSTAND.value,
            messages=[],
            diagnosis={},
            emotion_snapshot=ctx["emotion_type"],
            mastery_before=ctx["mastery"],
            mode=mode,
            turn_count=0,
        )
        db.add(conv)
        await db.flush()

        # 如果有初始消息，直接处理第一轮
        if initial_message:
            return await DiagnosticTutorService._process_turn(db, conv, initial_message, ctx)

        # 否则生成欢迎消息
        welcome = f"你好！我是你的学习私教。关于「{ctx['node_title']}」，你有什么想问的吗？"
        if ctx["mastery"] < 0.3:
            welcome = f"你好！我注意到你在「{ctx['node_title']}」上还在起步阶段，我们一起来攻克它。有什么让你困惑的地方吗？"
        elif ctx["emotion_type"] == "frustration":
            welcome = f"嘿，别担心！「{ctx['node_title']}」确实有些挑战性。我们慢慢来，先告诉我哪里卡住了？"

        conv.messages = [{"role": "assistant", "content": welcome, "phase": TutorPhase.UNDERSTAND.value}]
        await db.flush()

        return {
            "session_id": session_id,
            "conversation_id": conv.id,
            "message": welcome,
            "phase": TutorPhase.UNDERSTAND.value,
            "emotion": ctx["emotion_type"],
            "mastery": ctx["mastery"],
        }

    @staticmethod
    async def send_message(
        db: AsyncSession,
        user_id: int,
        session_id: str,
        message: str,
    ) -> Dict[str, Any]:
        """在已有对话中发送消息"""
        result = await db.execute(
            select(StudentConversation).where(
                and_(
                    StudentConversation.user_id == user_id,
                    StudentConversation.session_id == session_id,
                )
            )
        )
        conv = result.scalar_one_or_none()
        if not conv:
            raise ValueError(f"对话 {session_id} 不存在")

        ctx = await DiagnosticTutorService._get_context(db, user_id, conv.knowledge_node_id)
        return await DiagnosticTutorService._process_turn(db, conv, message, ctx)

    @staticmethod
    async def _process_turn(
        db: AsyncSession,
        conv: StudentConversation,
        user_message: str,
        ctx: Dict[str, Any],
    ) -> Dict[str, Any]:
        """处理一轮对话"""
        # 追加用户消息
        msgs = list(conv.messages or [])
        msgs.append({"role": "user", "content": user_message, "phase": conv.tutor_phase})
        conv.messages = msgs
        conv.turn_count = (conv.turn_count or 0) + 1

        # 确定当前阶段
        phase = DiagnosticTutorService._determine_phase(conv)
        conv.tutor_phase = phase.value

        # 构建系统提示
        system_prompt = DiagnosticTutorService._build_system_prompt(phase, ctx, conv)

        # 构建LLM消息历史
        llm_messages = []
        for m in msgs:
            role = "user" if m["role"] == "user" else "assistant"
            llm_messages.append(Message(role=role, content=m["content"]))

        # 调用LLM
        llm = get_llm_service()
        response_text = await llm.generate_tutor_response(
            user_message=user_message,
            context={"system_prompt_override": system_prompt},
            conversation_history=llm_messages[:-1],  # 不含最后一条用户消息
        )

        # 追加助手回复
        msgs.append({"role": "assistant", "content": response_text, "phase": phase.value})
        conv.messages = msgs

        # 阶段转换逻辑：根据轮次自动推进诊断状态
        diagnosis = dict(conv.diagnosis or {})
        if phase == TutorPhase.DIAGNOSE and conv.turn_count >= 2:
            diagnosis["identified"] = True
        elif phase == TutorPhase.SCAFFOLD and conv.turn_count >= 4:
            diagnosis["scaffolded"] = True
        elif phase == TutorPhase.EXPLAIN and conv.turn_count >= 5:
            diagnosis["understood"] = True
        elif phase == TutorPhase.VERIFY and conv.turn_count >= 6:
            diagnosis["verified"] = True
            conv.resolved = True
        conv.diagnosis = diagnosis

        await db.flush()

        return {
            "session_id": conv.session_id,
            "conversation_id": conv.id,
            "message": response_text,
            "phase": phase.value,
            "turn_count": conv.turn_count,
            "emotion": ctx["emotion_type"],
            "mastery": ctx["mastery"],
            "resolved": conv.resolved or False,
        }

    @staticmethod
    async def get_conversation(
        db: AsyncSession, user_id: int, session_id: str
    ) -> Optional[Dict[str, Any]]:
        """获取对话详情"""
        result = await db.execute(
            select(StudentConversation).where(
                and_(
                    StudentConversation.user_id == user_id,
                    StudentConversation.session_id == session_id,
                )
            )
        )
        conv = result.scalar_one_or_none()
        if not conv:
            return None
        return {
            "conversation_id": conv.id,
            "session_id": conv.session_id,
            "knowledge_node_id": conv.knowledge_node_id,
            "phase": conv.tutor_phase,
            "messages": conv.messages,
            "diagnosis": conv.diagnosis,
            "mode": conv.mode,
            "turn_count": conv.turn_count,
            "resolved": conv.resolved,
            "mastery_before": conv.mastery_before,
            "mastery_after": conv.mastery_after,
            "created_at": conv.created_at,
        }

    @staticmethod
    async def get_conversation_history(
        db: AsyncSession, user_id: int, knowledge_node_id: Optional[int] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取对话历史列表"""
        query = select(StudentConversation).where(
            StudentConversation.user_id == user_id
        )
        if knowledge_node_id:
            query = query.where(StudentConversation.knowledge_node_id == knowledge_node_id)
        query = query.order_by(desc(StudentConversation.created_at)).limit(limit)

        result = await db.execute(query)
        convs = result.scalars().all()
        return [
            {
                "conversation_id": c.id,
                "session_id": c.session_id,
                "knowledge_node_id": c.knowledge_node_id,
                "phase": c.tutor_phase,
                "mode": c.mode,
                "turn_count": c.turn_count,
                "resolved": c.resolved,
                "created_at": c.created_at,
            }
            for c in convs
        ]
