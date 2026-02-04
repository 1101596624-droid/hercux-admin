"""
Core utility functions for handling database type compatibility.

The production database uses TEXT columns for enum-like fields, while the code
defines proper Enum types. These utilities bridge the gap.
"""
from sqlalchemy import cast, String, or_


def get_enum_value(enum_obj) -> str:
    """
    Get value from enum or string, handling both types.

    This is needed because SQLAlchemy may return either:
    - Enum object (when using native enum type)
    - String (when using string-based enum storage)

    Args:
        enum_obj: Either an Enum instance or a string

    Returns:
        The string value
    """
    if enum_obj is None:
        return None
    return enum_obj.value if hasattr(enum_obj, 'value') else enum_obj


def status_equals(column, enum_value):
    """
    Create a condition that matches status/enum value as string.

    PostgreSQL stores status as text, so we cast the column to string
    and compare against the string value.

    Usage:
        # Instead of: LearningProgress.status == NodeStatus.COMPLETED
        # Use: status_equals(LearningProgress.status, NodeStatus.COMPLETED)

    Args:
        column: SQLAlchemy column to compare
        enum_value: Enum value to match

    Returns:
        SQLAlchemy comparison condition
    """
    str_value = enum_value.value if hasattr(enum_value, 'value') else enum_value
    return cast(column, String) == str_value


def status_not_equals(column, enum_value):
    """
    Create a condition that checks status/enum value is NOT equal.

    Usage:
        # Instead of: LearningProgress.status != NodeStatus.LOCKED
        # Use: status_not_equals(LearningProgress.status, NodeStatus.LOCKED)
    """
    str_value = enum_value.value if hasattr(enum_value, 'value') else enum_value
    return cast(column, String) != str_value


def status_in(column, enum_values):
    """
    Create a condition that checks status/enum value is in a list.

    Usage:
        # Instead of: LearningProgress.status.in_([NodeStatus.COMPLETED, NodeStatus.IN_PROGRESS])
        # Use: status_in(LearningProgress.status, [NodeStatus.COMPLETED, NodeStatus.IN_PROGRESS])
    """
    str_values = [v.value if hasattr(v, 'value') else v for v in enum_values]
    return cast(column, String).in_(str_values)


def enum_equals(column, enum_value):
    """Alias for status_equals - use for non-status enum columns like type, difficulty."""
    return status_equals(column, enum_value)


def enum_in(column, enum_values):
    """Alias for status_in - use for non-status enum columns."""
    return status_in(column, enum_values)
