"""
用户特征分析服务
基于AI对话历史分析用户学习特征并生成画像
"""

import json
from typing import List, Dict, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.models import User, ChatHistory, UserProfile, LearningProgress, CourseNode
from app.services.llm_factory import get_llm_service, Message


class UserProfileService:
    """用户特征分析服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.claude = get_llm_service()

    async def analyze_user_profile(self, user_id: int, force_update: bool = False) -> Optional[Dict]:
        """
        分析用户特征并更新画像

        Args:
            user_id: 用户ID
            force_update: 是否强制更新（忽略已分析的消息数）

        Returns:
            用户画像数据
        """
        # 获取用户
        user_result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            return None

        # 获取现有画像
        profile_result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        existing_profile = profile_result.scalar_one_or_none()

        # 获取用户的所有对话历史
        chat_result = await self.db.execute(
            select(ChatHistory)
            .where(ChatHistory.user_id == user_id)
            .order_by(ChatHistory.created_at.desc())
            .limit(200)  # 最多分析最近200条消息
        )
        chat_messages = chat_result.scalars().all()

        if not chat_messages:
            return None

        # 检查是否需要更新
        total_messages = len(chat_messages)
        if existing_profile and not force_update:
            if existing_profile.messages_analyzed >= total_messages:
                # 没有新消息，返回现有画像
                return self._profile_to_dict(existing_profile)

        # 获取用户学习进度信息
        progress_data = await self._get_user_progress_summary(user_id)

        # 构建对话文本用于分析
        conversation_text = self._build_conversation_text(chat_messages)

        # 调用AI分析
        analysis_result = await self._analyze_with_ai(
            conversation_text,
            progress_data,
            user.username
        )

        if not analysis_result:
            return None

        # 更新或创建画像
        if existing_profile:
            profile = existing_profile
        else:
            profile = UserProfile(user_id=user_id)
            self.db.add(profile)

        # 更新画像字段
        profile.learning_style = analysis_result.get("learning_style")
        profile.knowledge_levels = analysis_result.get("knowledge_levels")
        profile.interests = analysis_result.get("interests")
        profile.strengths = analysis_result.get("strengths")
        profile.weaknesses = analysis_result.get("weaknesses")
        profile.communication_style = analysis_result.get("communication_style")
        profile.engagement_level = analysis_result.get("engagement_level")
        profile.question_patterns = analysis_result.get("question_patterns")
        profile.learning_pace = analysis_result.get("learning_pace")
        profile.personality_traits = analysis_result.get("personality_traits")
        profile.recommended_approach = analysis_result.get("recommended_approach")
        profile.analysis_summary = analysis_result.get("analysis_summary")
        profile.messages_analyzed = total_messages
        profile.last_analyzed_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(profile)

        return self._profile_to_dict(profile)

    async def get_user_profile(self, user_id: int) -> Optional[Dict]:
        """获取用户画像（不触发分析）"""
        profile_result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        profile = profile_result.scalar_one_or_none()

        if not profile:
            return None

        return self._profile_to_dict(profile)

    async def _get_user_progress_summary(self, user_id: int) -> Dict:
        """获取用户学习进度摘要"""
        # 获取完成的节点数
        completed_query = select(func.count(LearningProgress.id)).where(
            LearningProgress.user_id == user_id,
            LearningProgress.status == "completed"
        )
        completed_count = await self.db.scalar(completed_query) or 0

        # 获取总学习时间
        time_query = select(func.sum(LearningProgress.time_spent_seconds)).where(
            LearningProgress.user_id == user_id
        )
        total_time = await self.db.scalar(time_query) or 0

        # 获取学习的课程节点类型分布
        type_query = select(
            CourseNode.type,
            func.count(LearningProgress.id)
        ).join(
            CourseNode, LearningProgress.node_id == CourseNode.id
        ).where(
            LearningProgress.user_id == user_id
        ).group_by(CourseNode.type)

        type_result = await self.db.execute(type_query)
        type_distribution = {str(row[0]): row[1] for row in type_result.all()}

        return {
            "completed_nodes": completed_count,
            "total_time_hours": round(total_time / 3600, 1),
            "node_type_distribution": type_distribution
        }

    def _build_conversation_text(self, messages: List[ChatHistory]) -> str:
        """构建对话文本"""
        conversations = []
        for msg in reversed(messages):  # 按时间正序
            role_label = "用户" if msg.role == "user" else "AI导师"
            conversations.append(f"{role_label}: {msg.content}")

        return "\n".join(conversations)

    async def _analyze_with_ai(
        self,
        conversation_text: str,
        progress_data: Dict,
        username: str
    ) -> Optional[Dict]:
        """使用AI分析用户特征"""
        system_prompt = """你是一位专业的学习分析师，擅长从对话中分析学习者的特征和模式。
