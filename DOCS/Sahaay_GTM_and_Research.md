# Sahaay: Go-to-Market & User Research Plan
## Getting from MVP to Product-Market Fit

---

## Phase 1: Validation (Weeks 1–8)
### Goal: Prove the core value proposition with 50–100 real users

---

## 1. User Research Strategy

### 1.1 Primary Research: Who to Interview

**Segment 1: Elderly individuals (60+ years)**
- Live alone or with one family member
- Manage 2+ medications
- Low digital literacy (but own a smartphone + WhatsApp)
- In India (urban or semi-urban)

**Segment 2: Primary caregivers (30–50 years)**
- Manage elderly parent or dependent
- Employed full-time
- Currently use phone/WhatsApp for reminders
- Express frustration with current solutions

**Segment 3: ADHD adults (25–40 years)**
- Self-diagnosed or clinically diagnosed
- Use some organizational tools (Notes app, calendar, etc.)
- Express friction with current solutions
- Interested in AI/tech support

**Segment 4: Busy families (parents with multiple responsibilities)**
- Manage kids' schedules, own work, extended family
- Express overwhelm with organization
- Use multiple apps/tools

### 1.2 Recruitment Strategy

**Where to find users:**

1. **Geriatric care centers / Senior living facilities**
   - Contact: HelpAge India, Aasra, local nursing homes
   - Pitch: "Help us improve our elderly care with AI"
   - Sample size: 30 users (15 elderly + 15 caregivers)

2. **ADHD communities**
   - Reddit: r/ADHD_India, r/ADHD
   - Facebook groups: "ADHD Adults India," "ADHD Support"
   - LinkedIn: Reach out directly to ADHD advocates
   - Sample size: 15 users

3. **WhatsApp/social media recruitment**
   - Your personal network first (cheapest, fastest)
   - Local community groups
   - Incentive: Free access to product for 3 months

4. **Direct outreach**
   - Cold email to caregiver organizations
   - In-person visits to senior centers
   - Partner with local clinics for referrals

### 1.3 Interview Script

**For Elderly Users (15–20 min, in Hindi/Gujarati)**

```
Opening:
"Hi, I'm building an AI assistant to help people remember medicines and 
important tasks. Can I ask you about your experience?"

Warm-up:
- What medications do you currently take?
- How do you remember when to take them?
- What's the hardest part?

Problem exploration:
- Have you ever forgotten your medicine?
- What happened?
- Who reminds you usually?
- What tools have you tried? (phone reminders, calendar, etc.)

Solution exploration:
- If an AI could talk to you on WhatsApp like a friend and remind you, 
  would that be helpful?
- Would you feel comfortable giving it your routine info via voice?
- Would you want your kids to get alerts if something's wrong?

Closing:
- Would you be willing to test this for 2 weeks?
- What would make this perfect for you?
```

**For Caregivers (20–30 min, in English/Hindi)**

```
Opening:
"I'm building a tool to reduce caregiver burden. I'd love to understand 
your experience managing your parent's routine."

Warm-up:
- How long have you been managing your parent's care?
- What are the hardest parts?
- What tools do you currently use?

Problem exploration:
- How many hours/week do you spend on reminders and check-ins?
- What's the worst scenario that's happened?
- How does it affect your relationship?
- What would change your life most?

Solution exploration:
- Would you trust an AI to monitor routine and alert you only when needed?
- What would "only when needed" look like for you?
- How would you feel about your parent using it?
- Would you pay for this? If yes, how much?

Closing:
- Would you co-test this with your parent?
- What's your biggest concern?
```

### 1.4 Interview Cadence

| Week | Activity | Sample Size | Goal |
|------|----------|-------------|------|
| Week 1–2 | Problem interviews (pre-launch) | 20 | Validate core problem |
| Week 3–4 | Closed beta (MVP) | 30 | Test product usability |
| Week 5–6 | User testing (iterate) | 50 | Refine core features |
| Week 7–8 | Scale test (500 users) | 200 | Measure retention |

---

## 2. Beta Launch Strategy

### 2.1 Closed Beta (Week 3–4)

**Who:** 30 invited users from interviews

**Logistics:**
- Add them manually to Twilio account
- Send welcome message with instructions
- Daily standups with research team (brief, 5 min calls)

**What to measure daily:**
- Onboarding completion rate
- Time to completion
- Routine extraction accuracy
- User questions/blockers
- Sentiment (thumbs up/down)

