"""Activity logging and health score computation."""

import json
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import Activity, ElderProfile, HealthScore, Reminder, WellnessCheck


def log_activity(
    db: Session,
    elder_profile_id: int,
    activity_type: str,
    title: str,
    description: str | None = None,
) -> Activity:
    activity = Activity(
        elder_profile_id=elder_profile_id,
        activity_type=activity_type,
        title=title,
        description=description,
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


def get_elder_profile_by_session(db: Session, session_id: str) -> ElderProfile | None:
    return db.query(ElderProfile).filter(ElderProfile.session_id == session_id).first()


def compute_health_score(db: Session, elder_profile_id: int) -> HealthScore:
    since = datetime.utcnow() - timedelta(days=7)
    wellness = (
        db.query(WellnessCheck)
        .filter(
            WellnessCheck.elder_profile_id == elder_profile_id,
            WellnessCheck.created_at >= since,
        )
        .order_by(WellnessCheck.created_at.desc())
        .all()
    )
    reminders = (
        db.query(Reminder)
        .filter(
            Reminder.elder_profile_id == elder_profile_id,
            Reminder.created_at >= since,
        )
        .all()
    )

    mood_scores = {"great": 100, "good": 85, "okay": 70, "low": 50, "poor": 35}
    appetite_scores = {"good": 100, "normal": 80, "poor": 55, "skipped": 40}
    sleep_scores = {"good": 100, "fair": 75, "poor": 50, "restless": 45}

    wellness_score = 75.0
    if wellness:
        latest = wellness[0]
        wellness_score = (
            mood_scores.get(latest.mood, 70)
            + appetite_scores.get(latest.appetite, 70)
            + sleep_scores.get(latest.sleep_quality, 70)
        ) / 3

    adherence_score = 80.0
    if reminders:
        completed = sum(1 for r in reminders if r.status == "completed")
        adherence_score = (completed / len(reminders)) * 100

    score = round(wellness_score * 0.6 + adherence_score * 0.4, 1)
    factors = {
        "wellness_score": round(wellness_score, 1),
        "adherence_score": round(adherence_score, 1),
        "wellness_checks_7d": len(wellness),
        "reminders_7d": len(reminders),
    }

    if score >= 85:
        summary = "Doing well overall. Routines and wellness look stable."
    elif score >= 70:
        summary = "Mostly stable with a few areas to watch this week."
    elif score >= 55:
        summary = "Some missed routines or low wellness signals — gentle check-in recommended."
    else:
        summary = "Needs attention. Consider calling or visiting soon."

    record = HealthScore(
        elder_profile_id=elder_profile_id,
        score=score,
        summary=summary,
        factors=json.dumps(factors),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_latest_health_score(db: Session, elder_profile_id: int) -> HealthScore | None:
    return (
        db.query(HealthScore)
        .filter(HealthScore.elder_profile_id == elder_profile_id)
        .order_by(HealthScore.computed_at.desc())
        .first()
    )
