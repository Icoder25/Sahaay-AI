# Sahaay – AI Care Companion for Elderly

**Version:** 1.0 (MVP)
**Status:** Canonical product requirements
**Product:** Responsive web application
**Frontend:** Next.js (unchanged by the backend rebuild)
**Backend:** FastAPI
**Data and identity:** Supabase Auth + Supabase Postgres
**Notifications:** Firebase Cloud Messaging (FCM) + in-app notifications
**AI:** Claude, Exa, and ElevenLabs

This document is the product source of truth. Supporting documents must defer to it when scope or terminology differs.

## 1. Product summary

Sahaay helps families care for elderly loved ones from a distance. It combines reminders, conversational check-ins, routine monitoring, health indicators, emergency alerts, and family dashboards. The goal is not surveillance or diagnosis: it is independence for the elder and timely, understandable signals for approved family members.

**Vision:** Make distance irrelevant through AI-powered companionship, intelligent reminders, and proactive care insights.

**Core promise:** A family member should be able to open Sahaay and understand within 30 seconds:

- whether today's medicines and meals were completed;
- how the elder is feeling;
- whether their routine has changed;
- what is upcoming; and
- whether attention is needed now.

## 2. Problem and research basis

Older adults managing medicines, meals, sleep, appointments, and bills can miss tasks even when they are motivated. Adult children compensate with repeated calls and messages, creating anxiety and relationship strain. Traditional reminder tools still require the user to configure and manage the system.

Existing research in this repository remains directionally useful:

- medication adherence and routine recall are high-frequency problems;
- caregivers want exceptions and summaries, not constant notifications;
- elders value autonomy, simple language, and non-judgmental interactions;
- trust requires consent, clear data access, and reliable escalation;
- English, Hindi, and Gujarati are important initial languages.

Research claims, quotes, market sizes, and traction figures must be labeled as validated, sourced, or projected before external use.

## 3. Users and roles

### Owner

Creates a family, invites members, manages elder profiles, assigns reminders, and controls membership and permissions.

### Family member

Views authorized dashboards and history, creates or assigns reminders, receives configured alerts, and responds to SOS or escalations.

### Elder

Views a simplified dashboard and calendar, completes reminders, answers wellness questions, chats with the companion, controls language preferences, and triggers SOS.

Professional caregivers and clinicians are future roles, not MVP roles.

## 4. Product principles

- **Support, not surveillance:** show useful care signals with elder consent.
- **Simple by default:** large controls, plain language, minimal navigation.
- **Exceptions over noise:** notify family when action is useful.
- **Explainable indicators:** health scores identify contributing factors.
- **Non-diagnostic AI:** supportive guidance only; emergencies route to people and local services.
- **Secure family boundaries:** every read and write is authenticated and family-scoped.
- **Web-first:** Next.js is the product interface; WhatsApp and Twilio are not MVP dependencies.

## 5. MVP requirements

### 5.1 Authentication and profiles

- Email/password registration and login through Supabase Auth.
- Email verification, password reset, access-token refresh, and logout.
- FastAPI validates Supabase JWTs through JWKS.
- User profile includes name, avatar, locale, and timezone.
- Audit security-sensitive membership, reminder, and SOS actions.

### 5.2 Family management and RBAC

- Create and rename a family.
- Invite members by email; accept, decline, expire, or revoke invitations.
- List and remove members; change permitted roles.
- Enforce Owner, Family Member, and Elder permissions in both FastAPI and Postgres RLS.
- Keep data isolated between families.

### 5.3 Elder profiles

- Create and manage one or more elders per family.
- Store photo, date of birth or age, gender, emergency contact, medical notes, preferred language, and timezone.
- Link an elder profile to a user account when the elder signs in.
- Restrict sensitive notes to authorized family members and the elder.

### 5.4 Reminders, completion, and calendar

