"""Deterministic health scores and risk signals derived from existing records."""

from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.models import Activity, HealthScore, Notification, Reminder, ReminderCompletion, WellnessEntry, utcnow

WINDOW_DAYS = 7
WEIGHTS = {
    "medicine": 0.25,
    "meal": 0.15,
    "sleep": 0.20,
    "mood": 0.15,
    "activity": 0.10,
    "adherence": 0.15,
}


def _percent(items: list[ReminderCompletion]) -> int | None:
    if not items:
        return None
    return round(sum(item.status == "completed" for item in items) / len(items) * 100)


def _bounded(value: float) -> int:
    return max(0, min(100, round(value)))


def calculate_health_score(db: Session, elder_id: str, score_date: date | None = None) -> HealthScore:
    day = score_date or date.today()
    start = datetime.combine(day - timedelta(days=WINDOW_DAYS - 1), datetime.min.time())
    end = datetime.combine(day + timedelta(days=1), datetime.min.time())
    pairs = db.query(ReminderCompletion, Reminder).join(Reminder).filter(
        Reminder.elder_id == elder_id,
        ReminderCompletion.scheduled_for >= start,
        ReminderCompletion.scheduled_for < end,
    ).all()
    completions = [completion for completion, _ in pairs]
    by_type = {
        kind: [completion for completion, reminder in pairs if reminder.type == kind]
        for kind in ("medicine", "meal", "exercise")
    }
    entries = db.query(WellnessEntry).filter(
        WellnessEntry.elder_id == elder_id,
        WellnessEntry.check_date >= day - timedelta(days=WINDOW_DAYS - 1),
        WellnessEntry.check_date <= day,
    ).all()

    medicine = _percent(by_type["medicine"])
    meal = _percent(by_type["meal"])
    adherence = _percent(completions)
    moods = [entry.mood for entry in entries if entry.mood is not None]
    mood = _bounded(sum(moods) / len(moods) / 5 * 100) if moods else None
    sleep_quality = [entry.sleep_quality for entry in entries if entry.sleep_quality is not None]
    sleep_hours = [float(entry.sleep_hours) for entry in entries if entry.sleep_hours is not None]
    if sleep_quality:
        sleep = _bounded(sum(sleep_quality) / len(sleep_quality) / 5 * 100)
    elif sleep_hours:
        sleep = _bounded(sum(max(0, 100 - abs(hours - 8) * 20) for hours in sleep_hours) / len(sleep_hours))
    else:
        sleep = None
    exercise = _percent(by_type["exercise"])
    interaction_days = {
        activity.occurred_at.date()
        for activity in db.query(Activity).filter(
            Activity.elder_id == elder_id,
            Activity.occurred_at >= start,
            Activity.occurred_at < end,
            Activity.activity_type.in_(["wellness_check", "ai_conversation"]),
        ).all()
    }
    activity = exercise if exercise is not None else (
        _bounded(len(interaction_days) / WINDOW_DAYS * 100) if interaction_days else None
    )

    components = {
        "medicine": medicine,
        "meal": meal,
        "sleep": sleep,
        "mood": mood,
        "activity": activity,
        "adherence": adherence,
    }
    available = {name: value for name, value in components.items() if value is not None}
    weight_total = sum(WEIGHTS[name] for name in available)
    score = (
        round(sum(value * WEIGHTS[name] for name, value in available.items()) / weight_total)
        if weight_total else 50
    )
    missing = [name for name, value in components.items() if value is None]
    factors: dict[str, Any] = {
        "window_days": WINDOW_DAYS,
        "components": components,
        "weights": WEIGHTS,
        "missing_data": missing,
        "samples": {
            "reminder_completions": len(completions),
            "wellness_checks": len(entries),
            "interaction_days": len(interaction_days),
        },
        "method": "weighted_average_of_available_components",
    }
    insights = []
    if missing:
        insights.append(f"Missing data for: {', '.join(missing)}.")
    if adherence is not None and adherence < 70:
        insights.append("Reminder adherence has been below 70% in the last 7 days.")
    if mood is not None and mood < 50:
        insights.append("Recent mood check-ins have been low.")
    if not insights:
        insights.append("No deterministic concern was found in the available 7-day data.")

    row = db.query(HealthScore).filter_by(elder_id=elder_id, score_date=day).first()
    values = {
        "score": score,
        "medicine_score": medicine,
        "meal_score": meal,
        "sleep_score": sleep,
        "mood_score": mood,
        "activity_score": activity,
        "adherence_score": adherence,
        "factors": factors,
        "insights": insights,
        "generated_at": utcnow(),
    }
    if row is None:
        row = HealthScore(elder_id=elder_id, score_date=day, **values)
        db.add(row)
    else:
        for key, value in values.items():
            setattr(row, key, value)
    db.flush()
    return row


