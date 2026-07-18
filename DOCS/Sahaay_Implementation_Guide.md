# Sahaay: Implementation Guide
## From Idea to MVP in 2 Months

---

## Phase 1: MVP (Weeks 1–4)
### Goal: Proof that the core loop works

**Core loop:**
1. User talks to Sahaay on WhatsApp
2. Sahaay extracts routines from natural conversation
3. Sahaay stores routine model
4. Sahaay sends reminders at scheduled times
5. Logging for later analysis

---

## Architecture: MVP Version

```
┌─────────────────────────────────────────────────────┐
│                  WhatsApp User                       │
│                   (via Twilio)                       │
└────────────────────┬────────────────────────────────┘
                     │ Message
                     ▼
┌─────────────────────────────────────────────────────┐
│           FastAPI Server (Your Code)                 │
│  - Webhook receiver (/webhook/whatsapp)             │
│  - Message router                                    │
│  - Session manager                                   │
└────────────────────┬────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
   ┌──────────────┐    ┌──────────────────┐
   │ Claude API   │    │  PostgreSQL DB   │
   │ (Understand  │    │  - Routines      │
   │  + Extract)  │    │  - Sessions      │
   └──────────────┘    │  - Logs          │
                       └──────────────────┘
          │                     │
          └──────────┬──────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │  Celery + Redis      │
          │  - Schedule reminders │
          │  - Drift detection    │
          └──────────┬───────────┘
                     │
                     ▼
            ┌──────────────────┐
            │  Twilio (Send)   │
            │  WhatsApp msgs   │
            └──────────────────┘
```

---

## Step 1: Setup (Day 1)

### 1.1 Create Twilio Account & WhatsApp Integration
```bash
# Visit twilio.com → Sign up for free trial
# Enable WhatsApp Sandbox (free testing account)
# Get credentials:
# - TWILIO_ACCOUNT_SID
# - TWILIO_AUTH_TOKEN
# - TWILIO_WHATSAPP_NUMBER (provided by Twilio, e.g., +1 415 523 8886)

# To test: Send "join <code>" to Twilio's sandbox number
# You'll get messages from the sandbox number
```

### 1.2 Setup Anthropic API
```bash
pip install anthropic

# Get your API key from console.anthropic.com
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 1.3 Database Setup
```bash
# Use PostgreSQL (free tier on AWS RDS or local)
# Create schema:

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  phone_number VARCHAR UNIQUE,
  name VARCHAR,
  language VARCHAR DEFAULT 'en',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE routines (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id),
  name VARCHAR,
  type VARCHAR, -- 'medication', 'bill', 'appointment', 'task'
  timing VARCHAR, -- '08:00' or '5th of month'
  frequency VARCHAR, -- 'daily', 'weekly', 'monthly'
  last_confirmed TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE logs (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id),
  routine_id INT REFERENCES routines(id),
  action VARCHAR, -- 'reminder_sent', 'confirmed', 'skipped', 'alert'
  timestamp TIMESTAMP DEFAULT NOW()
);
```

---

## Step 2: Core Backend (Days 2–4)

### 2.1 FastAPI Server + Twilio Webhook

**File: `app.py`**
```python
from fastapi import FastAPI, Request
from twilio.rest import Client
from pydantic import BaseModel
import psycopg2
import anthropic
import os
import json
from datetime import datetime

app = FastAPI()

# Initialize clients
twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)
anthropic_client = anthropic.Anthropic()

# Database connection
db_conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "localhost"),
    database="sahaay",
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
db_cursor = db_conn.cursor()

TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "+1 415 523 8886")

# ===== WEBHOOK RECEIVER =====
@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    """Receive incoming WhatsApp messages from Twilio"""
    
    form_data = await request.form()
    incoming_msg = form_data.get("Body", "").strip()
    from_number = form_data.get("From", "").replace("whatsapp:", "")
    
    print(f"[{datetime.now()}] Message from {from_number}: {incoming_msg}")
    
    # Get or create user
    user_id = get_or_create_user(from_number)
    
    # Get user's session state (are they in onboarding? confirmation? etc.)
    session_state = get_session_state(user_id)
    
    # Route the message
    if session_state == "onboarding":
        response = handle_onboarding(user_id, incoming_msg)
    elif session_state == "routine_confirmation":
        response = handle_confirmation(user_id, incoming_msg)
    else:
        response = handle_general(user_id, incoming_msg)
    
    # Send response back
    send_whatsapp_message(from_number, response)
    
    # Log the interaction
    log_interaction(user_id, "message_received", incoming_msg)
    
    return {"status": "ok"}

