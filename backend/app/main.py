from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import AUDIO_DIR, BACKEND_ROOT, get_settings
from app.db import init_db
from app.routers import chat, reminders, routines, voice
from app.schemas import HealthResponse


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="Sahaay API",
    description="Ambient AI Care Companion — Hackathon MVP backend",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AUDIO_DIR.mkdir(parents=True, exist_ok=True)
static_root = BACKEND_ROOT / "static"
static_root.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_root)), name="static")

app.include_router(chat.router)
app.include_router(routines.router)
app.include_router(reminders.router)
app.include_router(voice.router)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        services={
            "anthropic": bool(settings.anthropic_api_key),
            "exa": bool(settings.exa_api_key),
            "elevenlabs": bool(settings.elevenlabs_api_key) and settings.enable_voice,
        },
    )
