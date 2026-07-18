# Sahaay Backend

Runnable FastAPI MVP for family-based elder care. All product routes are under `/api/v1`; Swagger is at `/docs`.

## Run locally

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

SQLite is the zero-configuration default. Set `DATABASE_URL` to a SQLAlchemy Postgres URL, or set `SUPABASE_URL` plus `SUPABASE_DB_PASSWORD` (and the pooler host/port) for deployment. SQLite tables are created at startup for local use and tests. Postgres tables are never auto-created; they must be managed by the checked-in Supabase migrations.

## Authentication

Clients sign in with Google through Firebase and send the Firebase ID token to `POST /api/v1/auth/firebase`. The API verifies the token with Firebase Admin, atomically creates or updates the Supabase user record, and inserts `login_history`. Subsequent protected requests send `Authorization: Bearer <firebase-id-token>`. Authorization uses the internal user UUID and database-backed family membership—not client-provided identity data.

Authentication routes:

- `POST /api/v1/auth/firebase`
- `GET /api/v1/auth/me`

Set `FIREBASE_CREDENTIALS_JSON`, `FIREBASE_PROJECT_ID`, `SUPABASE_URL`, and `SUPABASE_SERVICE_ROLE_KEY`. The service-role key is backend-only.

## API groups

- Profiles: current profile read/update
- Families: CRUD, invitation accept/decline/revoke, members, owner/admin/caregiver/member RBAC
- Elders: manager-controlled CRUD plus linked-elder self-service access
- Reminders: occurrence completion, pause/resume, idempotent snooze, date filtering and calendar
- Activities and wellness check-ins
- AI conversations using Claude, optional Exa grounding and ElevenLabs audio
- Explainable health scores across medicine, meals, sleep, mood, activity and adherence
- Deterministic 14-day risk insights for misses, pain, mood, check-ins and interactions
- Elder/family dashboards and family adherence analytics
- FCM device tokens, persisted notifications and read state
- SOS trigger/history/resolve with family notifications

Missing integration credentials fail closed: authentication returns an error, AI returns `503`, voice/search remain off, FCM notifications remain `pending`, and Celery uses an in-memory inert broker unless configured.

Recurring reminders stay `active`: completing an occurrence inserts a `reminder_completions` row and advances `next_run_at`. Once-only reminders become `completed`; exhausted escalation retries record a `missed` occurrence and advance recurring schedules. Significant mutations also write `audit_logs`.

Pause and resume preserve the pending occurrence. Snooze requires the caller's expected `scheduled_for`, stores an idempotency marker in `repeat_rule`, and keeps completion history tied to the original occurrence.

Linked users (`elder_profiles.user_id`) may read only their own elder data and can chat, submit wellness checks, complete reminders, and trigger SOS. Creating or changing elder profiles and reminders requires an active `owner`, `admin`, or `caregiver` family role.

AI prompts receive only approved conversation memory, preferred language, recent wellness, and upcoming reminders. Conversation summaries and bounded memory are persisted without diagnosis. Daily workers persist a real summary notification and matching activity containing completion, wellness, score, and next-day appointment data.

Useful workflow routes:

- `POST /api/v1/invitations/{id}/decline`
- `POST /api/v1/families/{family_id}/invitations/{id}/revoke`
- `POST /api/v1/reminders/{id}/pause|resume|snooze`
- `POST /api/v1/sos/{id}/acknowledge`
- `GET /api/v1/elders/{id}/risk-insights`

## Workers

Set `REDIS_URL`, then run:

```powershell
celery -A app.tasks.celery_app worker --loglevel=info
celery -A app.tasks.celery_app beat --loglevel=info
```

Scheduled jobs dispatch reminders, escalate incomplete reminders, create daily summaries, recalculate health scores, and retry failed notifications. Set `CELERY_ALWAYS_EAGER=true` only for local testing.

## Tests

Tests use SQLite and override authentication/integrations:

```powershell
pytest -q
python -m compileall app tests
```

## Safety

- Do not commit `.env`; use `.env.example`.
- Never expose the Supabase service-role key to a frontend.
- Medical notes and AI output are not diagnosis or emergency care.
- Use an emergency service directly when immediate danger exists.
