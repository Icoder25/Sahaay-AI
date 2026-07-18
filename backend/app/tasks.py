"""Celery jobs aligned with migration reminder and notification states."""

from datetime import date, timedelta

from celery import Celery
from sqlalchemy import or_

from app.config import get_settings
from app.db import SessionLocal
from app.models import Activity, Elder, FamilyMember, Notification, Reminder, ReminderCompletion, utcnow
from app.services.health import calculate_health_score
from app.services.notifications import deliver_notification, send_notification
from app.services.scheduling import as_utc, next_occurrence
from app.services.summaries import build_daily_summary

settings = get_settings()
celery_app = Celery("sahaay", broker=settings.redis_url or "memory://", backend=settings.redis_url or "cache+memory://")
celery_app.conf.update(
    task_always_eager=settings.celery_always_eager,
    timezone="Asia/Kolkata",
    beat_schedule={
        "dispatch-reminders": {"task": "sahaay.dispatch_reminders", "schedule": 60.0},
        "escalate-reminders": {"task": "sahaay.escalate_reminders", "schedule": 300.0},
        "daily-summaries": {"task": "sahaay.daily_summaries", "schedule": 86400.0},
        "health-scores": {"task": "sahaay.health_scores", "schedule": 86400.0},
        "retry-notifications": {"task": "sahaay.retry_notifications", "schedule": 300.0},
    },
)


def _family_users(db, family_id: str) -> list[str]:
    return [
        row.user_id
        for row in db.query(FamilyMember).filter_by(family_id=family_id, status="active").all()
    ]


@celery_app.task(name="sahaay.dispatch_reminders")
def dispatch_reminders() -> int:
    db = SessionLocal()
    try:
        now = utcnow()
        rows = db.query(Reminder).filter(
            Reminder.status == "active",
            Reminder.next_run_at <= now,
            or_(Reminder.last_run_at.is_(None), Reminder.last_run_at < Reminder.next_run_at),
        ).all()
        for row in rows:
            elder = db.get(Elder, row.elder_id)
            if elder:
                for user_id in _family_users(db, elder.family_id):
                    send_notification(
                        db, user_id, row.title, row.description or "Reminder due",
                        {"reminder_id": row.id}, notification_type="reminder", elder_id=elder.id,
                    )
            row.last_run_at = row.next_run_at
        db.commit()
        return len(rows)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@celery_app.task(name="sahaay.escalate_reminders")
def escalate_reminders() -> int:
    db = SessionLocal()
    try:
        now = utcnow()
        candidates = db.query(Reminder).filter(
            Reminder.status == "active", Reminder.last_run_at.is_not(None)
        ).all()
        overdue = []
        for row in candidates:
            scheduled_for = as_utc(row.last_run_at)
            if scheduled_for + timedelta(minutes=row.escalation_after_minutes) > now:
                continue
            recorded = db.query(ReminderCompletion).filter_by(
                reminder_id=row.id, scheduled_for=row.last_run_at
            ).first()
            if recorded is None:
                overdue.append(row)
        for row in overdue:
            scheduled_for = as_utc(row.last_run_at)
            prior_retries = [
                item for item in db.query(Notification).filter_by(
                    elder_id=row.elder_id, type="family_alert"
                ).all()
                if item.data.get("reminder_id") == row.id
                and item.data.get("scheduled_for") == scheduled_for.isoformat()
            ]
            if len(prior_retries) >= row.max_retries:
                db.add(ReminderCompletion(
                    reminder_id=row.id, scheduled_for=scheduled_for, status="missed",
                    metadata_json={"reason": "max_retries_exhausted"},
                ))
                following = next_occurrence(row, scheduled_for)
                row.next_run_at = following
                if following is None:
                    row.status = "completed"
                continue
            elder = db.get(Elder, row.elder_id)
            if elder:
                for user_id in _family_users(db, elder.family_id):
                    send_notification(
                        db, user_id, f"Follow-up: {row.title}",
                        "This reminder occurrence is still incomplete.",
                        {
                            "reminder_id": row.id, "priority": "high",
                            "scheduled_for": scheduled_for.isoformat(),
                        },
                        notification_type="family_alert", elder_id=elder.id,
                    )
        db.commit()
        return len(overdue)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@celery_app.task(name="sahaay.daily_summaries")
def daily_summaries() -> int:
    db = SessionLocal()
    try:
        elders = db.query(Elder).filter_by(is_active=True).all()
        for elder in elders:
            summary = build_daily_summary(db, elder.id)
            recipients = set(_family_users(db, elder.family_id))
            if elder.user_id:
                recipients.add(elder.user_id)
            for user_id in recipients:
                send_notification(
                    db, user_id, f"{elder.full_name}'s daily summary",
                    summary["body"], summary["data"],
                    notification_type="daily_summary", elder_id=elder.id,
                )
            db.add(Activity(
                elder_id=elder.id,
                activity_type="notification",
                title="Daily summary generated",
                description=summary["body"],
                source="system",
                metadata_json=summary["data"],
            ))
        db.commit()
        return len(elders)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@celery_app.task(name="sahaay.health_scores")
def health_scores() -> int:
    db = SessionLocal()
    try:
        elders = db.query(Elder).filter_by(is_active=True).all()
        for elder in elders:
            calculate_health_score(db, elder.id, date.today())
        db.commit()
        return len(elders)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@celery_app.task(name="sahaay.retry_notifications", autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def retry_notifications() -> int:
    db = SessionLocal()
    try:
        rows = db.query(Notification).filter_by(status="failed").all()
        for row in rows:
            row.status, row.failure_reason = "pending", None
            deliver_notification(db, row)
        db.commit()
        return len(rows)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
