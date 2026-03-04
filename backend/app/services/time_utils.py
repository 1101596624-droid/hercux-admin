"""Timezone-safe datetime helpers used by service-layer logic."""

from datetime import datetime, timezone
from typing import Optional


def utcnow() -> datetime:
    """Return an aware UTC datetime."""
    return datetime.now(timezone.utc)


def as_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """
    Normalize datetime to aware UTC.

    SQLite often returns naive datetimes even when columns are declared with
    timezone=True. We treat naive values as UTC to keep service math stable.
    """
    if dt is None:
        return None
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)