**Communication:**
```
Welcome message:
"Hi Rajesh! Welcome to Sahaay beta. 🎉

Over the next 2 weeks, I'll learn your routine through our chats, 
then remind you about medicines and bills.

Let's start: What medicines do you take? What time?
(Just reply here—no fancy steps needed!)"
```

### 2.2 User Testing Protocol

**For each user, track:**

1. **Onboarding**
   - Time to complete (target: <10 min)
   - Clarity of instructions (1–5)
   - Any confusion points

2. **Core loop** (over 2 weeks)
   - % of reminders confirmed
   - % of reminders missed
   - User satisfaction with reminder timing (early/late/perfect?)

3. **Drift detection**
   - When first drift alert is sent
   - Does user understand the alert? (ask)
   - Did it lead to action? (follow-up)

4. **Engagement**
   - Daily active usage (open WhatsApp + respond)
   - Response time to reminders
   - Churn (stop using by day 3/7/14)

**Weekly debrief:**
```
Message to user:
"Hey Rajesh, it's Friday! Quick question: 
Have the Sahaay reminders been helpful? 
[Very helpful / Somewhat helpful / Not helpful]"

For caregivers:
"Hi Anjali! How's your experience? 
Any alerts from Sahaay helped? 
[Yes / No / Not needed yet]"
```

---

## 3. Iteration Based on Feedback

### 3.1 Common Issues & Fixes

| Issue | Root Cause | Fix |
|-------|-----------|-----|
| Users don't respond to onboarding | Too many questions at once | Reduce to 3–4 questions; ask rest later |
| Routine extraction fails | Claude misunderstands regional language | Fine-tune prompt with examples |
| Drift alerts too frequent | Threshold too sensitive | Increase from 5 to 7+ |
| Caregivers overwhelmed | Sending too many alerts | Filter to only "high confidence" drifts |
| Low adoption after week 1 | Unclear value; friction in confirmation | Simplify confirmation (just "done ✓") |

### 3.2 A/B Testing Candidates

**Onboarding messaging:**
- Version A: "Hi! Let's set up your routine..." (formal)
- Version B: "Hey! Tell me about your day..." (casual)
→ Measure completion rate, time to complete

**Reminder format:**
- Version A: "⏰ Time for BP Medicine" (short)
- Version B: "Good morning! It's 8 AM—time for your BP medicine. Reply ✓ when done." (detailed)
→ Measure confirmation rate

**Alert threshold:**
- Version A: Alert caregiver on drift > 5 (sensitive)
- Version B: Alert caregiver on drift > 7 (conservative)
→ Measure alert usefulness, caregiver satisfaction

---

## 4. Metrics That Matter

### 4.1 North Star Metric: Routine Adherence Improvement

For each user, track:

```
Adherence % = (Confirmed tasks / Total reminded) × 100

Example:
Week 1: 70% (14/20 reminders confirmed)
Week 2: 85% (17/20 reminders confirmed)
→ +15% improvement
```

**Target for MVP:** Users improve adherence by 20–30% after 2 weeks.

### 4.2 Secondary Metrics

| Metric | Target | Why |
|--------|--------|-----|
| Onboarding completion | >80% | Product-market fit signal |
| Weekly active users | >60% of cohort | Engagement |
| Drift detection accuracy | >80% | Core feature working |
| Caregiver satisfaction | >70% NPS | Secondary user satisfied |
| Retention (day 7) | >70% | Not a fad |
| Retention (day 30) | >50% | Real value |

### 4.3 Qualitative Feedback (Weekly Survey)

```
1. "Sahaay has reduced my stress about remembering medicine"
   (Strongly disagree / Disagree / Neutral / Agree / Strongly agree)

2. "I would recommend Sahaay to a friend"
   (Yes / Maybe / No) → Use for NPS

3. "What's one thing that annoyed you this week?"
   (Free text)

4. "What's one thing that worked really well?"
   (Free text)
```

---

## 5. Scaling from Beta to 500 Users

### 5.1 Self-Service Signup (Week 5)

Once MVP is stable:

1. Create simple landing page
```
"Sahaay: Never Forget Your Medicine Again"

✓ Simple 5-minute setup
✓ Personalized reminders
✓ Peace of mind for family

Get Started: [Send "Hi" to WhatsApp link]
```

2. Share link to:
   - Your personal network
   - Caregiver Facebook groups
   - Reddit ADHD communities
   - WhatsApp groups

3. Measure viral coefficient:
   - % of users who invite friends
   - # of invites per user
   - If >20% invite 1+ friend → viral loop exists

### 5.2 Paid Acquisition (Week 7, if PMF found)

Once confirmed product-market fit (70%+ retention, NPS >40):

| Channel | Cost | Notes |
|---------|------|-------|
| Facebook ads (to caregivers) | $200–500 | Target: "caregiver," "elderly parent," "reminder" |
| Google ads (to seniors) | $100–300 | "medicine reminder," "I keep forgetting medicine" |
| Influencer partnerships | $500–1000 | ADHD advocates, caregiver influencers |
| Affiliate program | CPA model | Partner with healthcare apps |

**Target CAC (Customer Acquisition Cost):** ₹100–200 (~$1.25–2.50)

---

## 6. Addressing Safety & Trust

### 6.1 Privacy by Design

**What users care about:**
- "Will you sell my data?" → No. Clear privacy policy.
- "Who can see my medicines?" → Only you + caregivers you approve.
- "What if my WhatsApp is hacked?" → Same risk as your photos/messages.

**Transparency measures:**
- Publish privacy policy (in simple Hindi/Gujarati)
- Show users what data Sahaay stores (clear dashboard)
- Allow data export/deletion anytime
- No ads, no data selling (ever)

### 6.2 Medical Liability

**Position as:** "Lifestyle assistant" not "medical device"

**Clear disclaimers:**
- "Sahaay is not a doctor. If you have medical concerns, see a doctor."
- "Sahaay reminds; it doesn't diagnose or treat."
- "Tell your doctor you're using Sahaay."

**In conversations:**
```
If user says "I have chest pain":
Sahaay: "That sounds serious. Please call your doctor or go to the 
nearest hospital right now. I can't help with medical emergencies.
Stay safe! ❤️"
```

### 6.3 Trust-Building with Elderly Users

**Day 1–3:** Focus on proving value, not features

```
User: "How does this work?"
Sahaay: "Simple! I learn your routine from chatting, then remind you 
like a caring friend. No forms, no buttons—just talk to me."

[After first reminder is successfully confirmed]
Sahaay: "See? It worked! Tomorrow I'll remind you again. 
You can trust me. ✓"
```

**Week 2:** Introduce family involvement carefully

```
"Your daughter wants to help. If you agree, I can let her know 
if something's unusual (like you missing medicine). 
She won't see everything—just: 'All good' or 'Check on dad.'
Is that okay?"
```

---

## 7. Competitive Landscape & Positioning

### 7.1 Why Sahaay is Different

| Aspect | Existing Apps | Sahaay |
|--------|---------------|--------|
| **Onboarding** | Forms, settings | Talk naturally (5 min) |
| **Intelligence** | Passive reminders | Proactive anomaly detection |
| **For elderly** | App installation required | WhatsApp/voice (native) |
| **Caregiver integration** | Shares all data | Privacy-first summary |
| **Language** | English only | Multilingual from day 1 |
| **Cost** | $5–10/month | Free → ₹299/month (family) |

### 7.2 Positioning Statement

```
For: Elderly individuals, caregivers, ADHD adults
Who: Struggle with remembering medicines, bills, and daily tasks
Sahaay is: An AI companion that learns your routine and notices when 
something's wrong
Unlike: Reminder apps that burden users with setup
We deliver: Peace of mind for users + caregivers, through AI that 
understands their life.
```

---

## 8. Post-Launch: Monetization Plan

### 8.1 Pricing (After PMF Validation)

**Free Tier:**
- 1 user profile
- 3 routines
- Basic reminders
- Ad-supported dashboard
→ Conversion target: 20%

**Family Plan:** ₹299/month ($3.60)
- 5 user profiles (elderly parent + kids)
- Unlimited routines
- Caregiver dashboard
- Multi-language support
- Priority support
→ Target: 60% of users move here

**Care Provider Plan:** ₹999/month ($12)
- Up to 50 elderly residents
- Staff dashboard
- Analytics on adherence trends
- Integration with health apps
→ Target: Nursing homes, senior centers

### 8.2 Monetization Mechanics

**How to reduce friction from free → paid:**

1. **Free trial (14 days)** for paid features
   - No credit card to start
   - Reminder: "Your trial ends in 3 days"

2. **Freemium upsell triggers**
   - Trying to add 4th routine: "Upgrade to Family plan for unlimited"
   - Share with caregiver: "Caregiver dashboard needs Family plan"

3. **Payment methods**
   - In-app (via Razorpay/PayU)
   - Bank transfer (for older users)
   - Caregiver pays for parent's plan

---

## 9. Long-Term Vision (Year 2+)

### 9.1 Feature Roadmap

