from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.schemas import ChatRequest, ChatResponse, RoutineOut
from app.services.claude import process_chat
from app.services.elevenlabs import synthesize_speech

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    settings = get_settings()
    if not settings.anthropic_api_key:
        raise HTTPException(
            status_code=503,
            detail="ANTHROPIC_API_KEY is not configured. Copy .env.example to .env and add your key.",
        )

    try:
        result = process_chat(db, body.session_id, body.message.strip())
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI request failed: {exc}") from exc

    audio_url = None
    if body.speak:
        audio_url = synthesize_speech(result["reply"])

    routines_out = [RoutineOut.model_validate(r) for r in result["routines_updated"]]

    return ChatResponse(
        reply=result["reply"],
        session_id=body.session_id,
        routines_updated=routines_out,
        citations=result["citations"],
        audio_url=audio_url,
        intent=result["intent"],
    )
