# Sahaay v1.0 – Go-to-Market and Research

## Positioning

**For** families caring for elderly loved ones from another city or country, **Sahaay is** a web-based AI care companion that combines reminders, check-ins, routine signals, SOS, and a shared family dashboard. **Unlike** standalone reminder apps, it explains what happened and alerts approved family members when attention is useful.

Sahaay is a responsive Next.js application with FCM push—not a WhatsApp/Twilio product.

## Initial market

Start narrowly:

- adult children managing an independently living parent;
- elders who use a smartphone/browser with light assistance;
- households managing medicines plus at least one daily routine;
- English, Hindi, or Gujarati speakers.

ADHD, busy-family, professional-caregiver, and clinician use cases remain useful research context but are not the v1.0 launch focus.

## Research questions

1. Can a family configure useful care in under 15 minutes?
2. Can an elder understand and complete tasks without repeated coaching?
3. Does the dashboard reduce uncertainty in under 30 seconds?
4. Which misses deserve family escalation?
5. Does the elder feel supported rather than monitored?
6. Are health-score explanations understandable and trusted?
7. What happens when push permission or delivery fails?
8. Which household member will pay, and for what outcome?

## Recruitment

Recruit elder/family pairs through:

- personal networks and local resident groups;
- geriatric clinics and senior-living communities;
- caregiver communities and NGOs such as HelpAge India;
- multilingual community organizations.

Do not claim formal partnerships until agreements exist. Provide clear consent, withdrawal, data handling, and beta-risk information. Avoid recruiting participants who need clinical monitoring the MVP cannot provide.

## Interview guide

### Family member

- Walk me through the last time you worried about a parent's routine.
- What do you check, how often, and with whom?
- Which missed events require action? Which do not?
- What information would let you stop calling?
- Who should see medicines, notes, wellness, and AI conversations?
- Would a daily summary be useful? At what time?
- What would make a health score misleading?
- What would you pay to reduce this uncertainty?

### Elder

- How do you remember medicines, meals, and appointments today?
- Which reminders are helpful or annoying?
- Show me how you would complete, snooze, or find today's tasks.
- How should family be involved?
- Which language and text/audio style are easiest?
- How do you feel about wellness questions and routine trends?
- When would you press SOS?

Ask about real behavior before presenting Sahaay. Separate observed evidence from stated willingness.

## Beta phases

### Phase 1: problem and prototype research

- 10–15 family/elder interviews.
- Validate core questions, access expectations, and escalation rules.
- Test current Next.js flows with a clickable or staging build.

### Phase 2: closed beta

- 5–10 households for two weeks.
- Assisted setup once; then observe normal use.
- Daily technical review and twice-weekly participant check-ins.

### Phase 3: evidence beta

- 25–50 households for four to eight weeks.
- Compare baseline and in-product adherence.
- Segment results by push permission, language, and elder independence.

### Phase 4: partnership pilots

- Clinics, senior communities, and caregiver organizations.
- Define referral, consent, support, and outcome ownership before launch.

## Metrics

**Activation**

- verified account;
- family and elder created;
- member invited;
- first reminder scheduled and completed.

**Core value**

- medicine/reminder completion;
- wellness completion;
- family dashboard time-to-understanding;
- useful escalation rate;
- caregiver confidence and time saved;
- elder comfort and autonomy.

**Reliability**

- persisted notification rate;
- FCM delivery, retry, and invalid-token rate;
- scheduled-job lateness;
- duplicate occurrence/incident count;
- SOS acknowledgment time.

**Retention**

- elder day-7/day-30 activity;
- family dashboard return;
- active households and elders;
- reminders retained after four weeks.

## Safety and trust

- Obtain consent before sharing elder data with family.
- Show exactly who can access an elder.
- Do not expose raw AI conversation content by default where consent is unclear.
- Explain health-score components and missing data.
- Position Sahaay as supportive software, not a medical device or emergency service.
- Provide data export, deletion, notification controls, and an accessible privacy notice.

## Messaging

**Family:** “Know what needs attention without turning every call into a checklist.”

**Elder:** “Gentle help with your day, in your language, with you in control.”

Avoid unsupported claims about preventing hospitalization, diagnosing risk, or guaranteed adherence.

## Pricing hypothesis

Test before fixing prices:

- free trial for one elder and core reminders;
- family plan for multiple members, summaries, trends, and escalation;
- future organizational plan after the consumer workflow is validated.

The previous ₹299/₹999 tiers may be tested as hypotheses, not presented as validated economics.

## Launch decision

Expand only if:

- no critical security, consent, or safety failures;
- elders can complete the core flow;
- families understand the dashboard quickly;
- alerts are more useful than noisy;
- retention and adherence show repeat value;
- at least one repeatable acquisition channel emerges.

Otherwise iterate on the narrowest failing assumption before adding channels or features.
