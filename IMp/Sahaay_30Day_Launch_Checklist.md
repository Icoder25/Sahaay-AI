# Sahaay: 30-Day Launch Checklist
## From Today to First Users

---

## Week 1: Setup & Planning

### Day 1–2: Core Infrastructure
- [ ] Create Anthropic API account (console.anthropic.com)
  - Save API key: `sk-ant-...`
  - Test with simple request
  
- [ ] Create Twilio account (twilio.com)
  - Sign up for free trial (₹300+ free credits)
  - Enable WhatsApp Sandbox
  - Save: Account SID, Auth Token, WhatsApp number
  - Test: Send yourself a message from sandbox
  
- [ ] Set up PostgreSQL database
  - [ ] Option A (local): `brew install postgresql` or Docker
  - [ ] Option B (cloud): AWS RDS free tier, or use supabase.com (easier)
  - Save connection string
  
- [ ] Set up Redis (for task scheduling)
  - [ ] Option A (local): `brew install redis`
  - [ ] Option B (cloud): Redis Cloud (free tier)
  - Save connection string

### Day 3–4: Code Setup
- [ ] Create GitHub repo
  - [ ] Add `.env` template
  - [ ] Add `.gitignore`
  - [ ] Initial commit
  
- [ ] Create Python project structure
  ```
  sahaay/
  ├── app.py              # FastAPI server + webhooks
  ├── tasks.py            # Celery reminders + drift detection
  ├── requirements.txt
  ├── .env.example
  └── README.md
  ```
  
- [ ] Install dependencies
  ```bash
  pip install fastapi uvicorn twilio anthropic psycopg2 celery redis pydantic python-dotenv
  ```

### Day 5: Problem Validation Interviews (Start Early!)
- [ ] Recruit 5 people to interview (1–2 hours each)
  - Elderly person + caregiver OR
  - ADHD adult OR
  - Busy parent
  
- [ ] Conduct interviews (see GTM plan for script)
  - Take notes, record if possible
  - Key question: "How often do you/your relative forget important tasks?"
  
- [ ] Summarize learnings
  - [ ] Top 3 pain points confirmed?
  - [ ] Would they use a conversational AI? (Yes/Excited/Maybe/No)
  - [ ] Who would they tell?

---

## Week 2: MVP Build (Core Loop)

### Day 8–10: WhatsApp + Claude Integration
- [ ] Build FastAPI server with Twilio webhook

```python
# app.py (simplified)
from fastapi import FastAPI, Request
from twilio.rest import Client
import anthropic

app = FastAPI()

twilio = Client(ACCOUNT_SID, AUTH_TOKEN)
claude = anthropic.Anthropic()

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    # Get incoming message
    form_data = await request.form()
    incoming = form_data.get("Body")
    from_number = form_data.get("From")
    
    # Send to Claude for response
    response = claude.messages.create(
        model="claude-opus-4-6",
        max_tokens=500,
        system="You are Sahaay, a helpful daily routine assistant.",
        messages=[{"role": "user", "content": incoming}]
    )
    
    reply = response.content[0].text
    
    # Send back via Twilio
    twilio.messages.create(
        from_=f"whatsapp:{TWILIO_NUM}",
        body=reply,
        to=from_number
    )
    
    return {"ok": True}

# Run with: uvicorn app:app --reload
```

- [ ] Test locally with ngrok
  ```bash
  ngrok http 8000
  # Copy forwarding URL to Twilio webhook settings
  ```
  
- [ ] Send test message from Twilio sandbox
  - [ ] Confirm message arrives in your script
  - [ ] Confirm response comes back

### Day 11–13: Routine Extraction

- [ ] Build Claude function to extract routines from conversation

```python
def extract_routine(conversation_history):
    """Extract structured routines from conversation"""
    
    response = claude.messages.create(
        model="claude-opus-4-6",
        max_tokens=1000,
        system="""Extract routine info from conversation.
        Return ONLY JSON:
        {"routines": [{"name": "BP medicine", "time": "08:00", "frequency": "daily"}]}""",
        messages=conversation_history
    )
    
    # Parse JSON from response
    text = response.content[0].text
    # Extract JSON...
    return routines_list
```

- [ ] Save routines to PostgreSQL
  ```python
  def save_routine(user_id, name, time, frequency):
      cursor.execute(
          "INSERT INTO routines (user_id, name, timing, frequency) VALUES (%s, %s, %s, %s)",
          (user_id, name, time, frequency)
      )
      db_conn.commit()
  ```

- [ ] Test: Have a conversation with your bot
  - Conversation: "I take BP medicine at 8 AM every day"
  - Confirm: Routine saved to DB
  - Query DB to verify

### Day 14: Database Setup
- [ ] Create tables
  ```sql
  CREATE TABLE users (id SERIAL PRIMARY KEY, phone_number VARCHAR UNIQUE);
  CREATE TABLE routines (id SERIAL PRIMARY KEY, user_id INT, name VARCHAR, timing VARCHAR, frequency VARCHAR);
  CREATE TABLE logs (id SERIAL PRIMARY KEY, user_id INT, action VARCHAR, timestamp TIMESTAMP DEFAULT NOW());
  ```