- Reminder types: medicine, meal, sleep, appointment, and other routine.
- Store title, description, note, local time, timezone, recurrence rule, start/end dates, assignee, creator, status, and escalation threshold.
- Create, read, update, pause, and delete reminders.
- Record each due occurrence and completion independently.
- Support completion, skip, miss, snooze, and idempotent updates.
- Show past and upcoming occurrences in day/week/month calendar queries.
- Escalate repeated misses to approved family members.

Reminder workflow:

1. A scheduled worker creates or finds the due occurrence.
2. FCM and an in-app notification are sent.
3. The elder can complete or snooze it.
4. A follow-up is sent when configured.
5. After the threshold, family members receive an actionable alert.
6. Delivery and user actions appear in the activity timeline.

### 5.5 AI care companion

- Maintain elder-scoped conversations and messages.
- Start check-ins and answer in English, Hindi, or Gujarati.
- Remember approved preferences, common responses, schedules, and reminder behavior.
- Follow up on reminders and wellness responses.
- Produce daily summaries, weekly insights, and risk signals.
- Use Claude for conversation and structured extraction.
- Use Exa for web-grounded informational answers with visible citations.
- Use ElevenLabs for optional spoken replies; voice is an enhancement and must fail safely when credentials are absent.
- Never diagnose, prescribe, alter medication instructions, or claim certainty about health.

### 5.6 Daily wellness

Capture a brief daily check-in:

- mood;
- sleep quality;
- breakfast or meal status;
- pain or discomfort;
- hydration; and
- optional note.

Responses feed summaries and deterministic health scoring. Concerning answers should suggest contacting family or professional help; emergency symptoms should show an urgent safety message.

### 5.7 Routine and risk signals

Detect sustained changes such as:

- missed medicines or meals;
- late waking or irregular sleep;
- reduced activity or interaction;
- worsening mood or pain; and
- repeated ignored reminders.

Signals must include the observed evidence, confidence or severity, and recommended family action. One isolated event should not be presented as a medical conclusion.

### 5.8 Activity timeline

Persist and display reminder delivery/completion, wellness checks, conversations, alerts, appointments, summaries, and SOS events. Family views must be filterable by elder, date, and event type.

### 5.9 Health score

Generate an explainable 0–100 daily score using deterministic inputs:

- medicine adherence;
- meal completion;
- sleep and wellness responses;
- activity/interaction;
- overall reminder adherence.

Store component values with the total. Show trends, not diagnoses. Missing data must be distinguished from poor health.

### 5.10 Dashboards and analytics

**Family dashboard**

- multiple-elder overview;
- current health score and trend;
- today's completed, pending, and missed tasks;
- missed medicines and upcoming appointments;
- activity timeline, AI insights, daily summary, calendar, and alerts;
- notification and SOS status.

**Elder dashboard**

- large, accessible controls;
- today's tasks and calendar;
- companion chat and optional audio;
- health score with simple explanation;
- upcoming reminders;
- persistent SOS action;
- language switcher.

**Analytics**

- reminder and medicine adherence;
- wellness and health-score trends;
- completion response times;
- notification delivery;
- dashboard engagement and SOS response time.

### 5.11 Notifications and devices

- Register, refresh, and revoke FCM device tokens.
- Persist every notification and delivery state.
- Types: reminder, family alert, SOS, appointment, daily summary, and emergency.
- Retry transient delivery failures through Celery.
- Preserve in-app notifications when Firebase credentials are absent or a push fails.
- Allow users to configure non-critical notification preferences.

### 5.12 SOS

- A prominent elder-facing SOS control.
- One action creates a durable alert, activity, audit entry, and immediate family notification fan-out.
- Family members can acknowledge and resolve it with timestamps.
- Retries are idempotent and must not create duplicate incidents.
- Clearly state that Sahaay does not replace local emergency services.

### 5.13 Daily summary

Generate an evening summary per elder containing medicine and meal completion, mood/wellness, health score, important exceptions, and tomorrow's appointments. Persist it and notify configured family members.

