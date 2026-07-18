# Sahaay Frontend — Project Context

Context for developers and AI agents working in `frontend/`. Read this before making changes.

## What this is

**Sahaay** is an ambient AI care companion: it learns routines through conversation, answers health questions with grounded citations (Exa), speaks replies (ElevenLabs), and sends gentle reminders. The long-term product targets elderly users and caregivers in India (WhatsApp-first); this **frontend is the hackathon demo UI** that talks to the FastAPI backend.

| In scope (MVP demo) | Out of scope (this build) |
|---------------------|---------------------------|
| Chat UI wired to `POST /chat` | Auth / user accounts |
| Session-scoped routine panel | Caregiver dashboard |
| Citation links on Q&A answers | Payments / subscriptions |
| Audio playback for voice replies | WhatsApp / Twilio integration |
| “Demo reminder” trigger | Production deployment hardening |

Product docs live in [`../DOCS/`](../DOCS/). Start with [`../DOCS/Sahaay_User_Journeys.md`](../DOCS/Sahaay_User_Journeys.md) for UX tone and flows.

## Current state

The app is a **fresh Next.js scaffold** (`create-next-app`). Only the default home page exists under `src/app/`. No API client, chat components, or backend integration yet.

**Backend contract:** [`../backend/README.md`](../backend/README.md) — treat it as the source of truth for endpoints and response shapes.

## Tech stack

| Layer | Choice |
|-------|--------|
| Framework | Next.js **16.2.10** (App Router) |
| UI | React **19.2.4** |
| Language | TypeScript 5 (strict) |
| Styling | CSS Modules + `globals.css` (no Tailwind yet) |
| Fonts | Geist Sans / Geist Mono via `next/font/google` |
| Compiler | React Compiler enabled (`reactCompiler: true` in `next.config.ts`) |
| Lint | ESLint 9 + `eslint-config-next` |

### Next.js version note

This repo uses **Next.js 16**, which may differ from older training data. Before writing Next.js code, check `node_modules/next/dist/docs/` and follow [`AGENTS.md`](./AGENTS.md). Heed deprecation notices.

## Repository layout

```
frontend/
├── context.md          ← this file
├── AGENTS.md           ← Next.js agent rules (referenced by CLAUDE.md)
├── CLAUDE.md           → @AGENTS.md
├── next.config.ts
├── package.json
├── tsconfig.json       ← path alias @/* → ./src/*
├── eslint.config.mjs
├── public/             ← static assets (SVGs, etc.)
└── src/
    └── app/
        ├── layout.tsx  ← root layout, metadata, fonts
        ├── page.tsx    ← home (placeholder — replace with demo UI)
        ├── page.module.css
        ├── globals.css
        └── favicon.ico
```

Prefer adding feature code under `src/` (e.g. `src/components/`, `src/lib/`, `src/hooks/`) rather than expanding `app/` with unrelated files.

## Backend integration

**Base URL (local):** `http://localhost:8000`  
**CORS:** all origins allowed — browser calls from `localhost:3000` work without a proxy.

Run backend first:

```bash
cd ../backend
# activate venv, then:
uvicorn app.main:app --reload --port 8000
```

### Session model

Generate one **UUID per demo user** on first load, persist in `sessionStorage` (or `localStorage`), and send it on every API call as `session_id`.

### Endpoints the UI should use

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/health` | Optional status / service flags |
| `POST` | `/chat` | Send user message; get reply, routines, citations, audio |
| `GET` | `/routines/{session_id}` | List routines for side panel |
| `GET` | `/reminders/demo?session_id=...&speak=true` | Trigger demo proactive reminder |
| `POST` | `/reminders` | Create a scheduled reminder (optional in demo) |
| `POST` | `/voice/speak` | Standalone TTS (usually via `/chat` with `speak: true`) |

### Key response fields (`POST /chat`)

```ts
{
  reply: string;
  session_id: string;
  routines_updated: Routine[];
  citations: { title: string; url: string; snippet: string }[];
  audio_url: string | null;  // relative, e.g. "/static/audio/abc.mp3"
  intent: "routine_update" | "question" | "chat";
}
```

Prepend base URL for audio: `http://localhost:8000${audio_url}`.

Set `"speak": false` on chat requests to skip TTS when testing text-only.

### Suggested demo UI flow

1. **On load** — create or restore `session_id`; optionally call `/health`.
2. **Chat** — message list + input; `POST /chat` on send; append user + assistant messages.
3. **Routines panel** — show `routines_updated` from chat responses and/or poll `GET /routines/{session_id}`.
4. **Citations** — under assistant messages when `intent === "question"` and `citations.length > 0`; render as external links.
5. **Voice** — if `audio_url`, play with `<audio autoPlay />` or a play control.
6. **Demo reminder** — button calling `GET /reminders/demo`; show returned message and play audio if present.

Example onboarding message for demos:

> Hi, I'm Rajesh. I take BP medicine at 8 AM every day.

## Conventions

- **Path alias:** import from `@/components/...`, `@/lib/...`, etc.
- **App Router:** use Server Components by default; add `"use client"` only for interactivity (chat input, audio, session storage).
- **Env vars:** use `NEXT_PUBLIC_API_BASE_URL` (default `http://localhost:8000`) for the backend base URL so builds can target other hosts.
- **Types:** mirror backend schemas in `src/lib/types.ts` or generate from OpenAPI later; keep request/response types in one place.
- **Styling:** match existing CSS Modules pattern (`*.module.css`) unless the team adopts a design system later.
- **Accessibility:** large tap targets and readable type — primary users include elderly people and stressed caregivers; prefer clarity over density.
- **Tone:** warm, respectful, non-clinical copy aligned with user journeys (e.g. “Namaste”, gentle reminders, no shame language).

## Commands

```bash
npm install
npm run dev      # http://localhost:3000
npm run build
npm run start
npm run lint
```

## Related files

| File | Role |
|------|------|
| [`../README.md`](../README.md) | Monorepo overview |
| [`../backend/README.md`](../backend/README.md) | API contract + curl demo script |
| [`../DOCS/Sahaay_Real_PRD.md`](../DOCS/Sahaay_Real_PRD.md) | Product requirements |
| [`../DOCS/Sahaay_User_Journeys.md`](../DOCS/Sahaay_User_Journeys.md) | UX journeys and voice |
| [`AGENTS.md`](./AGENTS.md) | Mandatory Next.js 16 guidance for agents |

## Implementation priorities

When building out the frontend, prefer this order:

1. API client + env config + shared types
2. Session bootstrap (UUID persistence)
3. Chat thread UI + loading/error states
4. Routines side panel
5. Citations + audio playback
6. Demo reminder button
7. Polish: empty states, mobile-friendly layout, basic health indicator

Keep changes minimal and focused until the core demo loop works end-to-end with the backend running locally.
