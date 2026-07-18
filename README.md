# Sahaay

Sahaay is a web-first AI care companion that helps families support elderly loved ones through reminders, wellness check-ins, routine insights, dashboards, summaries, and SOS alerts.

The canonical product scope is [DOCS/Sahaay_Real_PRD.md](DOCS/Sahaay_Real_PRD.md).

## Architecture

```text
Next.js responsive web app (existing frontend; unchanged in backend rebuild)
        │ HTTPS + Supabase bearer token
        ▼
FastAPI /api/v1
  ├─ Auth, profiles, families, members, elders
  ├─ Reminders, calendar, activities, wellness
  ├─ Dashboards, analytics, health scores, SOS
  ├─ Claude + Exa + optional ElevenLabs
  └─ FCM + persisted in-app notifications
        │
        ├─ Supabase Auth
        ├─ Supabase Postgres + RLS
        └─ Redis → Celery worker and beat
```

WhatsApp and Twilio are not v1.0 product dependencies.

## Repository

| Path | Purpose |
|---|---|
| [`frontend/`](frontend/) | Existing Next.js web interface |
| [`backend/`](backend/) | FastAPI API, services, jobs, and tests |
| [`supabase/`](supabase/) | Postgres migrations, constraints, indexes, and RLS |
| [`DOCS/`](DOCS/) | Canonical PRD and delivery documents |

## Backend quickstart

Prerequisites: Python 3.11+, a Supabase project, and Redis for background jobs.

PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Fill local Supabase settings and optional provider credentials.
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API documentation: `http://localhost:8000/docs`
Health check: `http://localhost:8000/health`

Optional integrations remain safely disabled when credentials are absent. FCM delivery requires Firebase Admin credentials; AI features require their corresponding provider keys.

## Background workers

Start Redis, then run these in separate PowerShell terminals:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
```

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
celery -A app.tasks.celery_app beat --loglevel=info
```

The worker handles due reminders, escalation, daily summaries, health scores, FCM retries, and related scheduled work. `--pool=solo` is recommended for local Windows development.

## Frontend

The frontend is intentionally unchanged by the backend rebuild.

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`. Configure only browser-safe Supabase and API values in the frontend environment; never expose service-role or Firebase Admin secrets.

## Database and auth

- Supabase Auth issues user sessions and access tokens.
- FastAPI validates bearer tokens through Supabase JWKS.
- FastAPI RBAC and Postgres RLS enforce family/elder boundaries.
- Apply forward migrations from `supabase/migrations/`.
- Never commit `.env` files or provider credentials.

## Tests

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest
python -m compileall app
```

Before release, test two-family isolation, reminder idempotency, FCM fallback/retries, deterministic health scores, and SOS acknowledgment.

## Documentation

- [Start here](DOCS/START_HERE.md)
- [Canonical v1.0 PRD](DOCS/Sahaay_Real_PRD.md)
- [Implementation guide](DOCS/Sahaay_Implementation_Guide.md)
- [User journeys](DOCS/Sahaay_User_Journeys.md)
- [30-day launch checklist](DOCS/Sahaay_30Day_Launch_Checklist.md)
- [GTM and research](DOCS/Sahaay_GTM_and_Research.md)
- [Pitch deck outline](DOCS/Sahaay_Pitch_Deck_Outline.md)
- [Quick reference](DOCS/Sahaay_Quick_Reference.txt)

## Safety

Sahaay is supportive care software, not a doctor, medical device, or emergency dispatch service. AI must not diagnose, prescribe, or alter medication instructions. In an emergency, contact local emergency services and trusted people directly.