- [ ] Test: Insert sample user, routine
- [ ] Verify tables are queryable

---

## Week 3: Reminders & Testing

### Day 15–17: Scheduled Reminders
- [ ] Set up Celery + Redis

```python
# tasks.py
from celery import Celery
from celery.schedules import crontab

celery_app = Celery('sahaay')
celery_app.conf.broker_url = "redis://localhost:6379"

@celery_app.task
def send_daily_reminders():
    # Get all routines
    # For each, check if it's time to remind
    # Send Twilio message
    pass

# In __main__:
celery_app.conf.beat_schedule = {
    'send-reminders': {
        'task': 'tasks.send_daily_reminders',
        'schedule': crontab(minute='*'),  # Every minute
    }
}
```

- [ ] Run Celery worker: `celery -A tasks worker --loglevel=info`
- [ ] Run Celery beat: `celery -A tasks beat --loglevel=info`
- [ ] Test: Add a routine with timing "now+1min", confirm reminder arrives

### Day 18–19: Caregiver Setup (Basic)
- [ ] Add caregiver phone to routine
  ```python
  # In extraction, ask: "Should we notify your daughter? [Yes/No]"
  # If yes, save her phone number to routine record
  ```

- [ ] Send caregiver alert when user confirms
  ```python
  cursor.execute("SELECT caregiver_phone FROM routines WHERE id = %s", (routine_id,))
  caregiver = cursor.fetchone()
  if caregiver:
      twilio.messages.create(
          from_=f"whatsapp:{TWILIO_NUM}",
          body=f"✓ Your mom confirmed her BP medicine",
          to=f"whatsapp:{caregiver[0]}"
      )
  ```

### Day 20: End-to-End Test
- [ ] Scenario: "Elderly user Rajesh"
  - [ ] Rajesh sends: "Hi, can you help me?"
  - [ ] Sahaay responds with onboarding
  - [ ] Rajesh gives routine info
  - [ ] Routine saved to DB
  - [ ] Tomorrow at 8 AM: Reminder sent
  - [ ] Rajesh confirms: "Done ✓"
  - [ ] Caregiver (daughter) gets alert
  
- [ ] If this works end-to-end, you're ready for beta

---

## Week 4: Beta Launch & Iteration

### Day 21–22: Recruit 5 Beta Testers
- [ ] Contact elderly person + caregiver you interviewed
- [ ] Explain: "We're testing a new AI assistant. It's free. Can you try it for 2 weeks?"
- [ ] Offer incentive: Free 3-month access / ₹500 recharge
- [ ] Send them Twilio sandbox number
- [ ] Schedule 5-min check-in call each day

### Day 23–26: Daily Iteration
- [ ] Each morning, review logs
  - [ ] Any errors? Fix immediately
  - [ ] Users confused about anything? Adjust onboarding
  - [ ] Missing features? Note for later
  
- [ ] Each evening, brief call with testers
  - "How was it today? Anything confusing?"
  - Take detailed notes
  
- [ ] Fixes to prioritize:
  1. Critical bugs (message not sent, crash)
  2. Comprehension (user confused by phrasing)
  3. Small improvements (speed, clarity)

### Day 27–28: Fix & Polish
- [ ] Fix top 3 issues found during testing
- [ ] Test fixes with testers
- [ ] Clean up code, add basic error handling
- [ ] Write simple README

### Day 29–30: Reflection & Planning
- [ ] Summarize learnings
  - [ ] What worked?
  - [ ] What didn't?
  - [ ] Would testers recommend to a friend? (NPS)
  
- [ ] Decide next step:
  - Option A: Expand beta to 20 users
  - Option B: Build missing feature first
  - Option C: Redesign based on feedback
  
- [ ] Create 30-day plan for month 2

---

## Quick Build Checklist (Simplified)

### Must-Have This Week:
- [ ] FastAPI + Twilio integration working
- [ ] Claude conversation loop
- [ ] Routine extraction from conversation
- [ ] Routine saved to PostgreSQL
- [ ] Database queries working

### Nice-to-Have (if time):
- [ ] Celery reminders scheduling
- [ ] Caregiver alerts
- [ ] Simple logging/analytics

### Don't Build Yet:
- ❌ Fancy UI/Dashboard (text only is fine)
- ❌ Mobile app (WhatsApp is your app)
- ❌ Drift detection (too early)
- ❌ Multi-language (English only for now)
- ❌ Admin panel (manual DB queries are fine)

---

## Debugging Guide

### Problem: Message not arriving in my Flask/FastAPI app
**Solution:**
1. Check Twilio webhook URL is correct (copy from webhook settings)
2. URL must be HTTPS (use ngrok in local dev)
3. Check webhook logs in Twilio console
4. Add `print()` or logging to see if request arrives

