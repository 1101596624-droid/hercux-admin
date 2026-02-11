"""
AI Tutor Service with Learning Integration

Main service layer that integrates dialogue generation with learning capabilities.
Provides enhanced chat functionality that learns from past high-quality interactions.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import json

from app.services.ai_tutor.dialogue_generator import DialogueGenerator
from app.services.deepseek_service import get_deepseek_service, Message


class AITutorService:
    """AI Tutor service with learning integration"""

    def __init__(self, db: Session):
        self.db = db
        self.dialogue_generator = DialogueGenerator(db)
        self.deepseek = get_deepseek_service()

    async def generate_enhanced_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        node_info: Dict[str, Any],
        subject: str,
        topic: str,
        base_system_prompt: Optional[str] = None,
    ) -> str:
        """
        Generate AI tutor response with learning-enhanced prompt

        Args:
            user_message: User's message
            conversation_history: Previous dialogue messages
            node_info: Node information (title, objectives, etc.)
            subject: Subject area (e.g., "biomechanics")
            topic: Specific topic (e.g., "joint_mechanics")
            base_system_prompt: Base system prompt (optional)

        Returns:
            AI-generated response
        """
        # Build base system prompt if not provided
        if not base_system_prompt:
            base_system_prompt = self._build_base_system_prompt(node_info)

        # Enhance system prompt with learning context
        enhanced_prompt = await self.dialogue_generator.enhance_system_prompt(
            base_prompt=base_system_prompt,
            subject=subject,
            topic=topic,
            min_quality=85.0,
        )

        # Prepare messages for LLM
        messages = [Message(role="system", content=enhanced_prompt)]

        # Add conversation history
        for msg in conversation_history:
            messages.append(Message(role=msg["role"], content=msg["content"]))

        # Add current user message
        messages.append(Message(role="user", content=user_message))

        # Generate response
        response = await self.deepseek.chat_completion(messages)
        response_text = response["choices"][0]["message"]["content"]

        return response_text

    async def evaluate_dialogue_session(
        self,
        dialogue: List[Dict[str, str]],
        subject: str,
        topic: str,
        node_id: int,
    ) -> Dict[str, Any]:
        """
        Evaluate a completed dialogue session and save if high quality

        Args:
            dialogue: Complete dialogue history
            subject: Subject area
            topic: Specific topic
            node_id: Course node ID

        Returns:
            Evaluation results with quality scores and insights
        """
        return await self.dialogue_generator.evaluate_and_save_dialogue(
            dialogue=dialogue,
            subject=subject,
            topic=topic,
            node_id=node_id,
            save_threshold=85.0,
        )

    async def get_learning_insights(
        self,
        subject: str,
        topic: str,
    ) -> Dict[str, Any]:
        """
        Get learning insights for a specific topic

        Args:
            subject: Subject area
            topic: Specific topic

        Returns:
            Insights from high-quality past dialogues
        """
        return await self.dialogue_generator.get_dialogue_insights(
            subject=subject,
            topic=topic,
        )

    def _build_base_system_prompt(self, node_info: Dict[str, Any]) -> str:
        """
        Build base system prompt from node information

        Args:
            node_info: Node metadata

        Returns:
            Base system prompt
        """
        title = node_info.get("title", "this topic")
        objectives = node_info.get("learning_objectives", [])

        objectives_text = "\n".join([f"- {obj}" for obj in objectives]) if objectives else "N/A"

        prompt = f"""You are an expert AI tutor helping students learn about "{title}".

Learning Objectives:
{objectives_text}

# YOUR ROLE
- Guide students through questions and explanations
- Adapt to their understanding level
- Use examples and analogies
- Encourage critical thinking
- Provide constructive feedback

# TEACHING STRATEGIES
- Ask guiding questions to assess understanding
- Break complex concepts into digestible parts
- Use real-world examples and analogies
- Encourage students to explain concepts in their own words
- Provide positive reinforcement and encouragement

# COMMUNICATION STYLE
- Be conversational and engaging
- Use clear, accessible language
- Show empathy and patience
- Celebrate student progress
"""

        return prompt

    async def generate_welcome_message(
        self,
        node_info: Dict[str, Any],
        subject: str,
        topic: str,
    ) -> str:
        """
        Generate a personalized welcome message with learning context

        Args:
            node_info: Node metadata
            subject: Subject area
            topic: Specific topic

        Returns:
            Welcome message
        """
        # Check if we have learning insights
        insights = await self.get_learning_insights(subject, topic)

        title = node_info.get("title", "this lesson")

        if insights["template_count"] > 0:
            # We have past high-quality dialogues to learn from
            best_practices = insights.get("best_practices", [])
            practice_hint = best_practices[0] if best_practices else ""

            welcome = f"""欢迎学习「{title}」!👋

我是你的AI导师,已经从{insights['template_count']}个高质量对话中学习了最佳教学方法。

{practice_hint if practice_hint else '有任何问题随时问我,我会用最有效的方式帮助你理解。'}

你想从哪里开始?"""
        else:
            # First time teaching this topic
            welcome = f"""欢迎学习「{title}」!👋

我是你的AI导师,我会通过对话引导你深入理解这个主题。

有任何问题随时问我,让我们一起探索吧!"""

        return welcome
