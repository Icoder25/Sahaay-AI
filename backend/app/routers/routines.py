"""Routines listing endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import RoutineOut
from app.services import memory as memory_service

router = APIRouter(tags=["routines"])


@router.get("/routines/{session_id}", response_model=list[RoutineOut])
def list_routines(session_id: str, db: Session = Depends(get_db)) -> list[RoutineOut]:
    """Return all routines stored for a demo session."""
    routines = memory_service.get_routines(db, session_id)
    return [RoutineOut.model_validate(r) for r in routines]
