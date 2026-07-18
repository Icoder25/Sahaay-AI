from sqlalchemy.orm import Session

from app.models import ChatSession, Message, Reminder, Routine


def get_or_create_session(db: Session, session_id: str) -> ChatSession:
    session = db.get(ChatSession, session_id)
    if session is None:
        session = ChatSession(id=session_id)
        db.add(session)
        db.commit()
        db.refresh(session)
    return session


def add_message(db: Session, session_id: str, role: str, content: str) -> Message:
    get_or_create_session(db, session_id)
    msg = Message(session_id=session_id, role=role, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_recent_messages(db: Session, session_id: str, limit: int = 20) -> list[Message]:
    return (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.id.desc())
        .limit(limit)
        .all()[::-1]
    )


def get_routines(db: Session, session_id: str) -> list[Routine]:
    return (
        db.query(Routine)
        .filter(Routine.session_id == session_id)
        .order_by(Routine.id.asc())
        .all()
    )


def upsert_routines(db: Session, session_id: str, routines_data: list[dict]) -> list[Routine]:
    """Upsert routines by name (case-insensitive) within a session."""
    get_or_create_session(db, session_id)
    existing = {r.name.lower(): r for r in get_routines(db, session_id)}
    updated: list[Routine] = []

    for item in routines_data:
        name = (item.get("name") or "").strip()
        if not name:
            continue
        key = name.lower()
        if key in existing:
            routine = existing[key]
            routine.type = item.get("type") or routine.type
            routine.timing = item.get("timing") or routine.timing
            routine.frequency = item.get("frequency") or routine.frequency
            routine.notes = item.get("notes") if item.get("notes") is not None else routine.notes
            routine.priority = item.get("priority") or routine.priority
        else:
            routine = Routine(
                session_id=session_id,
                name=name,
                type=item.get("type") or "habit",
                timing=item.get("timing"),
                frequency=item.get("frequency") or "daily",
                notes=item.get("notes"),
                priority=item.get("priority") or "normal",
            )
            db.add(routine)
            existing[key] = routine
        updated.append(routine)

    db.commit()
    for r in updated:
        db.refresh(r)
    return updated


def set_user_name(db: Session, session_id: str, name: str | None) -> None:
    if not name:
        return
    session = get_or_create_session(db, session_id)
    session.user_name = name.strip()
    db.commit()


def create_reminder(
    db: Session,
    session_id: str,
    message: str,
    routine_id: int | None = None,
    scheduled_time: str | None = None,
    is_demo: bool = False,
) -> Reminder:
    get_or_create_session(db, session_id)
    reminder = Reminder(
        session_id=session_id,
        routine_id=routine_id,
        message=message,
        scheduled_time=scheduled_time,
        is_demo=is_demo,
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder
