# Sahaay v1.0 – Pitch Deck Outline

Use verified data only. Replace bracketed placeholders and label beta targets, projections, and research findings accurately.

## 1. The problem

**Headline:** Distance turns everyday care into recurring uncertainty.

- Did a parent take today's medicine?
- Did they eat and sleep normally?
- Are they feeling unwell?
- Does the family need to act now?

Reminder apps answer what was scheduled, not what happened or what needs attention.

## 2. The user

Primary buyer: an adult child caring remotely for an elderly parent.
Primary user: an elder who wants independence and a simple daily experience.

Show one sourced market statistic and one validated user story. Avoid unsourced market totals.

## 3. The solution

Sahaay is a responsive web platform that combines:

- reminders and calendar;
- daily wellness;
- multilingual AI companionship;
- activity and health-score trends;
- family dashboards and summaries;
- proportionate escalation and SOS.

**Positioning:** support for elders, clarity for families.

## 4. Product demo

Demonstrate one connected day:

1. Family owner creates an elder and medicine reminder.
2. Elder receives FCM/in-app reminder and completes it.
3. Elder answers a Hindi wellness check and talks to Sahaay.
4. Family dashboard updates the timeline and explainable health score.
5. Show a missed-reminder escalation and SOS acknowledgment.

Do not demo WhatsApp or Twilio as the product.

## 5. Why now and why different

- Families increasingly coordinate care across distance.
- Modern web push and AI make a lightweight companion feasible.
- Sahaay joins the elder and family experience instead of adding another isolated reminder list.
- Claude supports conversation; Exa grounds current information; ElevenLabs can make replies accessible; deterministic logic preserves score explainability.

The moat is trusted household workflow and longitudinal, consented context—not an LLM call alone.

## 6. Architecture and trust

```text
Next.js → FastAPI → Supabase Auth/Postgres
                  ├→ Redis/Celery → FCM
                  └→ Claude / Exa / ElevenLabs
```

- Supabase JWT, family RBAC, and RLS.
- Explicit membership and consent.
- Audit logs and durable notification/SOS records.
- Non-diagnostic AI with cited grounded answers.
- In-app fallback when push is unavailable.

State clearly: the backend rebuild leaves the existing Next.js frontend unchanged.

## 7. Validation

Report only actual evidence:

- interviews completed: `[n]`;
- activated households: `[n]`;
- onboarding completion: `[x%]`;
- medicine/reminder completion change: `[x]`;
- family dashboard comprehension: `[time/result]`;
- useful escalation rate: `[x%]`;
- day-7 retention: `[x%]`;
- elder comfort/caregiver confidence: `[finding]`.

Previous figures in older materials were projections and must not be represented as traction.

## 8. Go-to-market

1. Paired elder/family research.
2. Closed household beta.
3. Evidence cohort through caregiver communities.
4. Referral pilots with clinics, NGOs, and senior communities.

Start with families caring remotely; defer broad ADHD and professional-care markets.

## 9. Business model

Hypothesis:

- free trial or basic single-elder tier;
- paid family plan for members, summaries, trends, and escalation;
- future organization plan after consumer validation.

Show tested willingness-to-pay and real delivery costs before presenting unit economics. Pricing such as ₹299/month is a research candidate, not established fact.

## 10. Roadmap and ask

**MVP:** secure family care loop, reminders, wellness, AI, scores, dashboards, FCM, SOS, three languages.

**Phase 2:** richer voice, memory, routine prediction, and analytics.

**Phase 3:** clinician/professional caregiver portals, wearables, and smart-home integration.

Ask for the resources needed to achieve a measurable next milestone: `[households]`, `[retention]`, `[adherence]`, and `[safety/reliability gate]`.

## 30-second pitch

Sahaay helps families care for elderly loved ones from a distance. Its web app combines intelligent reminders, daily wellness, multilingual AI companionship, activity and health trends, and a shared family dashboard. Elders get simple support and remain in control; families receive summaries and alerts only when action is useful. Sahaay is built with Next.js, FastAPI, Supabase, FCM, and safely bounded AI.