## 6. Data model

The web-first schema contains:

- `profiles`
- `families`, `family_members`, `invitations`
- `elder_profiles`
- `reminders`, `reminder_completions`
- `activities`, `wellness_checks`
- `ai_conversations`, `ai_messages`
- `device_tokens`, `notifications`
- `health_scores`
- `sos_alerts`
- `audit_logs`

Use UUID primary keys, `timestamptz`, foreign keys and supporting indexes, constrained status/type values, update triggers, and RLS on every public table. Authorization helpers belong in a private schema.

## 7. Technical architecture

```text
Next.js responsive web app (existing frontend; unchanged in rebuild)
        │ HTTPS + Supabase bearer token
        ▼
FastAPI /api/v1
  ├─ auth/profile/family/elder APIs
  ├─ reminders/calendar/activity/wellness
  ├─ dashboards/analytics/health scores/SOS
  ├─ Claude + Exa + ElevenLabs services
  └─ FCM notification service
        │
        ├─ Supabase Auth
        ├─ Supabase Postgres + RLS
        └─ Redis → Celery workers/beat
```

FastAPI is the application boundary; clients must not receive service-role credentials. Provider integrations remain disabled safely when unconfigured.

## 8. Security and privacy

- HTTPS in deployed environments.
- Supabase-issued JWTs; no custom password storage.
- RBAC in FastAPI and defense-in-depth RLS in Postgres.
- Explicit family membership and elder consent.
- Secrets only in environment or secret managers.
- Audit logs for privileged actions.
- Data export/deletion and retention policy before public launch.
- No selling health or behavioral data.
- Validate rate limits, CORS allowlists, input size, and file uploads before production.

## 9. Success metrics

MVP KPIs:

- daily active elders;
- onboarding and family-invite completion;
- reminder and medicine completion rate;
- wellness and AI conversation completion;
- family dashboard visits;
- average health score and data completeness;
- FCM delivery and retry success;
- SOS acknowledgment time;
- day-7 and day-30 retention;
- caregiver confidence and elder comfort.

Initial product targets are hypotheses: onboarding >80%, day-7 retention >70%, useful notification delivery >95%, and measurable adherence improvement. Beta research must validate them.

## 10. Non-goals

- Clinical diagnosis, treatment, or medication decisions.
- Continuous biometric monitoring.
- Doctor or care-provider portals.
- Wearables, smart-home integrations, or native mobile apps.
- WhatsApp/Twilio as the primary product channel.
- Fully autonomous emergency response.

## 11. Delivery and acceptance

The MVP is accepted when:

- authenticated families cannot access one another's data;
- an owner can invite family and configure an elder;
- reminder delivery, completion, escalation, and calendar work end to end;
- wellness, activity, health score, and summaries appear on dashboards;
- AI chat is multilingual and safely grounded;
- FCM degrades to persisted in-app notifications;
- SOS reaches authorized family and can be acknowledged;
- automated tests cover auth/RBAC and critical care workflows.

## 12. Roadmap

**MVP:** all requirements in section 5.

**Phase 2:** speech-to-text, richer ElevenLabs voice conversations, smarter memory and routine prediction, and richer analytics.

**Phase 3:** professional caregiver and doctor portals, wearables, medication analytics, smart-home integrations, and additional platforms/channels.

## 13. Key risks

| Risk | Mitigation |
|---|---|
| Elders ignore reminders | Conversational follow-up, configurable repetition, proportionate family escalation |
| Push delivery fails | Persist in-app notification, retry FCM, monitor delivery state |
| Family over-monitoring | Consent, least privilege, summaries, explicit access controls |
| AI hallucination | Narrow prompts, citations, deterministic scoring, medical safety boundaries |
| False risk signals | Explain evidence, require sustained patterns, collect feedback |
| Emergency ambiguity | Prominent local-emergency disclaimer and immediate human notification |
