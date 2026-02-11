"""
Quiz Service Layer

Provides high-level APIs for quiz generation with learning integration.
This service wraps the EnhancedQuizGenerator and handles database
interactions for storing quiz data.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import sqlite3
from sqlalchemy.orm import Session

from .quiz_generator import EnhancedQuizGenerator

logger = logging.getLogger(__name__)


class QuizService:
    """High-level quiz service with learning integration"""

    def __init__(self, db: Session):
        """
        Initialize quiz service

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.generator = EnhancedQuizGenerator(db)

    async def generate_quiz_for_node(
        self,
        node_id: int,
        node_title: str,
        learning_objectives: List[str],
        content: str,
        subject: str = "general",
        topic: str = None,
        db_path: str = None
    ) -> Dict[str, Any]:
        """
        Generate complete quiz bank for a course node and save to database

        Args:
            node_id: Node database ID
            node_title: Node title
            learning_objectives: Learning objectives
            content: Course content
            subject: Subject area
            topic: Specific topic
            db_path: SQLite database path (for legacy compatibility)

        Returns:
            Result dictionary with success status and quiz bank
        """
        try:
            logger.info(f"Generating quiz bank for node {node_id}: '{node_title}'")

            # Generate quiz bank with learning
            quiz_bank = await self.generator.generate_full_quiz_bank(
                node_title=node_title,
                learning_objectives=learning_objectives,
                content=content,
                subject=subject,
                topic=topic or node_title
            )

            # Calculate average quality score
            all_scores = []
            for difficulty_questions in quiz_bank.values():
                for q in difficulty_questions:
                    if "quality_score" in q:
                        all_scores.append(q["quality_score"])

            avg_quality = sum(all_scores) / len(all_scores) if all_scores else 0.0
            high_quality_count = sum(1 for s in all_scores if s >= 85.0)

            logger.info(f"Quiz bank generated - Avg quality: {avg_quality:.1f}, High quality: {high_quality_count}/{len(all_scores)}")

            # Save to database if db_path provided (legacy support)
            if db_path:
                await self._save_to_sqlite(
                    node_id=node_id,
                    quiz_bank=quiz_bank,
                    db_path=db_path
                )

            return {
                "success": True,
                "node_id": node_id,
                "quiz_bank": quiz_bank,
                "quality_stats": {
                    "average_quality": avg_quality,
                    "high_quality_count": high_quality_count,
                    "total_questions": len(all_scores),
                    "high_quality_percentage": (high_quality_count / len(all_scores) * 100) if all_scores else 0.0
                }
            }

        except Exception as e:
            logger.error(f"Failed to generate quiz for node {node_id}: {e}", exc_info=True)
            return {
                "success": False,
                "node_id": node_id,
                "error": str(e)
            }

    async def _save_to_sqlite(
        self,
        node_id: int,
        quiz_bank: Dict[str, List[Dict[str, Any]]],
        db_path: str
    ):
        """
        Save quiz bank to SQLite database (legacy compatibility)

        Args:
            node_id: Node ID
            quiz_bank: Quiz bank data
            db_path: Database path
        """
        conn = None
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Remove quality metadata before saving to legacy database
            clean_quiz_bank = {}
            for difficulty, questions in quiz_bank.items():
                clean_questions = []
                for q in questions:
                    clean_q = {
                        "id": q.get("id"),
                        "question": q.get("question"),
                        "options": q.get("options"),
                        "correct_option": q.get("correct_option"),
                        "explanation": q.get("explanation", ""),
                        "difficulty": difficulty
                    }
                    clean_questions.append(clean_q)
                clean_quiz_bank[difficulty] = clean_questions

            cursor.execute(
                "UPDATE course_nodes SET quiz_data = ? WHERE id = ?",
                (json.dumps(clean_quiz_bank, ensure_ascii=False), node_id)
            )

            conn.commit()
            logger.info(f"Quiz bank saved to SQLite for node {node_id}")

        except Exception as e:
            logger.error(f"Failed to save to SQLite: {e}", exc_info=True)
            raise
        finally:
            if conn:
                conn.close()

    async def generate_quiz_for_course(
        self,
        course_id: int,
        subject: str = "general",
        db_path: str = None
    ) -> Dict[str, Any]:
        """
        Generate quiz banks for all nodes in a course

        Args:
            course_id: Course ID
            subject: Subject area
            db_path: SQLite database path

        Returns:
            Generation statistics
        """
        if db_path is None:
            db_path = str(Path(__file__).parent.parent.parent.parent / "hercu_dev.db")

        conn = None
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id, title, learning_objectives, content_l1, content_l2 FROM course_nodes WHERE course_id = ?",
                (course_id,)
            )

            nodes = cursor.fetchall()
            conn.close()
            conn = None

            if not nodes:
                return {
                    "success": False,
                    "message": "Course has no nodes",
                    "generated": 0,
                    "failed": 0
                }

            logger.info(f"Found {len(nodes)} nodes in course {course_id}")

            generated = 0
            failed = 0
            total_quality = []
            high_quality_total = 0

            for idx, node in enumerate(nodes):
                logger.info(f"Processing node {idx+1}/{len(nodes)}: {node['title']} (ID: {node['id']})")

                # Parse learning objectives
                learning_objectives = []
                if node['learning_objectives']:
                    try:
                        learning_objectives = json.loads(node['learning_objectives'])
                    except:
                        pass

                content = node['content_l1'] or node['content_l2'] or ""

                # Generate quiz
                result = await self.generate_quiz_for_node(
                    node_id=node['id'],
                    node_title=node['title'],
                    learning_objectives=learning_objectives,
                    content=content,
                    subject=subject,
                    topic=node['title'],
                    db_path=db_path
                )

                if result["success"]:
                    generated += 1
                    stats = result.get("quality_stats", {})
                    total_quality.append(stats.get("average_quality", 0))
                    high_quality_total += stats.get("high_quality_count", 0)
                    logger.info(f"Node {node['id']} completed - Quality: {stats.get('average_quality', 0):.1f}")
                else:
                    failed += 1
                    logger.error(f"Node {node['id']} failed: {result.get('error', 'Unknown error')}")

            avg_course_quality = sum(total_quality) / len(total_quality) if total_quality else 0.0

            return {
                "success": True,
                "message": f"Quiz generation completed: {generated} succeeded, {failed} failed",
                "generated": generated,
                "failed": failed,
                "total": len(nodes),
                "quality_stats": {
                    "average_quality": avg_course_quality,
                    "high_quality_count": high_quality_total,
                    "total_questions": len(nodes) * 39  # 13 questions * 3 difficulties
                }
            }

        except Exception as e:
            logger.error(f"Failed to generate course quiz: {e}", exc_info=True)
            return {
                "success": False,
                "message": str(e),
                "generated": 0,
                "failed": 0
            }
        finally:
            if conn:
                conn.close()

    async def get_quiz_quality_report(
        self,
        subject: str = None,
        difficulty: str = None,
        min_date: str = None
    ) -> Dict[str, Any]:
        """
        Get quality report for generated quizzes

        Args:
            subject: Filter by subject
            difficulty: Filter by difficulty
            min_date: Filter by minimum date

        Returns:
            Quality report with statistics
        """
        try:
            from app.models.models import QualityEvaluation
            from sqlalchemy import func, and_

            # Build query
            query = self.db.query(QualityEvaluation).filter(
                QualityEvaluation.content_type == "quiz_question"
            )

            if min_date:
                query = query.filter(QualityEvaluation.evaluated_at >= min_date)

            evaluations = query.all()

            if not evaluations:
                return {
                    "success": True,
                    "message": "No evaluations found",
                    "total_evaluations": 0
                }

            # Calculate statistics
            scores = [e.quality_score for e in evaluations]
            high_quality_count = sum(1 for s in scores if s >= 85.0)
            baseline_count = sum(1 for s in scores if 75.0 <= s < 85.0)
            low_quality_count = sum(1 for s in scores if s < 75.0)

            return {
                "success": True,
                "total_evaluations": len(evaluations),
                "average_quality": sum(scores) / len(scores),
                "high_quality_count": high_quality_count,
                "high_quality_percentage": (high_quality_count / len(scores) * 100),
                "baseline_count": baseline_count,
                "low_quality_count": low_quality_count,
                "score_distribution": {
                    "min": min(scores),
                    "max": max(scores),
                    "median": sorted(scores)[len(scores) // 2]
                },
                "template_saved_count": sum(1 for e in evaluations if e.saved_as_template)
            }

        except Exception as e:
            logger.error(f"Failed to get quality report: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
