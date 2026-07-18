# Deploy Sahaay on Replit (frontend + backend)

Replit Autoscale = **one public port per Repl**. Use **two Repls** from the same GitHub repo.

| Repl | Copy to repo root | Port | Guide |
|------|-------------------|------|-------|
| **Backend** | [`backend/.replit`](backend/.replit) + [`backend/replit.nix`](backend/replit.nix) | 8000 → 80 | [backend/REPLIT.md](backend/REPLIT.md) |
| **Frontend** | [`frontend/.replit`](frontend/.replit) + [`frontend/replit.nix`](frontend/replit.nix) | 3000 → 80 | [frontend/REPLIT.md](frontend/REPLIT.md) |

## Quick path

1. **Repl A (API)** — Import GitHub → copy backend `.replit` / `replit.nix` to root → Secrets → Deploy  
   → `https://sahaay-api.replit.app`
2. **Repl B (UI)** — Import same repo → copy frontend `.replit` / `replit.nix` to root → Secret `NEXT_PUBLIC_API_BASE_URL` → Deploy  
   → `https://sahaay.replit.app`

## Env checklist

**Backend secrets (minimum):**
- `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_DB_PASSWORD`
- or `DATABASE_URL` (Postgres URI)
- `CORS_ORIGINS` = your frontend URL (e.g. `https://sahaay.replit.app`)
- `ANTHROPIC_API_KEY` (for AI chat)

**Optional backend:** `EXA_API_KEY`, `ELEVENLABS_API_KEY`, `ENABLE_VOICE`, `FIREBASE_CREDENTIALS_JSON`, `REDIS_URL`

**Frontend secrets:**
- `NEXT_PUBLIC_API_BASE_URL` = `https://sahaay-api.replit.app` (no trailing slash; set before build)

Docker: [backend/Dockerfile](backend/Dockerfile)
