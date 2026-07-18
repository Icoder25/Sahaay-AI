from datetime import datetime, timedelta, timezone

from app.db import SessionLocal
from app.models import Activity, Conversation, Notification, ReminderCompletion
from app.routers import api_v1
from app.tasks import daily_summaries

PREFIX = "/api/v1"
OWNER_ID = "11111111-1111-1111-1111-111111111111"


def family_elder(client, *, language="en"):
    family = client.post(f"{PREFIX}/families", json={"name": "Workflow Family"}).json()
    elder = client.post(
        f"{PREFIX}/families/{family['id']}/elders",
        json={"full_name": "Savitri", "preferred_language": language},
    ).json()
    return family, elder


def reminder(client, elder_id, *, kind="medicine", title="Medicine", frequency="daily", run=None):
    scheduled = run or datetime.now(timezone.utc)
    return client.post(
        f"{PREFIX}/elders/{elder_id}/reminders",
        json={
            "type": kind,
            "title": title,
            "local_time": scheduled.time().isoformat(),
            "start_date": scheduled.date().isoformat(),
            "frequency": frequency,
            "next_run_at": scheduled.isoformat(),
        },
    ).json()


def test_invitation_decline_and_revoke(client, as_user):
    family = client.post(f"{PREFIX}/families", json={"name": "Invitations"}).json()
    declined = client.post(
        f"{PREFIX}/families/{family['id']}/invitations",
        json={"email": "decline@example.com", "role": "member"},
    ).json()
    revoked = client.post(
        f"{PREFIX}/families/{family['id']}/invitations",
        json={"email": "revoke@example.com", "role": "caregiver"},
    ).json()

    as_user("66666666-6666-6666-6666-666666666666", "decline@example.com")
    response = client.post(f"{PREFIX}/invitations/{declined['id']}/decline")
    assert response.json()["status"] == "declined"
    assert client.post(f"{PREFIX}/invitations/{declined['id']}/decline").status_code == 200

    as_user(OWNER_ID, "owner@example.com")
    response = client.post(
        f"{PREFIX}/families/{family['id']}/invitations/{revoked['id']}/revoke"
    )
    assert response.json()["status"] == "revoked"
    assert client.post(
        f"{PREFIX}/families/{family['id']}/invitations/{revoked['id']}/revoke"
    ).status_code == 200


def test_reminder_pause_resume_snooze_and_occurrence_identity(client):
    _, elder = family_elder(client)
    original = datetime.now(timezone.utc) + timedelta(hours=1)
    row = reminder(client, elder["id"], run=original)
    assert client.post(f"{PREFIX}/reminders/{row['id']}/pause").json()["status"] == "paused"
    assert client.post(f"{PREFIX}/reminders/{row['id']}/pause").status_code == 200
    assert client.post(f"{PREFIX}/reminders/{row['id']}/resume").json()["status"] == "active"

    payload = {"scheduled_for": row["next_run_at"], "minutes": 20}
    first = client.post(f"{PREFIX}/reminders/{row['id']}/snooze", json=payload).json()
    second = client.post(f"{PREFIX}/reminders/{row['id']}/snooze", json=payload).json()
    assert first["next_run_at"] == second["next_run_at"]
    completed = client.post(f"{PREFIX}/reminders/{row['id']}/complete").json()
    assert completed["completion"]["scheduled_for"] == row["next_run_at"]
    snoozed_until = datetime.fromisoformat(completed["completion"]["metadata"]["snoozed_until"])
    returned_run = datetime.fromisoformat(first["next_run_at"])
    assert snoozed_until.replace(tzinfo=None) == returned_run.replace(tzinfo=None)
    db = SessionLocal()
    try:
        assert db.query(ReminderCompletion).filter_by(reminder_id=row["id"]).count() == 1
    finally:
        db.close()


