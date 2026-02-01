"""
同步数据库连接管理器
专门用于需要同步访问的场景（如 AI 导师功能）
"""

import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any
import json
from contextlib import contextmanager


class SyncDBManager:
    """同步数据库管理器"""

    def __init__(self, db_path: Optional[str] = None):
        """
        初始化数据库管理器

        Args:
            db_path: 数据库文件路径，如果为 None 则自动查找
        """
        if db_path is None:
            # 自动查找数据库文件
            possible_paths = [
                Path(__file__).parent.parent.parent / "hercu_dev.db",
                Path(__file__).parent.parent.parent.parent / "hercu_dev.db",
            ]
            for path in possible_paths:
                if path.exists():
                    db_path = str(path)
                    break

            if db_path is None:
                raise FileNotFoundError("Database file not found")

        self.db_path = db_path

    @contextmanager
    def get_connection(self):
        """
        获取数据库连接的上下文管理器

        使用方法:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM table")
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def get_node_info(self, node_id: int) -> Optional[Dict[str, Any]]:
        """
        获取节点信息

        Args:
            node_id: 节点 ID

        Returns:
            节点信息字典，如果不存在则返回 None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    id,
                    title,
                    learning_objectives,
                    content_l1,
                    content_l2,
                    content_l3,
                    ai_tutor_config,
                    quiz_data
                FROM course_nodes
                WHERE id = ?
                """,
                (node_id,)
            )

            row = cursor.fetchone()
            if not row:
                return None

            # 解析 JSON 字段
            return {
                "id": row["id"],
                "title": row["title"],
                "learning_objectives": json.loads(row["learning_objectives"]) if row["learning_objectives"] else [],
                "content_l1": json.loads(row["content_l1"]) if row["content_l1"] else {},
                "content_l2": json.loads(row["content_l2"]) if row["content_l2"] else {},
                "content_l3": json.loads(row["content_l3"]) if row["content_l3"] else {},
                "ai_tutor_config": json.loads(row["ai_tutor_config"]) if row["ai_tutor_config"] else {},
                "quiz_data": json.loads(row["quiz_data"]) if row["quiz_data"] else {},
            }

    def get_ai_tutor_config(self, node_id: int) -> Dict[str, Any]:
        """
        获取节点的 AI 导师配置

        Args:
            node_id: 节点 ID

        Returns:
            AI 导师配置字典
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT ai_tutor_config
                FROM course_nodes
                WHERE id = ?
                """,
                (node_id,)
            )

            row = cursor.fetchone()
            if not row:
                return {}

            return json.loads(row["ai_tutor_config"]) if row["ai_tutor_config"] else {}


# 全局单例
_db_manager: Optional[SyncDBManager] = None


def get_sync_db_manager() -> SyncDBManager:
    """获取同步数据库管理器单例"""
    global _db_manager

    if _db_manager is None:
        _db_manager = SyncDBManager()

    return _db_manager
