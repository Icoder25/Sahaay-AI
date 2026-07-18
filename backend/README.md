# Sahaay Backend — Hackathon MVP

FastAPI API for the Ambient AI Care Companion demo.

## Features

- Conversational chat (Claude) with session memory
- Structured routine extraction
- Exa-grounded answers with citations
- ElevenLabs voice (optional)
- Reminder create + demo endpoints

## Quick start

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # then fill in API keys
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open docs: http://localhost:8000/docs

## Environment

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Claude API key |
| `EXA_API_KEY` | For search | Exa search key |
| `ELEVENLABS_API_KEY` | For voice | ElevenLabs key |
| `ELEVENLABS_VOICE_ID` | No | Defaults to Rachel |
| `CLAUDE_MODEL` | No | Default `claude-sonnet-4-5` |
| `ENABLE_VOICE` | No | Default `true` |
| `DATABASE_URL` | No | Default SQLite `./sahaay.db` |

## Frontend contract

Base URL: `http://localhost:8000`  
CORS: `*` (all origins allowed)

Generate a `session_id` (UUID) once per demo user and reuse it.

---

### `GET /health`

```json
{
  "status": "ok",
  "services": { "anthropic": true, "exa": true, "elevenlabs": true }
}
```

---

### `POST /chat`

**Request**
```json
{
  "session_id": "11111111-1111-1111-1111-111111111111",
  "message": "Hi, I'm Rajesh. I take BP medicine at 8 AM every day.",
  "speak": true
}
```

**Response**
```json
{
  "reply": "Namaste Rajesh! I've noted your BP medicine at 8 AM daily...",
  "session_id": "11111111-1111-1111-1111-111111111111",
  "routines_updated": [
    {
      "id": 1,
      "name": "BP Medicine",
      "type": "medication",
      "timing": "08:00",
      "frequency": "daily",
      "notes": null,
      "priority": "critical"
    }
  ],
  "citations": [],
  "audio_url": "/static/audio/abc123.mp3",
  "intent": "routine_update"
}
```

`intent` is one of: `routine_update` | `question` | `chat`  
`audio_url` is relative — prepend base URL, e.g. `http://localhost:8000/static/audio/abc123.mp3`  
Set `"speak": false` to skip TTS.

**Grounded question example**
```json
{
  "session_id": "11111111-1111-1111-1111-111111111111",
  "message": "What should diabetics eat for breakfast?",
  "speak": true
}
```

Response includes `citations: [{ "title", "url", "snippet" }]` when Exa runs.

---

### `GET /routines/{session_id}`

Returns all stored routines for the session.

```bash
curl http://localhost:8000/routines/11111111-1111-1111-1111-111111111111
```

---

### `POST /reminders`

```json
{
  "session_id": "11111111-1111-1111-1111-111111111111",
  "routine_id": 1,
  "message": null,
  "scheduled_time": "08:00"
}
```

If `message` is null, a warm personalized reminder is generated from the routine.

---

### `GET /reminders/demo?session_id=...&speak=true`

Simulates a proactive companion reminder (prefers medication routines).

```bash
curl "http://localhost:8000/reminders/demo?session_id=11111111-1111-1111-1111-111111111111"
```

```json
{
  "message": "Good morning Rajesh. It's time for your BP Medicine (usually around 08:00).",
  "routine": { "id": 1, "name": "BP Medicine", "...": "..." },
  "audio_url": "/static/audio/....mp3",
  "reminder": { "id": 1, "is_demo": true, "...": "..." }
}
```

---

### `POST /voice/speak`

```json
{ "text": "Good morning. Time for your medicine.", "session_id": "optional" }
```

```json
{ "audio_url": "/static/audio/....mp3", "text": "Good morning. Time for your medicine." }
```

---

## Demo curl script (3-minute flow)

```bash
SID=11111111-1111-1111-1111-111111111111

# 1. Introduce + extract routine
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SID\",\"message\":\"Hi, I'm Rajesh. I take BP medicine at 8 AM and diabetes medicine at 8 AM and 6 PM.\",\"speak\":false}"

# 2. Grounded question
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SID\",\"message\":\"What should diabetics eat for breakfast?\",\"speak\":false}"

# 3. List routines
curl -s http://localhost:8000/routines/$SID

# 4. Reminder demo
curl -s "http://localhost:8000/reminders/demo?session_id=$SID&speak=false"
```

## Suggested frontend UI flow

1. On load: generate UUID → store as `session_id`
2. Chat UI → `POST /chat` on each send
3. Show `routines_updated` / poll `GET /routines/{id}` in a side panel
4. Show `citations` as source links under question answers
5. If `audio_url`, play `<audio src={BASE + audio_url} />`
6. "Demo reminder" button → `GET /reminders/demo`

## Project layout

```
backend/
  app/
    main.py
    config.py
    db.py
    models.py
    schemas.py
    routers/
    services/
  static/audio/
  requirements.txt
  .env.example
```
