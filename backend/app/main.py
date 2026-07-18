"""FastAPI application factory and operational health endpoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import AUDIO_DIR, BACKEND_ROOT, get_settings
from app.db import check_db_connection, init_db
from app.routers.api_v1 import router as api_v1_router
from app.schemas import HealthResponse


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Initialize database tables and audio storage on startup."""
    init_db()
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="Sahaay API",
    description="Authenticated family elder-care platform",
    version="1.0.0",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AUDIO_DIR.mkdir(parents=True, exist_ok=True)
static_root = BACKEND_ROOT / "static"
static_root.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_root)), name="static")

app.include_router(api_v1_router, prefix=settings.api_v1_prefix)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Return API health and whether Anthropic, Exa, and ElevenLabs are configured."""
    settings = get_settings()
    db_ok = check_db_connection()
    db_label = "supabase_postgres" if settings.uses_supabase_postgres else "sqlite"

    return HealthResponse(
        status="ok" if db_ok else "degraded",
        database=f"{db_label}:{'connected' if db_ok else 'disconnected'}",
        services={
            "anthropic": bool(settings.anthropic_api_key),
            "exa": bool(settings.exa_api_key),
            "elevenlabs": bool(settings.elevenlabs_api_key) and settings.enable_voice,
            "firebase_auth": bool(
                settings.firebase_credentials_json or settings.firebase_project_id
            ),
            "supabase": bool(settings.supabase_url and settings.supabase_service_role_key),
            "celery_redis": bool(settings.redis_url),
            "database": db_ok,
        },
    )
