#!/usr/bin/env python3
"""
Database Schema Pre-deployment Check
Run before deployment to verify production database schema matches code definitions.

This script automatically reads enum values from code, ensuring any new values
added to the codebase will be detected as missing in production.

Checks:
1. Enum types and values
2. Required tables
3. Column types (especially enum columns that might be TEXT in production)
4. Tables referenced in raw SQL
"""
import asyncio
import sys
import os
import re

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Import enums from models - this ensures we always check against actual code
from app.models.models import (
    DifficultyLevel,
    NodeType,
    NodeStatus,
    StudioPackageStatus,
    BadgeCategory,
    BadgeRarity,
    IconCategory,
)


def get_enum_values(enum_class):
    """Extract all values from an enum class"""
    return [e.value for e in enum_class]


# Auto-generate required enums from code definitions
REQUIRED_ENUMS = {
    'difficultylevel': get_enum_values(DifficultyLevel),
    'nodetype': get_enum_values(NodeType),
    'nodestatus': get_enum_values(NodeStatus),
    'studiopackagestatus': get_enum_values(StudioPackageStatus),
    'badgecategory': get_enum_values(BadgeCategory),
    'badgerarity': get_enum_values(BadgeRarity),
    'iconcategory': get_enum_values(IconCategory),
}

# Tables defined in ORM models
ORM_TABLES = [
    'users',
    'courses',
    'course_nodes',
    'learning_progress',
    'training_plans',
    'achievements',
    'user_courses',
    'chat_history',
    'simulator_results',
    'learning_statistics',
    'studio_processors',
    'studio_packages',
    'token_usage',
    'badge_configs',
    'skill_tree_configs',
    'skill_achievement_configs',
    'tag_dictionary',
    'pending_domains',
    'user_badges',
    'user_skill_progress',
    'user_skill_achievements',
    'user_profiles',
    'simulator_icons',
    'simulator_icon_presets',
    'user_notes',
    'user_learning_settings',
]

# Tables referenced in raw SQL (migrations, services, etc.)
RAW_SQL_TABLES = [
    'course_packages',  # Referenced in migrations and delete course logic
]

# Columns that should be enum type but might be TEXT in production
# Format: (table, column, expected_enum_type)
ENUM_COLUMNS = [
    ('learning_progress', 'status', 'nodestatus'),
    ('course_nodes', 'type', 'nodetype'),
    ('courses', 'difficulty', 'difficultylevel'),
    ('studio_packages', 'status', 'studiopackagestatus'),
]


