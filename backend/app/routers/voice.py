from fastapi import APIRouter, HTTPException

from app.schemas import VoiceSpeakRequest, VoiceSpeakResponse
from app.services.elevenlabs import synthesize_speech

router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/speak", response_model=VoiceSpeakResponse)
def speak(body: VoiceSpeakRequest) -> VoiceSpeakResponse:
    audio_url = synthesize_speech(body.text)
    if not audio_url:
        raise HTTPException(
            status_code=503,
            detail="Voice unavailable. Set ELEVENLABS_API_KEY and ENABLE_VOICE=true.",
        )
    return VoiceSpeakResponse(audio_url=audio_url, text=body.text)