### Problem: Claude API not responding
**Solution:**
1. Check API key is set: `echo $ANTHROPIC_API_KEY`
2. Check your API key is valid (test in curl/Postman)
3. Check rate limits (free tier has 50 req/min)
4. Add try-catch:
```python
try:
    response = claude.messages.create(...)
except anthropic.APIError as e:
    print(f"API Error: {e}")
    return "Sorry, I'm having trouble understanding. Can you repeat?"
```

### Problem: Database not saving
**Solution:**
1. Check connection string is correct
2. Check table exists: `\dt` in psql
3. Check INSERT statement syntax
4. Add debug print: `print(f"Saving routine: {name} at {time}")`

### Problem: Celery tasks not running
**Solution:**
1. Check Redis is running: `redis-cli ping` (should say "PONG")
2. Check Celery worker is running: `celery -A tasks worker --loglevel=info`
3. Check task is scheduled in beat_schedule
4. Check logs for errors

---

## Cost Breakdown (First Month)

| Item | Cost |
|------|------|
| Twilio (whatsapp + SMS) | Free (trial credits) |
| Anthropic API | ~₹200 ($2.50 for 1000s of messages) |
| PostgreSQL | Free (local) or $15 (AWS RDS) |
| Redis | Free (local) or $0–15 (ElastiCache) |
| Hosting | Free (ngrok testing) or $10/mo (AWS EC2) |
| **Total** | **~₹50–500** |

In production (10–100 users):
- Twilio: ₹500–2000/month
- Claude API: ₹200–500/month
- Database: ₹500–1000/month
- Hosting: ₹500/month
- **Total: ~₹2000–4000/month**

---

## Success Criteria After 30 Days

- [ ] ✓ 5+ real beta testers active
- [ ] ✓ 80%+ onboarding completion rate
- [ ] ✓ At least 1 user confirmed strong value ("This really helps!")
- [ ] ✓ System ran for 30 days without major crashes
- [ ] ✓ You have NPS feedback from testers (target: >30)
- [ ] ✓ Clear next 30-day roadmap

**If you hit these, you're ready to expand beta to 20–50 users.**

---

## Month 2 Quick Plan (If MVP Succeeds)

Week 1–2:
- [ ] Add drift detection (basic version)
- [ ] Improve onboarding based on feedback
- [ ] Scale to 20 testers

Week 3–4:
- [ ] Add caregiver dashboard (simple)
- [ ] Multi-language support (Hindi + English)
- [ ] Measure: retention, NPS, feature usage

Month 3:
- [ ] Public beta (50–100 users)
- [ ] Measure: PMF signals (70%+ retention week 1, NPS >40)
- [ ] Plan Series A or scale

---

## Resources

### Tools
- **Claude API:** https://console.anthropic.com
- **Twilio:** https://twilio.com
- **Supabase (PostgreSQL SaaS):** https://supabase.com
- **Redis Cloud:** https://redis.com/cloud

### Code Examples
- Claude API docs: https://docs.anthropic.com
- Twilio WhatsApp: https://twilio.com/docs/whatsapp
- FastAPI: https://fastapi.tiangolo.com

### Communities
- FastAPI: https://discord.gg/VQjSZaeJmf
- LLM builders: https://huggingface.co/spaces
- Indie hackers: https://indiehackers.com

---

## Mindset for the Next 30 Days

**Remember:**
1. **Ship over perfect.** A simple, working MVP beats a perfect app that doesn't exist.
2. **Users first.** Every feature decision should come from talking to users.
3. **Move fast.** If something is broken, fix it in hours, not days.
4. **Stay lean.** Don't hire, don't expand, don't build stuff nobody asked for.
5. **Measure everything.** What gets measured gets managed.

**Your north star for month 1:** Can real people use this to remember important things?

If yes → double down on that.
If no → figure out why and fix it.

That's it. You've got this. 🚀

---

## Sample Week 1 Message to Testers

```
Hi Rajesh!

I'm building Sahaay, an AI assistant that helps you remember medicines and 
important tasks. It talks to you on WhatsApp like a friend.

I'd love for you to try it for 2 weeks—it's free! All I ask is that you 
give me honest feedback.

Ready to start? Just reply "Hi" to begin. 👋

No pressure, no weird conditions. Just trying to help.

- [Your name]
```

**And if they say yes:**

```
Great! Let's start.

Tell me: What's the most important thing you often forget to do each day?

For example:
- "I take BP medicine at 8 AM"
- "I pay my electricity bill on the 5th"
- "I call my daughter on Sundays"

Just type it out however feels natural. 😊
```

Good luck! You're about to change someone's life. 💚

---

## Final Checklist Before You Start

- [ ] Have you talked to at least 3 real users about this problem?
- [ ] Do they actually want this solution?
- [ ] Do you have 5+ people willing to beta test?
- [ ] Have you set up API keys for Twilio, Claude, Database?
- [ ] Do you have 5–10 hours/week for next month?
- [ ] Are you ready to iterate based on feedback (not defend your ideas)?

If all are checkmarks → Start building TODAY. 

Don't wait for perfection. Users will teach you what's needed. 🎯