# ===== MESSAGE SENDING =====
def send_whatsapp_message(to_number, message_text):
    """Send WhatsApp message via Twilio"""
    message = twilio_client.messages.create(
        from_=f"whatsapp:{TWILIO_WHATSAPP_FROM}",
        body=message_text,
        to=f"whatsapp:{to_number}"
    )
    print(f"Sent message {message.sid}")
    return message.sid

# ===== CLAUDE INTEGRATION =====
def extract_routine_from_conversation(user_id, conversation_history: list):
    """
    Use Claude to extract structured routines from natural conversation.
    
    conversation_history = [
        {"role": "user", "content": "I take BP medicine at 8 AM every morning"},
        {"role": "assistant", "content": "Got it! ..."},
        {"role": "user", "content": "And my electricity bill is due on the 5th"},
        ...
    ]
    """
    
    system_prompt = """You are an AI assistant helping elderly users organize their daily routines.
Your task is to extract structured routine information from natural conversation.

Return ONLY a JSON object with this structure:
{
  "routines": [
    {
      "name": "BP Medicine",
      "type": "medication",
      "timing": "08:00",
      "frequency": "daily",
      "details": "1 tablet after breakfast"
    }
  ],
  "clarifications_needed": ["field1", "field2"] // if info is incomplete
}

Be conversational; extract only what the user has explicitly mentioned.
If something is unclear, return clarifications_needed."""
    
    response = anthropic_client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1000,
        system=system_prompt,
        messages=conversation_history
    )
    
    # Parse JSON from response
    response_text = response.content[0].text
    try:
        # Find JSON in response (Claude might add explanation text)
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            routine_data = json.loads(json_match.group())
            return routine_data
    except json.JSONDecodeError:
        print(f"Failed to parse routine JSON: {response_text}")
        return None
    
    return None

# ===== ONBOARDING FLOW =====
def handle_onboarding(user_id, user_message):
    """
    Guide user through routine setup via conversation.
    
    Sahaay: "Hi! What medicines do you take?"
    User: "BP medicine at 8 AM"
    Sahaay: "Great! Do you take it with food? Any other meds?"
    ...
    """
    
    # Get conversation history from session
    session_data = get_session(user_id)
    if not session_data:
        session_data = {"conversation": [], "routines_found": []}
    
    conversation = session_data.get("conversation", [])
    
    # Add user's latest message
    conversation.append({"role": "user", "content": user_message})
    
    # Use Claude to generate next response
    system_prompt = """You are Sahaay, an AI companion helping users organize daily routines.
You speak naturally and guide them through 5-10 minute onboarding.

Current goals:
1. Find all medications (names, times, frequency)
2. Find all recurring bills/payments
3. Find any important appointments
4. Find family members to notify (optional)

Be warm, encouraging, multilingual (switch to user's language if they start in another).
Ask one question at a time. After you've covered the basics, say:
"Thank you! I've understood your routine. Let me set this up for you."
"""
    
    response = anthropic_client.messages.create(
        model="claude-opus-4-6",
        max_tokens=500,
        system=system_prompt,
        messages=conversation
    )
    
    assistant_response = response.content[0].text
    
    # Add assistant response to conversation history
    conversation.append({"role": "assistant", "content": assistant_response})
    
    # Periodically extract routine data
    if len(conversation) > 4 and len(conversation) % 4 == 0:
        routine_data = extract_routine_from_conversation(user_id, conversation)
        if routine_data and routine_data.get("routines"):
            session_data["routines_found"] = routine_data["routines"]
            
            # If we have enough info, complete onboarding
            if len(routine_data["routines"]) >= 1 and not routine_data.get("clarifications_needed"):
                save_routines(user_id, routine_data["routines"])
                set_session_state(user_id, "ready")
                return f"""Perfect! I've saved your routine:
{json.dumps(routine_data['routines'], indent=2)}

From now on, I'll remind you about each task at the right time. Let's go!"""
    
    # Save updated session
    save_session(user_id, session_data)
    
    return assistant_response

def handle_confirmation(user_id, user_message):
    """Handle user confirming they completed a task"""
    
    # Parse intent (did user confirm or skip?)
    if any(word in user_message.lower() for word in ["yes", "✓", "done", "took", "paid", "completed"]):
        confirmed = True
    else:
        confirmed = False
    
    # Find most recent active routine
    # (In real system, track which routine we just reminded about)
    
    response = "✓ Great! I've recorded that. See you tomorrow!" if confirmed else "No worries! We'll try again tomorrow."
    
    return response

