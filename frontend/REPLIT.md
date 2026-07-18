# Deploy Sahaay frontend on Replit

Use a **second Repl** for the UI. Backend stays on its own Repl.

```
Browser → Frontend Repl (Next.js :3000)
              ↓ NEXT_PUBLIC_API_BASE_URL
       Backend Repl (FastAPI :8000) → Supabase
```

## 1. Deploy backend first

See [`../backend/REPLIT.md`](../backend/REPLIT.md). Note:

```
https://<backend-name>.replit.app
```

## 2. Create the frontend Repl

1. **Import from GitHub** → same `Sahaay-AI` repo
2. Copy to **repo root**:
   - `frontend/.replit` → `./.replit`
   - `frontend/replit.nix` → `./replit.nix`
3. **Run** to verify Next on port 3000

## 3. Secrets

| Key | Value |
|-----|--------|
| `NEXT_PUBLIC_API_BASE_URL` | `https://<backend-name>.replit.app` (no trailing slash) |

Set under **Deployment secrets before build** — Next inlines `NEXT_PUBLIC_*` at build time.

Local: copy `.env.example` → `frontend/.env.local`.

## 4. Deploy

1. **Deploy** → **Autoscale**
2. Build: `cd frontend && npm ci && npm run build`
3. Run: `cd frontend && npx next start -H 0.0.0.0 -p 3000`
4. URL: `https://<frontend-name>.replit.app`

Then add that URL to backend `CORS_ORIGINS`.

## 5. Client helper

[`src/lib/config.ts`](src/lib/config.ts) / [`src/lib/api.ts`](src/lib/api.ts) use `NEXT_PUBLIC_API_BASE_URL`.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| API network / CORS | Backend `CORS_ORIGINS` must include this frontend URL |
| Env ignored | Redeploy after changing `NEXT_PUBLIC_*` |
| Health check fails | Bind `0.0.0.0:3000`; map `3000 → 80` |
| Wrong app | Replace root `.replit` with `frontend/.replit` |
