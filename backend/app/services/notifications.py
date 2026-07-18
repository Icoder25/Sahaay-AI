"""Notification persistence and optional Firebase Cloud Messaging delivery."""

from typing import Any

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import DeviceToken, Notification
from app.services.firebase import get_firebase_app


def send_notification(
    db: Session,
    user_id: str,
    title: str,
    body: str,
    data: dict[str, Any] | None = None,
    *,
    notification_type: str = "family_alert",
    elder_id: str | None = None,
) -> Notification:
    row = Notification(
        user_id=user_id, elder_id=elder_id, type=notification_type,
        title=title, body=body, data=data or {}, status="pending",
    )
    db.add(row)
    db.flush()
    return deliver_notification(db, row)


def deliver_notification(db: Session, row: Notification) -> Notification:
    """Attempt delivery without committing the caller-owned transaction."""
    user_id = row.user_id
    tokens = db.query(DeviceToken).filter_by(user_id=user_id, is_active=True).all()
    settings = get_settings()
    if not tokens or not (
        settings.firebase_credentials_json or settings.firebase_project_id
    ):
        return row
    try:
        from firebase_admin import messaging

        response = messaging.send_each_for_multicast(
            messaging.MulticastMessage(
                notification=messaging.Notification(title=row.title, body=row.body),
                data={str(k): str(v) for k, v in (row.data or {}).items()},
                tokens=[item.token for item in tokens],
            ),
            app=get_firebase_app(),
        )
        if response.success_count:
            from app.models import utcnow
            row.status, row.sent_at = "sent", utcnow()
        else:
            row.status, row.failure_reason = "failed", "FCM rejected all device tokens"
    except Exception as exc:
        row.status, row.failure_reason = "failed", str(exc)[:1000]
    return row
