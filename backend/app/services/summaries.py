"""Deterministic daily elder summary generation."""

from datetime import date, datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models import Reminder, ReminderCompletion, WellnessEntry
from app.services.health import calculate_health_score


def build_daily_summary(db: Session, elder_id: str, day: date | None = None) -> dict[str, Any]:
    current = day or date.today()
    start = datetime.combine(current, datetime.min.time(), tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    tomorrow_end = end + timedelta(days=1)
    completions = db.query(ReminderCompletion).join(Reminder).filter(
        Reminder.elder_id == elder_id,
        ReminderCompletion.scheduled_for >= start,
        ReminderCompletion.scheduled_for < end,
    ).all()
    completed = sum(item.status == "completed" for item in completions)
    missed = sum(item.status == "missed" for item in completions)
    wellness = db.query(WellnessEntry).filter_by(elder_id=elder_id, check_date=current).first()
    appointments = db.query(Reminder).filter(
        Reminder.elder_id == elder_id,
        Reminder.type == "appointment",
        Reminder.status == "active",
        Reminder.next_run_at >= end,
        Reminder.next_run_at < tomorrow_end,
    ).order_by(Reminder.next_run_at).all()
    score = calculate_health_score(db, elder_id, current)

    wellness_text = "no wellness check-in"
    if wellness:
        details = []
        if wellness.mood is not None:
            details.append(f"mood {wellness.mood}/5")
        if wellness.sleep_hours is not None:
            details.append(f"sleep {float(wellness.sleep_hours):g}h")
        wellness_text = ", ".join(details) or "wellness check-in recorded"
    appointment_text = (
        ", ".join(item.title for item in appointments[:3])
        if appointments else "none"
    )
    body = (
        f"Today: {completed}/{len(completions)} reminder occurrences completed"
        f"{f', {missed} missed' if missed else ''}; {wellness_text}; "
        f"health score {score.score}/100. Tomorrow's appointments: {appointment_text}."
    )
    return {
        "body": body,
        "data": {
            "date": current.isoformat(),
            "completed": completed,
            "recorded_occurrences": len(completions),
            "missed": missed,
            "wellness_recorded": wellness is not None,
            "health_score": score.score,
            "tomorrow_appointments": [item.title for item in appointments],
        },
    }