请基于提供的对话历史和学习数据，分析用户的学习特征。

你需要输出一个JSON格式的分析结果，包含以下字段：

{
    "learning_style": {
        "visual": 0.0-1.0,      // 视觉学习偏好
        "auditory": 0.0-1.0,    // 听觉学习偏好
        "reading": 0.0-1.0,     // 阅读学习偏好
        "kinesthetic": 0.0-1.0  // 动手实践偏好
    },
    "knowledge_levels": {
        "领域名称": "beginner/intermediate/advanced"
    },
    "interests": ["兴趣1", "兴趣2"],
    "strengths": ["优势1", "优势2"],
    "weaknesses": ["待改进1", "待改进2"],
    "communication_style": "detailed/concise/questioning/passive",
    "engagement_level": "high/medium/low",
    "question_patterns": {
        "clarification": 数量,    // 澄清类问题
        "deep_dive": 数量,        // 深入探究类
        "practical": 数量,        // 实践应用类
        "conceptual": 数量        // 概念理解类
    },
    "learning_pace": "fast/moderate/slow",
    "personality_traits": ["特质1", "特质2"],
    "recommended_approach": "针对该用户的教学建议（一段话）",
    "analysis_summary": "用户特征总结（一段话）"
}

注意：
1. 所有分析必须基于实际对话内容，不要臆测
2. 如果某些特征无法从对话中判断，可以设为null或空数组
3. 分析要客观、专业，避免过度解读
4. 只输出JSON，不要有其他内容"""

        user_prompt = f"""请分析以下用户的学习特征：

用户名：{username}

学习数据：
- 已完成节点数：{progress_data['completed_nodes']}
- 总学习时长：{progress_data['total_time_hours']} 小时
- 学习内容类型分布：{json.dumps(progress_data['node_type_distribution'], ensure_ascii=False)}

对话历史（最近的对话）：
---
{conversation_text[:8000]}
---

请输出JSON格式的分析结果："""

        try:
            response = await self.claude.chat_completion(
                messages=[Message(role="user", content=user_prompt)],
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=2000
            )

            response_text = response["content"][0]["text"]

            # 提取JSON
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)

            return None

        except Exception as e:
            print(f"AI analysis failed: {e}")
            return None

    def _profile_to_dict(self, profile: UserProfile) -> Dict:
        """将画像模型转换为字典"""
        return {
            "id": profile.id,
            "user_id": profile.user_id,
            "learning_style": profile.learning_style,
            "knowledge_levels": profile.knowledge_levels,
            "interests": profile.interests,
            "strengths": profile.strengths,
            "weaknesses": profile.weaknesses,
            "communication_style": profile.communication_style,
            "engagement_level": profile.engagement_level,
            "question_patterns": profile.question_patterns,
            "learning_pace": profile.learning_pace,
            "personality_traits": profile.personality_traits,
            "recommended_approach": profile.recommended_approach,
            "analysis_summary": profile.analysis_summary,
            "messages_analyzed": profile.messages_analyzed,
            "last_analyzed_at": profile.last_analyzed_at.isoformat() if profile.last_analyzed_at else None,
            "created_at": profile.created_at.isoformat() if profile.created_at else None,
            "updated_at": profile.updated_at.isoformat() if profile.updated_at else None
        }


async def get_user_profile_service(db: AsyncSession) -> UserProfileService:
    """获取用户画像服务实例"""
    return UserProfileService(db)
