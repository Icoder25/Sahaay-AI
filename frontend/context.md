# Sahaay Frontend — Project Context

Context for developers and AI agents working in `frontend/`. Read this before making changes.

## What this is

**Sahaay** is an AI-powered caregiving platform for elderly users and their families in India. The product vision is in [`Sahaay_PRD_v1.md`](./Sahaay_PRD_v1.md).

**Important:** Frontend work stays in this folder. Do **not** modify the backend — PRD features that lack API support are implemented with **client-side state** (`localStorage`) until backend endpoints exist.

| Layer | Scope |
|-------|--------|
| **Backend API (existing)** | `/health`, `/chat`, `/routines`, `/reminders/demo`, `/voice/speak` |
| **Frontend-only (localStorage)** | Auth, families, elder profiles, activity timeline, wellness, health score, SOS alerts, notifications |
| **Frontend UI** | Landing, login/register, `/elder`, `/family`, calendar, i18n (EN/HI/GU) |

## Routes

| Route | Purpose |
|-------|---------|
| `/` | Landing — choose elder or family experience |
| `/login`, `/register` | Client-side auth (demo accounts in localStorage) |
| `/elder` | Chat companion + routines + SOS + wellness |
| `/elder/calendar` | Routine schedule from backend `/routines/{session_id}` |
| `/family` | PRD success-criteria dashboard for caregivers |

## Backend integration (live `/api/v1`)

**Base URL:** `NEXT_PUBLIC_API_BASE_URL` (default `http://localhost:8000`)

Requires Supabase Auth on the backend (`SUPABASE_URL`, publishable + service keys).

| Method | Path | Used by |
|--------|------|---------|
| `GET` | `/health` | Health indicator |
| `POST` | `/api/v1/auth/signup` · `/login` · `/refresh` · `/logout` | Auth |
| `GET/PATCH` | `/api/v1/auth/me` · `/profiles/me` | Profile |
| `POST/GET` | `/api/v1/families` · `/elders` | Family bootstrap |
| `POST/GET` | `/api/v1/conversations` · `/messages` | Elder chat |
| `GET/POST` | `/api/v1/elders/{id}/reminders` | Routines / calendar / family |

Flow: **Register/Login → bootstrap family+elder+conversation → chat & reminders via JWT.**

Demo routes (`/chat`, `/routines/...`) remain on the backend but the UI no longer calls them.

### Session model

- Chat uses a UUID in `sessionStorage` (`sahaay_session_id`).
- Elder profiles in localStorage link a display name to that `session_id` so the family dashboard can fetch the same routines.

## Client-side store (`src/lib/store.ts`)

| Data | Storage key | Purpose |
|------|-------------|---------|
| Users / login | `sahaay_users`, `sahaay_current_user` | Demo auth |
| Family + elders | `sahaay_family` | Family dashboard |
| Activities | `sahaay_activities` | Timeline + PRD summary |
| Wellness | `sahaay_wellness` | Health score + “how are they feeling?” |
| Notifications | `sahaay_notifications` | SOS + family alerts |

## Tech stack

Next.js 16 · React 19 · TypeScript · CSS Modules · Geist fonts

See [`AGENTS.md`](./AGENTS.md) before writing Next.js code.

## Commands

```bash
npm install
npm run dev
npm run build
npm run lint
```

## Related files

| File | Role |
|------|------|
| [`Sahaay_PRD_v1.md`](./Sahaay_PRD_v1.md) | Product north star |
| [`../backend/README.md`](../backend/README.md) | Backend API (do not change from frontend work) |
