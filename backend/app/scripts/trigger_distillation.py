"""
Manual Distillation Trigger Script

Manually trigger experience distillation for specific step types and subjects.
Useful for:
- On-demand pattern extraction
- Testing distillation process
- Recovering from failed auto-distillation
- Immediate learning from recent changes

Usage:
    python -m app.scripts.trigger_distillation --step-type text_content --subject physics

Created: 2026-02-13
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import argparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.services.learning.distillation_service import DistillationService
from app.models.models import QualityEvaluation, GenerationPattern
from app.core.config import settings


async def get_db_session() -> AsyncSession:
    """Create database session"""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return SessionLocal()


async def check_data_availability(
    db: AsyncSession,
    step_type: str,
    subject: str,
    lookback_days: int = 7
) -> dict:
    """
    Check if there's enough data for distillation

    Args:
        db: Database session
        step_type: Step type to check
        subject: Subject to check
        lookback_days: Days to look back

    Returns:
        Data availability statistics
    """
    from datetime import timedelta
    start_date = datetime.now() - timedelta(days=lookback_days)

    # Count evaluations
    result = await db.execute(
        select(QualityEvaluation).where(
            QualityEvaluation.content_type == step_type,
            QualityEvaluation.evaluated_at >= start_date
        )
    )
    evaluations = result.scalars().all()

    success_cases = [e for e in evaluations if e.quality_score >= 75]
    failure_cases = [e for e in evaluations if e.quality_score <= 60]

    # Check existing patterns
    result = await db.execute(
        select(GenerationPattern).where(
            GenerationPattern.step_type == step_type,
            GenerationPattern.subject == subject
        )
    )
    existing_patterns = result.scalars().all()

    return {
        "total_evaluations": len(evaluations),
        "success_cases": len(success_cases),
        "failure_cases": len(failure_cases),
        "existing_patterns": len(existing_patterns),
        "has_sufficient_data": len(evaluations) >= 10,  # Minimum threshold
        "can_extract_success_patterns": len(success_cases) >= 3,
        "can_extract_anti_patterns": len(failure_cases) >= 2,
    }


async def trigger_distillation(
    db: AsyncSession,
    step_type: str,
    subject: str,
    lookback_days: int = 7,
    min_quality_threshold: float = 75.0,
    max_quality_threshold: float = 60.0,
    dry_run: bool = False,
) -> dict:
    """
    Manually trigger distillation process

    Args:
        db: Database session
        step_type: Step type to distill
        subject: Subject area
        lookback_days: Days to look back
        min_quality_threshold: Minimum quality for success patterns
        max_quality_threshold: Maximum quality for failure patterns
        dry_run: If True, only simulate without saving

    Returns:
        Distillation results
    """
    print(f"\n{'='*80}")
    print("MANUAL DISTILLATION TRIGGER")
    print(f"{'='*80}")
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Step Type: {step_type}")
    print(f"Subject: {subject}")
    print(f"Lookback Days: {lookback_days}")
    print(f"Dry Run: {dry_run}")

    # Check data availability
    print(f"\n{'-'*80}")
    print("DATA AVAILABILITY CHECK")
    print(f"{'-'*80}")

    availability = await check_data_availability(db, step_type, subject, lookback_days)

    print(f"Total Evaluations: {availability['total_evaluations']}")
    print(f"Success Cases (≥75): {availability['success_cases']}")
    print(f"Failure Cases (≤60): {availability['failure_cases']}")
    print(f"Existing Patterns: {availability['existing_patterns']}")

    if not availability['has_sufficient_data']:
        print(f"\n⚠️  WARNING: Insufficient data for distillation (need at least 10 evaluations)")
        print("Recommendation: Continue generating content to gather more data.")
        return {"status": "insufficient_data", "details": availability}

    if not (availability['can_extract_success_patterns'] or availability['can_extract_anti_patterns']):
        print(f"\n⚠️  WARNING: Not enough distinct cases for pattern extraction")
        return {"status": "insufficient_cases", "details": availability}

    print(f"\n✅ Sufficient data available for distillation")

    if dry_run:
        print(f"\n💡 DRY RUN MODE - No patterns will be saved")
        return {"status": "dry_run", "details": availability}

    # Initialize distillation service
    print(f"\n{'-'*80}")
    print("INITIALIZING DISTILLATION SERVICE")
    print(f"{'-'*80}")

    api_key = settings.anthropic_key
    if not api_key:
        print(f"\n❌ ERROR: Anthropic API key not configured")
        return {"status": "error", "message": "Missing API key"}

    distillation_service = DistillationService(db, api_key)

    # Run distillation
    print(f"\n{'-'*80}")
    print("RUNNING DISTILLATION PROCESS")
    print(f"{'-'*80}")
    print("\nThis may take a few minutes as patterns are extracted using Claude...\n")

    try:
        results = await distillation_service.distill_patterns(
            step_type=step_type,
            subject=subject,
            lookback_days=lookback_days,
            min_quality_threshold=min_quality_threshold,
            max_quality_threshold=max_quality_threshold,
        )

        # Print results
        print(f"\n{'-'*80}")
        print("DISTILLATION RESULTS")
        print(f"{'-'*80}")

        success_patterns = results.get('success_patterns', [])
        anti_patterns = results.get('anti_patterns', [])

        print(f"\nSuccess Patterns Extracted: {len(success_patterns)}")
        if success_patterns:
            for i, pattern in enumerate(success_patterns, 1):
                print(f"\n  {i}. {pattern.description}")
                print(f"     Confidence: {pattern.confidence:.3f}")
                print(f"     Strategy: {pattern.strategy_guidance[:100]}...")

        print(f"\nAnti-Patterns Extracted: {len(anti_patterns)}")
        if anti_patterns:
            for i, pattern in enumerate(anti_patterns, 1):
                print(f"\n  {i}. {pattern.description}")
                print(f"     Confidence: {pattern.confidence:.3f}")
                print(f"     Pitfalls: {', '.join(pattern.common_pitfalls[:3])}")

        print(f"\n{'='*80}")
        print("✅ DISTILLATION COMPLETED SUCCESSFULLY")
        print(f"{'='*80}")

        return {
            "status": "success",
            "success_patterns_count": len(success_patterns),
            "anti_patterns_count": len(anti_patterns),
            "results": results,
        }

    except Exception as e:
        print(f"\n❌ ERROR during distillation: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}


async def list_distillation_targets(db: AsyncSession) -> dict:
    """
    List all available step types and subjects that can be distilled

    Args:
        db: Database session

    Returns:
        Available targets for distillation
    """
    from collections import defaultdict
    from datetime import timedelta

    start_date = datetime.now() - timedelta(days=7)

    result = await db.execute(
        select(QualityEvaluation).where(
            QualityEvaluation.evaluated_at >= start_date
        )
    )
    evaluations = result.scalars().all()

    # Group by step type
    by_type = defaultdict(lambda: defaultdict(int))
    for eval in evaluations:
        # Note: subject would need to be tracked in QualityEvaluation for accurate grouping
        by_type[eval.content_type]['count'] += 1
        if eval.quality_score >= 75:
            by_type[eval.content_type]['success'] += 1
        elif eval.quality_score <= 60:
            by_type[eval.content_type]['failure'] += 1

    targets = []
    for step_type, stats in by_type.items():
        targets.append({
            'step_type': step_type,
            'total_evaluations': stats['count'],
            'success_cases': stats.get('success', 0),
            'failure_cases': stats.get('failure', 0),
            'ready': stats['count'] >= 10,
        })

    return {'targets': targets}


def print_targets(targets: dict):
    """Print available distillation targets"""
    print(f"\n{'='*80}")
    print("AVAILABLE DISTILLATION TARGETS (Last 7 Days)")
    print(f"{'='*80}\n")

    if not targets['targets']:
        print("No evaluation data available for distillation.")
        return

    print(f"{'Step Type':<25} {'Total':<10} {'Success':<10} {'Failure':<10} {'Ready'}")
    print("-" * 80)

    for target in targets['targets']:
        ready_mark = "✅" if target['ready'] else "❌"
        print(
            f"{target['step_type']:<25} "
            f"{target['total_evaluations']:<10} "
            f"{target['success_cases']:<10} "
            f"{target['failure_cases']:<10} "
            f"{ready_mark}"
        )

    print("\n✅ = Ready for distillation (>= 10 evaluations)")
    print("❌ = Needs more data")
    print()


async def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="Manually trigger experience distillation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available targets
  python -m app.scripts.trigger_distillation --list

  # Trigger distillation for text_content
  python -m app.scripts.trigger_distillation --step-type text_content --subject physics

  # Dry run (preview without saving)
  python -m app.scripts.trigger_distillation --step-type assessment --subject math --dry-run

  # Custom thresholds
  python -m app.scripts.trigger_distillation --step-type illustrated_content --subject biology --min-quality 80 --max-quality 55
        """
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List available distillation targets"
    )
    parser.add_argument(
        "--step-type",
        type=str,
        choices=["text_content", "illustrated_content", "assessment", "ai_tutor"],
        help="Step type to distill"
    )
    parser.add_argument(
        "--subject",
        type=str,
        help="Subject area (e.g., physics, mathematics, biology)"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to look back (default: 7)"
    )
    parser.add_argument(
        "--min-quality",
        type=float,
        default=75.0,
        help="Minimum quality threshold for success patterns (default: 75.0)"
    )
    parser.add_argument(
        "--max-quality",
        type=float,
        default=60.0,
        help="Maximum quality threshold for failure patterns (default: 60.0)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate distillation without saving patterns"
    )

    args = parser.parse_args()

    # Get database session
    db = await get_db_session()

    try:
        if args.list:
            # List available targets
            targets = await list_distillation_targets(db)
            print_targets(targets)

        elif args.step_type and args.subject:
            # Trigger distillation
            result = await trigger_distillation(
                db=db,
                step_type=args.step_type,
                subject=args.subject,
                lookback_days=args.days,
                min_quality_threshold=args.min_quality,
                max_quality_threshold=args.max_quality,
                dry_run=args.dry_run,
            )

            # Exit with appropriate code
            if result['status'] in ['error', 'insufficient_data', 'insufficient_cases']:
                sys.exit(1)

        else:
            parser.print_help()
            print("\n⚠️  Error: Either --list or both --step-type and --subject are required")
            sys.exit(1)

    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())
