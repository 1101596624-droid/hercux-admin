"""
Cost Monitoring Script for Agent Learning System

Monitors and reports on:
- Agent evaluation frequency
- Cost statistics (token usage)
- Evaluation trends over time
- Skip rate analysis

Usage:
    python -m app.scripts.monitor_costs [--days 7] [--step-type text_content]

Created: 2026-02-13
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import argparse
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.models.models import QualityEvaluation, PatternApplication, GenerationPattern
from app.core.config import settings


# Cost estimation (approximate based on Claude 3.5 Sonnet pricing)
COST_PER_1K_INPUT_TOKENS = 0.003  # $3 per million input tokens
COST_PER_1K_OUTPUT_TOKENS = 0.015  # $15 per million output tokens
AVG_AGENT_INPUT_TOKENS = 2000  # Estimated average for agent evaluation
AVG_AGENT_OUTPUT_TOKENS = 500   # Estimated average for agent response


async def get_db_session() -> AsyncSession:
    """Create database session"""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return SessionLocal()


async def calculate_agent_evaluation_stats(
    db: AsyncSession,
    days: int = 7,
    step_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculate Agent evaluation statistics

    Args:
        db: Database session
        days: Number of days to look back
        step_type: Optional filter by step type

    Returns:
        Dictionary with cost and frequency statistics
    """
    start_date = datetime.now() - timedelta(days=days)

    # Build query
    query = select(QualityEvaluation).where(
        QualityEvaluation.evaluated_at >= start_date
    )

    if step_type:
        query = query.where(QualityEvaluation.content_type == step_type)

    result = await db.execute(query)
    evaluations = result.scalars().all()

    total_evaluations = len(evaluations)
    high_quality_count = sum(1 for e in evaluations if e.quality_score >= 75)
    low_quality_count = sum(1 for e in evaluations if e.quality_score < 60)

    # Estimate agent evaluations (those that used Agent review)
    # In real implementation, this would track actual agent usage
    # For now, estimate based on quality distribution
    estimated_agent_evals = low_quality_count + int(high_quality_count * 0.3)

    # Calculate costs
    estimated_input_tokens = estimated_agent_evals * AVG_AGENT_INPUT_TOKENS
    estimated_output_tokens = estimated_agent_evals * AVG_AGENT_OUTPUT_TOKENS

    estimated_cost = (
        (estimated_input_tokens / 1000) * COST_PER_1K_INPUT_TOKENS +
        (estimated_output_tokens / 1000) * COST_PER_1K_OUTPUT_TOKENS
    )

    # Calculate daily averages
    daily_evaluations = total_evaluations / max(days, 1)
    daily_cost = estimated_cost / max(days, 1)

    # Calculate skip rate (evaluations without agent)
    skip_rate = ((total_evaluations - estimated_agent_evals) / max(total_evaluations, 1)) * 100

    return {
        "period_days": days,
        "total_evaluations": total_evaluations,
        "estimated_agent_evaluations": estimated_agent_evals,
        "high_quality_count": high_quality_count,
        "low_quality_count": low_quality_count,
        "estimated_tokens": {
            "input": estimated_input_tokens,
            "output": estimated_output_tokens,
            "total": estimated_input_tokens + estimated_output_tokens,
        },
        "estimated_cost_usd": round(estimated_cost, 4),
        "daily_averages": {
            "evaluations": round(daily_evaluations, 2),
            "cost_usd": round(daily_cost, 4),
        },
        "skip_rate_percent": round(skip_rate, 2),
        "savings_percent": round(skip_rate, 2),  # Skip rate = cost savings
    }


