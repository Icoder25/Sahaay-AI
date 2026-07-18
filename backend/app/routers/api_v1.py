"""Complete authenticated API v1 surface for the Sahaay MVP."""

from datetime import date, datetime, timedelta, timezone
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import case, func, inspect
from sqlalchemy.orm import Session

from app.auth import AuthUser, bearer, get_current_profile, get_current_user
from app.config import get_settings
from app.db import get_db
from app.models import (
    Activity, AuditLog, Conversation, DeviceToken, Elder, Family, FamilyMember, HealthScore,
    Invitation, Message, Notification, Profile, Reminder, ReminderCompletion, SOSAlert,
    WellnessEntry, uid, utcnow,
)
from app.schemas import (
    AuthCredentials, AuthRefresh, ChatMessageCreate, ConversationCreate, DeviceTokenCreate,
    ElderCreate, ElderUpdate, FamilyCreate, FamilyUpdate, InvitationAccept, InvitationCreate,
    MemberRoleUpdate, NotificationCreate, PasswordRecovery, ProfileUpdate, ReminderCompletionCreate,
    ReminderCreate, ReminderSnooze, ReminderUpdate, SOSCreate, WellnessCreate,
)
from app.services.ai import answer
from app.services.health import calculate_health_score, calculate_risk_signals
from app.services.notifications import send_notification
from app.services.scheduling import as_utc, initial_run, next_occurrence

router = APIRouter()


def dump(row: Any) -> dict[str, Any]:
    return {
        prop.columns[0].name: getattr(row, prop.key)
        for prop in inspect(row).mapper.column_attrs
    }


def patch(row: Any, body: Any) -> None:
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(row, key, value)


def member(db: Session, family_id: str, user_id: str, roles: set[str] | None = None) -> FamilyMember:
    row = db.query(FamilyMember).filter_by(family_id=family_id, user_id=user_id, status="active").first()
    if row is None:
        raise HTTPException(403, "You are not a member of this family")
    if roles and row.role not in roles:
        raise HTTPException(403, "Your family role does not allow this action")
    return row


CARE_ROLES = {"owner", "admin", "caregiver"}


def elder_access(
    db: Session, elder_id: str, user_id: str, access: str = "read"
) -> Elder:
    elder = db.get(Elder, elder_id)
    if elder is None:
        raise HTTPException(404, "Elder not found")
    is_self = elder.user_id == user_id
    membership = db.query(FamilyMember).filter_by(
        family_id=elder.family_id, user_id=user_id, status="active"
    ).first()
    allowed = (
        (access == "read" and (is_self or membership is not None))
        or (access == "self_service" and (is_self or (membership and membership.role in CARE_ROLES)))
        or (access == "manage" and membership is not None and membership.role in CARE_ROLES)
    )
    if not allowed:
        raise HTTPException(403, "You do not have access to this elder")
    return elder


def actor_source(elder: Elder, user_id: str) -> str:
    return "user" if elder.user_id == user_id else "family"


def audit_family_id(db: Session, elder: Elder, user_id: str) -> str | None:
    membership = db.query(FamilyMember.id).filter_by(
        family_id=elder.family_id, user_id=user_id, status="active"
    ).first()
    return elder.family_id if membership else None


def log(
    db: Session, elder_id: str, actor_id: str | None, activity_type: str, title: str,
    metadata: dict | None = None, description: str | None = None, source: str = "family",
) -> None:
    db.add(Activity(
        elder_id=elder_id, actor_id=actor_id, activity_type=activity_type, title=title,
        description=description, source=source, metadata_json=metadata or {},
    ))


def audit(
    db: Session, actor_id: str, action: str, entity_type: str, entity_id: str,
    family_id: str | None = None, elder_id: str | None = None,
    old_values: dict | None = None, new_values: dict | None = None,
) -> None:
    # Use {} not None: psycopg Jsonb(None) binds as JSON null and fails
    # audit_logs_*_values_check (expects SQL NULL or a JSON object).
    db.add(AuditLog(
        actor_id=actor_id, family_id=family_id, elder_id=elder_id, action=action,
        entity_type=entity_type, entity_id=entity_id,
        old_values=old_values if old_values is not None else {},
        new_values=new_values if new_values is not None else {},
    ))


def delete_elder_records(db: Session, elder: Elder) -> None:
    conversation_ids = [row.id for row in db.query(Conversation.id).filter_by(elder_id=elder.id).all()]
    if conversation_ids:
        db.query(Message).filter(Message.conversation_id.in_(conversation_ids)).delete(synchronize_session=False)
    reminder_ids = [row.id for row in db.query(Reminder.id).filter_by(elder_id=elder.id).all()]
    if reminder_ids:
        db.query(ReminderCompletion).filter(ReminderCompletion.reminder_id.in_(reminder_ids)).delete(synchronize_session=False)
    for model in (Conversation, Activity, Reminder, WellnessEntry, HealthScore, SOSAlert, Notification):
        db.query(model).filter_by(elder_id=elder.id).delete(synchronize_session=False)
    db.delete(elder)


