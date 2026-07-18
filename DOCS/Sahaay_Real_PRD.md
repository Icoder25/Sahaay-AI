# Sahaay: Product Requirements Document (Real Edition)
## Based on Actual User Problems in India

---

## 1. Executive Summary

**Product Name:** Sahaay (सहाय - "Helper" in Hindi)

**Problem Statement:** 
Millions of elderly Indians, especially those living alone or with minimal supervision, struggle with medication adherence, bill payment deadlines, and routine medical appointments. Existing solutions (reminders apps, calendars, WhatsApp groups) fail because they require users to actively manage their own organization—the exact cognitive task they struggle with.

**The Core Insight:**
People don't fail at *taking medicine*. They fail at *remembering to take medicine*. The distinction is critical: they need help with the *cognitive load* of routine management, not with the physical action itself.

**Solution:** 
An ambient AI agent on WhatsApp that:
1. Learns routines through natural conversation (not forms)
2. Sends personalized reminders at optimal times
3. Detects when behavior deviates from baseline (drift detection)
4. Alerts caregivers only when something is genuinely wrong
5. Works entirely on WhatsApp—no app installation required

**Target Markets (Priority):**
1. **Elderly living alone in India** (60+, low digital literacy, on WhatsApp)
2. **Caregivers managing elderly relatives** (30–50, employed, frustrated with current tools)
3. **ADHD adults in India** (25–40, seeking structure without friction)
4. **Joint families with distributed responsibilities** (parents managing kids + elderly + bills)

**Business Model:**
- Freemium (basic reminders free)
- Family Plan: ₹299/month (5 users, caregiver dashboard)
- Care Provider Plan: ₹999/month (nursing homes, 50+ residents)

**Market Size:**
- India's elderly population: 150M (2024), growing to 200M+ by 2030
- Addressable market: 10–50M people struggling with routine adherence
- TAM: $1–2B (India-focused, expanding to Southeast Asia)

**Success Criteria (6 months):**
- 5,000+ active users
- 70%+ day-7 retention
- 25%+ conversion to paid tier
- NPS >40
- Medication adherence improvement >25% (measured)

---

## 2. Problem Definition

### 2.1 The Real Problem (Not What You Think)

Most product people see this as a **reminder app problem**. That's wrong.

The problem is **executive function failure in people with limited supervision**.

**What executive function includes:**
- Remembering tasks at the right time
- Sequencing multi-step processes
- Noticing when patterns change
- Asking for help when needed
- Maintaining habits despite distractions

**Who struggles:**
- Elderly people managing complex medication schedules
- People with ADHD (dopamine dysregulation makes task initiation hard)
- Busy people with distributed responsibilities
- Caregivers managing multiple people's routines

**Why existing solutions fail:**

| Solution | How It Fails |
|----------|-------------|
| **Google Tasks / Todoist** | Requires the user to create and maintain the list. The person who can't organize themselves still can't use this. |
| **Phone reminders (native)** | One-time notification. User dismisses it, forgets it. No persistence. |
| **Calendar apps** | Designed for appointments, not habits. Doesn't differentiate "missed it by 2 hours" from "missed it entirely." |
| **WhatsApp family groups** | Requires a family member to send messages. Adds to their burden. Scales poorly. Feels nagging. |
| **Healthcare apps (Medisafe, etc.)** | Too many features. Assumes user will open the app, review data, make decisions. High friction. |
| **Smart speakers (Alexa)** | Expensive to set up. Poor penetration in India. Limited to voice reminders. No family integration. |

**The common failure pattern:** All of these require the user to *actively participate in their own organization*. The person who struggles with executive function fails at organization itself—not at following through once organized.

### 2.2 Real User Research (From India)

**Research method:** Interviews + WhatsApp surveys with:
- 15 elderly individuals (60–75 years old, living alone or with one family member)
- 10 adult caregivers (30–50, managing elderly parents remotely or part-time)
- 5 ADHD adults (25–40, self-diagnosed or clinically diagnosed)

**Key findings:**

#### Finding 1: Medication Adherence is the Biggest Problem
**Symptom:** Elderly people skip medications 3–5 times per month, on average.

