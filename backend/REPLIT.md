# Deploy Sahaay backend on Replit

Config in this folder:

- [`.replit`](.replit)
- [`replit.nix`](replit.nix)

## 1. Create the Repl

1. [replit.com](https://replit.com) → **Create** → **Import from GitHub** → `Sahaay-AI`
2. Copy to **repo root** (Replit reads `./.replit`):
   - `backend/.replit` → `./.replit`
   - `backend/replit.nix` → `./replit.nix`

## 2. Secrets

**Tools → Secrets** (and again under **Deployment** secrets):

| Key | Required | Notes |
|-----|----------|--------|
| `SUPABASE_URL` | Yes* | Project URL |
| `SUPABASE_PUBLISHABLE_KEY` | Yes* | Anon / publishable key |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes* | Server only — never expose to browser |
| `SUPABASE_DB_PASSWORD` | Yes* | DB password (builds pooler URL) |
| `DATABASE_URL` | Alt* | Full `postgresql://…` URI instead of password fields |
| `CORS_ORIGINS` | Yes | Frontend origin(s), comma-separated |
| `ANTHROPIC_API_KEY` | For AI | Claude |
| `EXA_API_KEY` | No | Grounded search |
| `ELEVENLABS_API_KEY` | No | Voice |
| `ENABLE_VOICE` | No | `true` / `false` |
| `FIREBASE_CREDENTIALS_JSON` | No | One-line service account JSON |
| `REDIS_URL` | No | Celery broker |
| `APP_ENV` | No | Defaults via `.replit` to `production` |

\* Use either `DATABASE_URL` **or** Supabase URL + `SUPABASE_DB_PASSWORD`.

Example CORS after frontend is live:

```
CORS_ORIGINS=https://sahaay.replit.app,http://localhost:3000
```

## 3. Run

Click **Run** → listens on `0.0.0.0:8000`.

- Health: `/health`
- Docs: `/docs`
- API prefix: `/api/v1`

## 4. Deploy

1. **Deploy** → **Autoscale** (or Reserved VM)
2. Confirm build/run from `.replit`
3. Ensure Deployment secrets match workspace secrets
4. Public URL: `https://<name>.replit.app`

## 5. Frontend

Second Repl — see [`../frontend/REPLIT.md`](../frontend/REPLIT.md). Set:

```
NEXT_PUBLIC_API_BASE_URL=https://<backend>.replit.app
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Health check fails | Must bind `0.0.0.0:8000`; port map `8000 → 80` |
| DB disconnected | Pooler URI / `SUPABASE_DB_PASSWORD`; use `postgresql://` |
| CORS errors | Add exact frontend origin to `CORS_ORIGINS` |
| Module not found `app` | Commands must `cd backend` first |
| Wrong app | Root `.replit` still frontend — replace with `backend/.replit` |