# ===== DATABASE HELPERS =====
def get_or_create_user(phone_number):
    """Get user ID or create new user"""
    db_cursor.execute("SELECT id FROM users WHERE phone_number = %s", (phone_number,))
    user = db_cursor.fetchone()
    if user:
        return user[0]
    
    db_cursor.execute("INSERT INTO users (phone_number) VALUES (%s) RETURNING id", (phone_number,))
    db_conn.commit()
    return db_cursor.fetchone()[0]

def get_session_state(user_id):
    """Get user's current conversation state"""
    db_cursor.execute("SELECT state FROM sessions WHERE user_id = %s ORDER BY updated_at DESC LIMIT 1", (user_id,))
    result = db_cursor.fetchone()
    return result[0] if result else "onboarding"

def get_session(user_id):
    """Get full session data"""
    db_cursor.execute("SELECT data FROM sessions WHERE user_id = %s ORDER BY updated_at DESC LIMIT 1", (user_id,))
    result = db_cursor.fetchone()
    return json.loads(result[0]) if result else None

def save_session(user_id, data):
    """Save session data"""
    db_cursor.execute(
        "INSERT INTO sessions (user_id, state, data) VALUES (%s, %s, %s) ON CONFLICT (user_id) DO UPDATE SET data = %s",
        (user_id, "onboarding", json.dumps(data), json.dumps(data))
    )
    db_conn.commit()

def save_routines(user_id, routines_list):
    """Save extracted routines to DB"""
    for routine in routines_list:
        db_cursor.execute(
            """INSERT INTO routines (user_id, name, type, timing, frequency)
               VALUES (%s, %s, %s, %s, %s)""",
            (user_id, routine["name"], routine["type"], routine["timing"], routine["frequency"])
        )
    db_conn.commit()

def log_interaction(user_id, action, details=""):
    """Log all interactions for analytics"""
    db_cursor.execute(
        "INSERT INTO logs (user_id, action, details) VALUES (%s, %s, %s)",
        (user_id, action, details)
    )
    db_conn.commit()

# ===== STARTUP =====
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

### 2.2 Scheduled Reminders (Celery + Redis)

**File: `tasks.py`**
```python
from celery import Celery
from celery.schedules import crontab
import psycopg2
from datetime import datetime, time
from twilio.rest import Client
import os

celery_app = Celery('sahaay')
celery_app.conf.broker_url = os.getenv("REDIS_URL", "redis://localhost:6379")
celery_app.conf.result_backend = os.getenv("REDIS_URL", "redis://localhost:6379")

twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

db_conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database="sahaay",
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

# ===== SCHEDULED TASKS =====

@celery_app.task
def send_daily_reminders():
    """Send daily reminders for all users at their set times"""
    
    cursor = db_conn.cursor()
    
    # Get all routines for today
    cursor.execute("""
        SELECT u.phone_number, r.name, r.timing, r.type, u.id, r.id
        FROM routines r
        JOIN users u ON r.user_id = u.id
        WHERE r.frequency IN ('daily', 'weekday', 'weekend')
        AND r.enabled = true
    """)
    
    routines = cursor.fetchall()
    
    now = datetime.now()
    current_hour_minute = f"{now.hour:02d}:{now.minute:02d}"
    
    for phone_number, routine_name, timing, routine_type, user_id, routine_id in routines:
        # Check if it's time to remind
        if timing == current_hour_minute[:5]:  # Match hour:minute
            message = f"⏰ Time for: {routine_name}"
            send_whatsapp_reminder(f"whatsapp:+91{phone_number}", message, user_id, routine_id)

@celery_app.task
def check_drift_detection():
    """Run drift detection every hour"""
    
    cursor = db_conn.cursor()
    
    # For each user, check if routine was confirmed at expected time
    cursor.execute("""
        SELECT r.id, u.phone_number, r.name, r.timing, r.last_confirmed, u.id
        FROM routines r
        JOIN users u ON r.user_id = u.id
        WHERE r.enabled = true
    """)
    
    routines = cursor.fetchall()
    
    for routine_id, phone_number, name, timing, last_confirmed, user_id in routines:
        drift_score = calculate_drift(routine_id, name, timing, last_confirmed)
        
        if drift_score > 5:  # Medium/high drift
            message = f"Hey, you usually confirm '{name}' at {timing}. Everything okay?"
            send_whatsapp_reminder(f"whatsapp:+91{phone_number}", message, user_id, routine_id)

def calculate_drift(routine_id, name, expected_time, last_confirmed):
    """
    Calculate how far the user's behavior has drifted from baseline.
    Returns score 0-10 (0=on-time, 10=very late/missed)
    """
    
    cursor = db_conn.cursor()
    
    # Get last 14 confirmations
    cursor.execute("""
        SELECT timestamp FROM logs
        WHERE routine_id = %s AND action = 'confirmed'
        ORDER BY timestamp DESC
        LIMIT 14
    """, (routine_id,))
    
    confirmations = [row[0] for row in cursor.fetchall()]
    
    if not confirmations:
        return 0  # No data yet
    
    # Calculate average delay
    now = datetime.now()
    hour, minute = map(int, expected_time.split(':'))
    expected_time_today = now.replace(hour=hour, minute=minute, second=0)
    
    if now < expected_time_today:
        expected_time_today = expected_time_today.replace(day=expected_time_today.day - 1)
    
    time_since_expected = (now - expected_time_today).total_seconds() / 3600  # hours
    
    # Scoring: +1 point per hour late (capped at 10)
    drift = min(int(time_since_expected), 10)
    
    return drift

def send_whatsapp_reminder(to_number, message, user_id, routine_id):
    """Send reminder and log it"""
    try:
        twilio_client.messages.create(
            from_=f"whatsapp:{os.getenv('TWILIO_WHATSAPP_FROM')}",
            body=message,
            to=to_number
        )
        
        cursor = db_conn.cursor()
        cursor.execute(
            "INSERT INTO logs (user_id, routine_id, action) VALUES (%s, %s, %s)",
            (user_id, routine_id, 'reminder_sent')
        )
        db_conn.commit()
    except Exception as e:
        print(f"Failed to send reminder: {e}")

# ===== CELERY BEAT SCHEDULE =====
celery_app.conf.beat_schedule = {
    'send-reminders-every-minute': {
        'task': 'tasks.send_daily_reminders',
        'schedule': crontab(minute='*'),  # Every minute
    },
    'check-drift-every-hour': {
        'task': 'tasks.check_drift_detection',
        'schedule': crontab(minute=0),  # Every hour
    },
}
```

