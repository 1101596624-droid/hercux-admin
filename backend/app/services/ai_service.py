"""
AI Service - Claude API Integration
Implements the "AI Muscles" for Socratic guidance and training plan generation
"""
from typing import List, Dict, Optional, Any
from anthropic import AsyncAnthropic
from app.core.config import settings
from app.models.models import CourseNode, ChatHistory
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
import json
import re
import logging

logger = logging.getLogger(__name__)


def get_enum_value(enum_obj) -> str:
    """Get value from enum or string"""
    if enum_obj is None:
        return None
    return enum_obj.value if hasattr(enum_obj, 'value') else enum_obj


class AIService:
    """Service for AI-powered features using Claude API"""

    def __init__(self, db: AsyncSession):
        self.db = db
        # Use configured base URL for API proxy support
        base_url = getattr(settings, 'ANTHROPIC_BASE_URL', None)
        if base_url:
            self.client = AsyncAnthropic(
                api_key=settings.ANTHROPIC_API_KEY,
                base_url=base_url
            )
        else:
            self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-3-5-sonnet-20241022"  # Latest Claude model
        self.max_retries = 3
        self.timeout = 120  # Increased timeout for training plan generation

    async def guide_chat(
        self,
        user_id: int,
        node_id: int,
        user_message: str,
        node_context: Optional[Dict] = None
    ) -> str:
        """
        AI tutor conversation with Socratic guidance
        Used in the right sidebar of the Learning Workstation

        Args:
            user_id: User ID
            node_id: Current course node ID
            user_message: User's question/message
            node_context: Additional context (simulator state, video timestamp, etc.)

        Returns:
            AI assistant's response
        """
        # Get conversation history
        history = await self._get_chat_history(user_id, node_id, limit=10)

        # Get node information for context
        node = await self.db.get(CourseNode, node_id)
        if not node:
            return "抱歉，无法找到当前课程节点信息。"

        # Build system prompt with node context
        system_prompt = self._build_guide_system_prompt(node, node_context)

        # Build message history
        messages = []
        for msg in history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })

        # Call Claude API
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=messages
            )

            assistant_message = response.content[0].text

            # Save conversation to database
            await self._save_chat_message(user_id, node_id, "user", user_message)
            await self._save_chat_message(user_id, node_id, "assistant", assistant_message)

            return assistant_message

        except Exception as e:
            print(f"Claude API error: {e}")
            return "抱歉，AI 导师暂时无法响应。请稍后再试。"

    async def generate_training_plan(
        self,
        user_id: int,
        role: str,
        goal: str,
        weeks: int,
        sessions_per_week: int,
        experience_level: str,
        available_equipment: List[str],
        constraints: Optional[str] = None
    ) -> Dict:
        """
        Generate a structured training plan using Claude

        Args:
            user_id: User ID
            role: User's role (e.g., "运动员", "教练")
            goal: Training goal (e.g., "提高爆发力")
            weeks: Plan duration in weeks
            sessions_per_week: Training sessions per week
            experience_level: "beginner", "intermediate", "advanced"
            available_equipment: List of available equipment
            constraints: Additional constraints (injuries, time limits, etc.)

        Returns:
            Structured training plan as JSON
        """
        system_prompt = """你是一位专业的运动训练计划生成专家。你需要根据用户的需求生成一个结构化的训练计划。

计划必须包含以下结构：
1. 周期划分（Periodization）：GPP（一般准备期）、SPP（专项准备期）、赛前期、恢复期
2. 每周计划：包含周目标、训练重点、强度分配
3. 每日课表：具体的训练动作、组数、次数、休息时间、负荷、RPE

请以 JSON 格式返回，结构如下：
{
  "title": "训练计划标题",
  "duration_weeks": 12,
  "periods": [
    {
      "name": "GPP - 一般准备期",
      "weeks": [1, 2, 3, 4],
      "focus": "建立基础体能",
      "intensity": "中等"
    }
  ],
  "weekly_plans": [
    {
      "week": 1,
      "goal": "适应训练负荷",
      "distribution": {
        "strength": 40,
        "endurance": 30,
        "speed": 20,
        "recovery": 10
      },
      "sessions": [
        {
          "day": 1,
          "type": "力量训练",
          "exercises": [
            {
              "name": "深蹲",
              "sets": 4,
              "reps": "8-10",
              "rest": "2分钟",
              "load": "70% 1RM",
              "rpe": 7
            }
          ]
        }
      ]
    }
  ]
}

请确保计划科学合理，符合运动训练学原理。只返回JSON，不要添加其他文字说明。"""

        user_prompt = f"""请为我生成一个训练计划：

角色：{role}
目标：{goal}
时长：{weeks} 周
每周训练：{sessions_per_week} 次
经验水平：{experience_level}
可用器材：{', '.join(available_equipment)}
{f'特殊要求：{constraints}' if constraints else ''}

请生成详细的训练计划。"""

        # Call Claude API with retry
        plan_text = await self._call_claude_with_retry(
            system_prompt=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            max_tokens=4096
        )

        if not plan_text:
            logger.error("Failed to generate training plan after retries")
            return self._create_fallback_plan(goal, weeks, sessions_per_week)

        # Extract JSON from response
        plan_json = self._extract_json_from_text(plan_text)

        if not plan_json:
            logger.warning("Failed to extract JSON from AI response")
            return self._create_fallback_plan(goal, weeks, sessions_per_week, plan_text)

        # Validate plan structure
        is_valid, error_msg = self._validate_training_plan(plan_json)

        if not is_valid:
            logger.warning(f"Invalid training plan structure: {error_msg}")
            # Try to fix common issues
            if "duration_weeks" not in plan_json:
                plan_json["duration_weeks"] = weeks
            if "title" not in plan_json:
                plan_json["title"] = f"{goal} - {weeks}周训练计划"

            # Re-validate
            is_valid, _ = self._validate_training_plan(plan_json)
            if not is_valid:
                return self._create_fallback_plan(goal, weeks, sessions_per_week, plan_text)

        # Add metadata
        plan_json["generated_at"] = datetime.now(timezone.utc).isoformat()
        plan_json["user_id"] = user_id
        plan_json["status"] = "success"

        return plan_json

    async def adjust_training_plan(
        self,
        plan_id: int,
        current_plan: Dict,
        adjustment_request: str
    ) -> Dict:
        """
        Adjust an existing training plan based on natural language request

        Args:
            plan_id: Training plan ID
            current_plan: Current plan JSON
            adjustment_request: Natural language adjustment (e.g., "把周三改成恢复日")

        Returns:
            Updated plan JSON
        """
        system_prompt = """你是一位训练计划调整助手。用户会提供当前的训练计划和调整需求，你需要：
1. 理解用户的调整意图
2. 修改计划的相应部分
3. 确保修改后的计划仍然科学合理
4. 返回完整的更新后的计划 JSON

请只返回 JSON，不要添加额外的解释文字。"""

        user_prompt = f"""当前训练计划：
```json
{json.dumps(current_plan, ensure_ascii=False, indent=2)}
```

调整需求：{adjustment_request}

请返回调整后的完整计划 JSON。"""

        # Call Claude API with retry
        plan_text = await self._call_claude_with_retry(
            system_prompt=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            max_tokens=4096
        )

        if not plan_text:
            logger.error("Failed to adjust training plan after retries")
            return current_plan  # Return original plan if adjustment fails

        # Extract JSON from response
        updated_plan = self._extract_json_from_text(plan_text)

        if not updated_plan:
            logger.warning("Failed to extract JSON from adjustment response")
            return current_plan

        # Validate adjusted plan
        is_valid, error_msg = self._validate_training_plan(updated_plan)

        if not is_valid:
            logger.warning(f"Invalid adjusted plan structure: {error_msg}")
            return current_plan

        # Add adjustment metadata
        updated_plan["last_adjusted"] = datetime.now(timezone.utc).isoformat()
        updated_plan["adjustment_request"] = adjustment_request

        return updated_plan

    def _build_guide_system_prompt(
        self,
        node: CourseNode,
        context: Optional[Dict] = None
    ) -> str:
        """Build system prompt for AI guide based on node context"""

        base_prompt = f"""你是 HERCU 学习平台的 AI 导师。你的角色是通过苏格拉底式提问引导学生深入思考，而不是直接给出答案。

当前课程节点信���：
- 标题：{node.title}
- 类型：{get_enum_value(node.type)}
- 描述：{node.description or '无'}

教学原则：
1. 使用苏格拉底式提问法：通过问题引导学生自己发现答案
2. 不要直接给出答案，而是引导学生思考
3. 根据学生的回答调整问题难度
4. 鼓励学生观察、实验、推理
5. 当学生遇到困难时，提供渐进式的提示
6. 使用简洁、友好的语言

"""

        # Add node-specific context
        if node.timeline_config and "guidePrompt" in node.timeline_config:
            base_prompt += f"\n课程设计者的引导建议：{node.timeline_config['guidePrompt']}\n"

        # Add runtime context (simulator state, video position, etc.)
        if context:
            if "simulator_state" in context:
                base_prompt += f"\n当前模拟器状态：{context['simulator_state']}\n"
            if "video_timestamp" in context:
                base_prompt += f"\n当前视频时间：{context['video_timestamp']} 秒\n"
            if "quiz_attempt" in context:
                base_prompt += f"\n学生的答题尝试：{context['quiz_attempt']}\n"

        return base_prompt

    async def _get_chat_history(
        self,
        user_id: int,
        node_id: int,
        limit: int = 10
    ) -> List[ChatHistory]:
        """Get recent chat history for a node"""
        from sqlalchemy import select, and_

        stmt = select(ChatHistory).where(
            and_(
                ChatHistory.user_id == user_id,
                ChatHistory.node_id == node_id
            )
        ).order_by(ChatHistory.created_at.desc()).limit(limit)

        result = await self.db.execute(stmt)
        history = result.scalars().all()

        # Reverse to get chronological order
        return list(reversed(history))

    async def _save_chat_message(
        self,
        user_id: int,
        node_id: int,
        role: str,
        content: str
    ):
        """Save a chat message to database"""
        message = ChatHistory(
            user_id=user_id,
            node_id=node_id,
            role=role,
            content=content,
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(message)
        await self.db.commit()

    def _extract_json_from_text(self, text: str) -> Optional[Dict]:
        """
        Extract JSON from text response
        Handles cases where Claude wraps JSON in markdown code blocks
        """
        # Try to find JSON in markdown code blocks
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, text, re.DOTALL)

        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to find raw JSON
        start_idx = text.find('{')
        end_idx = text.rfind('}') + 1

        if start_idx != -1 and end_idx > start_idx:
            try:
                return json.loads(text[start_idx:end_idx])
            except json.JSONDecodeError:
                pass

        return None

    def _validate_training_plan(self, plan: Dict) -> tuple[bool, Optional[str]]:
        """
        Validate training plan structure

        Returns:
            (is_valid, error_message)
        """
        required_fields = ["title", "duration_weeks"]

        for field in required_fields:
            if field not in plan:
                return False, f"Missing required field: {field}"

        # Validate duration_weeks is a number
        if not isinstance(plan.get("duration_weeks"), (int, float)):
            return False, "duration_weeks must be a number"

        # Validate periods structure if present
        if "periods" in plan:
            if not isinstance(plan["periods"], list):
                return False, "periods must be a list"

            for period in plan["periods"]:
                if not isinstance(period, dict):
                    return False, "Each period must be an object"
                if "name" not in period or "weeks" not in period:
                    return False, "Each period must have 'name' and 'weeks'"

        # Validate weekly_plans structure if present
        if "weekly_plans" in plan:
            if not isinstance(plan["weekly_plans"], list):
                return False, "weekly_plans must be a list"

            for week_plan in plan["weekly_plans"]:
                if not isinstance(week_plan, dict):
                    return False, "Each weekly plan must be an object"
                if "week" not in week_plan:
                    return False, "Each weekly plan must have 'week' field"

        return True, None

    def _create_fallback_plan(
        self,
        goal: str,
        weeks: int,
        sessions_per_week: int,
        raw_text: Optional[str] = None
    ) -> Dict:
        """
        Create a fallback training plan when AI generation fails
        """
        return {
            "title": f"{goal} - {weeks}周训练计划",
            "duration_weeks": weeks,
            "sessions_per_week": sessions_per_week,
            "status": "fallback",
            "message": "AI生成的计划格式不完整，已创建基础计划框架",
            "raw_plan": raw_text,
            "periods": [
                {
                    "name": "训练周期",
                    "weeks": list(range(1, weeks + 1)),
                    "focus": goal,
                    "intensity": "根据个人情况调整"
                }
            ],
            "weekly_plans": [
                {
                    "week": i,
                    "goal": f"第{i}周训练",
                    "sessions": []
                }
                for i in range(1, min(weeks + 1, 5))  # Only create first 4 weeks as template
            ]
        }

    async def _call_claude_with_retry(
        self,
        system_prompt: str,
        messages: List[Dict],
        max_tokens: int = 1024
    ) -> Optional[str]:
        """
        Call Claude API with retry logic and error handling

        Returns:
            Response text or None if all retries fail
        """
        for attempt in range(self.max_retries):
            try:
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    system=system_prompt,
                    messages=messages,
                    timeout=self.timeout
                )

                return response.content[0].text

            except Exception as e:
                logger.error(f"Claude API error (attempt {attempt + 1}/{self.max_retries}): {e}")

                if attempt == self.max_retries - 1:
                    # Last attempt failed
                    return None

                # Wait before retry (exponential backoff)
                import asyncio
                await asyncio.sleep(2 ** attempt)

        return None
