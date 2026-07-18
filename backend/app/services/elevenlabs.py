from __future__ import annotations

import uuid
from pathlib import Path

from app.config import AUDIO_DIR, get_settings


def ensure_audio_dir() -> Path:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    return AUDIO_DIR


def synthesize_speech(text: str) -> str | None:
    """Generate TTS audio; return public path like /static/audio/<id>.mp3 or None."""
    settings = get_settings()
    if not settings.enable_voice or not settings.elevenlabs_api_key:
        return None

    clean = (text or "").strip()
    if not clean:
        return None

    # Keep TTS short for demo latency / cost
    if len(clean) > 600:
        clean = clean[:600] + "..."

    ensure_audio_dir()
    filename = f"{uuid.uuid4().hex}.mp3"
    filepath = AUDIO_DIR / filename

    try:
        from elevenlabs.client import ElevenLabs

        client = ElevenLabs(api_key=settings.elevenlabs_api_key)
        audio_iter = client.text_to_speech.convert(
            voice_id=settings.elevenlabs_voice_id,
            text=clean,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )
        with open(filepath, "wb") as f:
            for chunk in audio_iter:
                if isinstance(chunk, bytes):
                    f.write(chunk)
        return f"/static/audio/{filename}"
    except Exception:
        if filepath.exists():
            filepath.unlink(missing_ok=True)
        return None
