from datetime import datetime, timedelta, timezone

from app.db import SessionLocal
from app.models import AuditLog, LoginHistory, Notification, Reminder, ReminderCompletion, User
from app.services.notifications import send_notification
from app.tasks import dispatch_reminders


def test_migration_table_and_column_names():
    assert ReminderCompletion.__tablename__ == "reminder_completions"
    assert AuditLog.__tablename__ == "audit_logs"
    expected = {
        "users": {"firebase_uid", "last_login_at", "login_count", "onboarding_completed"},
        "login_history": {"firebase_uid", "login_time", "ip_address", "session_id"},
        "elder_profiles": {"user_id", "created_by", "preferred_language"},
        "wellness_checks": {"check_date", "sleep_quality", "drank_enough_water"},
        "ai_conversations": {"started_by", "status", "memory", "last_message_at"},
        "reminders": {"assigned_by", "type", "local_time", "frequency", "next_run_at"},
        "notifications": {"type", "status", "scheduled_at", "failure_reason"},
    }
    metadata = AuditLog.metadata
    for table_name, columns in expected.items():
        assert columns <= set(metadata.tables[table_name].columns.keys())
    assert User.__tablename__ == "users"
    assert LoginHistory.__tablename__ == "login_history"


def test_notification_helper_does_not_commit(client):
    client.get("/api/v1/profiles/me")
    db = SessionLocal()
    try:
        row = send_notification(
            db,
            "11111111-1111-1111-1111-111111111111",
            "Transaction test",
            "This must roll back",
        )
        assert row.status == "pending"
        db.rollback()
        assert db.query(Notification).filter_by(title="Transaction test").count() == 0
    finally:
        db.close()


def test_due_reminder_dispatch_is_idempotent(client):
    family = client.post("/api/v1/families", json={"name": "Task Family"}).json()
    elder = client.post(
        f"/api/v1/families/{family['id']}/elders", json={"full_name": "Savitri"}
    ).json()
    due = datetime.now(timezone.utc) - timedelta(minutes=1)
    reminder = client.post(
        f"/api/v1/elders/{elder['id']}/reminders",
        json={
            "type": "hydration",
            "title": "Drink water",
            "local_time": due.time().isoformat(),
            "start_date": due.date().isoformat(),
            "frequency": "daily",
            "next_run_at": due.isoformat(),
        },
    ).json()
    assert dispatch_reminders.run() == 1
    assert dispatch_reminders.run() == 0
    db = SessionLocal()
    try:
        stored = db.get(Reminder, reminder["id"])
        assert stored.last_run_at is not None
        assert db.query(Notification).filter_by(type="reminder").count() == 1
        assert db.query(AuditLog).filter_by(action="reminder.created").count() == 1
    finally:
        db.close()
