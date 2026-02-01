"""
Admin AI Monitor API
Provides AI API usage monitoring and cost tracking for administrators
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, distinct, desc
from typing import Optional
from datetime import datetime, timedelta, timezone

from app.db.session import get_db
from app.models.models import User, TokenUsage, ChatHistory
from app.core.security import get_current_admin_user

router = APIRouter()

# Model pricing (per 1M tokens)
MODEL_PRICING = {
    "claude-sonnet-4-20250514": {"input": 3.0, "output": 15.0},
    "claude-3-5-sonnet-20241022": {"input": 3.0, "output": 15.0},
    "claude-haiku-4": {"input": 0.25, "output": 1.25},
    "gpt-4o": {"input": 2.5, "output": 10.0},
    "deepseek-chat": {"input": 0.14, "output": 0.28},
}

DEFAULT_PRICING = {"input": 3.0, "output": 15.0}


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate cost based on model and token counts"""
    pricing = MODEL_PRICING.get(model, DEFAULT_PRICING)
    cost = (input_tokens * pricing["input"] / 1_000_000) + (output_tokens * pricing["output"] / 1_000_000)
    return round(cost, 4)


# ============ AI Overview ============

@router.get("/ai/overview")
async def get_ai_overview(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI API usage overview for today
    """
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timedelta(days=1)

    # Today's stats
    today_result = await db.execute(
        select(
            func.count(),
            func.sum(TokenUsage.total_tokens),
            func.sum(TokenUsage.input_tokens),
            func.sum(TokenUsage.output_tokens)
        ).where(TokenUsage.created_at >= today_start)
    )
    today_row = today_result.one()
    today_calls = today_row[0] or 0
    today_total_tokens = today_row[1] or 0
    today_input_tokens = today_row[2] or 0
    today_output_tokens = today_row[3] or 0

    # Yesterday's stats for comparison
    yesterday_result = await db.execute(
        select(
            func.count(),
            func.sum(TokenUsage.input_tokens),
            func.sum(TokenUsage.output_tokens)
        ).where(
            TokenUsage.created_at >= yesterday_start,
            TokenUsage.created_at < today_start
        )
    )
    yesterday_row = yesterday_result.one()
    yesterday_calls = yesterday_row[0] or 0
    yesterday_input = yesterday_row[1] or 0
    yesterday_output = yesterday_row[2] or 0

    # Calculate costs
    today_cost = 0.0
    cost_result = await db.execute(
        select(TokenUsage.model, TokenUsage.input_tokens, TokenUsage.output_tokens)
        .where(TokenUsage.created_at >= today_start)
    )
    for row in cost_result.all():
        today_cost += calculate_cost(row[0], row[1], row[2])

    yesterday_cost = 0.0
    yesterday_cost_result = await db.execute(
        select(TokenUsage.model, TokenUsage.input_tokens, TokenUsage.output_tokens)
        .where(
            TokenUsage.created_at >= yesterday_start,
            TokenUsage.created_at < today_start
        )
    )
    for row in yesterday_cost_result.all():
        yesterday_cost += calculate_cost(row[0], row[1], row[2])

    # Calculate comparisons
    calls_change = ((today_calls - yesterday_calls) / max(yesterday_calls, 1))
    cost_change = ((today_cost - yesterday_cost) / max(yesterday_cost, 0.01))

    # Error rate (simplified - count failed requests if we had status tracking)
    # For now, assume 0.8% error rate as placeholder
    error_rate = 0.008

    # Average latency (placeholder - would need latency tracking)
    avg_latency = 1250

    return {
        "today": {
            "call_count": today_calls,
            "total_tokens": today_total_tokens,
            "total_cost": round(today_cost, 2),
            "avg_latency_ms": avg_latency,
            "error_rate": error_rate
        },
        "comparisons": {
            "calls_vs_yesterday": round(calls_change, 2),
            "cost_vs_yesterday": round(cost_change, 2)
        }
    }


# ============ AI Trends ============

@router.get("/ai/trends")
async def get_ai_trends(
    period: str = Query("24h", description="Period: 24h, 7d, 30d"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI API call trends over time
    """
    now = datetime.now(timezone.utc)
    hours = {"24h": 24, "7d": 168, "30d": 720}.get(period, 24)
    start_time = now - timedelta(hours=hours)

    trend_data = []

    if period == "24h":
        # Hourly data for 24h
        for i in range(0, 24, 4):  # Every 4 hours
            hour_start = start_time + timedelta(hours=i)
            hour_end = hour_start + timedelta(hours=4)

            result = await db.execute(
                select(
                    func.count(),
                    func.sum(TokenUsage.total_tokens),
                    func.sum(TokenUsage.input_tokens),
                    func.sum(TokenUsage.output_tokens)
                ).where(
                    TokenUsage.created_at >= hour_start,
                    TokenUsage.created_at < hour_end
                )
            )
            row = result.one()
            call_count = row[0] or 0
            tokens = row[1] or 0
            input_t = row[2] or 0
            output_t = row[3] or 0

            # Calculate cost for this period
            cost = (input_t * 3.0 / 1_000_000) + (output_t * 15.0 / 1_000_000)

            trend_data.append({
                "time": hour_start.strftime("%H:00"),
                "call_count": call_count,
                "tokens": tokens,
                "cost": round(cost, 2)
            })
    else:
        # Daily data
        days = hours // 24
        for i in range(days):
            day_start = (start_time + timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)

            result = await db.execute(
                select(
                    func.count(),
                    func.sum(TokenUsage.total_tokens),
                    func.sum(TokenUsage.input_tokens),
                    func.sum(TokenUsage.output_tokens)
                ).where(
                    TokenUsage.created_at >= day_start,
                    TokenUsage.created_at < day_end
                )
            )
            row = result.one()
            call_count = row[0] or 0
            tokens = row[1] or 0
            input_t = row[2] or 0
            output_t = row[3] or 0

            cost = (input_t * 3.0 / 1_000_000) + (output_t * 15.0 / 1_000_000)

            trend_data.append({
                "time": day_start.strftime("%m/%d"),
                "call_count": call_count,
                "tokens": tokens,
                "cost": round(cost, 2)
            })

    return trend_data


# ============ AI Costs ============

@router.get("/ai/costs")
async def get_ai_costs(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI API cost breakdown by model
    """
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Get breakdown by model
    model_result = await db.execute(
        select(
            TokenUsage.model,
            func.count(),
            func.sum(TokenUsage.total_tokens),
            func.sum(TokenUsage.input_tokens),
            func.sum(TokenUsage.output_tokens)
        ).where(
            TokenUsage.created_at >= month_start
        ).group_by(TokenUsage.model)
    )

    breakdown = []
    total_cost = 0.0

    for row in model_result.all():
        model = row[0]
        call_count = row[1] or 0
        tokens = row[2] or 0
        input_t = row[3] or 0
        output_t = row[4] or 0

        cost = calculate_cost(model, input_t, output_t)
        total_cost += cost

        breakdown.append({
            "model": model,
            "call_count": call_count,
            "tokens": tokens,
            "cost": round(cost, 2),
            "percentage": 0  # Will calculate after
        })

    # Calculate percentages
    for item in breakdown:
        item["percentage"] = round(item["cost"] / max(total_cost, 0.01), 3)

    # Sort by cost descending
    breakdown.sort(key=lambda x: x["cost"], reverse=True)

    # Budget settings (could be from config)
    budget = 5000.0
    budget_usage = total_cost / budget

    # Forecast month-end cost
    days_passed = (now - month_start).days + 1
    days_in_month = 30
    daily_avg = total_cost / max(days_passed, 1)
    month_end_cost = daily_avg * days_in_month

    return {
        "total_cost": round(total_cost, 2),
        "budget": budget,
        "budget_usage": round(budget_usage, 3),
        "breakdown": breakdown,
        "forecast": {
            "month_end_cost": round(month_end_cost, 2),
            "will_exceed_budget": month_end_cost > budget
        }
    }


# ============ AI Logs ============

@router.get("/ai/logs")
async def get_ai_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    feature: Optional[str] = Query(None, description="Filter by feature"),
    model: Optional[str] = Query(None, description="Filter by model"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI API call logs with pagination
    """
    # Build query
    query = select(TokenUsage, User).outerjoin(User, TokenUsage.user_id == User.id)

    filters = []
    if feature:
        filters.append(TokenUsage.feature == feature)
    if model:
        filters.append(TokenUsage.model == model)

    if filters:
        query = query.where(and_(*filters))

    # Get total count
    count_query = select(func.count()).select_from(TokenUsage)
    if filters:
        count_query = count_query.where(and_(*filters))
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination and ordering
    offset = (page - 1) * limit
    query = query.order_by(desc(TokenUsage.created_at)).offset(offset).limit(limit)

    result = await db.execute(query)
    rows = result.all()

    logs = []
    for token_usage, user in rows:
        cost = calculate_cost(token_usage.model, token_usage.input_tokens, token_usage.output_tokens)
        logs.append({
            "id": f"log_{token_usage.id}",
            "user_id": token_usage.user_id,
            "user_name": user.username if user else "匿名用户",
            "scene": token_usage.feature,
            "model": token_usage.model,
            "input_tokens": token_usage.input_tokens,
            "output_tokens": token_usage.output_tokens,
            "latency_ms": 1200,  # Placeholder - would need latency tracking
            "status": "success",
            "cost": cost,
            "created_at": token_usage.created_at.isoformat() if token_usage.created_at else None
        })

    return {
        "data": logs,
        "total": total,
        "page": page,
        "limit": limit
    }


# ============ AI Alerts ============

@router.get("/ai/alerts")
async def get_ai_alerts(
    status: Optional[str] = Query(None, description="Filter by status: open, acknowledged, resolved"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI API alerts (cost thresholds, error rates, etc.)
    """
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    alerts = []

    # Check today's cost
    cost_result = await db.execute(
        select(
            func.sum(TokenUsage.input_tokens),
            func.sum(TokenUsage.output_tokens)
        ).where(TokenUsage.created_at >= today_start)
    )
    cost_row = cost_result.one()
    today_input = cost_row[0] or 0
    today_output = cost_row[1] or 0
    today_cost = (today_input * 3.0 / 1_000_000) + (today_output * 15.0 / 1_000_000)

    # Cost threshold alert
    cost_threshold = 300.0
    if today_cost > cost_threshold:
        alerts.append({
            "id": 1,
            "alert_type": "cost_exceed",
            "severity": "critical",
            "title": "日成本超过阈值",
            "message": f"今日 AI 成本已达 ${today_cost:.2f}，超过设定阈值 ${cost_threshold:.2f}",
            "metric_value": round(today_cost, 2),
            "threshold_value": cost_threshold,
            "status": "open",
            "created_at": now.isoformat()
        })

    # Check for high usage users
    high_usage_result = await db.execute(
        select(
            TokenUsage.user_id,
            func.count()
        ).where(
            TokenUsage.created_at >= today_start,
            TokenUsage.user_id.isnot(None)
        ).group_by(TokenUsage.user_id).having(func.count() > 100)
    )
    high_usage_users = high_usage_result.all()

    for user_id, call_count in high_usage_users:
        alerts.append({
            "id": len(alerts) + 1,
            "alert_type": "user_abuse",
            "severity": "warning",
            "title": "用户调用异常",
            "message": f"用户 ID:{user_id} 今日调用次数达 {call_count} 次",
            "metric_value": call_count,
            "threshold_value": 100,
            "status": "open",
            "created_at": now.isoformat()
        })

    # Filter by status if provided
    if status:
        alerts = [a for a in alerts if a["status"] == status]

    # Calculate stats
    stats = {
        "open": len([a for a in alerts if a["status"] == "open"]),
        "acknowledged": len([a for a in alerts if a["status"] == "acknowledged"]),
        "resolved": len([a for a in alerts if a["status"] == "resolved"])
    }

    return {
        "data": alerts,
        "stats": stats
    }
