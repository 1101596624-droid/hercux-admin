"""
Pattern Library Inspector

Browse and inspect stored generation patterns including:
- Pattern details and metadata
- Confidence scores
- Application history
- Success rates

Usage:
    python -m app.scripts.inspect_patterns [--step-type text_content] [--subject physics]

Created: 2026-02-13
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import argparse
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.models.models import GenerationPattern, PatternApplication
from app.core.config import settings


async def get_db_session() -> AsyncSession:
    """Create database session"""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return SessionLocal()


async def list_patterns(
    db: AsyncSession,
    step_type: Optional[str] = None,
    subject: Optional[str] = None,
    min_confidence: float = 0.0,
    pattern_type: Optional[str] = None,
) -> List[GenerationPattern]:
    """
    List patterns with optional filters

    Args:
        db: Database session
        step_type: Optional step type filter
        subject: Optional subject filter
        min_confidence: Minimum confidence threshold
        pattern_type: Optional pattern type filter

    Returns:
        List of matching patterns
    """
    query = select(GenerationPattern)

    # Apply filters
    filters = []
    if step_type:
        filters.append(GenerationPattern.step_type == step_type)
    if subject:
        filters.append(GenerationPattern.subject == subject)
    if pattern_type:
        filters.append(GenerationPattern.pattern_type == pattern_type)
    if min_confidence > 0:
        filters.append(GenerationPattern.confidence >= min_confidence)

    if filters:
        query = query.where(*filters)

    query = query.order_by(GenerationPattern.confidence.desc())

    result = await db.execute(query)
    return result.scalars().all()


async def get_pattern_details(
    db: AsyncSession,
    pattern_id: int
) -> dict:
    """
    Get detailed information about a specific pattern

    Args:
        db: Database session
        pattern_id: Pattern ID

    Returns:
        Pattern details including application history
    """
    # Get pattern
    result = await db.execute(
        select(GenerationPattern).where(GenerationPattern.id == pattern_id)
    )
    pattern = result.scalar_one_or_none()

    if not pattern:
        return {"error": "Pattern not found"}

    # Get applications
    result = await db.execute(
        select(PatternApplication)
        .where(PatternApplication.pattern_id == pattern_id)
        .order_by(PatternApplication.applied_at.desc())
    )
    applications = result.scalars().all()

    # Calculate application statistics
    if applications:
        successful = sum(1 for a in applications if a.was_successful)
        success_rate = (successful / len(applications)) * 100
        avg_quality = sum(a.result_quality_score for a in applications) / len(applications)
    else:
        success_rate = 0
        avg_quality = 0

    return {
        "pattern": pattern,
        "applications": applications,
        "stats": {
            "total_applications": len(applications),
            "successful_applications": successful if applications else 0,
            "success_rate": round(success_rate, 2),
            "average_result_quality": round(avg_quality, 2),
        }
    }


async def get_summary_statistics(db: AsyncSession) -> dict:
    """
    Get overall pattern library statistics

    Args:
        db: Database session

    Returns:
        Summary statistics
    """
    # Total patterns
    result = await db.execute(select(func.count(GenerationPattern.id)))
    total_patterns = result.scalar()

    # Get all patterns for detailed stats
    result = await db.execute(select(GenerationPattern))
    patterns = result.scalars().all()

    if not patterns:
        return {"total_patterns": 0}

    # Group by type
    by_step_type = defaultdict(int)
    by_pattern_type = defaultdict(int)
    by_subject = defaultdict(int)

    for pattern in patterns:
        by_step_type[pattern.step_type] += 1
        by_pattern_type[pattern.pattern_type] += 1
        by_subject[pattern.subject] += 1

    # Confidence distribution
    high_confidence = sum(1 for p in patterns if p.confidence >= 0.8)
    medium_confidence = sum(1 for p in patterns if 0.7 <= p.confidence < 0.8)
    low_confidence = sum(1 for p in patterns if p.confidence < 0.7)

    avg_confidence = sum(p.confidence for p in patterns) / len(patterns)

    # Get application stats
    result = await db.execute(select(PatternApplication))
    applications = result.scalars().all()

    total_applications = len(applications)
    successful_applications = sum(1 for a in applications if a.was_successful)

    return {
        "total_patterns": total_patterns,
        "by_step_type": dict(by_step_type),
        "by_pattern_type": dict(by_pattern_type),
        "by_subject": dict(by_subject),
        "confidence_distribution": {
            "high": high_confidence,
            "medium": medium_confidence,
            "low": low_confidence,
            "average": round(avg_confidence, 3),
        },
        "applications": {
            "total": total_applications,
            "successful": successful_applications,
            "success_rate": round((successful_applications / max(total_applications, 1)) * 100, 2),
        }
    }


def print_pattern_list(patterns: List[GenerationPattern]):
    """Print formatted list of patterns"""
    if not patterns:
        print("\nNo patterns found matching the criteria.")
        return

    print(f"\nFound {len(patterns)} patterns:\n")
    print("-" * 120)
    print(f"{'ID':<5} {'Type':<20} {'Step':<18} {'Subject':<12} {'Confidence':<12} {'Description'[:40]}")
    print("-" * 120)

    for pattern in patterns:
        desc = pattern.description[:50] + "..." if len(pattern.description) > 50 else pattern.description
        print(
            f"{pattern.id:<5} "
            f"{pattern.pattern_type:<20} "
            f"{pattern.step_type:<18} "
            f"{pattern.subject:<12} "
            f"{pattern.confidence:<12.3f} "
            f"{desc}"
        )

    print("-" * 120)


def print_pattern_details(details: dict):
    """Print detailed pattern information"""
    if "error" in details:
        print(f"\nError: {details['error']}")
        return

    pattern = details["pattern"]
    stats = details["stats"]
    applications = details["applications"]

    print("\n" + "=" * 80)
    print(f"PATTERN #{pattern.id} DETAILS")
    print("=" * 80)

    print("\nBASIC INFORMATION:")
    print(f"  Pattern Type:     {pattern.pattern_type}")
    print(f"  Step Type:        {pattern.step_type}")
    print(f"  Subject:          {pattern.subject}")
    print(f"  Topic:            {pattern.topic}")
    print(f"  Confidence:       {pattern.confidence:.3f}")
    print(f"  Created:          {pattern.created_at}")
    print(f"  Last Updated:     {pattern.updated_at}")

    print("\nDESCRIPTION:")
    print(f"  {pattern.description}")

    print("\nSTRATEGY GUIDANCE:")
    print(f"  {pattern.strategy_guidance}")

    if pattern.success_indicators:
        print("\nSUCCESS INDICATORS:")
        for indicator in pattern.success_indicators:
            print(f"  ✓ {indicator}")

    if pattern.common_pitfalls:
        print("\nCOMMON PITFALLS:")
        for pitfall in pattern.common_pitfalls:
            print(f"  ✗ {pitfall}")

    print("\nSOURCE INFORMATION:")
    print(f"  Templates Used:   {pattern.created_from_count}")
    if pattern.source_templates:
        print(f"  Source IDs:       {', '.join(str(s) for s in pattern.source_templates[:5])}")

    print("\nAPPLICATION STATISTICS:")
    print(f"  Total Applications:     {stats['total_applications']}")
    print(f"  Successful:             {stats['successful_applications']}")
    print(f"  Success Rate:           {stats['success_rate']:.2f}%")
    print(f"  Avg Result Quality:     {stats['average_result_quality']:.2f}")

    if applications:
        print("\nRECENT APPLICATIONS (last 5):")
        for app in applications[:5]:
            status = "✓" if app.was_successful else "✗"
            print(f"  {status} {app.applied_at} - Quality: {app.result_quality_score:.2f}")

    print("\n" + "=" * 80)


def print_summary(stats: dict):
    """Print summary statistics"""
    print("\n" + "=" * 80)
    print("PATTERN LIBRARY SUMMARY")
    print("=" * 80)

    print(f"\nTotal Patterns: {stats['total_patterns']}")

    if stats['total_patterns'] == 0:
        print("\nNo patterns in the library yet.")
        return

    print("\nBY STEP TYPE:")
    for step_type, count in stats['by_step_type'].items():
        print(f"  {step_type:<20} {count:>5} patterns")

    print("\nBY PATTERN TYPE:")
    for pattern_type, count in stats['by_pattern_type'].items():
        print(f"  {pattern_type:<20} {count:>5} patterns")

    print("\nBY SUBJECT:")
    for subject, count in stats['by_subject'].items():
        print(f"  {subject:<20} {count:>5} patterns")

    print("\nCONFIDENCE DISTRIBUTION:")
    conf = stats['confidence_distribution']
    print(f"  High (≥0.8):       {conf['high']:>5} patterns")
    print(f"  Medium (0.7-0.8):  {conf['medium']:>5} patterns")
    print(f"  Low (<0.7):        {conf['low']:>5} patterns")
    print(f"  Average:           {conf['average']:.3f}")

    print("\nAPPLICATION STATISTICS:")
    apps = stats['applications']
    print(f"  Total Applications:    {apps['total']}")
    print(f"  Successful:            {apps['successful']}")
    print(f"  Success Rate:          {apps['success_rate']:.2f}%")

    print("\n" + "=" * 80)


async def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="Inspect Agent Learning System pattern library"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all patterns"
    )
    parser.add_argument(
        "--detail",
        type=int,
        metavar="ID",
        help="Show detailed information for pattern ID"
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show summary statistics (default)"
    )
    parser.add_argument(
        "--step-type",
        type=str,
        help="Filter by step type"
    )
    parser.add_argument(
        "--subject",
        type=str,
        help="Filter by subject"
    )
    parser.add_argument(
        "--pattern-type",
        type=str,
        choices=["best_practice", "failure_recovery", "optimization"],
        help="Filter by pattern type"
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.0,
        help="Minimum confidence threshold (0-1)"
    )

    args = parser.parse_args()

    # Default to summary if no action specified
    if not (args.list or args.detail or args.summary):
        args.summary = True

    # Get database session
    db = await get_db_session()

    try:
        if args.detail:
            # Show detailed pattern information
            details = await get_pattern_details(db, args.detail)
            print_pattern_details(details)

        elif args.list:
            # List patterns
            patterns = await list_patterns(
                db,
                step_type=args.step_type,
                subject=args.subject,
                min_confidence=args.min_confidence,
                pattern_type=args.pattern_type,
            )
            print_pattern_list(patterns)

        elif args.summary:
            # Show summary statistics
            stats = await get_summary_statistics(db)
            print_summary(stats)

    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())