def auth_proxy(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    settings = get_settings()
    key = settings.supabase_publishable_key
    if not settings.supabase_url or not key:
        raise HTTPException(503, "Supabase auth wrapper is not configured")
    try:
        response = httpx.post(
            f"{settings.supabase_url.rstrip('/')}/auth/v1/{path}",
            json=payload,
            headers={"apikey": key},
            timeout=10,
        )
    except httpx.HTTPError as exc:
        raise HTTPException(503, "Supabase Auth is unavailable") from exc
    if response.status_code >= 400:
        detail = response.json().get("msg") or response.json().get("error_description") or "Authentication failed"
        raise HTTPException(response.status_code, detail)
    return response.json()


@router.post("/auth/signup", tags=["auth"])
def signup(body: AuthCredentials) -> dict:
    return auth_proxy("signup", body.model_dump(mode="json"))


@router.post("/auth/login", tags=["auth"])
def login(body: AuthCredentials) -> dict:
    return auth_proxy("token?grant_type=password", body.model_dump(mode="json"))


@router.post("/auth/refresh", tags=["auth"])
def refresh(body: AuthRefresh) -> dict:
    return auth_proxy("token?grant_type=refresh_token", body.model_dump())


@router.post("/auth/forgot-password", tags=["auth"])
def forgot_password(body: PasswordRecovery) -> dict:
    payload = body.model_dump(mode="json", exclude_none=True)
    return auth_proxy("recover", payload)


@router.post("/auth/logout", status_code=204, tags=["auth"])
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    user: AuthUser = Depends(get_current_user),
) -> Response:
    settings = get_settings()
    if settings.supabase_url and settings.supabase_publishable_key:
        try:
            response = httpx.post(
                f"{settings.supabase_url.rstrip('/')}/auth/v1/logout",
                headers={
                    "apikey": settings.supabase_publishable_key,
                    "Authorization": f"Bearer {credentials.credentials}",
                },
                timeout=10,
            )
            if response.status_code >= 400:
                raise HTTPException(response.status_code, "Supabase logout failed")
        except httpx.HTTPError as exc:
            raise HTTPException(503, "Supabase Auth is unavailable") from exc
    return Response(status_code=204)


@router.get("/auth/me", tags=["auth"])
@router.get("/profiles/me", tags=["profiles"])
def my_profile(profile: Profile = Depends(get_current_profile)) -> dict:
    return dump(profile)