def test_explainable_scores_and_risk_signals(client):
    _, elder = family_elder(client)
    now = datetime.now(timezone.utc)
    medicine = reminder(client, elder["id"], kind="medicine", run=now)
    meal = reminder(client, elder["id"], kind="meal", title="Breakfast", run=now)
    exercise = reminder(client, elder["id"], kind="exercise", title="Walk", run=now)
    client.post(f"{PREFIX}/reminders/{medicine['id']}/complete")
    client.post(f"{PREFIX}/reminders/{meal['id']}/complete", json={"status": "skipped"})
    client.post(f"{PREFIX}/reminders/{exercise['id']}/complete")
    client.post(
        f"{PREFIX}/elders/{elder['id']}/wellness",
        json={"mood": 2, "sleep_quality": 4, "pain_level": 8},
    )
    db = SessionLocal()
    try:
        db.add_all([
            ReminderCompletion(
                reminder_id=medicine["id"],
                scheduled_for=now - timedelta(days=2),
                status="missed",
                metadata_json={},
            ),
            ReminderCompletion(
                reminder_id=medicine["id"],
                scheduled_for=now - timedelta(days=3),
                status="missed",
                metadata_json={},
            ),
        ])
        db.commit()
    finally:
        db.close()

    score = client.get(f"{PREFIX}/elders/{elder['id']}/health-score").json()
    assert score["medicine_score"] is not None
    assert score["meal_score"] == 0
    assert score["sleep_score"] == 80
    assert score["mood_score"] == 40
    assert score["adherence_score"] is not None
    assert score["factors"]["components"]["activity"] is not None
    risk = client.get(f"{PREFIX}/elders/{elder['id']}/risk-insights").json()
    assert risk["risk_level"] == "high"
    assert {"repeated_misses", "high_pain"} <= {item["code"] for item in risk["signals"]}
    assert "not a diagnosis" in risk["disclaimer"]


def test_ai_context_and_memory_are_bounded(client, monkeypatch):
    _, elder = family_elder(client, language="hi")
    client.post(f"{PREFIX}/elders/{elder['id']}/wellness", json={"mood": 4, "sleep_hours": 7})
    reminder(client, elder["id"], title="Morning medicine")
    conversation = client.post(
        f"{PREFIX}/conversations", json={"elder_id": elder["id"], "title": "Hindi check-in"}
    ).json()
    captured = {}

    def fake_answer(history, prompt, use_search, speak, context=None):
        captured["context"] = context
        return {
            "content": "नमस्ते, मैं आपकी मदद के लिए यहाँ हूँ।",
            "citations": [],
            "audio_url": None,
            "summary": "Hindi wellbeing check-in.",
            "memory_update": {
                "last_topic": "wellbeing",
                "preferred_language": "hi",
                "diagnosis": "must not persist",
            },
        }

    monkeypatch.setattr(api_v1, "answer", fake_answer)
    response = client.post(
        f"{PREFIX}/conversations/{conversation['id']}/messages",
        json={"content": "आज कैसा रहना चाहिए?", "use_search": False},
    )
    assert response.status_code == 200
    assert captured["context"]["preferred_language"] == "hi"
    assert captured["context"]["recent_wellness"]
    assert captured["context"]["upcoming_reminders"]
    db = SessionLocal()
    try:
        stored = db.get(Conversation, conversation["id"])
        assert stored.summary == "Hindi wellbeing check-in."
        assert stored.memory["preferred_language"] == "hi"
        assert "diagnosis" not in stored.memory
    finally:
        db.close()


def test_daily_summary_persists_real_notification_and_activity(client):
    _, elder = family_elder(client)
    now = datetime.now(timezone.utc)
    med = reminder(client, elder["id"], run=now)
    client.post(f"{PREFIX}/reminders/{med['id']}/complete")
    client.post(f"{PREFIX}/elders/{elder['id']}/wellness", json={"mood": 4, "sleep_hours": 8})
    tomorrow = now + timedelta(days=1)
    reminder(
        client, elder["id"], kind="appointment", title="Doctor visit",
        frequency="once", run=tomorrow,
    )

    assert daily_summaries.run() == 1
    db = SessionLocal()
    try:
        notification = db.query(Notification).filter_by(
            elder_id=elder["id"], type="daily_summary"
        ).one()
        assert "health score" in notification.body
        assert "Doctor visit" in notification.body
        activity = db.query(Activity).filter_by(
            elder_id=elder["id"], activity_type="notification"
        ).one()
        assert activity.source == "system"
        assert activity.metadata_json["tomorrow_appointments"] == ["Doctor visit"]
    finally:
        db.close()
