"""Reminder occurrence calculation shared by API and Celery tasks."""

from calendar import monthrange
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from app.models import Reminder


def as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def initial_run(start_date: date, local_time, timezone_name: str) -> datetime:
    local = datetime.combine(start_date, local_time).replace(tzinfo=ZoneInfo(timezone_name))
    return local.astimezone(timezone.utc)


def next_occurrence(reminder: Reminder, current: datetime) -> datetime | None:
    current = as_utc(current)
    if reminder.frequency == "once":
        return None
    if reminder.frequency == "daily":
        result = current + timedelta(days=1)
    elif reminder.frequency == "weekly":
        result = current + timedelta(days=7)
    elif reminder.frequency == "monthly":
        year = current.year + (1 if current.month == 12 else 0)
        month = 1 if current.month == 12 else current.month + 1
        result = current.replace(year=year, month=month, day=min(current.day, monthrange(year, month)[1]))
    else:
        days = int((reminder.repeat_rule or {}).get("interval_days", 1))
        result = current + timedelta(days=max(1, days))
    if reminder.end_date and result.date() > reminder.end_date:
        return None
    return result
