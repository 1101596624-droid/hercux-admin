"""
Phase 1-16 regression + concurrency benchmark (in-process ASGI mode).

Usage:
  cd backend
  python scripts/run_phase_regression_and_load.py

Output:
  backend/reports/phase_regression_load_report.json
"""

from __future__ import annotations

import asyncio
import faulthandler
import json
import logging
import os
import random
import statistics
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from httpx import ASGITransport, AsyncClient


# Ensure settings can load in standalone mode
os.environ.setdefault("TEST_MODE", "true")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./.tmp_phase_regression.db")
os.environ.setdefault("ENV", "production")
os.environ.setdefault("REDIS_URL", "redis://127.0.0.1:6379/0")
os.environ.setdefault("NEO4J_URI", "bolt://127.0.0.1:7687")
os.environ.setdefault("NEO4J_USER", "neo4j")
os.environ.setdefault("NEO4J_PASSWORD", "neo4j")
os.environ.setdefault("SECRET_KEY", "local-test-secret")

# Ensure backend root is importable when script is executed from scripts/
BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app
from app.db.session import Base, get_db
from app.core.security import create_access_token, get_password_hash
from app.models.models import (
    AgentStrategyWeight,
    ConceptBridge,
    Course,
    CourseNode,
    CourseRelation,
    CourseRecommendation,
    KnowledgeNode,
    LearningHabit,
    LearningReport,
    LearningProgress,
    MetacognitiveLog,
    NodeStatus,
    RecommendedGrinder,
    RecommendedLesson,
    ReviewSchedule,
    StudentAssessment,
    StudentCourseProgress,
    StudentEmotionState,
    StudentEvent,
    StudentFeedback,
    StudentGoal,
    StudentKnowledgeState,
    StudentLearningPath,
    StudentMisconception,
    StudentSubjectTransfer,
    Subject,
    SubjectRelation,
    User,
    UserCourse,
    UserProfile,
)


REPORT_DIR = Path(__file__).resolve().parent.parent / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Keep regression output compact and deterministic.
logging.getLogger("aiosqlite").setLevel(logging.WARNING)
logging.getLogger("app.core.middleware").setLevel(logging.WARNING)
logging.getLogger("app.core.errors").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Optional debug aid for local diagnosis only.
if os.getenv("PHASE_REG_TRACEBACK_DEBUG", "").lower() in {"1", "true", "yes"}:
    faulthandler.enable()
    faulthandler.dump_traceback_later(180, repeat=True)


@dataclass
class StepResult:
    name: str
    ok: bool
    status_code: int
    latency_ms: float
    detail: str = ""