@router.patch("/profiles/me", tags=["profiles"])
def update_profile(body: ProfileUpdate, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> dict:
    patch(profile, body)
    db.commit()
    db.refresh(profile)
    return dump(profile)


@router.post("/families", status_code=201, tags=["families"])
def create_family(body: FamilyCreate, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> dict:
    family = Family(owner_id=profile.id, **body.model_dump())
    db.add(family)
    db.flush()
    db.add(FamilyMember(family_id=family.id, user_id=profile.id, role="owner"))
    audit(db, profile.id, "family.created", "family", family.id, family_id=family.id)
    db.commit()
    db.refresh(family)
    return dump(family)


@router.get("/families", tags=["families"])
def list_families(db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> list[dict]:
    rows = db.query(Family).join(FamilyMember).filter(FamilyMember.user_id == profile.id).all()
    return [dump(row) for row in rows]


@router.get("/families/{family_id}", tags=["families"])
def get_family(family_id: str, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> dict:
    member(db, family_id, profile.id)
    row = db.get(Family, family_id)
    if row is None:
        raise HTTPException(404, "Family not found")
    return dump(row)


@router.patch("/families/{family_id}", tags=["families"])
def update_family(family_id: str, body: FamilyUpdate, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> dict:
    member(db, family_id, profile.id, {"owner"})
    row = db.get(Family, family_id)
    if row is None:
        raise HTTPException(404, "Family not found")
    patch(row, body)
    db.commit()
    return dump(row)


@router.delete("/families/{family_id}", status_code=204, tags=["families"])
def delete_family(family_id: str, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> Response:
    member(db, family_id, profile.id, {"owner"})
    row = db.get(Family, family_id)
    if row is None:
        raise HTTPException(404, "Family not found")
    for elder in db.query(Elder).filter_by(family_id=family_id).all():
        delete_elder_records(db, elder)
    db.query(Invitation).filter_by(family_id=family_id).delete(synchronize_session=False)
    db.query(FamilyMember).filter_by(family_id=family_id).delete(synchronize_session=False)
    db.delete(row)
    db.commit()
    return Response(status_code=204)


@router.get("/families/{family_id}/members", tags=["families"])
def list_members(family_id: str, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> list[dict]:
    member(db, family_id, profile.id)
    rows = db.query(FamilyMember, Profile).join(Profile, Profile.id == FamilyMember.user_id).filter(FamilyMember.family_id == family_id).all()
    return [{**dump(m), "profile": dump(p)} for m, p in rows]


@router.patch("/families/{family_id}/members/{member_id}", tags=["families"])
def update_member(family_id: str, member_id: str, body: MemberRoleUpdate, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> dict:
    member(db, family_id, profile.id, {"owner"})
    row = db.get(FamilyMember, member_id)
    if row is None or row.family_id != family_id:
        raise HTTPException(404, "Member not found")
    if row.role == "owner":
        raise HTTPException(409, "Owner role cannot be changed")
    row.role = body.role
    db.commit()
    return dump(row)


@router.delete("/families/{family_id}/members/{member_id}", status_code=204, tags=["families"])
def remove_member(family_id: str, member_id: str, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> Response:
    member(db, family_id, profile.id, {"owner"})
    row = db.get(FamilyMember, member_id)
    if row is None or row.family_id != family_id:
        raise HTTPException(404, "Member not found")
    if row.role == "owner":
        raise HTTPException(409, "Owner cannot be removed")
    db.delete(row)
    db.commit()
    return Response(status_code=204)


@router.post("/families/{family_id}/invitations", status_code=201, tags=["families"])
def invite(family_id: str, body: InvitationCreate, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> dict:
    member(db, family_id, profile.id, {"owner"})
    row = Invitation(
        family_id=family_id, email=str(body.email).lower(), role=body.role,
        token=uid(), invited_by=profile.id, expires_at=utcnow() + timedelta(days=7),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return dump(row)


@router.get("/families/{family_id}/invitations", tags=["families"])
def list_invites(family_id: str, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> list[dict]:
    member(db, family_id, profile.id, {"owner"})
    return [dump(row) for row in db.query(Invitation).filter_by(family_id=family_id).all()]


@router.post("/invitations/accept", tags=["families"])
def accept_invite(body: InvitationAccept, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> dict:
    row = db.query(Invitation).filter_by(token=body.token, status="pending").first()
    if row is None or as_utc(row.expires_at) < utcnow():
        raise HTTPException(404, "Invitation is invalid or expired")
    if not profile.email or profile.email.lower() != row.email.lower():
        raise HTTPException(403, "Invitation email does not match authenticated user")
    existing = db.query(FamilyMember).filter_by(family_id=row.family_id, user_id=profile.id).first()
    if existing is None:
        existing = FamilyMember(
            family_id=row.family_id, user_id=profile.id, invitation_id=row.id,
            role=row.role, status="active",
        )
        db.add(existing)
    else:
        existing.invitation_id, existing.role, existing.status = row.id, row.role, "active"
    row.status, row.accepted_by, row.accepted_at = "accepted", profile.id, utcnow()
    audit(db, profile.id, "invitation.accepted", "invitation", row.id, family_id=row.family_id)
    db.commit()
    db.refresh(existing)
    return dump(existing)


@router.post("/invitations/{invitation_id}/decline", tags=["families"])
def decline_invite(
    invitation_id: str,
    db: Session = Depends(get_db),
    profile: Profile = Depends(get_current_profile),
) -> dict:
    row = db.get(Invitation, invitation_id)
    if row is None:
        raise HTTPException(404, "Invitation not found")
    if not profile.email or profile.email.lower() != row.email.lower():
        raise HTTPException(403, "Only the invitation recipient may decline")
    if row.status == "declined":
        return dump(row)
    if row.status != "pending":
        raise HTTPException(409, f"Cannot decline an invitation with status {row.status}")
    row.status = "declined"
    audit(db, profile.id, "invitation.declined", "invitation", row.id)
    db.commit()
    return dump(row)


@router.post("/families/{family_id}/invitations/{invitation_id}/revoke", tags=["families"])
def revoke_invite(
    family_id: str,
    invitation_id: str,
    db: Session = Depends(get_db),
    profile: Profile = Depends(get_current_profile),
) -> dict:
    member(db, family_id, profile.id, {"owner"})
    row = db.get(Invitation, invitation_id)
    if row is None or row.family_id != family_id:
        raise HTTPException(404, "Invitation not found")
    if row.status == "revoked":
        return dump(row)
    if row.status != "pending":
        raise HTTPException(409, f"Cannot revoke an invitation with status {row.status}")
    row.status = "revoked"
    audit(db, profile.id, "invitation.revoked", "invitation", row.id, family_id=family_id)
    db.commit()
    return dump(row)


@router.post("/families/{family_id}/elders", status_code=201, tags=["elders"])
def create_elder(family_id: str, body: ElderCreate, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> dict:
    member(db, family_id, profile.id, CARE_ROLES)
    row = Elder(family_id=family_id, created_by=profile.id, **body.model_dump())
    db.add(row)
    db.flush()
    log(db, row.id, profile.id, "profile_update", f"{row.full_name} was added")
    audit(db, profile.id, "elder.created", "elder_profile", row.id, family_id=family_id, elder_id=row.id)
    db.commit()
    db.refresh(row)
    return dump(row)


@router.get("/families/{family_id}/elders", tags=["elders"])
def list_elders(family_id: str, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> list[dict]:
    member(db, family_id, profile.id)
    return [dump(row) for row in db.query(Elder).filter_by(family_id=family_id).all()]


@router.get("/elders/me", tags=["elders"])
def get_my_elder(db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> dict:
    row = db.query(Elder).filter_by(user_id=profile.id, is_active=True).first()
    if row is None:
        raise HTTPException(404, "No elder profile is linked to this user")
    return dump(row)


@router.get("/elders/{elder_id}", tags=["elders"])
def get_elder(elder_id: str, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> dict:
    return dump(elder_access(db, elder_id, profile.id))


@router.patch("/elders/{elder_id}", tags=["elders"])
def update_elder(elder_id: str, body: ElderUpdate, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> dict:
    row = elder_access(db, elder_id, profile.id, "manage")
    patch(row, body)
    log(db, elder_id, profile.id, "profile_update", f"{row.full_name}'s profile was updated")
    db.commit()
    return dump(row)


@router.delete("/elders/{elder_id}", status_code=204, tags=["elders"])
def delete_elder(elder_id: str, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> Response:
    row = elder_access(db, elder_id, profile.id, "manage")
    delete_elder_records(db, row)
    db.commit()
    return Response(status_code=204)


@router.post("/elders/{elder_id}/reminders", status_code=201, tags=["reminders"])
def create_reminder(elder_id: str, body: ReminderCreate, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> dict:
    elder_access(db, elder_id, profile.id, "manage")
    values = body.model_dump()
    if values["end_date"] and values["end_date"] < values["start_date"]:
        raise HTTPException(422, "end_date must be on or after start_date")
    values["next_run_at"] = values["next_run_at"] or initial_run(
        values["start_date"], values["local_time"], values["timezone"]
    )
    row = Reminder(elder_id=elder_id, assigned_by=profile.id, **values)
    db.add(row)
    db.flush()
    log(db, elder_id, profile.id, "reminder_created", f"Reminder created: {row.title}", {"reminder_id": row.id})
    audit(
        db, profile.id, "reminder.created", "reminder", row.id,
        family_id=elder_access(db, elder_id, profile.id).family_id, elder_id=elder_id,
    )
    db.commit()
    db.refresh(row)
    return dump(row)


@router.get("/elders/{elder_id}/reminders", tags=["reminders"])
def list_reminders(
    elder_id: str, start: datetime | None = None, end: datetime | None = None,
    db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile),
) -> list[dict]:
    elder_access(db, elder_id, profile.id)
    query = db.query(Reminder).filter_by(elder_id=elder_id)
    if start:
        query = query.filter(Reminder.next_run_at >= start)
    if end:
        query = query.filter(Reminder.next_run_at <= end)
    return [dump(row) for row in query.order_by(Reminder.next_run_at).all()]


@router.get("/elders/{elder_id}/calendar", tags=["reminders"])
def calendar(
    elder_id: str, month: date = Query(default_factory=date.today),
    db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile),
) -> dict:
    elder_access(db, elder_id, profile.id)
    start = month.replace(day=1)
    next_month = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
    rows = db.query(Reminder).filter(
        Reminder.elder_id == elder_id,
        Reminder.next_run_at >= datetime.combine(start, datetime.min.time(), tzinfo=timezone.utc),
        Reminder.next_run_at < datetime.combine(next_month, datetime.min.time(), tzinfo=timezone.utc),
    ).all()
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        if row.next_run_at:
            grouped.setdefault(row.next_run_at.date().isoformat(), []).append(dump(row))
    return {"month": start.strftime("%Y-%m"), "days": grouped}


@router.get("/reminders/{reminder_id}", tags=["reminders"])
def get_reminder(reminder_id: str, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> dict:
    row = db.get(Reminder, reminder_id)
    if row is None:
        raise HTTPException(404, "Reminder not found")
    elder_access(db, row.elder_id, profile.id)
    return dump(row)


@router.patch("/reminders/{reminder_id}", tags=["reminders"])
def update_reminder(reminder_id: str, body: ReminderUpdate, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> dict:
    row = db.get(Reminder, reminder_id)
    if row is None:
        raise HTTPException(404, "Reminder not found")
    elder_access(db, row.elder_id, profile.id, "manage")
    patch(row, body)
    if row.end_date and row.end_date < row.start_date:
        raise HTTPException(422, "end_date must be on or after start_date")
    db.commit()
    return dump(row)


@router.post("/reminders/{reminder_id}/pause", tags=["reminders"])
def pause_reminder(
    reminder_id: str,
    db: Session = Depends(get_db),
    profile: Profile = Depends(get_current_profile),
) -> dict:
    row = db.get(Reminder, reminder_id)
    if row is None:
        raise HTTPException(404, "Reminder not found")
    elder_access(db, row.elder_id, profile.id, "manage")
    if row.status == "paused":
        return dump(row)
    if row.status != "active":
        raise HTTPException(409, f"Cannot pause a reminder with status {row.status}")
    row.status = "paused"
    log(db, row.elder_id, profile.id, "other", f"Paused reminder: {row.title}")
    db.commit()
    return dump(row)


@router.post("/reminders/{reminder_id}/resume", tags=["reminders"])
def resume_reminder(
    reminder_id: str,
    db: Session = Depends(get_db),
    profile: Profile = Depends(get_current_profile),
) -> dict:
    row = db.get(Reminder, reminder_id)
    if row is None:
        raise HTTPException(404, "Reminder not found")
    elder_access(db, row.elder_id, profile.id, "manage")
    if row.status == "active":
        return dump(row)
    if row.status != "paused":
        raise HTTPException(409, f"Cannot resume a reminder with status {row.status}")
    row.status = "active"
    if row.next_run_at is None:
        row.next_run_at = initial_run(row.start_date, row.local_time, row.timezone)
    log(db, row.elder_id, profile.id, "other", f"Resumed reminder: {row.title}")
    db.commit()
    return dump(row)


@router.post("/reminders/{reminder_id}/snooze", tags=["reminders"])
def snooze_reminder(
    reminder_id: str,
    body: ReminderSnooze,
    db: Session = Depends(get_db),
    profile: Profile = Depends(get_current_profile),
) -> dict:
    row = db.get(Reminder, reminder_id)
    if row is None:
        raise HTTPException(404, "Reminder not found")
    elder_access(db, row.elder_id, profile.id, "manage")
    if row.status != "active" or row.next_run_at is None:
        raise HTTPException(409, "Only an active scheduled reminder can be snoozed")
    expected = as_utc(body.scheduled_for)
    marker = (row.repeat_rule or {}).get("_last_snooze")
    if marker and marker.get("scheduled_for") == expected.isoformat() and marker.get("minutes") == body.minutes:
        return dump(row)
    if as_utc(row.next_run_at) != expected:
        raise HTTPException(409, "Reminder occurrence changed; refresh before snoozing")
    target = expected + timedelta(minutes=body.minutes)
    row.next_run_at = target
    row.repeat_rule = {
        **(row.repeat_rule or {}),
        "_last_snooze": {
            "scheduled_for": expected.isoformat(),
            "minutes": body.minutes,
            "snoozed_until": target.isoformat(),
        },
    }
    log(
        db, row.elder_id, profile.id, "other", f"Snoozed reminder: {row.title}",
        {"reminder_id": row.id, "minutes": body.minutes},
        source="family",
    )
    db.commit()
    return dump(row)


@router.post("/reminders/{reminder_id}/complete", tags=["reminders"])
def complete_reminder(
    reminder_id: str, body: ReminderCompletionCreate | None = None,
    db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile),
) -> dict:
    row = db.get(Reminder, reminder_id)
    if row is None:
        raise HTTPException(404, "Reminder not found")
    elder = elder_access(db, row.elder_id, profile.id, "self_service")
    payload = body or ReminderCompletionCreate()
    current_run = row.next_run_at or utcnow()
    snooze_marker = (row.repeat_rule or {}).get("_last_snooze")
    was_snoozed = bool(
        snooze_marker
        and snooze_marker.get("snoozed_until") == as_utc(current_run).isoformat()
    )
    scheduled_for = (
        datetime.fromisoformat(snooze_marker["scheduled_for"])
        if was_snoozed else current_run
    )
    existing = db.query(ReminderCompletion).filter_by(
        reminder_id=row.id, scheduled_for=scheduled_for
    ).first()
    if existing:
        raise HTTPException(409, "This reminder occurrence is already recorded")
    completion = ReminderCompletion(
        reminder_id=row.id,
        scheduled_for=scheduled_for,
        status=payload.status,
        completed_at=utcnow() if payload.status == "completed" else None,
        completed_by=profile.id,
        response_text=payload.response_text,
        metadata_json={
            **payload.metadata,
            **({"snoozed_until": snooze_marker["snoozed_until"]} if was_snoozed else {}),
        },
    )
    db.add(completion)
    following = next_occurrence(row, scheduled_for)
    row.next_run_at = following
    if was_snoozed:
        row.repeat_rule = {key: value for key, value in row.repeat_rule.items() if key != "_last_snooze"}
    if following is None:
        row.status = "completed"
    log(
        db, row.elder_id, profile.id, "reminder_completed", f"Completed: {row.title}",
        {"reminder_id": row.id}, source=actor_source(elder, profile.id),
    )
    audit(
        db, profile.id, f"reminder.{payload.status}", "reminder_completion", completion.id,
        family_id=audit_family_id(db, elder, profile.id), elder_id=row.elder_id,
    )
    db.commit()
    db.refresh(completion)
    return {"reminder": dump(row), "completion": dump(completion)}


@router.delete("/reminders/{reminder_id}", status_code=204, tags=["reminders"])
def delete_reminder(reminder_id: str, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> Response:
    row = db.get(Reminder, reminder_id)
    if row is None:
        raise HTTPException(404, "Reminder not found")
    elder_access(db, row.elder_id, profile.id, "manage")
    db.delete(row)
    db.commit()
    return Response(status_code=204)


@router.get("/elders/{elder_id}/activities", tags=["activities"])
def activities(elder_id: str, limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> list[dict]:
    elder_access(db, elder_id, profile.id)
    return [dump(row) for row in db.query(Activity).filter_by(elder_id=elder_id).order_by(Activity.created_at.desc()).limit(limit).all()]


@router.post("/elders/{elder_id}/wellness", status_code=201, tags=["wellness"])
def add_wellness(elder_id: str, body: WellnessCreate, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> dict:
    elder = elder_access(db, elder_id, profile.id, "self_service")
    if db.query(WellnessEntry).filter_by(elder_id=elder_id, check_date=body.check_date).first():
        raise HTTPException(409, "A wellness entry already exists for this date")
    row = WellnessEntry(
        elder_id=elder_id, recorded_by=profile.id, completed_at=utcnow(), **body.model_dump()
    )
    db.add(row)
    db.flush()
    log(
        db, elder_id, profile.id, "wellness_check", "Wellness check-in recorded",
        source=actor_source(elder, profile.id),
    )
    db.commit()
    db.refresh(row)
    return dump(row)


@router.get("/elders/{elder_id}/wellness", tags=["wellness"])
def wellness(elder_id: str, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> list[dict]:
    elder_access(db, elder_id, profile.id)
    return [dump(row) for row in db.query(WellnessEntry).filter_by(elder_id=elder_id).order_by(WellnessEntry.check_date.desc()).all()]


@router.post("/conversations", status_code=201, tags=["ai"])
def create_conversation(body: ConversationCreate, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> dict:
    elder_access(db, body.elder_id, profile.id, "self_service")
    row = Conversation(elder_id=body.elder_id, started_by=profile.id, title=body.title)
    db.add(row)
    db.commit()
    db.refresh(row)
    return dump(row)


@router.get("/conversations/{conversation_id}", tags=["ai"])
def get_conversation(conversation_id: str, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> dict:
    row = db.get(Conversation, conversation_id)
    if row is None:
        raise HTTPException(404, "Conversation not found")
    elder_access(db, row.elder_id, profile.id, "self_service")
    messages = db.query(Message).filter_by(conversation_id=row.id).order_by(Message.created_at).all()
    return {**dump(row), "messages": [dump(item) for item in messages]}


@router.post("/conversations/{conversation_id}/messages", tags=["ai"])
def chat(conversation_id: str, body: ChatMessageCreate, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> dict:
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(404, "Conversation not found")
    elder = elder_access(db, conversation.elder_id, profile.id, "self_service")
    previous = db.query(Message).filter_by(conversation_id=conversation_id).order_by(Message.created_at).limit(20).all()
    history = [{"role": item.role, "content": item.content} for item in previous]
    approved_keys = {"preferred_language", "communication_style", "routine_notes", "last_topic"}
    approved_memory = {
        key: value for key, value in (conversation.memory or {}).items() if key in approved_keys
    }
    wellness_context = db.query(WellnessEntry).filter_by(elder_id=elder.id).order_by(
        WellnessEntry.check_date.desc()
    ).limit(3).all()
    reminder_context = db.query(Reminder).filter_by(
        elder_id=elder.id, status="active"
    ).order_by(Reminder.next_run_at).limit(5).all()
    context = {
        "preferred_language": elder.preferred_language,
        "conversation_memory": approved_memory,
        "recent_wellness": [
            {
                "date": item.check_date.isoformat(),
                "mood": item.mood,
                "sleep_hours": float(item.sleep_hours) if item.sleep_hours is not None else None,
                "pain_level": item.pain_level,
            }
            for item in wellness_context
        ],
        "upcoming_reminders": [
            {
                "type": item.type,
                "title": item.title,
                "next_run_at": item.next_run_at.isoformat() if item.next_run_at else None,
            }
            for item in reminder_context
        ],
    }
    db.add(Message(conversation_id=conversation_id, sender_id=profile.id, role="user", content=body.content))
    try:
        result = answer(history, body.content, body.use_search, body.speak, context=context)
    except RuntimeError as exc:
        db.rollback()
        raise HTTPException(503, str(exc)) from exc
    assistant = Message(
        conversation_id=conversation_id, role="assistant", content=result["content"],
        metadata_json={"citations": result["citations"]},
    )
    db.add(assistant)
    conversation.last_message_at = utcnow()
    conversation.summary = result.get("summary") or result["content"].replace("\n", " ")[:240]
    conversation.memory = {
        **approved_memory,
        **{
            key: value
            for key, value in (result.get("memory_update") or {}).items()
            if key in approved_keys
        },
    }
    log(
        db, conversation.elder_id, profile.id, "ai_conversation",
        "Sahaay conversation updated", source=actor_source(elder, profile.id),
    )
    db.commit()
    db.refresh(assistant)
    return {**dump(assistant), "audio_url": result["audio_url"]}


@router.get("/elders/{elder_id}/health-score", tags=["analytics"])
def health_score(elder_id: str, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> dict:
    elder_access(db, elder_id, profile.id)
    row = calculate_health_score(db, elder_id)
    db.commit()
    return dump(row)


@router.get("/elders/{elder_id}/risk-insights", tags=["analytics"])
def risk_insights(
    elder_id: str,
    db: Session = Depends(get_db),
    profile: Profile = Depends(get_current_profile),
) -> dict:
    elder_access(db, elder_id, profile.id)
    return calculate_risk_signals(db, elder_id)


@router.get("/elders/{elder_id}/dashboard", tags=["analytics"])
def elder_dashboard(elder_id: str, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> dict:
    elder = elder_access(db, elder_id, profile.id)
    today = date.today()
    start = datetime.combine(today, datetime.min.time())
    end = start + timedelta(days=1)
    reminders = db.query(Reminder).filter(
        Reminder.elder_id == elder_id,
        Reminder.next_run_at >= start,
        Reminder.next_run_at < end,
    ).all()
    score = calculate_health_score(db, elder_id)
    active_sos = db.query(SOSAlert).filter_by(elder_id=elder_id, status="active").count()
    db.commit()
    return {"elder": dump(elder), "health_score": dump(score), "today_reminders": [dump(r) for r in reminders], "active_sos": active_sos}


@router.get("/families/{family_id}/dashboard", tags=["analytics"])
def family_dashboard(family_id: str, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> dict:
    member(db, family_id, profile.id)
    elders = db.query(Elder).filter_by(family_id=family_id).all()
    result = {
        "family_id": family_id,
        "elders": [{"elder": dump(e), "health_score": dump(calculate_health_score(db, e.id))} for e in elders],
        "pending_reminders": db.query(Reminder).join(Elder).filter(
            Elder.family_id == family_id, Reminder.status == "active"
        ).count(),
        "active_sos": db.query(SOSAlert).join(Elder).filter(Elder.family_id == family_id, SOSAlert.status == "active").count(),
    }
    db.commit()
    return result


@router.get("/families/{family_id}/analytics", tags=["analytics"])
def analytics(family_id: str, days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> dict:
    member(db, family_id, profile.id)
    since = utcnow() - timedelta(days=days)
    total, complete = db.query(
        func.count(ReminderCompletion.id),
        func.sum(case((ReminderCompletion.status == "completed", 1), else_=0)),
    ).join(Reminder, Reminder.id == ReminderCompletion.reminder_id).join(Elder).filter(
        Elder.family_id == family_id, ReminderCompletion.scheduled_for >= since
    ).one()
    return {"days": days, "reminders_total": total or 0, "reminders_completed": complete or 0, "adherence_percent": round((complete or 0) / total * 100, 1) if total else 100.0}


@router.post("/devices", status_code=201, tags=["notifications"])
def register_device(body: DeviceTokenCreate, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> dict:
    row = db.query(DeviceToken).filter_by(user_id=profile.id, token=body.token).first()
    if row is None:
        row = DeviceToken(user_id=profile.id, **body.model_dump())
        db.add(row)
    else:
        row.is_active, row.platform, row.device_name = True, body.platform, body.device_name
    db.commit()
    db.refresh(row)
    return dump(row)


@router.delete("/devices/{device_id}", status_code=204, tags=["notifications"])
def unregister_device(device_id: str, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> Response:
    row = db.get(DeviceToken, device_id)
    if row is None or row.user_id != profile.id:
        raise HTTPException(404, "Device token not found")
    db.delete(row)
    db.commit()
    return Response(status_code=204)


@router.get("/notifications", tags=["notifications"])
def notifications(db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> list[dict]:
    return [dump(row) for row in db.query(Notification).filter_by(user_id=profile.id).order_by(Notification.created_at.desc()).all()]


@router.post("/notifications/send", status_code=201, tags=["notifications"])
def create_notification(body: NotificationCreate, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> dict:
    shared = db.query(FamilyMember).filter(FamilyMember.user_id.in_([profile.id, body.user_id])).group_by(FamilyMember.family_id).having(func.count(FamilyMember.id) >= 2).first()
    if body.user_id != profile.id and shared is None:
        raise HTTPException(403, "Recipient is not in your family")
    row = send_notification(
        db, body.user_id, body.title, body.body, body.data,
        notification_type=body.type, elder_id=body.elder_id,
    )
    db.commit()
    db.refresh(row)
    return dump(row)


@router.post("/notifications/{notification_id}/read", tags=["notifications"])
def read_notification(notification_id: str, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> dict:
    row = db.get(Notification, notification_id)
    if row is None or row.user_id != profile.id:
        raise HTTPException(404, "Notification not found")
    row.read_at = utcnow()
    row.status = "read"
    db.commit()
    return dump(row)


@router.post("/elders/{elder_id}/sos", status_code=201, tags=["sos"])
def trigger_sos(elder_id: str, body: SOSCreate, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> dict:
    elder = elder_access(db, elder_id, profile.id, "self_service")
    values = body.model_dump()
    values["metadata_json"] = values.pop("metadata")
    row = SOSAlert(elder_id=elder_id, triggered_by=profile.id, **values)
    db.add(row)
    db.flush()
    log(
        db, elder_id, profile.id, "sos", body.message, {"sos_id": row.id},
        source=actor_source(elder, profile.id),
    )
    audit(
        db, profile.id, "sos.triggered", "sos_alert", row.id,
        family_id=audit_family_id(db, elder, profile.id), elder_id=elder_id,
    )
    for user_id in [m.user_id for m in db.query(FamilyMember).filter_by(family_id=elder.family_id).all() if m.user_id != profile.id]:
        send_notification(
            db, user_id, f"SOS: {elder.full_name}", body.message,
            {"sos_id": row.id, "priority": "critical"}, notification_type="sos", elder_id=elder_id,
        )
    db.commit()
    db.refresh(row)
    return dump(row)


@router.get("/elders/{elder_id}/sos", tags=["sos"])
def list_sos(elder_id: str, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> list[dict]:
    elder_access(db, elder_id, profile.id)
    return [dump(row) for row in db.query(SOSAlert).filter_by(elder_id=elder_id).order_by(SOSAlert.created_at.desc()).all()]


@router.post("/sos/{sos_id}/acknowledge", tags=["sos"])
def acknowledge_sos(
    sos_id: str,
    db: Session = Depends(get_db),
    profile: Profile = Depends(get_current_profile),
) -> dict:
    row = db.get(SOSAlert, sos_id)
    if row is None:
        raise HTTPException(404, "SOS alert not found")
    elder_access(db, row.elder_id, profile.id, "manage")
    if row.status == "acknowledged":
        return dump(row)
    if row.status != "active":
        raise HTTPException(409, f"Cannot acknowledge an SOS with status {row.status}")
    row.status = "acknowledged"
    row.acknowledged_by = profile.id
    row.acknowledged_at = utcnow()
    log(db, row.elder_id, profile.id, "sos", "SOS alert acknowledged", {"sos_id": row.id})
    db.commit()
    return dump(row)


@router.post("/sos/{sos_id}/resolve", tags=["sos"])
def resolve_sos(sos_id: str, db: Session = Depends(get_db), profile: Profile = Depends(get_current_profile)) -> dict:
    row = db.get(SOSAlert, sos_id)
    if row is None:
        raise HTTPException(404, "SOS alert not found")
    elder_access(db, row.elder_id, profile.id, "manage")
    if row.status == "resolved":
        return dump(row)
    if row.status not in {"active", "acknowledged"}:
        raise HTTPException(409, f"Cannot resolve an SOS with status {row.status}")
    now = utcnow()
    row.status, row.resolved_by, row.resolved_at = "resolved", profile.id, now
    row.acknowledged_by = row.acknowledged_by or profile.id
    row.acknowledged_at = row.acknowledged_at or now
    log(db, row.elder_id, profile.id, "sos", "SOS alert resolved", {"sos_id": row.id})
    db.commit()
    return dump(row)