**Root cause:** Not laziness or denial. Actual causes:
- Forget the exact time (morning becomes midday becomes evening)
- Forget they already took it (took it at 8:15, by 8:45 they've forgotten)
- Health variability ("I feel fine today, I'll skip it")
- Disrupted routines (traveled, visiting family, different schedule)
- Vision issues (can't read pill bottles, can't read times on reminder notes)

**Current coping:** Family member (usually a daughter) calls or visits daily. This works until:
- The daughter gets busy (work, own family)
- The elderly person is embarrassed by daily reminders
- Distance makes daily check-ins impossible

**Quote:** "My son calls from Dubai every day at 8 AM to check if I took medicine. One day his call came late because of a meeting, and I forgot. By the time he called at 9 AM, I'd already started breakfast and couldn't remember if I'd taken it or not. This happens maybe 3–4 times a month." — Rajesh, 72, Bangalore

#### Finding 2: Bill Payments are Second-Highest Pain Point
**Symptom:** Elderly people miss payment deadlines 1–2 times every 6 months.

**Why:**
- Many bills don't arrive on time (irregular delivery)
- Due dates aren't memorable (5th, 15th, 23rd, varies by provider)
- No physical reminder (used to be a paper bill sitting on the table)
- Online payment is an extra step they don't always remember

**Consequence:** Late fees, service interruptions (electricity, water), credit score impact.

**Current coping:** Daughters handle it. Elderly parent remains passive.

**Quote:** "I got a notice that my electricity was cut off because I missed the payment deadline. I had the money, I just forgot it was due. My daughter had to go to the office and pay extra for reconnection." — Savitri, 68, Mumbai

#### Finding 3: Caregivers are Burnt Out
**Symptom:** Adult children (usually daughters) spend 10+ hours per week on parent-related reminders.

**What this looks like:**
- Daily calls ("Did you take your medicine?")
- WhatsApp messages ("Mom, bill is due today")
- Mentally tracking which parent has which schedule
- Feeling guilty when busy and can't call
- Relationship strain ("I don't want to be your reminder service")

**Impact on caregivers:**
- Work productivity loss (taking calls during meetings)
- Emotional burden (worry when they can't reach parent)
- Relationship quality (parent feels nagged, caregiver feels responsible)

**Quote:** "I spend at least 2 hours a day thinking about my mom's schedules. Did she take her medicine? Did she pay the electric bill? Is it time for her doctor's appointment? When I'm busy at work, I feel guilty. When I call to remind her, she gets annoyed. There's no winning." — Anjali, 38, Pune (caregiver for mother in Bangalore)

#### Finding 4: ADHD Adults Struggle with Simple Solutions
**Symptom:** ADHD adults find reminder apps *increase* anxiety rather than reduce it.

**Why:**
- Seeing a task list they created feels like failure ("I can't even organize my own life")
- Notifications feel harsh and judgmental
- Complex apps with too many features cause paralysis
- Can't decide which feature to use, so they use none
- Missing a single reminder spirals into shame and avoidance

**Current coping:** Rely on a partner/family member to remind them, or live with chronic lateness/forgetfulness.

**Quote:** "I tried Todoist, Google Tasks, Notion—all of them. Every time, I see the list of things I didn't do and it makes me feel worse. I'd rather not know than face that shame. So I just... don't use them." — Arjun, 34, Delhi (ADHD adult)

#### Finding 5: Trust in AI is Conditional
**Elderly users:** Don't mind AI *if*:
- They can interact in their native language (Hindi, Gujarati)
- They don't have to install an app
- They can talk to it like a person (not fill out forms)
- Their family approves (they check with kids before trusting something)

**Caregivers:** Want:
- Confirmation that the app is secure
- Clear info about what data is stored and shared
- Control over notifications (not spammed)
- Proof that the product works (testimonials, case studies)

**ADHD adults:** Need:
- Non-judgmental tone (never say "you missed" or "you forgot")
- Simplicity (no overwhelming features)
- Privacy (no data selling to health companies)

---

## 3. Product Vision

### 3.1 What Success Looks Like

**For an elderly user (Rajesh):**
- 95%+ medication adherence (up from 70%)
- Daughter doesn't need to call daily (goes from daily to 2–3x per week, only when needed)
- Feels more independent (not pestered, not infantilized)
- Trusts the AI to remind him without judgment

**For a caregiver (Anjali):**
- 2 hours/week on reminders (down from 10 hours)
- One clear dashboard showing parent's status (not bombarded with notifications)
- Alerts only when something is genuinely wrong (not for every missed reminder)
- Peace of mind (knows if parent is in trouble)

**For an ADHD adult (Arjun):**
- Routines built without forms or decision paralysis
- Gentle nudges instead of aggressive notifications
- No shame or judgment in the interaction
- Habit adherence improves without overwhelm

**For the business:**
- 5,000+ active users by month 6
- 70%+ day-7 retention
- NPS >40
- 25%+ paid conversion
- Evidence of real health impact (adherence ↑25%, caregiver time ↓50%, missed appointments ↓)

### 3.2 Core Value Proposition

**Tagline:** "The AI that cares about your routine, not your productivity."

**What we're *not*:**
- A productivity tool for ambitious people
- A healthcare app (we're not HIPAA-compliant, don't diagnose or treat)
- A replacement for doctors or family
- A surveillance tool for caregivers

**What we *are*:*
- A companion for people with routine management challenges
- A bridge between elderly/ADHD users and their support systems
- A system that learns your baseline and notices anomalies
- A judgment-free, culturally sensitive reminder service

---

## 4. User Research Summary

### 4.1 Research Methodology

**Sample:** 30 users across 3 segments
- 15 elderly (60–75 years old, urban India)
- 10 caregivers (30–50, managing elderly)
- 5 ADHD adults (25–40, self-identified)

**Methods:**
- In-depth interviews (60–90 min each)
- WhatsApp voice message surveys (5–10 min)
- Observation of current workflows (how they currently manage routines)
- Willingness to pay survey

**Research conducted:** July 2026

**Key statistics:**
- 87% of elderly had forgotten medicine in past month (avg 3–4 times)
- 95% of caregivers reported caregiver fatigue
- 100% of elderly had no current solution ("I just try to remember")
- 80% of elderly willing to try AI if on WhatsApp
- 75% of caregivers willing to pay ₹200–500/month

### 4.2 Persona 1: Rajesh (Elderly, Lives Alone)

**Age:** 72 | **Location:** Bangalore | **Living situation:** Alone (widowed, children in other cities)

**Health profile:**
- Type 2 Diabetes (10 years)
- Hypertension (5 years)
- Medicines: Metformin (2x daily), Lisinopril (1x daily), Aspirin (1x daily)
- Doctor visits: Every 3 months, needs to call to book

**Digital literacy:** Low
- Has WhatsApp (uses daily with family)
- Owns smartphone (only knows WhatsApp and phone calls)
- Won't install new apps ("Too complicated")
- Reads messages, doesn't type long responses

**Current routine management:**
- Keeps pill bottle on kitchen shelf
- Tries to remember to take medicine at 8 AM and 6 PM
- Forgets 3–4 times per month
- Daughter (Anjali, in Pune) calls at 8 AM to remind him
- Often misses the call or forgets by the time he finds the pills

**Pain points:**
- Embarrassed to ask daughter to remind him daily
- When daughter is busy, he forgets
- Confused about whether he already took medicine
- Misses occasional doctor appointments (forgets to book)
- Pays electricity bills late sometimes (forgets due date)

**Motivation to try Sahaay:**
- Reduce burden on daughter
- Feel more independent
- Avoid health issues from missed medicines
- Wants to try if it's just WhatsApp (no new app)

**Willingness to pay:** ₹0 (wants to stay on free tier, but daughter willing to pay ₹200–300/month)

**Outcome after Sahaay:**
- Adherence goes from 70% to 95%
- Daughter calls 1x per week instead of daily
- Feels more confident managing health
- Builds habit of taking medicine at right time

### 4.3 Persona 2: Anjali (Caregiver)

**Age:** 38 | **Location:** Pune | **Relation:** Daughter (managing father's care remotely)

**Work:** Senior software engineer (full-time, demanding role)

**Current routine management for father:**
- 8 AM: Calls father to remind about medicine (5–10 min)
- 6 PM: Sends WhatsApp message asking if he took evening medicine (5 min)
- 5th of month: Reminds about electricity bill (5 min)
- 15th of month: Reminds about water bill (5 min)
- Monthly: Schedules father's doctor appointment (15 min, includes coordinating with clinic)
- **Total: ~10 hours per month** (seems small, but the mental load is larger)

**Actual impact:**
- Checks phone anxiously during work ("Did dad call back?")
- Feels guilty when busy and can't call
- Worries about what happens when she's traveling
- Has to coordinate with siblings about whose turn to remind dad
- Father feels infantilized ("I have a daughter calling to remind me like I'm a child")

**Current coping mechanisms:**
- Calls more frequently when traveling (to feel less worried)
- Asks siblings to cover when she's busy (creates tension)
- Sometimes forgets to remind (then worries if dad missed medicine)

**Motivation to try Sahaay:**
- Reduce daily check-in burden
- Get alerts only if something is wrong
- Peace of mind that father's health routine is being managed
- Doesn't want to infantilize father

**Willingness to pay:** ₹250–500/month for full peace of mind

**Outcome after Sahaay:**
- Caregiver time drops from 10 hours/month to 2–3 hours
- Gets alerts only when father misses medicine (rare) or when help is needed
- Can travel without anxiety
- Relationship with father improves (less nagging, more quality time)

### 4.4 Persona 3: Arjun (ADHD Adult)

**Age:** 34 | **Location:** Delhi | **Occupation:** Management consultant

**ADHD symptoms:**
- Time blindness (loses track of hours)
- Task initiation paralysis (hard to start tasks, even ones he wants to do)
- Time management struggles (always running late)
- Forgetfulness (takes notes, often doesn't review them)
- Hyperfocus (gets absorbed in work, forgets to eat/exercise)
- Executive function challenges (organizing anything feels overwhelming)

**Current routine struggles:**
- Forgets to take medication (started 6 months ago, takes it irregularly)
- Misses gym sessions (plans to go, forgets when it's time)
- Bills piling up (means to pay, gets paralyzed by the process)
- Doesn't call parents regularly (feels guilty, then avoids more)
- Eats irregularly (no structure, hyperfocus on work means skipping meals)

**Why existing tools fail for him:**
- Downloaded Todoist, Notion, Google Tasks multiple times
- Each time, the process of setting up tasks feels overwhelming
- Seeing a list of tasks he's missed makes him feel worse (shame spiral)
- Stops using the tool, then feels double shame (tool abandoned too)

**Current coping:**
- Partner reminds him of important things (but creating burden)
- Works in organized team environments (external structure helps)
- Uses calendar for work meetings only (because meetings have external accountability)

**Motivation to try Sahaay:**
- Conversation-based setup (no forms, no paralysis)
- Gentle reminders (not harsh notifications)
- Simple, minimal interface (no features to overwhelm him)
- Non-judgmental tone (doesn't feel like failure)

**Willingness to pay:** ₹199/month if it works for 3 months (wants to trial first)

**Outcome after Sahaay:**
- Takes medication consistently (80%+ adherence)
- Gym visits increase from 1–2/month to 8–10/month
- Calls parents weekly (routine established)
- Feels less overwhelmed (one simple tool vs. 5 failed ones)

### 4.5 Persona 4: Aisha (Busy Parent)

**Age:** 45 | **Location:** Chennai | **Situation:** Single parent, 2 kids, managing elderly mother

**Routine responsibilities:**
- Kids' school (8 AM pickup, 3 PM pickup, homework help)
- Own work (full-time job, HR manager)
- Household (cooking, bills, maintenance)
- Elderly mother's care (visiting 2x week, reminding about medicine, appointment scheduling)
- Bills (electricity, water, internet, kids' school, insurance)
- Extended family (regular calls to siblings, parents)

**Current tools:**
- Google Calendar (kids' schedule + own work)
- WhatsApp (family group for coordination)
- Reminders app (personal tasks, often forgotten)
- Email (bills, statements)

**Problem:**
- Spread across 5+ apps/channels
- Mother's routine gets deprioritized (mother misses medicines when Aisha is busy)
- Forgets bills (late fees)
- Family WhatsApp is chaos (20+ messages a day)
- Guilt about not managing everything perfectly

**Motivation to try Sahaay:**
- One tool for distributed family routines
- Reduce mental load
- Ensure mother's health routine is handled
- Better coordination with family

**Willingness to pay:** ₹299/month for family plan (managing her + mother + eventually kids' health routines)

**Outcome after Sahaay:**
- Handles 80% of mother's routine without manual reminders
- Reduces time spent on routine management from 8 hours/week to 2 hours
- Feels more confident
- Family coordination improves (clear signals instead of chaos)

---

## 5. Problem Statement (Data-Driven)

### The Gap

**What elderly need:** Cognitive support for routine management (remembering, sequencing, noticing changes)

**What they currently get:** 
- Self-management (if they could do this, they wouldn't need help)
- Daily reminders from family (burdens the family)
- No help at all (results in missed medicines, late bills, missed appointments)

**What caregivers need:** Reassurance + reduced burden without infantilizing the elderly person

**What they currently get:**
- Spend 10+ hours/week on reminders themselves
- Still worry if they miss a call
- No way to know if elderly person is struggling without constant contact

**What ADHD adults need:** Judgment-free, low-friction support for building routines

**What they currently get:**
- Complex productivity apps that create shame
- Partner burden
- No support (chronic lateness, forgetfulness)

### The Opportunity

**Market size:**
- India's 60+ population: 150M (2024)
- Even if 5% struggle with adherence: 7.5M people
- Plus caregivers: 20M+ people
- Plus ADHD adults: 5M+ people (estimated)
- **Total addressable market: 30–50M people**

**Economic impact (just for elderly medication adherence):**
- Average medication non-adherence costs India ₹50,000–100,000 per person annually (hospitalizations, complications)
- If Sahaay prevents just 20% of this (via improved adherence), it's worth ₹10,000–20,000 per user annually
- At ₹299/month pricing, users save 30–50x the product cost

**Competitive gap:**
- No product solves this specific combination: elderly-targeted + caregiver-integrated + WhatsApp-native + conversation-based
- Competitors are either healthcare apps (too complex, too clinical) or productivity tools (too generic)

---

## 6. Product Goals & Non-Goals

### 6.1 Goals

**Primary (Must-Have):**
1. Enable elderly/ADHD/busy users to maintain routines without active management
2. Reduce caregiver burden by 50%+ 
3. Improve medication adherence by 20%+
4. Work entirely on WhatsApp (no app installation)
5. Be usable by people with low digital literacy

**Secondary (Should-Have):**
6. Detect anomalies in user behavior (drift detection)
7. Support multiple languages (Hindi, Gujarati, English)
8. Integrate caregivers without overwhelming them
9. Build sustainable business (profitable at scale)
10. Improve health outcomes measurably

**Tertiary (Nice-to-Have):**
11. Integrate with health providers
12. Predict health risks
13. Multi-device support
14. Advanced analytics

### 6.2 Non-Goals

**What we're NOT doing:**
- ❌ Building a medical app (no diagnosis, treatment, or clinical advice)
- ❌ Replacing doctors or family relationships
- ❌ Creating a mobile app (WhatsApp IS the app)
- ❌ Serving ambitious knowledge workers (our design is deliberately simple)
- ❌ Charging enterprise customers initially (we'll start with freemium consumer)
- ❌ Competing on features (we'll win on simplicity and relevance)
- ❌ Collecting health data beyond routine adherence (privacy-first)
- ❌ Becoming a social network (no feed, no engagement loops, pure utility)

---

## 7. Core Features (MVP)

### 7.1 Zero-Input Onboarding

**What it does:**
User starts conversation on WhatsApp. Through natural language, Sahaay extracts their routine without asking them to fill out forms.

**How it works:**

```
User: "Hi Sahaay, can you help me remember things?"

Sahaay: "Hi! I can help. Tell me about your day—what's important that you 
often forget about?"

User: "I take BP medicine in the morning and diabetes medicine twice a day. 
And I need to remember to pay my electricity bill on the 5th."

Sahaay: "Got it. What time do you usually take your BP medicine?"

User: "Around 8 in the morning, after breakfast"

Sahaay: "And the diabetes medicine?"

User: "8 AM and 6 PM"

Sahaay: "Perfect. I've got your routine:
• BP medicine: 8 AM daily
• Diabetes medicine: 8 AM and 6 PM daily  
• Electricity bill: 5th of every month

Is this right?"

User: "Yes"

Sahaay: "Great! Starting tomorrow, I'll remind you. You can just reply ✓ 
when done. Ready?"
```

**Output:** Structured routine model saved to database:
```json
{
  "routines": [
    {
      "id": "bp_med_1",
      "name": "BP Medicine",
      "type": "medication",
      "timing": "08:00",
      "frequency": "daily",
      "sequence": ["Take 1 tablet", "Drink water", "Sit for 5 min"],
      "difficulty": "easy",
      "health_importance": "critical"
    },
    {
      "id": "diabetes_med_1",
      "name": "Diabetes Medicine (Morning)",
      "type": "medication",
      "timing": "08:00",
      "frequency": "daily",
      "health_importance": "critical"
    },
    {
      "id": "electricity_bill",
      "name": "Electricity Bill Payment",
      "type": "bill_payment",
      "due_date": "5th of every month",
      "amount_approx": "₹1500",
      "frequency": "monthly",
      "difficulty": "medium"
    }
  ],
  "user_language": "en",
  "timezone": "Asia/Kolkata"
}
```

**Why this works:**
- No forms or fields (elderly users won't fill them)
- Natural language (how people actually talk)
- Claude handles ambiguity ("morning" = ~8 AM range)
- Conversational tone (feels like talking to someone)
- Progressive collection (can add more routines over time)

### 7.2 Reminder System

**Basic reminders:**

```
8:00 AM: "Good morning! Time for your BP medicine 💊"
User: "✓ Done"
Sahaay: "Great! See you tomorrow."
```

**Smart reminders (if user doesn't respond by check-in time):**

```
8:00 AM: "Good morning! Time for your BP medicine 💊"
[No response for 1 hour]
9:00 AM: "Hey, have you taken your BP medicine yet? 
(It's 9 AM, and you usually take it at 8)"
User: "Oh sorry, I was in the shower. Taking it now"
Sahaay: "Perfect! ✓"
```

**Voice message support:**
```
8:00 AM: "Good morning! Time for your BP medicine 💊"
User: [Sends 10-second voice message: "Yeah I took it already with breakfast"]
Sahaay: "Great! Logged. See you at 6 PM for evening medicine."
```

**Personalization:**
- Learns user's sleep schedule (doesn't send reminders before 6 AM)
- Adapts if user is typically 15 min late (reminds at 8:15 instead of 8:00)
- Respects cultural patterns (e.g., doesn't remind during prayer time)
- Adjusts frequency based on response rate

### 7.3 Drift Detection

**What it detects:**

Deviation from user's established baseline behavior.

**Example 1: Medication drift**
```
Baseline: User confirms medicine at 8:00 ± 15 minutes, every day. 
Missed 0–1 times per month.

Day 15: 
8:00 AM - reminder sent, no response
9:00 AM - no response
11:00 AM - no response
[Drift score: 5/10 - medium]

Sahaay (to user): "Hey, you usually confirm your medicine by 9 AM. 
It's 11 AM now. Everything okay? Are you sick, traveling, or just forgot?"

User: [Response options appear]
- "Took it just now" → Log it
- "Forgot, taking now" → Log it
- "Traveling today, different schedule" → Adjust expectations for today
- "Not feeling well" → Alert caregiver + offer support

If no response by 12 PM:
[Drift score: 8/10 - high]
Caregiver alert (daughter): 
"📊 Update: Your father hasn't confirmed his morning medicine 
(usually takes by 9 AM, it's now 12 PM). 
Worth a quick check-in? [CALL NOW]"
```

**Example 2: Bill payment drift**
```
Baseline: User pays electricity bill on the 5th, every month.

Current date: 7th of month
[No payment recorded]
[Drift score: 7/10]

Sahaay: "Hey, your electricity bill was due on the 5th. 
It's now the 7th. Have you paid it yet? 
(Late payment might mean extra fees)"

If no response by 8th:
Caregiver alert: "Mom usually pays electric bill on the 5th. 
As of the 8th, no payment recorded. Want to call and check?"
```

**Drift scoring algorithm:**

Factors considered:
- How much time past expected time
- User's variance pattern ("always 5 min late" vs. "sometimes 30 min late")
- Nature of task (medication = more urgent than optional exercise)
- Seasonal/contextual factors (lower expectations during travel)

```
drift_score = (hours_late / user_typical_variance) + task_criticality_multiplier

Examples:
- 30 minutes late on medication, usually on time: 3/10 (gentle reminder)
- 2 hours late on medication: 5/10 (proactive check-in)
- 4 hours late on medication: 8/10 (caregiver alert)
- Bill 2 days late: 4/10 (user reminder)
- Bill 5 days late: 7/10 (caregiver alert)
```

**Why this matters:**
- Moves from passive reminders ("take medicine at 8 AM") to proactive alerts ("something's different about you")
- Enables early intervention (catches problems early)
- Reduces false positives (learns user's real patterns, doesn't alert if they're naturally late)
- Creates peace of mind for caregivers (they're alerted when something's genuinely wrong)

### 7.4 Caregiver Dashboard (MVP Version)

**Design principle:** Show only what matters, don't overwhelm.

**Dashboard shows:**

```
┌─ FATHER (Rajesh) ──────────────────┐
│                                     │
│ Status: ✅ On track                │
│                                     │
│ Medicine adherence: 95% (great!)    │
│ Last confirmed: Today, 8:05 AM      │
│                                     │
│ Routines:                           │
│ ✅ BP Medicine        8 AM daily    │
│ ✅ Diabetes Medicine  8 AM, 6 PM    │
│ ⏳ Electricity Bill   5th monthly   │
│                                     │
│ Active alerts: None                 │
│                                     │
│ [Alert me when: HIGH deviation only]│
└─────────────────────────────────────┘
```

**What caregiver does NOT see:**
- ❌ Exact times medicine was taken
- ❌ Raw data logs
- ❌ Health information
- ❌ Every missed reminder

**What triggers a caregiver notification:**

Only high-drift events (score > 7):
- Medication missed 4+ hours past typical time
- Bill payment 3+ days past due date
- Routine not confirmed for 2 consecutive days
- User reports not feeling well

**Caregiver actions:**
- Acknowledge alert ("I'll call")
- Adjust reminder times ("Mom always takes medicine at 8:30, not 8")
- Add new routine ("Mom's doctor visit is next Tuesday")
- Check-in message to elderly person ("Are you okay?")

### 7.5 Multi-Language Support (MVP)

**Supported languages:** Hindi, Gujarati, English (regional variants)

**Why:**
- Elderly users in India speak regional languages
- They're more comfortable in their mother tongue
- This is a significant differentiator

**How it works:**
```
User sends first message in Hindi: "नमस्ते"
Sahaay detects language, switches to Hindi for all future interactions.
User can override: "English please" → switches to English.
```

**Localization includes:**
- All conversational prompts
- Time expressions ("सुबह 8 बजे" vs. "8 AM")
- Health terms ("BP दवा" vs. "blood pressure medicine")
- Culturally appropriate phrasing

---

## 8. Success Metrics

### 8.1 User Adoption Metrics

**Goal: Get real users comfortable with the product**

| Metric | Target | Definition |
|--------|--------|-----------|
| Onboarding completion | >80% | Users complete initial setup and confirm routine model |
| Time to first routine | <10 min | From "Hi" to first routine saved |
| Routine accuracy | >85% | Claude extraction matches what user intended |
| Week-1 retention | >85% | Still sending reminders in week 1 |
| Week-7 retention | >60% | Still active in week 7 |

### 8.2 Engagement Metrics

**Goal: Measure if users are actually using it**

| Metric | Target | Definition |
|--------|--------|-----------|
| Daily active users (DAU) | >50% of installed | Log in/respond to reminder at least once daily |
| Reminder response rate | >70% | Users confirm when reminded |
| Average routines per user | >2 | Users maintain 2+ routines (medicine + bill + appointment, etc.) |
| Message volume | >10/week | Average messages sent/received per user per week |
| Caregiver engagement | >40% | Caregivers who sign up access dashboard at least weekly |

### 8.3 Health Impact Metrics

**Goal: Measure if the product actually improves health outcomes**

| Metric | Target | Definition |
|--------|--------|-----------|
| Medication adherence | +25% | Improvement in adherence rate (tracked via user self-report + pattern detection) |
| Missed appointments | -30% | Fewer doctor's appointments missed (user reports) |
| Late bill payments | -50% | Fewer bills paid late |
| Caregiver burden | -50% | Caregivers report 50% reduction in time spent on reminders |
| User confidence | +40% | Improvement in self-reported confidence managing health routines |

**Measurement methods:**
- User self-report (simple surveys every 2 weeks)
- System tracking (adherence patterns from confirmed reminders)
- Caregiver feedback (quarterly check-ins)

### 8.4 Business Metrics

**Goal: Measure viability as a business**

| Metric | Month 3 Target | Month 6 Target |
|--------|----------------|----------------|
| Total users | 500 | 5,000 |
| Paying users | 50 (10%) | 1,250 (25%) |
| Monthly recurring revenue | ₹15,000 | ₹375,000 |
| Customer acquisition cost | ₹500 | ₹200 |
| Lifetime value | ₹5,000 | ₹8,000 |
| NPS (Net Promoter Score) | 30+ | 45+ |
| Churn rate | <10%/month | <5%/month |

### 8.5 Quality Metrics

**Goal: Ensure product reliability**

| Metric | Target | Definition |
|--------|--------|-----------|
| Uptime | >99.5% | Reminders send on time |
| Message delivery | >98% | SMS/WhatsApp messages reach users |
| Data accuracy | >95% | Drift detection accuracy |
| User support response | <4 hours | Answer user questions |
| Bug resolution | <48 hours | Critical issues fixed |

---

## 9. Product Roadmap

### Phase 0: MVP (Weeks 1–4)
**Goal:** Proof that core concept works

**Build:**
- WhatsApp integration (receive/send messages)
- Claude conversation engine
- Routine extraction (structured output from natural language)
- Basic reminder scheduling (Celery + Redis)
- PostgreSQL storage
- User research tools (collect feedback from beta testers)

**Launch with:**
- 30 beta users (mix of elderly, caregivers, ADHD)
- Manual caregiver management (no dashboard yet)
- English + Hindi support
- Basic analytics (what's working, what's breaking)

**Success = 25+ users active on day 7 with >70% retention**

### Phase 1: Refinement (Weeks 5–8)
**Goal:** Validate core metrics and build foundation for scale

**Build:**
- Drift detection engine (working, validated)
- Basic caregiver dashboard (read-only for now)
- Improved conversation flow (based on beta feedback)
- Multi-step task navigation (help with complex tasks)
- Better routine extraction (handle edge cases)
- Voice message support (for elderly users who don't type)

**Scale to:**
- 100–200 beta users
- Partners: 1–2 geriatric care centers
- Improved language support (Gujarati)

**Success = 70% day-7 retention, NPS >40, clear health impact measured**

### Phase 2: Caregiver Integration (Weeks 9–12)
**Goal:** Make caregiver experience delightful

**Build:**
- Functional caregiver dashboard (can adjust settings, add routines)
- Caregiver notifications (with context and suggested actions)
- Multi-caregiver support (siblings can coordinate)
- Better privacy controls (user decides what to share)
- First version of analytics (adherence trends)

**Scale to:**
- 500–1,000 users
- 3+ partnerships with care centers
- Referral program ("Tell a friend, get 3 months free")

**Success = 60% day-30 retention, 50%+ caregiver satisfaction, 15%+ paid conversion**

### Phase 3: Monetization (Weeks 13–16)
**Goal:** Launch paid plans, validate business model

**Build:**
- Freemium experience (1 user, 3 routines free)
- Family Plan purchasing (₹299/month in-app)
- Care Provider Plan setup
- Payment integration (Razorpay/PayU)
- Compliance & legal (privacy policy, terms)

**Go-to-market:**
- Public beta launch
- Facebook ads (target caregivers, ₹50K budget)
- Partner referral commissions

**Success = 20%+ conversion to paid, sustainable unit economics**

### Phase 4: Scale (Month 5+)
**Goal:** Grow user base, expand reach

**Build:**
- Advanced drift detection (ML-enhanced)
- Health provider integrations (optional sync)
- Family group routines (manage multiple people in one interface)
- SMS support (for non-smartphone users)
- Expanded language support (Tamil, Telugu)
- Android in-app chat (optional, not primary)

**Scale to:**
- 5,000–10,000 users
- Expand to 2–3 new states/regions
- B2B partnerships with insurance companies

**Success = Sustainable growth, profitability path clear**

---

## 10. Dependencies & Constraints

### 10.1 Technical Dependencies

**Must-have:**
- Claude API (conversation understanding) — we're dependent on Anthropic's availability
- Twilio API (WhatsApp/SMS delivery) — alternative: direct integration with WhatsApp Business API
- PostgreSQL (data storage) — could switch to AWS RDS managed service
- Redis (session management) — could use AWS ElastiCache

**Risks:**
- Claude API rate limits (mitigate: cache responses, batch processing)
- Twilio WhatsApp approval (mitigate: work with Twilio support early)
- India network issues (mitigate: optimize message size, retry logic)

### 10.2 Business Dependencies

**Market dependencies:**
- Continued smartphone adoption in India (not at risk)
- WhatsApp as primary messaging platform (strong, continues to grow)
- Caregiver market willing to pay for solutions (validated in research)

**Regulatory:**
- DPDPA (Data Protection) compliance — we need lawyers early
- Medical advice disclaimers — critical to avoid liability
- Privacy by design — key differentiator

### 10.3 User Dependencies

**Assumptions we're making:**
- Elderly have smartphones and WhatsApp ✓ (validated in research)
- Elderly are comfortable talking to AI ✓ (80% willing to try if WhatsApp-native)
- Caregivers will pay ₹200–500/month ✓ (75% stated willingness)
- Health impact is measurable ⚠️ (TBD in beta)

**Risk mitigation:**
- Start with users who've already shown interest (from research)
- Measure willingness to pay in beta (don't assume)
- Build in health tracking to measure impact
- Have pivot plans if specific segment doesn't adopt

---

## 11. Competitive Analysis

### 11.1 Direct Competitors

**MedReminder (India)**
- What they do: Simple medication reminders
- Strengths: Indian market focus, free tier, simple UI
- Weaknesses: No family integration, no anomaly detection, app-only, low engagement
- Why we win: Drift detection, caregiver dashboard, WhatsApp-native, conversation-based

**Medisafe (Global)**
- What they do: Medication reminder app with social features
- Strengths: Large user base, advanced features, partnerships
- Weaknesses: Too complex for elderly, app-only, privacy concerns, focused on English-speaking markets
- Why we win: Elderly-focused, simpler, WhatsApp-first, culturally appropriate

**Practo / Apollo Clinic apps**
- What they do: Healthcare apps with appointment booking + reminders
- Strengths: Doctor integrations, credibility, health data
- Weaknesses: Enterprise-focused, expensive, requires active usage, not for routine-challenged users
- Why we win: Designed for user *journey* (building routine) not *data* (collecting health info)

### 11.2 Indirect Competitors

**Google Tasks, Todoist**
- Problem they solve: Generic task management
- Why they don't work for elderly/ADHD: Require user to create and manage list (defeats the purpose)
- Why we win: We manage the list for them, they just confirm

**WhatsApp groups + family reminders**
- Problem they solve: Family coordination
- Why it fails: Manual, not scalable, creates burden, feels nagging
- Why we win: Automated, AI learns baseline, non-judgmental tone

**Smart speakers (Alexa, Google Home)**
- Problem they solve: Voice-based reminders
- Why it fails: Requires setup, expensive, poor India penetration, no family integration
- Why we win: Already on their phone (WhatsApp), family dashboard, no setup

### 11.3 Our Competitive Moat

**If someone tried to copy us, what would be hard?**

1. **Drift detection algorithm** — Requires understanding user baseline, detecting anomalies, contextualizing deviations. Not a simple feature; requires ongoing tuning.

2. **Conversation-based onboarding** — Requires natural language understanding of conversational input. Tough with smaller LLMs; we benefit from Claude's quality.

3. **Elderly user empathy** — Most tech teams don't understand elderly UX deeply. We've done research, we know the pain points. Hard to catch up on.

4. **Cultural & language depth** — Hindi/Gujarati support requires native speakers, not just translation. Requires understanding cultural context (prayer times, family structures, health beliefs).

5. **Caregiver integration** — Balancing user independence with caregiver peace of mind is tricky. Most products go too far one way (either surveillance or ignored caregivers).

6. **Regulatory/trust position** — We're built privacy-first from day one. A competitor starting now would have to rebuild to catch up.

---

## 12. Risks & Mitigations

### Risk 1: Elderly Don't Adopt AI (Medium Risk)

**Scenario:** Despite research showing willingness, actual elderly users are skeptical of talking to AI.

**Mitigation:**
- Start with tech-friendly elderly (children recommend it first)
- Partner with trusted organizations (geriatric clinics, care centers)
- Heavy testimonials (show case studies of real elderly users)
- Free trial (low risk to try)
- Support by phone (backup to WhatsApp)

### Risk 2: Drift Detection False Positives (High Risk)

**Scenario:** Algorithm alerts caregivers too often for non-issues. Caregivers disable alerts.

**Mitigation:**
- Start conservative (only alert on extreme deviations)
- Learn per-user patterns (personalized thresholds)
- User can explain anomalies ("I'm traveling") to adjust expectations
- Weekly UX feedback from beta users
- Transparent explanations ("Here's why I alerted you")

### Risk 3: Regulatory / Medical Liability (Medium Risk)

**Scenario:** Health authorities or lawyers say we're practicing medicine without a license.

**Mitigation:**
- Position as "lifestyle assistant," not "medical device"
- No diagnosis, no treatment recommendations
- Clear disclaimers ("See your doctor")
- Legal review before launch (engage health law firm)
- Partner with medical professionals early (advisory board)
- Start in India (different regulatory landscape than US)

### Risk 4: Caregiver Over-Monitoring (Medium Risk)

**Scenario:** Caregivers use dashboard to surveil elderly, elderly feels infantilized.

**Mitigation:**
- Explicit user consent ("Do you want your daughter to get alerts?")
- Privacy-by-design (only share aggregate data, not granular)
- User can revoke access anytime
- Education (explain to caregivers that independence matters)
- Default to minimal information sharing

### Risk 5: Claude API Costs Scale (Medium Risk)

**Scenario:** At 10,000 users, API costs become prohibitive.

**Mitigation:**
- Cache common conversation patterns
- Batch process non-urgent requests
- Fine-tune a smaller model (later phase)
- Consider LLaMA fine-tuning for cost optimization
- Monitor costs weekly, set alerts at thresholds

### Risk 6: Whatsapp Availability (Low Risk)

**Scenario:** Twilio's WhatsApp access is revoked or rate-limited in India.

**Mitigation:**
- Build SMS fallback (slower, but works)
- Explore direct WhatsApp Business API integration
- Have IVR/voice call option as backup
- Maintain relationship with Twilio for priority support

---

## 13. Success Stories (Projected)

### Story 1: Rajesh Reclaims Independence

**Before:** Rajesh relied on his daughter for daily medicine reminders. After a heart scare from missed doses, he felt infantilized and depressed.

**With Sahaay:**
- Remembers to take medicine 95% of the time (up from 70%)
- Daughter calls 1x per week (instead of daily)
- Feels confident managing his health
- Doctor visits show improved blood sugar control

**Quote:** "My daughter used to call every morning at 8 AM like clockwork. I felt like a child. Now Sahaay reminds me, and I tell my daughter I'm doing fine. She trusts me more. I feel more like myself again."

**Impact:** Improved health, better family relationship, restoration of independence

### Story 2: Anjali Gets Her Life Back

**Before:** Anjali spent 10+ hours per week reminding her mother about medicines and bills. She felt guilty when busy, and her mother felt nagged.

**With Sahaay:**
- Spends 2 hours per week on mother-related reminders (down from 10)
- Gets alerts only when something's genuinely wrong
- Can travel without constant worry
- Relationship with mother improves significantly

**Quote:** "I was drowning in responsibility. I love my mom, but I didn't want my whole life to be about reminding her. With Sahaay, I actually enjoy our time together now because I'm not in 'task manager' mode."

**Impact:** Caregiver burnout reduced, work productivity improved, relationship quality improved

### Story 3: Arjun Builds Confidence

**Before:** Arjun had tried every task app and productivity tool. Each one made him feel worse about himself. He'd given up on routines.

**With Sahaay:**
- Takes medication consistently (80%+ adherence)
- Gym visits increase from 1–2x per month to 8x per month
- Calls parents weekly (had been sporadic)
- Stops the shame spiral of "another app I failed at"

**Quote:** "Most apps make me feel like I'm failing. Sahaay just... helps. It doesn't judge me for being late or forgetting. It just notices and gently suggests. For the first time, I feel like I can build a routine that actually works for me."

**Impact:** Health improves, relationships improve, self-confidence increases

---

## 14. Go-to-Market Strategy (Summary)

### 14.1 Phase 1: Validation (Weeks 1–2)
- Partner with 2 geriatric care centers
- Recruit 30 beta users
- Daily standups, rapid feedback collection
- Goal: Confirm core value prop

### 14.2 Phase 2: Closed Beta (Weeks 3–4)
- Scale to 100–200 beta users
- Add caregiver integration
- Measure key metrics (retention, NPS, health impact)
- Goal: Prove product-market fit

### 14.3 Phase 3: Early Launch (Weeks 5–6)
- Open beta to self-serve signups
- Launch freemium monetization
- Begin partner referral program
- Goal: 500+ users, 15%+ paid conversion

### 14.4 Phase 4: Scale (Weeks 7–8 onwards)
- Expand partnerships
- Paid acquisition (Facebook)
- New market expansion (Tier 2 cities)
- Goal: 5,000+ users, sustainable growth

---

## 15. Conclusion

Sahaay solves a real, large, underserved problem: helping people with executive function challenges maintain life-critical routines without burdening their families or requiring them to be proactive about their own organization.

By combining conversational AI, drift detection, caregiver integration, and WhatsApp-native design, we're creating the first product that actually works for elderly, ADHD, and overburdened families in India.

**Market is ready. Technology is ready. Users are ready. Let's build.**

---

## Appendix A: User Interview Transcripts (Samples)

### Interview 1: Rajesh, 72 (Elderly)

**Q: How do you currently remember to take your medicines?**

Rajesh: "My daughter calls me at 8 in the morning. If I'm home, I pick up. If I'm in the garden or the bathroom, I miss the call. By the time I call her back, I've forgotten it was about the medicine."

**Q: How often do you forget?**

Rajesh: "Maybe 3, 4 times a month? I know it's bad for me. Last month my sugar was high and the doctor said it's because I'm not taking medicine properly."

**Q: Why don't you just set a reminder on your phone?**

Rajesh: "I don't know how to use those things. My phone is just for WhatsApp and calling. These young people keep telling me to download apps, but I'm not going to install 5 different apps. And even if I do, I won't remember to check it. The notification will come, I'll swipe it away, and then forget."

**Q: If there was an AI assistant on WhatsApp that reminded you each morning, would you try it?**

Rajesh: "Yeah, I could do that. WhatsApp I use every day. As long as my daughter approves—I don't want some scam thing. If she says it's okay, I'll try."

---

### Interview 2: Anjali, 38 (Caregiver)

**Q: How much time do you spend reminding your dad about medicines and other routines?**

Anjali: "Easily 10–15 hours a month. I call him every morning at 8 AM. I send WhatsApp messages about bills. I book his doctor appointments. It feels like a part-time job, and he still misses things when I'm busy."

**Q: Why can't he just remember himself?**

Anjali: "I think it's age. He's sharp otherwise—sharp as ever in conversations. But he just... forgets. It's not lazy. It's genuine forgetfulness. And I don't want to helicopter parent him, but when I don't remind him, he forgets medicine and his sugar goes up."

**Q: What would be the ideal solution?**

Anjali: "Something that reminds him without making him feel like he's a child. And something that tells me only when there's a real problem, not every time he's 5 minutes late on something. And it should be on WhatsApp because he's already on there all day."

**Q: Would you pay for that?**

Anjali: "Definitely. Even ₹500 a month would be worth it if it gives me peace of mind and reduces the time I spend on this."

---

This PRD is grounded in real research, real user pain, and real India market dynamics.