def _pct(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    k = max(0, min(len(values) - 1, int(round((len(values) - 1) * p))))
    return sorted(values)[k]


async def seed_data(session_maker: async_sessionmaker[AsyncSession]) -> None:
    print("[seed] start", flush=True)
    async with session_maker() as db:
        now = datetime.now(timezone.utc)

        # user/admin
        await db.execute(
            insert(User),
            [
                {
                    "id": 1,
                    "email": "perf_user@example.com",
                    "username": "perf_user",
                    "full_name": "Perf User",
                    "hashed_password": get_password_hash("Passw0rd!"),
                    "is_active": 1,
                    "is_admin": 1,
                    "is_premium": 1,
                }
            ],
        )
        print("[seed] user/profile/subjects", flush=True)

        # profile (Phase 16 style adaptation)
        await db.execute(
            insert(UserProfile),
            [
                {
                    "user_id": 1,
                    "learning_style": {"visual": 0.5, "auditory": 0.2, "reading": 0.2, "kinesthetic": 0.1},
                }
            ],
        )

        # subjects
        await db.execute(
            insert(Subject),
            [
                {"id": 1, "name": "Physics", "description": "Physics subject"},
                {"id": 2, "name": "Mathematics", "description": "Math subject"},
            ],
        )

        # courses
        courses = []
        for i in range(1, 21):
            courses.append(
                {
                    "id": i,
                    "name": f"Course {i}",
                    "description": f"Demo course {i}",
                    "difficulty": random.choice(["beginner", "intermediate", "advanced"]),
                    "tags": ["demo", "phase"],
                    "is_published": 1,
                    "created_at": now - timedelta(days=i),
                }
            )
        await db.execute(insert(Course), courses)
        print("[seed] courses", flush=True)

        # course nodes + knowledge nodes
        course_nodes = []
        knowledge_nodes = []
        for i in range(1, 121):
            course_id = ((i - 1) % 20) + 1
            subject_id = 1 if i <= 80 else 2
            course_nodes.append(
                {
                    "id": i,
                    "course_id": course_id,
                    "node_id": f"node_{i}",
                    "type": "lesson",
                    "component_id": "demo-component",
                    "title": f"Node {i}",
                    "sequence": i,
                    "unlock_condition": {"type": "previous_complete"},
                }
            )
            prerequisites = [i - 1] if i > 1 and i % 5 != 0 else []
            knowledge_nodes.append(
                {
                    "id": i,
                    "subject_id": subject_id,
                    "course_node_id": i,
                    "code": f"KN_{i:04d}",
                    "name": f"Knowledge {i}",
                    "difficulty": round(random.uniform(0.2, 0.9), 2),
                    "prerequisites": prerequisites,
                }
            )
        await db.execute(insert(CourseNode), course_nodes)
        await db.execute(insert(KnowledgeNode), knowledge_nodes)
        print("[seed] course_nodes + knowledge_nodes", flush=True)

        # learning progress
        progress_rows = []
        for i in range(1, 61):
            progress_rows.append(
                {
                    "user_id": 1,
                    "node_id": i,
                    "status": random.choice(
                        [NodeStatus.COMPLETED.value, NodeStatus.IN_PROGRESS.value, NodeStatus.UNLOCKED.value]
                    ),
                    "completion_percentage": random.uniform(20, 100),
                    "time_spent_seconds": random.randint(120, 2400),
                    "last_accessed": now - timedelta(minutes=random.randint(1, 10000)),
                }
            )
        await db.execute(insert(LearningProgress), progress_rows)
        print("[seed] learning_progress", flush=True)

        # student knowledge states
        sks_rows = []
        for i in range(1, 121):
            mastery = round(random.uniform(0.1, 0.95), 3)
            sks_rows.append(
                {
                    "user_id": 1,
                    "knowledge_node_id": i,
                    "mastery": mastery,
                    "stability": round(random.uniform(0.5, 12.0), 3),
                    "practice_count": random.randint(1, 50),
                    "correct_count": random.randint(0, 50),
                    "streak": random.randint(0, 10),
                    "last_practice_at": now - timedelta(hours=random.randint(1, 240)),
                    "updated_at": now - timedelta(minutes=random.randint(1, 300)),
                }
            )
        await db.execute(insert(StudentKnowledgeState), sks_rows)
        print("[seed] student_knowledge_state", flush=True)

        # student events
        event_rows = []
        for _ in range(1500):
            k = random.randint(1, 120)
            is_correct = random.choice([0, 1])
            ev_type = random.choices(["answer", "hint", "skip", "review"], weights=[70, 10, 10, 10])[0]
            event_rows.append(
                {
                    "user_id": 1,
                    "knowledge_node_id": k,
                    "event_type": ev_type,
                    "is_correct": is_correct if ev_type == "answer" else None,
                    "response_time_ms": random.randint(1200, 60000) if ev_type == "answer" else None,
                    "event_data": {"seed": True},
                    "created_at": now - timedelta(minutes=random.randint(1, 60 * 24 * 14)),
                }
            )
        await db.execute(insert(StudentEvent), event_rows)
        print("[seed] student_events", flush=True)

        # emotion states
        emo_rows = []
        emo_types = ["frustration", "anxiety", "boredom", "focus", "excitement"]
        for i in range(1, 121):
            emo_rows.append(
                {
                    "user_id": 1,
                    "emotion_type": random.choice(emo_types),
                    "intensity": round(random.uniform(0.2, 0.95), 2),
                    "confidence": round(random.uniform(0.4, 0.95), 2),
                    "trigger_type": "seed",
                    "context": {"sample": i},
                    "created_at": now - timedelta(minutes=i),
                }
            )
        await db.execute(insert(StudentEmotionState), emo_rows)
        print("[seed] student_emotion_states", flush=True)

        # misconceptions
        mis_rows = []
        for i in range(1, 21):
            mis_rows.append(
                {
                    "user_id": 1,
                    "knowledge_node_id": random.randint(1, 80),
                    "misconception": f"Misconception {i}",
                    "frequency": random.randint(1, 8),
                    "resolved": 0 if i % 3 else 1,
                    "last_seen_at": now - timedelta(hours=random.randint(1, 96)),
                }
            )
        await db.execute(insert(StudentMisconception), mis_rows)
        print("[seed] student_misconceptions", flush=True)

        # review schedule
        rs_rows = []
        for i in range(1, 81):
            rs_rows.append(
                {
                    "user_id": 1,
                    "knowledge_node_id": i,
                    "next_review_at": now - timedelta(minutes=random.randint(1, 300)) if i <= 80 else now + timedelta(days=1),
                    "last_review_at": now - timedelta(days=random.randint(1, 10)),
                    "review_count": random.randint(0, 15),
                    "interval_days": round(random.uniform(0.5, 14), 2),
                }
            )
        await db.execute(insert(ReviewSchedule), rs_rows)
        print("[seed] review_schedule", flush=True)

        # learning path
        path_items = []
        for i in range(1, 9):
            path_items.append(
                {
                    "knowledge_node_id": i,
                    "node_code": f"KN_{i:04d}",
                    "node_name": f"Knowledge {i}",
                    "activity_type": random.choice(["learn", "practice", "review"]),
                    "estimated_minutes": random.choice([3, 5, 8]),
                    "target_difficulty": round(random.uniform(0.2, 0.7), 2),
                    "mastery_before": round(random.uniform(0.2, 0.8), 2),
                    "reason": "seed path item",
                    "completed": i < 3,
                }
            )
        await db.execute(
            insert(StudentLearningPath),
            [
                {
                    "id": 1,
                    "user_id": 1,
                    "subject_id": 1,
                    "status": "active",
                    "session_duration": 30,
                    "path_items": path_items,
                    "emotion_snapshot": "focus",
                    "total_nodes": len(path_items),
                    "completed_nodes": 2,
                    "created_at": now - timedelta(minutes=30),
                }
            ],
        )
        print("[seed] learning_paths", flush=True)

        # goals/habits
        await db.execute(
            insert(StudentGoal),
            [
                {
                    "user_id": 1,
                    "goal_type": "mastery",
                    "title": "Raise Physics Mastery",
                    "subject_id": 1,
                    "target_value": 0.8,
                    "current_value": 0.55,
                    "status": "active",
                    "deadline": now + timedelta(days=14),
                }
            ],
        )

        habits = []
        for d in range(1, 31):
            day = date.today() - timedelta(days=d)
            habits.append(
                {
                    "user_id": 1,
                    "date": day,
                    "events_count": random.randint(0, 30),
                    "study_minutes": random.randint(5, 90),
                    "subjects_touched": random.randint(1, 3),
                    "accuracy": round(random.uniform(0.45, 0.95), 3),
                    "dominant_emotion": random.choice(emo_types),
                }
            )
        await db.execute(insert(LearningHabit), habits)
        print("[seed] goals/habits", flush=True)

        # relation data
        await db.execute(
            insert(CourseRecommendation),
            [
                {
                    "source_course_id": 1,
                    "target_course_id": 2,
                    "relation_type": "advanced",
                    "weight": 0.8,
                    "reason": "seed relation",
                },
                {
                    "source_course_id": 1,
                    "target_course_id": 3,
                    "relation_type": "complementary",
                    "weight": 0.6,
                    "reason": "seed relation",
                },
            ],
        )
        await db.execute(
            insert(SubjectRelation),
            [
                {
                    "source_subject_id": 1,
                    "target_subject_id": 2,
                    "relation_type": "cross_discipline",
                    "weight": 0.7,
                    "transfer_coefficient": 0.45,
                }
            ],
        )
        await db.execute(
            insert(StudentSubjectTransfer),
            [
                {
                    "user_id": 1,
                    "source_subject_id": 1,
                    "target_subject_id": 2,
                    "observed_transfer": 0.5,
                    "confidence": 0.6,
                    "sample_count": 5,
                }
            ],
        )

        # adaptive weights
        await db.execute(
            insert(AgentStrategyWeight),
            [
                {
                    "strategy_type": "task_generation",
                    "weights": {"learn": 0.3, "review": 0.2, "practice": 0.2, "remediate": 0.2, "challenge": 0.1},
                    "total_episodes": 20,
                    "avg_reward": 0.12,
                },
                {
                    "strategy_type": "content_type",
                    "weights": {"lecture": 0.25, "simulator": 0.25, "grinder": 0.25, "tutor": 0.25},
                    "total_episodes": 20,
                    "avg_reward": 0.08,
                },
            ],
        )

        await db.commit()
        print("[seed] done", flush=True)


async def run_regression(client: AsyncClient, headers: Dict[str, str]) -> List[StepResult]:
    out: List[StepResult] = []

    async def call(
        name: str,
        method: str,
        url: str,
        *,
        json_body: Optional[dict] = None,
        expect: Optional[Callable[[Any], bool]] = None,
    ) -> Optional[dict]:
        t0 = time.perf_counter()
        try:
            resp = await client.request(method, url, json=json_body, headers=headers)
            latency = (time.perf_counter() - t0) * 1000
            ok = resp.status_code < 400
            detail = ""
            data = None
            if ok:
                try:
                    data = resp.json()
                    if expect and not expect(data):
                        ok = False
                        detail = "schema/assertion failed"
                except Exception as exc:
                    ok = False
                    detail = f"json parse failed: {exc}"
            else:
                detail = resp.text[:200]
            out.append(StepResult(name=name, ok=ok, status_code=resp.status_code, latency_ms=latency, detail=detail))
            return data
        except Exception as exc:
            latency = (time.perf_counter() - t0) * 1000
            out.append(
                StepResult(
                    name=name,
                    ok=False,
                    status_code=599,
                    latency_ms=latency,
                    detail=f"request exception: {exc}",
                )
            )
            return None

    # Phase 1-2
    await call(
        "phase1_record_event",
        "POST",
        "/api/v1/knowledge/events",
        json_body={
            "knowledge_node_id": 1,
            "event_type": "answer",
            "is_correct": 1,
            "response_time_ms": 4800,
            "event_data": {"misconception": "none"},
        },
    )
    await call("phase1_my_state", "GET", "/api/v1/knowledge/my-state?subject_id=1")
    await call("phase1_weak_nodes", "GET", "/api/v1/knowledge/weak-nodes?threshold=0.5&limit=80")
    path_resp = await call(
        "phase2_generate_path",
        "POST",
        "/api/v1/knowledge/learning-path",
        json_body={"subject_id": 1, "session_duration": 30},
        expect=lambda d: "id" in d,
    )
    await call("phase2_next_activity", "GET", "/api/v1/knowledge/next-activity?subject_id=1")

    path_id = path_resp.get("id") if isinstance(path_resp, dict) else 1
    await call(
        "phase2_complete_path_node",
        "POST",
        f"/api/v1/knowledge/learning-path/{path_id}/complete",
        json_body={"knowledge_node_id": 1},
    )
    await call("phase2_path_history", "GET", "/api/v1/knowledge/learning-path/history?limit=10")
    await call("phase2_admin_emotion_current", "GET", "/api/v1/admin/knowledge/students/1/emotion/current")

    # Phase 4
    await call("phase4_review_init", "POST", "/api/v1/review/init?subject_id=1")
    await call("phase4_review_due", "GET", "/api/v1/review/due?max_count=20&max_minutes=30&subject_id=1")
    await call("phase4_review_stats", "GET", "/api/v1/review/stats")

    # Phase 5
    await call("phase5_report_session", "GET", "/api/v1/learning/report/session?minutes_back=120")
    await call("phase5_report_growth", "GET", "/api/v1/learning/report/growth?period=weekly")
    await call("phase5_report_history", "GET", "/api/v1/learning/report/history?report_type=weekly&limit=5")

    # Phase 6-8
    await call("phase6_recommendation", "GET", "/api/v1/recommendation/recommended-content?limit=12")
    await call(
        "phase7_progress_feedback",
        "POST",
        "/api/v1/smart-feedback/progress-feedback?user_id=1",
        json_body={"subject_id": 1, "include_suggestions": True},
    )
    await call(
        "phase7_emotion_feedback",
        "POST",
        "/api/v1/smart-feedback/emotion-feedback?user_id=1",
        json_body={"subject_id": 1},
    )
    await call(
        "phase7_smart_report",
        "POST",
        "/api/v1/smart-feedback/smart-report?user_id=1",
        json_body={"period": "weekly", "subject_id": 1},
    )

    # Phase 9-11
    await call("phase10_cross_recommendations", "GET", "/api/v1/cross-disciplinary/recommendations?limit=5")
    await call("phase10_concept_recommendations", "GET", "/api/v1/cross-disciplinary/concept-recommendations?limit=5")
    await call(
        "phase11_course_recommended",
        "POST",
        "/api/v1/course-rec/recommended-courses",
        json_body={"limit": 6, "subject_id": 1},
    )
    await call(
        "phase11_course_path",
        "POST",
        "/api/v1/course-rec/learning-path",
        json_body={"course_id": 1, "session_minutes": 30},
    )
    await call("phase11_course_progress", "GET", "/api/v1/course-rec/course-progress")

    # Phase 13
    await call(
        "phase13_adaptive_tasks",
        "POST",
        "/api/v1/adaptive-agent/adaptive-tasks?user_id=1",
        json_body={"subject_id": 1, "session_minutes": 30},
    )
    await call(
        "phase13_adaptive_path",
        "POST",
        "/api/v1/adaptive-agent/adaptive-path?user_id=1",
        json_body={"subject_id": 1, "session_minutes": 30, "include_cross_discipline": True},
    )
    await call("phase13_strategy_weights", "GET", "/api/v1/adaptive-agent/strategy-weights")

    # Phase 15
    goal = await call(
        "phase15_goal_create",
        "POST",
        "/api/v1/goals/?user_id=1",
        json_body={
            "goal_type": "mastery",
            "title": "Weekly Mastery Goal",
            "subject_id": 1,
            "target_value": 0.85,
        },
    )
    await call("phase15_goal_list", "GET", "/api/v1/goals/?user_id=1")
    await call("phase15_goal_progress", "GET", "/api/v1/goals/progress?user_id=1")
    if isinstance(goal, dict) and goal.get("id"):
        await call(
            "phase15_goal_update",
            "PUT",
            f"/api/v1/goals/{goal['id']}?user_id=1",
            json_body={"status": "active", "target_value": 0.9},
        )

    await call("phase15_habit_summary", "GET", "/api/v1/habits/summary?user_id=1")
    await call("phase15_habit_calendar", "GET", "/api/v1/habits/calendar?user_id=1&days=30")
    await call("phase15_habit_bests", "GET", "/api/v1/habits/personal-bests?user_id=1")

    await call("phase15_predictive", "GET", "/api/v1/predictive/predictions?user_id=1&subject_id=1&target_mastery=0.8")
    await call("phase15_forgetting_risks", "GET", "/api/v1/predictive/forgetting-risks?user_id=1&subject_id=1")
    await call("phase15_bottlenecks", "GET", "/api/v1/predictive/bottlenecks?user_id=1&subject_id=1")
    await call("phase15_comparative", "GET", "/api/v1/predictive/comparative?user_id=1&period=weekly&subject_id=1")

    # Phase 16
    await call("phase16_transfer_coeff", "GET", "/api/v1/transfer/my-coefficients")
    await call(
        "phase16_transfer_update",
        "POST",
        "/api/v1/transfer/update",
        json_body={"source_subject_id": 1, "target_subject_id": 2},
    )
    await call("phase16_temporal_patterns", "GET", "/api/v1/temporal/patterns?days=30")
    await call("phase16_temporal_optimal", "GET", "/api/v1/temporal/optimal-schedule")

    # Admin overview (query aggregation hot path)
    await call("admin_knowledge_overview", "GET", "/api/v1/admin/knowledge/overview")

    return out


async def run_concurrency(
    client: AsyncClient,
    headers: Dict[str, str],
    name: str,
    method: str,
    url: str,
    *,
    json_body: Optional[dict] = None,
    requests_count: int = 120,
    concurrency: int = 24,
) -> Dict[str, Any]:
    semaphore = asyncio.Semaphore(concurrency)
    latencies: List[float] = []
    failures = 0

    async def one() -> None:
        nonlocal failures
        async with semaphore:
            t0 = time.perf_counter()
            try:
                resp = await client.request(method, url, headers=headers, json=json_body)
                lat = (time.perf_counter() - t0) * 1000
                latencies.append(lat)
                if resp.status_code >= 400:
                    failures += 1
            except Exception:
                lat = (time.perf_counter() - t0) * 1000
                latencies.append(lat)
                failures += 1

    t_start = time.perf_counter()
    await asyncio.gather(*[one() for _ in range(requests_count)])
    duration = time.perf_counter() - t_start

    return {
        "endpoint": name,
        "requests": requests_count,
        "concurrency": concurrency,
        "failures": failures,
        "success_rate": round((requests_count - failures) / requests_count, 4),
        "rps": round(requests_count / duration, 2) if duration > 0 else 0.0,
        "latency_ms": {
            "p50": round(_pct(latencies, 0.50), 2),
            "p95": round(_pct(latencies, 0.95), 2),
            "p99": round(_pct(latencies, 0.99), 2),
            "avg": round(statistics.mean(latencies), 2) if latencies else 0.0,
            "max": round(max(latencies), 2) if latencies else 0.0,
        },
    }


async def main() -> int:
    db_path = Path(__file__).resolve().parent.parent / f".tmp_phase_regression_{uuid.uuid4().hex}.db"

    engine = create_async_engine(
        f"sqlite+aiosqlite:///{db_path.as_posix()}",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)

    required_tables = [
        User.__table__,
        UserProfile.__table__,
        Subject.__table__,
        Course.__table__,
        CourseNode.__table__,
        KnowledgeNode.__table__,
        UserCourse.__table__,
        LearningProgress.__table__,
        StudentKnowledgeState.__table__,
        StudentEvent.__table__,
        StudentEmotionState.__table__,
        StudentMisconception.__table__,
        ReviewSchedule.__table__,
        StudentLearningPath.__table__,
        StudentCourseProgress.__table__,
        StudentAssessment.__table__,
        StudentFeedback.__table__,
        LearningHabit.__table__,
        LearningReport.__table__,
        MetacognitiveLog.__table__,
        StudentGoal.__table__,
        CourseRecommendation.__table__,
        CourseRelation.__table__,
        SubjectRelation.__table__,
        ConceptBridge.__table__,
        StudentSubjectTransfer.__table__,
        RecommendedLesson.__table__,
        RecommendedGrinder.__table__,
        AgentStrategyWeight.__table__,
    ]

    print("[setup] creating tables", flush=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=required_tables)
    print("[setup] tables ready", flush=True)

    await seed_data(session_maker)

    async def override_get_db():
        async with session_maker() as session:
            try:
                yield session
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db

    token = create_access_token({"sub": "1"})
    headers = {"Authorization": f"Bearer {token}"}

    regression_results: List[StepResult]
    concurrency_results: List[Dict[str, Any]] = []

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test", timeout=30.0) as client:
        print("[run] regression", flush=True)
        regression_results = await run_regression(client, headers)
        print("[run] concurrency", flush=True)

        # high-concurrency hot paths
        concurrency_results.append(
            await run_concurrency(
                client,
                headers,
                "knowledge_weak_nodes",
                "GET",
                "/api/v1/knowledge/weak-nodes?threshold=0.5&limit=80",
                requests_count=40,
                concurrency=10,
            )
        )
        concurrency_results.append(
            await run_concurrency(
                client,
                headers,
                "learning_next_activity",
                "GET",
                "/api/v1/knowledge/next-activity?subject_id=1",
                requests_count=40,
                concurrency=10,
            )
        )
        concurrency_results.append(
            await run_concurrency(
                client,
                headers,
                "recommendation_content",
                "GET",
                "/api/v1/recommendation/recommended-content?limit=12",
                requests_count=30,
                concurrency=8,
            )
        )
        concurrency_results.append(
            await run_concurrency(
                client,
                headers,
                "admin_knowledge_overview",
                "GET",
                "/api/v1/admin/knowledge/overview",
                requests_count=40,
                concurrency=10,
            )
        )

    app.dependency_overrides.clear()
    await engine.dispose()

    passed = sum(1 for r in regression_results if r.ok)
    total = len(regression_results)
    regression_summary = {
        "passed": passed,
        "failed": total - passed,
        "pass_rate": round(passed / total, 4) if total else 0.0,
    }

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "regression_summary": regression_summary,
        "regression_results": [r.__dict__ for r in regression_results],
        "concurrency_results": concurrency_results,
        "targets": {
            "api_p95_ms_target": 200,
            "api_success_rate_target": 0.99,
        },
    }

    out_path = REPORT_DIR / "phase_regression_load_report.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Regression: {passed}/{total} passed")
    for item in concurrency_results:
        print(
            f"[{item['endpoint']}] p95={item['latency_ms']['p95']}ms "
            f"p99={item['latency_ms']['p99']}ms success={item['success_rate']*100:.2f}%"
        )
    print(f"Report written: {out_path}")

    try:
        if db_path.exists():
            db_path.unlink()
    except Exception:
        pass

    return 0 if (total - passed) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