async def calculate_step_type_breakdown(
    db: AsyncSession,
    days: int = 7
) -> Dict[str, Dict[str, Any]]:
    """
    Calculate cost breakdown by step type

    Args:
        db: Database session
        days: Number of days to look back

    Returns:
        Dictionary with stats per step type
    """
    start_date = datetime.now() - timedelta(days=days)

    result = await db.execute(
        select(QualityEvaluation).where(
            QualityEvaluation.evaluated_at >= start_date
        )
    )
    evaluations = result.scalars().all()

    # Group by content type
    by_type = defaultdict(list)
    for eval in evaluations:
        by_type[eval.content_type].append(eval)

    breakdown = {}
    for content_type, evals in by_type.items():
        total = len(evals)
        high_quality = sum(1 for e in evals if e.quality_score >= 75)
        avg_score = sum(e.quality_score for e in evals) / max(total, 1)

        # Estimate agent usage
        estimated_agent = int(total * 0.4)  # Rough estimate
        estimated_cost = (
            (estimated_agent * AVG_AGENT_INPUT_TOKENS / 1000) * COST_PER_1K_INPUT_TOKENS +
            (estimated_agent * AVG_AGENT_OUTPUT_TOKENS / 1000) * COST_PER_1K_OUTPUT_TOKENS
        )

        breakdown[content_type] = {
            "total_evaluations": total,
            "high_quality_count": high_quality,
            "average_score": round(avg_score, 2),
            "estimated_cost_usd": round(estimated_cost, 4),
        }

    return breakdown


async def calculate_pattern_usage_stats(
    db: AsyncSession,
    days: int = 7
) -> Dict[str, Any]:
    """
    Calculate pattern application statistics

    Args:
        db: Database session
        days: Number of days to look back

    Returns:
        Pattern usage statistics
    """
    start_date = datetime.now() - timedelta(days=days)

    result = await db.execute(
        select(PatternApplication).where(
            PatternApplication.applied_at >= start_date
        )
    )
    applications = result.scalars().all()

    total_applications = len(applications)
    successful_applications = sum(1 for a in applications if a.was_successful)

    # Average quality improvement
    avg_quality = sum(a.result_quality_score for a in applications) / max(total_applications, 1)

    success_rate = (successful_applications / max(total_applications, 1)) * 100

    return {
        "total_pattern_applications": total_applications,
        "successful_applications": successful_applications,
        "success_rate_percent": round(success_rate, 2),
        "average_result_quality": round(avg_quality, 2),
    }


async def calculate_trend_analysis(
    db: AsyncSession,
    days: int = 30
) -> Dict[str, Any]:
    """
    Analyze trends over time

    Args:
        db: Database session
        days: Number of days to analyze

    Returns:
        Trend analysis data
    """
    start_date = datetime.now() - timedelta(days=days)

    result = await db.execute(
        select(QualityEvaluation).where(
            QualityEvaluation.evaluated_at >= start_date
        ).order_by(QualityEvaluation.evaluated_at)
    )
    evaluations = result.scalars().all()

    if not evaluations:
        return {"trend": "no_data"}

    # Split into two halves
    mid_point = len(evaluations) // 2
    first_half = evaluations[:mid_point]
    second_half = evaluations[mid_point:]

    avg_first = sum(e.quality_score for e in first_half) / max(len(first_half), 1)
    avg_second = sum(e.quality_score for e in second_half) / max(len(second_half), 1)

    improvement = avg_second - avg_first
    improvement_percent = (improvement / max(avg_first, 1)) * 100

    return {
        "period_days": days,
        "first_half_avg_score": round(avg_first, 2),
        "second_half_avg_score": round(avg_second, 2),
        "improvement": round(improvement, 2),
        "improvement_percent": round(improvement_percent, 2),
        "trend": "improving" if improvement > 0 else "declining" if improvement < 0 else "stable",
    }