---

## Step 3: Frontend (Days 5–7)

### 3.1 Simple Web Dashboard

For MVP, build a minimal dashboard for caregivers:

**File: `dashboard.html`**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Sahaay Dashboard</title>
    <style>
        body { font-family: Arial; max-width: 1000px; margin: 0 auto; padding: 20px; }
        .routine { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 8px; }
        .status-ok { border-left: 4px solid #4CAF50; }
        .status-drifting { border-left: 4px solid #FFC107; }
        .status-alert { border-left: 4px solid #F44336; }
        .routine h3 { margin: 0 0 10px 0; }
        .routine-time { color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>Sahaay - Caregiver Dashboard</h1>
    
    <div id="routines-container"></div>
    
    <script>
        async function loadRoutines() {
            const response = await fetch('/api/caregiver/routines');
            const routines = await response.json();
            
            const container = document.getElementById('routines-container');
            container.innerHTML = '';
            
            routines.forEach(routine => {
                const status = routine.drift_score > 5 ? 'drifting' : 'ok';
                const statusText = routine.drift_score > 7 ? '⚠️ Needs Attention' : 
                                   routine.drift_score > 5 ? '⏳ Drifting' : '✓ On Track';
                
                const el = document.createElement('div');
                el.className = `routine status-${status}`;
                el.innerHTML = `
                    <h3>${routine.name}</h3>
                    <p class="routine-time">Expected: ${routine.timing}</p>
                    <p>Last confirmed: ${routine.last_confirmed || 'Never'}</p>
                    <p>Status: ${statusText}</p>
                    <p>Adherence: ${routine.adherence_percent}%</p>
                `;
                container.appendChild(el);
            });
        }
        
        // Load every 30 seconds
        loadRoutines();
        setInterval(loadRoutines, 30000);
    </script>
</body>
</html>
```

---

## Step 4: Testing & Launch (Weeks 4+)

### 4.1 Test with Real Users

**Recruitment:**
- Partner with 1 local geriatric care center
- Recruit 20–30 elderly users + 10 caregivers
- Run for 2 weeks; collect feedback daily

**What to measure:**
- Onboarding time (target: <10 min)
- Adoption (% who use at least 3x/week)
- Accuracy of routine extraction
- False positive rate on drift detection
- NPS (Net Promoter Score)

### 4.2 Deploy to Production

**Minimal infra:**
- FastAPI on AWS EC2 (t3.micro, ~$8/month)
- PostgreSQL on AWS RDS free tier
- Redis on AWS ElastiCache or local
- Celery workers on same EC2

**Twilio costs:** ~$0.01–0.05 per message (include in budget)

---

## Step 5: Scale to V1 (Weeks 5–8)

### 5.1 Add Drift Detection Accuracy

Based on user feedback, refine the drift detection algorithm:

```python
def improved_drift_detection(routine_id, expected_time, user_id):
    """
    V1: Smarter drift detection
    - Learn user's personal variance (some always 15 min late)
    - Account for context (weekday vs weekend, season)
    - Reduce false positives with "are you ok?" before alert
    """
    
    cursor = db_conn.cursor()
    
    # Get baseline for this specific user+routine
    cursor.execute("""
        SELECT 
            AVG(EXTRACT(EPOCH FROM (timestamp - expected_time))/3600) as avg_delay,
            STDDEV(EXTRACT(EPOCH FROM (timestamp - expected_time))/3600) as delay_std
        FROM logs
        WHERE routine_id = %s AND action = 'confirmed'
        AND timestamp > NOW() - INTERVAL '30 days'
    """, (routine_id,))
    
    result = cursor.fetchone()
    if not result or result[0] is None:
        return None  # Not enough data
    
    avg_delay, delay_std = result
    
    # Current delay
    now_hour = datetime.now().hour + datetime.now().minute / 60
    expected_hour = int(expected_time.split(':')[0]) + int(expected_time.split(':')[1]) / 60
    current_delay = now_hour - expected_hour
    
    # Z-score: how many standard deviations from their baseline?
    if delay_std > 0:
        z_score = abs((current_delay - avg_delay) / delay_std)
    else:
        z_score = 0
    
    # Alert if >2 standard deviations (99% of their behavior)
    return {"should_alert": z_score > 2, "z_score": z_score, "current_delay_hours": current_delay}
```

### 5.2 Add Multi-Language Support

```python
def detect_user_language(user_id):
    """Detect or get user's preferred language"""
    # Check if user preference stored
    cursor.execute("SELECT preferred_language FROM users WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    
    # Default to English
    return 'en'

def get_localized_message(key, language='en', **kwargs):
    """Get translated message"""
    
    messages = {
        'en': {
            'greeting': "Hi! I'm Sahaay, your daily routine assistant.",
            'medication_reminder': "⏰ Time for {routine_name}",
        },
        'hi': {
            'greeting': "नमस्ते! मैं साहाय हूँ, आपका दैनिक सहायक।",
            'medication_reminder': "⏰ समय है {routine_name} का",
        },
        'gu': {
            'greeting': "નમસ્તે! હું સહાય છું, તમારો દૈનિક સહાયક।",
            'medication_reminder': "⏰ {routine_name} નો સમય છે",
        }
    }
    
    if language not in messages:
        language = 'en'
    
    template = messages[language].get(key, key)
    return template.format(**kwargs)
```

---

## Deployment Checklist

### Before Going Live:
- [ ] All environment variables set (.env file)
- [ ] Database backups configured
- [ ] Twilio webhook HTTPS (use ngrok for testing, proper domain for prod)
- [ ] Rate limiting on API endpoints
- [ ] Logging & monitoring setup
- [ ] Privacy policy written & accessible
- [ ] Basic load testing (expect 10–100 users first week)
- [ ] User manual/FAQ written

### Monitoring:
```python
# Add to FastAPI
from prometheus_client import Counter, Histogram
import time

message_count = Counter('messages_received', 'Total messages received')
routine_created = Counter('routines_created', 'Total routines created')
response_time = Histogram('response_time_seconds', 'API response time')

@app.middleware("http")
async def add_metrics(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    response_time.observe(duration)
    return response
```

---

## Cost Estimate (First 1,000 Users)

| Service | Cost/Month |
|---------|-----------|
| AWS EC2 (server) | $10 |
| RDS PostgreSQL | $15 |
| Redis (ElastiCache) | $0 (use free tier or local) |
| Twilio (1,000 users × 10 msgs/month × $0.01) | $100 |
| Monitoring/logging | $20 |
| **Total** | **~$145/month** |

---

## Next Steps

1. **This week:** Set up Twilio + FastAPI + basic conversation flow
2. **Week 2:** Integrate Claude API for routine extraction
3. **Week 3:** Add scheduled reminders (Celery + Redis)
4. **Week 4:** Test with 10 real users; iterate
5. **Weeks 5–8:** Add drift detection, caregiver dashboard, multilingual support

Good luck! 🚀
