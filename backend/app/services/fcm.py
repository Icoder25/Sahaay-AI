"""Firebase Cloud Messaging stub — logs sends until FCM is configured."""

import logging

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import DeviceToken, Notification

logger = logging.getLogger(__name__)


def register_device_token(
    db: Session, user_id: int, token: str, platform: str = "web"
) -> DeviceToken:
    existing = db.query(DeviceToken).filter(DeviceToken.token == token).first()
    if existing:
        existing.user_id = user_id
        existing.platform = platform
        db.commit()
        db.refresh(existing)
        return existing

    record = DeviceToken(user_id=user_id, token=token, platform=platform)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def send_push_to_user(
    db: Session,
    user_id: int,
    title: str,
    body: str,
    notification_type: str = "info",
    elder_profile_id: int | None = None,
) -> Notification:
    settings = get_settings()
    notification = Notification(
        user_id=user_id,
        elder_profile_id=elder_profile_id,
        title=title,
        body=body,
        notification_type=notification_type,
    )

    tokens = db.query(DeviceToken).filter(DeviceToken.user_id == user_id).all()
    if settings.enable_fcm and settings.fcm_server_key and tokens:
        for device in tokens:
            logger.info("FCM send to %s: %s — %s", device.token[:12], title, body)
        notification.sent_via_fcm = True
    else:
        logger.info("In-app notification for user %s: %s — %s", user_id, title, body)

    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def notify_family_members(
    db: Session,
    family_id: int,
    title: str,
    body: str,
    notification_type: str,
    elder_profile_id: int | None = None,
) -> list[Notification]:
    from app.models import FamilyMember

    members = db.query(FamilyMember).filter(FamilyMember.family_id == family_id).all()
    sent: list[Notification] = []
    for member in members:
        sent.append(
            send_push_to_user(
                db,
                member.user_id,
                title,
                body,
                notification_type=notification_type,
                elder_profile_id=elder_profile_id,
            )
        )
    return sent
