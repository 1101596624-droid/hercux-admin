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
            # 自动查找数据库文件 - 优先使用生产环境数据库
            possible_paths = [
                Path("/www/wwwroot/hercu-backend/hercu.db"),  # 服务器生产环境
                Path(__file__).parent.parent.parent / "hercu.db",
                Path(__file__).parent.parent.parent / "hercu_dev.db",
                Path(__file__).parent.parent.parent.parent / "hercu.db",
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
                    description,
                    content,
                    config,
                    timeline_config
                FROM course_nodes
                WHERE id = ?
                """,
                (node_id,)
            )

            row = cursor.fetchone()
            if not row:
                return None

            # 解析 JSON 字段
            content = json.loads(row["content"]) if row["content"] else {}
            config = json.loads(row["config"]) if row["config"] else {}
            timeline_config = json.loads(row["timeline_config"]) if row["timeline_config"] else {}

            # 从 content 和 config 中提取 AI 相关配置
            ai_tutor_config = config.get("ai_tutor", {}) or timeline_config.get("ai_tutor", {}) or {}
            learning_objectives = content.get("learning_objectives", []) or config.get("learning_objectives", []) or []

            return {
                "id": row["id"],
                "title": row["title"],
                "description": row["description"] or "",
                "learning_objectives": learning_objectives,
                "content": content,
                "config": config,
                "timeline_config": timeline_config,
                "ai_tutor_config": ai_tutor_config,
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
                SELECT config, timeline_config, content
                FROM course_nodes
                WHERE id = ?
                """,
                (node_id,)
            )

            row = cursor.fetchone()
            if not row:
                return {}

            config = json.loads(row["config"]) if row["config"] else {}
            timeline_config = json.loads(row["timeline_config"]) if row["timeline_config"] else {}
            content = json.loads(row["content"]) if row["content"] else {}

            # 从多个位置查找 ai_tutor 配置
            ai_tutor_config = (
                config.get("ai_tutor", {}) or
                timeline_config.get("ai_tutor", {}) or
                content.get("ai_tutor", {}) or
                {}
            )

            return ai_tutor_config


# 全局单例
_db_manager: Optional[SyncDBManager] = None


def get_sync_db_manager() -> SyncDBManager:
    """获取同步数据库管理器单例"""
    global _db_manager

    if _db_manager is None:
        _db_manager = SyncDBManager()

    return _db_manager
