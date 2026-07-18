# Sahaay-AI

Ambient AI care companion that learns routines through conversation, grounds answers with Exa, speaks via ElevenLabs, and reminds gently — alerting caregivers only when needed.

## Repo layout

| Path | Purpose |
|------|---------|
| [`backend/`](backend/) | **Hackathon MVP API** (FastAPI) — chat, routines, Exa, voice, reminders |
| `Sahaay_*.md` / `START_HERE.md` | Product research & PRD docs |

## Backend (start here for the demo)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env          # add ANTHROPIC_API_KEY, EXA_API_KEY, ELEVENLABS_API_KEY
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs  
Contract for frontend: [`backend/README.md`](backend/README.md)

## Hackathon MVP scope

- Conversational onboarding + routine extraction (Claude)
- Grounded Q&A with citations (Exa)
- Voice replies (ElevenLabs)
- Reminder demo endpoint
- No auth, payments, caregiver dashboard, or WhatsApp in this build