def calculate_risk_signals(db: Session, elder_id: str, as_of: date | None = None) -> dict[str, Any]:
    day = as_of or date.today()
    start = datetime.combine(day - timedelta(days=13), datetime.min.time())
    split = datetime.combine(day - timedelta(days=6), datetime.min.time())
    end = datetime.combine(day + timedelta(days=1), datetime.min.time())
    completions = db.query(ReminderCompletion).join(Reminder).filter(
        Reminder.elder_id == elder_id,
        ReminderCompletion.scheduled_for >= start,
        ReminderCompletion.scheduled_for < end,
    ).all()
    entries = db.query(WellnessEntry).filter(
        WellnessEntry.elder_id == elder_id,
        WellnessEntry.check_date >= day - timedelta(days=13),
        WellnessEntry.check_date <= day,
    ).all()
    activities = db.query(Activity).filter(
        Activity.elder_id == elder_id, Activity.occurred_at >= start, Activity.occurred_at < end
    ).all()
    notifications = db.query(Notification).filter(
        Notification.elder_id == elder_id, Notification.created_at >= start, Notification.created_at < end
    ).all()

    missed = sum(item.status == "missed" for item in completions)
    high_pain = [entry for entry in entries if entry.pain_level is not None and entry.pain_level >= 7]
    low_mood = [entry for entry in entries if entry.mood is not None and entry.mood <= 2]
    recent_checks = sum(entry.check_date >= day - timedelta(days=6) for entry in entries)
    prior_checks = len(entries) - recent_checks
    recent_interactions = sum(activity.occurred_at >= split for activity in activities)
    prior_interactions = len(activities) - recent_interactions
    failed_notifications = sum(item.status == "failed" for item in notifications)

    signals = []
    if missed >= 2:
        signals.append({"code": "repeated_misses", "severity": "high", "count": missed})
    if high_pain:
        signals.append({"code": "high_pain", "severity": "high", "count": len(high_pain)})
    if len(low_mood) >= 2:
        signals.append({"code": "low_mood", "severity": "medium", "count": len(low_mood)})
    if prior_checks >= 2 and recent_checks < prior_checks / 2:
        signals.append({"code": "reduced_checkins", "severity": "medium", "recent": recent_checks, "prior": prior_checks})
    if prior_interactions >= 2 and recent_interactions < prior_interactions / 2:
        signals.append({"code": "reduced_interactions", "severity": "medium", "recent": recent_interactions, "prior": prior_interactions})
    if failed_notifications:
        signals.append({"code": "notification_delivery_failures", "severity": "medium", "count": failed_notifications})

    missing = []
    if not completions:
        missing.append("reminder_completions")
    if not entries:
        missing.append("wellness_checks")
    if not activities:
        missing.append("activities")
    severity_rank = {"low": 1, "medium": 2, "high": 3}
    level = (
        max((item["severity"] for item in signals), key=severity_rank.get)
        if signals else ("unknown" if len(missing) >= 2 else "low")
    )
    return {
        "elder_id": elder_id,
        "window_days": 14,
        "risk_level": level,
        "signals": signals,
        "missing_data": missing,
        "disclaimer": "Deterministic care signals only; not a diagnosis or medical advice.",
    }
