from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Routine
from app.schemas import ReminderCreate, ReminderDemoResponse, ReminderOut, RoutineOut
from app.services import memory as memory_service
from app.services.elevenlabs import synthesize_speech
from app.services.reminders import build_reminder_message, pick_demo_routine

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.post("", response_model=ReminderOut)
def create_reminder(body: ReminderCreate, db: Session = Depends(get_db)) -> ReminderOut:
    routine: Routine | None = None
    if body.routine_id is not None:
        routine = db.get(Routine, body.routine_id)
        if routine is None or routine.session_id != body.session_id:
            raise HTTPException(status_code=404, detail="Routine not found for this session")

    session = memory_service.get_or_create_session(db, body.session_id)
    message = build_reminder_message(
        routine,
        user_name=session.user_name,
        custom_message=body.message,
    )
    scheduled = body.scheduled_time or (routine.timing if routine else None)
    reminder = memory_service.create_reminder(
        db,
        session_id=body.session_id,
        message=message,
        routine_id=body.routine_id,
        scheduled_time=scheduled,
        is_demo=False,
    )
    return ReminderOut.model_validate(reminder)


@router.get("/demo", response_model=ReminderDemoResponse)
def reminder_demo(
    session_id: str,
    speak: bool = True,
    db: Session = Depends(get_db),
) -> ReminderDemoResponse:
    routine, user_name = pick_demo_routine(db, session_id)
    message = build_reminder_message(routine, user_name=user_name)
    reminder = memory_service.create_reminder(
        db,
        session_id=session_id,
        message=message,
        routine_id=routine.id if routine else None,
        scheduled_time=routine.timing if routine else None,
        is_demo=True,
    )
    audio_url = synthesize_speech(message) if speak else None
    return ReminderDemoResponse(
        message=message,
        routine=RoutineOut.model_validate(routine) if routine else None,
        audio_url=audio_url,
        reminder=ReminderOut.model_validate(reminder),
    )
