# Sahaay v1.0 Implementation Guide

This guide implements the web-first MVP defined in [Sahaay_Real_PRD.md](Sahaay_Real_PRD.md). WhatsApp and Twilio are not part of the MVP architecture.

> Backend rebuild boundary: the existing Next.js frontend remains unchanged. Backend, database, jobs, and contracts are rebuilt behind it.

## 1. Architecture

```text
Next.js web app
    │ HTTPS /api/v1 + Supabase access token
    ▼
FastAPI
    ├── Supabase JWT/JWKS authentication
    ├── family-scoped RBAC and domain APIs
    ├── Claude conversation and extraction
    ├── Exa grounded search
    ├── ElevenLabs optional speech
    └── FCM push delivery
          │
          ├── Supabase Postgres + RLS
          └── Redis + Celery worker/beat
```

## 2. Local prerequisites

- Python 3.11+
- PostgreSQL through the linked Supabase project
- Redis for queued and scheduled work
- Supabase project URL and publishable/server credentials
- Optional Anthropic, Exa, ElevenLabs, and Firebase credentials

Copy `backend/.env.example` to `backend/.env` and fill only local secrets. Never expose the Supabase service role or Firebase private key to Next.js.

## 3. Run the backend

PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000/docs` and check `GET /health`.

Run Redis separately, then start background processes:

```powershell
celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
celery -A app.tasks.celery_app beat --loglevel=info
```

Use `--pool=solo` for reliable local Windows development. Production may use the platform's normal prefork worker pool.

## 4. Runtime configuration

Configuration groups should include:

- `SUPABASE_URL`, database connection, JWT issuer/audience, and JWKS settings;
- Redis broker/result URLs and Celery timezone;
- Firebase Admin service-account configuration;
- `ANTHROPIC_API_KEY` and Claude model;
- `EXA_API_KEY`;
- `ELEVENLABS_API_KEY`, voice ID, and voice enable flag;
- allowed CORS origins and environment/logging settings.

Provider services must report disabled status and preserve core behavior when optional credentials are missing. FCM failure still creates an in-app notification; AI provider failure returns a safe fallback.

## 5. Database and authorization

Apply forward migrations from `supabase/migrations/`. The target schema is listed in the canonical PRD and uses:

- UUID identifiers and timezone-aware timestamps;
- foreign keys plus foreign-key indexes;
- constrained roles, statuses, and event types;
- `updated_at` triggers;
- RLS on every public table;
- private security-definer helpers for family and elder authorization.

FastAPI must validate the bearer token and repeat authorization checks. RLS is defense in depth, not a substitute for API RBAC. Test owner, member, elder, revoked invitation, and cross-family access.

## 6. API organization

All product APIs live under `/api/v1`.

| Domain | Responsibilities |
|---|---|
| Auth/profile | Supabase auth wrappers, current profile |
| Families | Family CRUD, invitations, members, roles |
| Elders | Profiles, preferences, emergency contacts |
| Reminders/calendar | CRUD, recurrence, due occurrences, completion, escalation |
| Activities/wellness | Timeline and daily check-ins |
| AI | Conversations, messages, multilingual responses, grounded answers |
| Health scores | Deterministic score generation and trends |
| Dashboards/analytics | Family and elder aggregates, KPI queries |
| Notifications | Device tokens, in-app records, delivery state |
| SOS | Create, fan out, acknowledge, resolve |

Use Pydantic request/response models, dependency-injected identity, pagination, consistent errors, and idempotency for reminder delivery and SOS.

## 7. Background jobs

Celery beat schedules:

- due-reminder dispatch;
- missed-reminder follow-up and escalation;
- evening family summaries;
- daily health-score generation;
- transient FCM retry.

Jobs should lock or upsert durable records before external delivery. Retries must not duplicate reminder occurrences, notifications, activities, or SOS incidents.

## 8. AI and safety

- Claude handles supportive conversation and structured extraction.
- Exa is invoked only when current external information is useful; return citations.
- ElevenLabs converts approved response text to audio when enabled.
- Store conversation and memory by elder and authorized family.
- Use deterministic code—not an LLM—for the numeric health score.
- Never diagnose, prescribe, or suggest changing medication.
- Escalate emergency language to an urgent safety response and family notification.

## 9. FCM flow

1. The web client obtains an FCM registration token with consent.
2. `POST /api/v1/notifications/devices` registers it to the authenticated profile.
3. A service persists the notification before attempting push.
4. Firebase Admin sends to active tokens.
5. Success/failure is recorded; transient errors are retried.
6. Invalid tokens are deactivated.

## 10. Verification

```powershell
cd backend
pytest
python -m compileall app
```

Minimum test coverage:

- Supabase JWT validation and RBAC;
- family isolation and invitation lifecycle;
- reminder recurrence, completion, escalation, and calendar;
- wellness and deterministic health scores;
- dashboard aggregates;
- FCM disabled/mocked delivery and retry;
- SOS idempotency and acknowledgment;
- Claude/Exa/ElevenLabs mocked behavior;
- startup and health check.

Before release, run Supabase security/performance advisors, verify RLS manually with two families, and perform an end-to-end browser test.

## 11. Deployment

- Next.js: Vercel or equivalent.
- FastAPI and Celery: container-capable host.
- Postgres/Auth: Supabase.
- Redis: managed Redis with persistence appropriate to the queue.
- Push: Firebase Cloud Messaging.

Use HTTPS, restricted CORS, secret management, database backups, structured logs, error monitoring, worker health monitoring, and separate staging/production projects.