async def check_schema(database_url: str, auto_fix: bool = False, full_check: bool = False):
    """Check database schema consistency"""
    engine = create_async_engine(database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    errors = []
    warnings = []
    fixes_applied = []

    async with async_session() as db:
        # Check enum types
        print("\n=== Checking Enum Types ===")
        for enum_name, expected_values in REQUIRED_ENUMS.items():
            result = await db.execute(text("""
                SELECT enumlabel FROM pg_enum e
                JOIN pg_type t ON e.enumtypid = t.oid
                WHERE t.typname = :enum_name
                ORDER BY e.enumsortorder
            """), {"enum_name": enum_name})

            db_values = [row[0] for row in result.fetchall()]

            if not db_values:
                errors.append(f"MISSING ENUM: {enum_name}")
                print(f"  ❌ {enum_name}: NOT FOUND")
                print(f"     Expected values: {expected_values}")

                if auto_fix:
                    values_str = ", ".join([f"'{v}'" for v in expected_values])
                    try:
                        await db.execute(text(f"CREATE TYPE {enum_name} AS ENUM ({values_str})"))
                        await db.commit()
                        fixes_applied.append(f"Created enum {enum_name}")
                        print(f"     ✅ FIXED: Created enum {enum_name}")
                    except Exception as e:
                        print(f"     ❌ Failed to create: {e}")
            else:
                missing = set(expected_values) - set(db_values)
                extra = set(db_values) - set(expected_values)

                if missing:
                    warnings.append(f"ENUM {enum_name} missing values: {missing}")
                    print(f"  ⚠️  {enum_name}: missing {missing}")
                    print(f"     DB has: {db_values}")
                    print(f"     Code expects: {expected_values}")

                    if auto_fix:
                        for value in missing:
                            try:
                                await db.execute(text(
                                    f"ALTER TYPE {enum_name} ADD VALUE IF NOT EXISTS '{value}'"
                                ))
                                await db.commit()
                                fixes_applied.append(f"Added '{value}' to {enum_name}")
                                print(f"     ✅ FIXED: Added '{value}'")
                            except Exception as e:
                                print(f"     ❌ Failed to add '{value}': {e}")
                elif extra:
                    print(f"  ✅ {enum_name}: OK (DB has extra values: {extra})")
                else:
                    print(f"  ✅ {enum_name}: OK")

        # Check ORM tables
        print("\n=== Checking ORM Tables ===")
        for table_name in ORM_TABLES:
            result = await db.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = :table_name
                )
            """), {"table_name": table_name})

            exists = result.scalar()
            if exists:
                print(f"  ✅ {table_name}: OK")
            else:
                errors.append(f"MISSING TABLE: {table_name}")
                print(f"  ❌ {table_name}: NOT FOUND")

        # Check raw SQL tables (optional, just warnings)
        print("\n=== Checking Raw SQL Tables ===")
        for table_name in RAW_SQL_TABLES:
            result = await db.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = :table_name
                )
            """), {"table_name": table_name})

            exists = result.scalar()
            if exists:
                print(f"  ✅ {table_name}: OK")
            else:
                warnings.append(f"RAW SQL TABLE MISSING: {table_name} (code handles gracefully)")
                print(f"  ⚠️  {table_name}: NOT FOUND (code handles gracefully)")

        # Check column types (full check only)
        if full_check:
            print("\n=== Checking Column Types ===")
            for table, column, expected_type in ENUM_COLUMNS:
                result = await db.execute(text("""
                    SELECT data_type, udt_name
                    FROM information_schema.columns
                    WHERE table_name = :table AND column_name = :column
                """), {"table": table, "column": column})

                row = result.fetchone()
                if row:
                    data_type, udt_name = row
                    if udt_name == expected_type:
                        print(f"  ✅ {table}.{column}: {udt_name}")
                    elif data_type == 'text':
                        warnings.append(f"COLUMN TYPE: {table}.{column} is TEXT, expected {expected_type}")
                        print(f"  ⚠️  {table}.{column}: TEXT (expected {expected_type})")
                        print(f"     Note: Code uses status_equals() to handle this")
                    else:
                        print(f"  ℹ️  {table}.{column}: {udt_name}")
                else:
                    print(f"  ❌ {table}.{column}: NOT FOUND")

    await engine.dispose()

    # Summary
    print("\n=== Summary ===")
    if fixes_applied:
        print(f"🔧 {len(fixes_applied)} fixes applied:")
        for f in fixes_applied:
            print(f"   - {f}")

    if errors:
        print(f"❌ {len(errors)} errors found:")
        for e in errors:
            print(f"   - {e}")
        if not auto_fix:
            print("\nRun with --fix to auto-fix missing enum values")
        return False
    elif warnings:
        print(f"⚠️  {len(warnings)} warnings:")
        for w in warnings:
            print(f"   - {w}")
        if not auto_fix:
            print("\nRun with --fix to auto-fix missing enum values")
        # Warnings don't fail the check if code handles them
        return True
    else:
        print("✅ All checks passed!")
        return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Check database schema against code definitions')
    parser.add_argument('--env', choices=['local', 'production'], default='local',
                       help='Environment to check')
    parser.add_argument('--url', help='Database URL (overrides --env)')
    parser.add_argument('--fix', action='store_true',
                       help='Auto-fix missing enum values')
    parser.add_argument('--full', action='store_true',
                       help='Full check including column types')
    args = parser.parse_args()

    if args.url:
        db_url = args.url
    elif args.env == 'production':
        db_url = os.getenv('DATABASE_URL', 'postgresql+asyncpg://hercu:Hercu2026Secure@localhost/hercu_db')
    else:
        db_url = 'postgresql+asyncpg://postgres:postgres@localhost/hercu_test'

    print(f"Checking database: {args.env}")
    print(f"Auto-fix: {'enabled' if args.fix else 'disabled'}")
    print(f"Full check: {'enabled' if args.full else 'disabled'}")

    # Show what we're checking
    print("\n=== Code-defined Enum Values ===")
    for name, values in REQUIRED_ENUMS.items():
        print(f"  {name}: {values}")

    success = asyncio.run(check_schema(db_url, auto_fix=args.fix, full_check=args.full))
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