def print_cost_dashboard(stats: Dict[str, Any]):
    """Print formatted cost dashboard"""
    print("\n" + "=" * 80)
    print("AGENT LEARNING SYSTEM - COST MONITORING DASHBOARD")
    print("=" * 80)
    print(f"\nReport Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Analysis Period: Last {stats['overview']['period_days']} days")

    print("\n" + "-" * 80)
    print("OVERVIEW")
    print("-" * 80)
    overview = stats['overview']
    print(f"Total Evaluations:           {overview['total_evaluations']}")
    print(f"Agent Evaluations (est.):    {overview['estimated_agent_evaluations']}")
    print(f"High Quality (≥75):          {overview['high_quality_count']}")
    print(f"Low Quality (<60):           {overview['low_quality_count']}")
    print(f"\nEstimated Token Usage:")
    print(f"  Input Tokens:              {overview['estimated_tokens']['input']:,}")
    print(f"  Output Tokens:             {overview['estimated_tokens']['output']:,}")
    print(f"  Total Tokens:              {overview['estimated_tokens']['total']:,}")
    print(f"\nEstimated Cost:              ${overview['estimated_cost_usd']:.4f}")
    print(f"Daily Average Cost:          ${overview['daily_averages']['cost_usd']:.4f}")
    print(f"\nSmart Skip Rate:             {overview['skip_rate_percent']:.2f}%")
    print(f"Estimated Cost Savings:      {overview['savings_percent']:.2f}%")

    print("\n" + "-" * 80)
    print("BREAKDOWN BY STEP TYPE")
    print("-" * 80)
    for step_type, data in stats['breakdown'].items():
        print(f"\n{step_type}:")
        print(f"  Evaluations:               {data['total_evaluations']}")
        print(f"  High Quality:              {data['high_quality_count']}")
        print(f"  Average Score:             {data['average_score']:.2f}")
        print(f"  Estimated Cost:            ${data['estimated_cost_usd']:.4f}")

    print("\n" + "-" * 80)
    print("PATTERN USAGE")
    print("-" * 80)
    patterns = stats['patterns']
    print(f"Total Pattern Applications:  {patterns['total_pattern_applications']}")
    print(f"Successful Applications:     {patterns['successful_applications']}")
    print(f"Success Rate:                {patterns['success_rate_percent']:.2f}%")
    print(f"Avg Result Quality:          {patterns['average_result_quality']:.2f}")

    print("\n" + "-" * 80)
    print("TREND ANALYSIS (30 days)")
    print("-" * 80)
    trends = stats['trends']
    if trends['trend'] != 'no_data':
        print(f"First Half Avg Score:        {trends['first_half_avg_score']:.2f}")
        print(f"Second Half Avg Score:       {trends['second_half_avg_score']:.2f}")
        print(f"Improvement:                 {trends['improvement']:+.2f}")
        print(f"Improvement %:               {trends['improvement_percent']:+.2f}%")
        print(f"Trend:                       {trends['trend'].upper()}")
    else:
        print("Insufficient data for trend analysis")

    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)

    # Generate recommendations
    if overview['skip_rate_percent'] < 40:
        print("⚠️  Skip rate is low. Consider adjusting AGENT_EVAL_PROBABILITY_THRESHOLD")

    if overview['estimated_cost_usd'] / overview['period_days'] > 1.0:
        print("⚠️  Daily costs are high. Review evaluation frequency.")

    if patterns['success_rate_percent'] < 70:
        print("⚠️  Pattern success rate is low. Review pattern quality and applicability.")

    if trends.get('trend') == 'declining':
        print("⚠️  Quality trend is declining. Review recent changes and patterns.")

    if stats['overview']['high_quality_count'] / max(stats['overview']['total_evaluations'], 1) > 0.8:
        print("✅ High quality rate is excellent! Learning system is effective.")

    print("\n")


async def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="Monitor Agent Learning System costs and usage"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to analyze (default: 7)"
    )
    parser.add_argument(
        "--step-type",
        type=str,
        default=None,
        help="Filter by specific step type"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    # Get database session
    db = await get_db_session()

    try:
        # Gather all statistics
        overview = await calculate_agent_evaluation_stats(
            db, days=args.days, step_type=args.step_type
        )
        breakdown = await calculate_step_type_breakdown(db, days=args.days)
        patterns = await calculate_pattern_usage_stats(db, days=args.days)
        trends = await calculate_trend_analysis(db, days=30)

        stats = {
            "overview": overview,
            "breakdown": breakdown,
            "patterns": patterns,
            "trends": trends,
        }

        # Output
        if args.json:
            import json
            print(json.dumps(stats, indent=2))
        else:
            print_cost_dashboard(stats)

    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())
