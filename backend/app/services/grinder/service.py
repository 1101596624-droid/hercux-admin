"""
小课堂服务 - 提供监督式题目生成 API
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from .supervisor import get_grinder_supervisor

logger = logging.getLogger(__name__)


class GrinderService:
    """小课堂服务"""

    def __init__(self, db: Session = None):
        self.db = db
        self.supervisor = get_grinder_supervisor(db)

    async def generate_exam(
        self,
        topic: str,
        question_count: int = 5,
        focus_categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        生成考试题目（带监督和学习集成）

        Args:
            topic: 考试主题
            question_count: 题目数量
            focus_categories: 重点知识分类

        Returns:
            包含考试数据、审核结果和质量评分的字典
        """
        return await self.supervisor.generate_exam_with_supervision(
            topic=topic,
            question_count=question_count,
            focus_categories=focus_categories
        )


def get_grinder_service(db: Session = None) -> GrinderService:
    """获取GrinderService实例"""
    return GrinderService(db)
