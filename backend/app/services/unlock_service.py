"""
Node Unlock Service - Rule-based Control System (RCS)
Implements the deterministic logic for node unlocking and progress tracking
"""
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.models import CourseNode, LearningProgress, NodeStatus, User
from app.core.utils import get_enum_value
from datetime import datetime, timezone
import json


def parse_json_field(value) -> dict:
    """Parse JSON field from database - handles both dict and JSON string formats"""
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    return {}


class UnlockService:
    """Service for managing node unlock logic"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_unlock_condition(
        self,
        node: CourseNode,
        user_id: int
    ) -> tuple[bool, Optional[str]]:
        """
        Check if a node can be unlocked for a user

        Returns:
            (can_unlock: bool, reason: Optional[str])
        """
        if not node.unlock_condition:
            # No condition means always unlocked
            return True, None

        # Parse unlock_condition if it's a JSON string
        unlock_condition = parse_json_field(node.unlock_condition)
        condition_type = unlock_condition.get("type")

        if condition_type == "none":
            return True, None

        if condition_type == "previous_complete":
            # Find previous sibling node
            prev_node = await self._find_previous_sibling(node)
            if not prev_node:
                # First node in sequence
                return True, None

            # Check if previous node is completed
            prev_progress = await self._get_progress(user_id, prev_node.id)
            if prev_progress and get_enum_value(prev_progress.status) == NodeStatus.COMPLETED.value:
                return True, None
            else:
                return False, f"需要先完成: {prev_node.title}"

        if condition_type == "manual":
            # Manual unlock (e.g., premium content)
            return False, "此内容需要手动解锁"

        if condition_type == "prerequisites":
            # Check multiple prerequisite nodes
            prereq_node_ids = unlock_condition.get("node_ids", [])
            for prereq_id in prereq_node_ids:
                prereq_progress = await self._get_progress(user_id, prereq_id)
                if not prereq_progress or get_enum_value(prereq_progress.status) != NodeStatus.COMPLETED.value:
                    prereq_node = await self.db.get(CourseNode, prereq_id)
                    return False, f"需要先完成前置课程: {prereq_node.title if prereq_node else '未知'}"
            return True, None

        # Unknown condition type
        return False, "未知的解锁条件"

    async def unlock_node(self, user_id: int, node_id: int) -> bool:
        """
        Attempt to unlock a node for a user

        Returns:
            True if unlocked successfully, False otherwise
        """
        node = await self.db.get(CourseNode, node_id)
        if not node:
            return False

        can_unlock, reason = await self.check_unlock_condition(node, user_id)
        if not can_unlock:
            return False

        # Get or create progress record
        progress = await self._get_progress(user_id, node_id)
        if not progress:
            progress = LearningProgress(
                user_id=user_id,
                node_id=node_id,
                status=NodeStatus.UNLOCKED,
                last_accessed=datetime.now(timezone.utc)
            )
            self.db.add(progress)
        elif get_enum_value(progress.status) == NodeStatus.LOCKED.value:
            progress.status = NodeStatus.UNLOCKED
            progress.last_accessed = datetime.now(timezone.utc)

        await self.db.commit()
        return True

    async def complete_node(self, user_id: int, node_id: int) -> List[int]:
        """
        Mark a node as completed and unlock dependent nodes

        Returns:
            List of newly unlocked node IDs
        """
        # Update current node status
        progress = await self._get_progress(user_id, node_id)
        if not progress:
            progress = LearningProgress(
                user_id=user_id,
                node_id=node_id,
                status=NodeStatus.COMPLETED,
                completion_percentage=100.0,
                completed_at=datetime.now(timezone.utc)
            )
            self.db.add(progress)
        else:
            progress.status = NodeStatus.COMPLETED
            progress.completion_percentage = 100.0
            progress.completed_at = datetime.now(timezone.utc)

        await self.db.commit()

        # Find and unlock dependent nodes
        newly_unlocked = await self._unlock_dependent_nodes(user_id, node_id)

        return newly_unlocked

    async def _unlock_dependent_nodes(self, user_id: int, completed_node_id: int) -> List[int]:
        """
        Find and unlock nodes that depend on the completed node

        Returns:
            List of newly unlocked node IDs
        """
        completed_node = await self.db.get(CourseNode, completed_node_id)
        if not completed_node:
            return []

        newly_unlocked = []

        # Strategy 1: Unlock next sibling (same parent, next sequence)
        next_sibling = await self._find_next_sibling(completed_node)
        if next_sibling:
            unlocked = await self.unlock_node(user_id, next_sibling.id)
            if unlocked:
                newly_unlocked.append(next_sibling.id)

        # Strategy 2: Unlock first child (if this is a chapter node)
        if completed_node.children:
            first_child = min(completed_node.children, key=lambda n: n.sequence)
            unlocked = await self.unlock_node(user_id, first_child.id)
            if unlocked:
                newly_unlocked.append(first_child.id)

        # Strategy 3: Find nodes that explicitly list this as a prerequisite
        stmt = select(CourseNode).where(CourseNode.course_id == completed_node.course_id)
        result = await self.db.execute(stmt)
        all_nodes = result.scalars().all()

        for node in all_nodes:
            if node.unlock_condition and node.unlock_condition.get("type") == "prerequisites":
                prereq_ids = node.unlock_condition.get("node_ids", [])
                if completed_node_id in prereq_ids:
                    # Check if all prerequisites are now met
                    can_unlock, _ = await self.check_unlock_condition(node, user_id)
                    if can_unlock:
                        unlocked = await self.unlock_node(user_id, node.id)
                        if unlocked:
                            newly_unlocked.append(node.id)

        return newly_unlocked

    async def _find_previous_sibling(self, node: CourseNode) -> Optional[CourseNode]:
        """Find the previous sibling node (same parent, lower sequence)"""
        stmt = select(CourseNode).where(
            and_(
                CourseNode.course_id == node.course_id,
                CourseNode.parent_id == node.parent_id,
                CourseNode.sequence < node.sequence
            )
        ).order_by(CourseNode.sequence.desc())

        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def _find_next_sibling(self, node: CourseNode) -> Optional[CourseNode]:
        """Find the next sibling node (same parent, higher sequence)"""
        stmt = select(CourseNode).where(
            and_(
                CourseNode.course_id == node.course_id,
                CourseNode.parent_id == node.parent_id,
                CourseNode.sequence > node.sequence
            )
        ).order_by(CourseNode.sequence.asc())

        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def _get_progress(self, user_id: int, node_id: int) -> Optional[LearningProgress]:
        """Get user's progress for a specific node"""
        stmt = select(LearningProgress).where(
            and_(
                LearningProgress.user_id == user_id,
                LearningProgress.node_id == node_id
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_course_progress_map(
        self,
        user_id: int,
        course_id: int
    ) -> Dict[int, Dict]:
        """
        Get a complete progress map for all nodes in a course
        Used by the left sidebar (Cognitive Map)

        Returns:
            Dict mapping node_id to progress info
        """
        # Get all nodes for the course
        stmt = select(CourseNode).where(CourseNode.course_id == course_id)
        result = await self.db.execute(stmt)
        nodes = result.scalars().all()

        # Get all progress records for this user and course
        node_ids = [node.id for node in nodes]
        progress_stmt = select(LearningProgress).where(
            and_(
                LearningProgress.user_id == user_id,
                LearningProgress.node_id.in_(node_ids)
            )
        )
        progress_result = await self.db.execute(progress_stmt)
        progress_records = progress_result.scalars().all()

        # Build progress map
        progress_map = {}
        for progress in progress_records:
            # Handle both enum and string status values
            status_value = progress.status.value if hasattr(progress.status, 'value') else progress.status
            progress_map[progress.node_id] = {
                "status": status_value,
                "completion_percentage": progress.completion_percentage,
                "last_accessed": progress.last_accessed,
                "completed_at": progress.completed_at
            }

        # Fill in missing nodes with locked status
        for node in nodes:
            if node.id not in progress_map:
                # Check if node should be unlocked by default
                can_unlock, _ = await self.check_unlock_condition(node, user_id)
                progress_map[node.id] = {
                    "status": NodeStatus.UNLOCKED.value if can_unlock else NodeStatus.LOCKED.value,
                    "completion_percentage": 0.0,
                    "last_accessed": None,
                    "completed_at": None
                }

        return progress_map

    async def initialize_course_progress(self, user_id: int, course_id: int):
        """
        Initialize progress for a newly enrolled course
        Unlocks the first node(s) automatically
        """
        # Get all root nodes (no parent) for the course
        stmt = select(CourseNode).where(
            and_(
                CourseNode.course_id == course_id,
                CourseNode.parent_id.is_(None)
            )
        ).order_by(CourseNode.sequence.asc())

        result = await self.db.execute(stmt)
        root_nodes = result.scalars().all()

        # Unlock the first root node
        if root_nodes:
            first_node = root_nodes[0]
            await self.unlock_node(user_id, first_node.id)
