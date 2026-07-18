"""Reminder message composition and demo routine selection."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import ChatSession, Routine
from app.services import memory as memory_service


def build_reminder_message(
    routine: Routine | None,
    user_name: str | None = None,
    custom_message: str | None = None,
) -> str:
    """Build a warm personalized reminder string for a routine."""
    if custom_message:
        return custom_message

    name = user_name or "there"
    if routine is None:
        return (
            f"Good morning {name}. "
            "I'm here whenever you need a gentle reminder about your routine."
        )

    time_bit = f" (usually around {routine.timing})" if routine.timing else ""
    if routine.type == "medication":
        return f"Good morning {name}. It's time for your {routine.name}{time_bit}."
    if routine.type == "appointment":
        return f"Hi {name}. Reminder about your {routine.name}{time_bit}."
    if routine.type == "bill":
        return f"Hi {name}. Don't forget: {routine.name}{time_bit}."
    return f"Hi {name}. Gentle nudge for {routine.name}{time_bit}."


def pick_demo_routine(db: Session, session_id: str) -> tuple[Routine | None, str | None]:
    """Pick the best routine for the demo reminder and return it with the user name."""
    session = db.get(ChatSession, session_id)
    user_name = session.user_name if session else None
    routines = memory_service.get_routines(db, session_id)
    if not routines:
        return None, user_name

    # Prefer critical medications, then any medication, then first routine
    meds = [r for r in routines if r.type == "medication"]
    critical = [r for r in meds if r.priority == "critical"]
    if critical:
        return critical[0], user_name
    if meds:
        return meds[0], user_name
    return routines[0], user_name