**Q1 (Months 10–12):**
- Family group routines (coordinate across siblings)
- Health provider integration (sync with medical records)
- Advanced analytics (trends, patterns for doctors)

**Q2–Q3 (Year 2):**
- Insurance partnerships (subsidize for high-risk elderly)
- SMS + IVR support (for non-smartphone users)
- Smartwatch integration
- Offline mode (for low-connectivity areas)

**Q4+ (Year 2):**
- Government partnerships (ICDS, ASHA worker integration)
- Predictive health alerts (beyond routine drift)
- Cross-cultural expansion (Southeast Asia, Middle East)

### 9.2 Revenue Projections (Year 2)

| Segment | Users | Avg Price | Annual |
|---------|-------|-----------|--------|
| Elderly (free) | 30,000 | ₹0 | ₹0 |
| Families (paid) | 15,000 | ₹3,000 | ₹4.5 crore |
| Care providers (paid) | 20 | ₹12,000 | ₹24 lakhs |
| **Total** | **45,000** | - | **₹4.74 crore (~$570K)** |

---

## 10. Key Partnerships to Pursue

| Partner | Why | Approach |
|---------|-----|----------|
| **HelpAge India** | Reach + credibility | Co-market to members |
| **Caregivers community (Aasra)** | Target audience | Advisory board + referrals |
| **Geriatric clinics** | Health endorsement | Integration + referrals |
| **ADHD India communities** | Segment expansion | Testimonials + partnerships |
| **Insurance companies** | Sustainability | Bundling for elderly plans |
| **ASHA workers** | Government reach | Deploy via health workers |

---

## 11. Launch Timeline

| Timeline | Milestone | Success Criteria |
|----------|-----------|------------------|
| **Week 1–2** | Problem validation interviews (20 users) | >70% confirm problem; strong quotes for pitch |
| **Week 3–4** | MVP launch with 30 beta users | >80% onboarding completion; zero critical bugs |
| **Week 5–6** | Iterate based on feedback; scale to 100 users | >60% weekly active; NPS >40 |
| **Week 7–8** | Scale to 500 users; measure PMF metrics | >70% retention (day 7); adherence +20% |
| **Month 3** | Public launch; paid model (freemium) | 1,000+ users; 20%+ conversion |
| **Month 6** | Scale to 5,000+ users; partnership pipeline | 5,000+ users; 3+ partnerships active |

---

## 12. Communication Playbook

### For Elderly Users:
```
Voice:
- Warm, encouraging, never technical
- Celebrate small wins ("Great job remembering today!")
- Use their language (not English)
- Respect their time (don't spam)

Sample message:
"Good morning, Rajesh! ☀️ 
Time for your BP medicine? Just reply 'done' or 'not yet.' 
No need to be perfect—I'm here to help. 💚"
```

### For Caregivers:
```
Voice:
- Efficient, clear, data-driven
- Respect their time (summaries, not details)
- Empower them to help (clear actions)
- Build trust slowly

Sample message:
"Weekly update for your mom:
✓ Medicine: 95% adherence (great job!)
⏳ Bills: Paid electricity; water pending
🔔 Alert: Missed morning routine Wed + Thu—followed up with her
[Action: Click if you want to call her]"
```

### For ADHD Adults:
```
Voice:
- Non-judgmental, encouraging
- Celebrate effort, not perfection
- Gentle nudges, not harsh reminders
- Offer flexibility

Sample message:
"Hey! I know you wanted to take your meds this morning. 
It's 2 PM now. No judgment—just checking in. 
Still want to take it? Or reschedule for tomorrow? 💙"
```

---

## 13. Failure Modes & Contingency

**If onboarding completion <50%:**
- Simplify to 3 questions only
- Add video walkthrough
- Offer human help (WhatsApp support)

**If drift detection accuracy <70%:**
- Collect more data (slow rollout)
- Hand-tune thresholds per user
- Combine with manual caregiver input

**If retention <40% (day 7):**
- Add gamification (streaks, badges)
- Increase reminder frequency
- Offer free support calls

**If adoption stalls at 500 users:**
- Double down on partnerships (NGOs, clinics)
- Paid acquisition on Facebook (test ads)
- Reduce pricing (₹99/month → ₹49/month)

---

## Conclusion

This plan takes Sahaay from MVP to product-market fit in 8 weeks, with clear metrics for success at each stage. **The key is to talk to real users constantly**—let their feedback drive the roadmap, not your assumptions.

Start with problem validation. Build small. Iterate fast. Scale when you have evidence of real value.

Good luck! 🚀
