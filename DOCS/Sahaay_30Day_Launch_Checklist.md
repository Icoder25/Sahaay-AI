# Sahaay v1.0 – 30-Day Launch Checklist

Goal: validate a secure web-first care loop with a small family/elder cohort. The existing Next.js frontend is unchanged during the backend rebuild.

## Week 1 — Foundation and safety

- [ ] Confirm [Sahaay_Real_PRD.md](Sahaay_Real_PRD.md) as scope.
- [ ] Map every existing Next.js screen to `/api/v1` contracts; do not redesign the frontend.
- [ ] Configure separate local/staging Supabase and Firebase projects.
- [ ] Apply and verify the complete web-first migration.
- [ ] Enable RLS on every public table and test with two isolated families.
- [ ] Configure Supabase Auth email verification and password reset.
- [ ] Start FastAPI, Redis, Celery worker, and Celery beat.
- [ ] Verify optional Claude, Exa, ElevenLabs, and FCM integrations fail safely.
- [ ] Approve medical-safety wording, privacy notice, consent, and SOS disclaimer.
- [ ] Recruit 5–10 elder/family pairs; obtain explicit research consent.

**Exit:** authentication, family isolation, health checks, and local processes work.

## Week 2 — Complete the care loop

- [ ] Owner creates family, invites member, and creates an elder.
- [ ] Reminder CRUD supports medicine, meals, sleep, appointments, and recurrence.
- [ ] Due occurrence triggers persisted in-app notification and FCM attempt.
- [ ] Elder can complete, skip, and snooze without duplicate updates.
- [ ] Missed reminders follow up and escalate at the configured threshold.
- [ ] Calendar and activity timeline show the same source events.
- [ ] Daily wellness answers are stored and visible to authorized users.
- [ ] Health score is deterministic, explainable, and handles missing data.
- [ ] Family and elder dashboards return complete aggregates.
- [ ] SOS create, notify, acknowledge, and resolve work end to end.

**Exit:** a test family can complete one full day and review it.

## Week 3 — AI, notifications, and reliability

- [ ] Claude conversation works in English, Hindi, and Gujarati.
- [ ] Exa-grounded answers display citations.
- [ ] Medical advice and emergency prompts pass safety tests.
- [ ] ElevenLabs audio is optional and does not block text chat.
- [ ] Device registration, token refresh, revocation, and invalid-token cleanup work.
- [ ] FCM transient errors retry without duplicate notification records.
- [ ] Evening summary and daily health-score jobs run at elder timezone.
- [ ] Audit logs cover membership, sensitive reminder, and SOS actions.
- [ ] Run automated auth/RBAC, recurrence, dashboard, AI mock, FCM mock, and SOS tests.
- [ ] Run Supabase security/performance advisors and resolve launch-critical findings.

**Exit:** scheduled jobs are observable, idempotent, and safe.

## Week 4 — Closed beta

- [ ] Onboard 5–10 consented households.
- [ ] Test on desktop and mobile browsers with push allowed and denied.
- [ ] Observe setup without coaching; record confusion, not credentials or private notes.
- [ ] Review errors and delivery failures daily.
- [ ] Interview elder and family participants separately.
- [ ] Measure reminder completion, wellness completion, dashboard understanding, push delivery, escalations, and SOS drill response.
- [ ] Classify every alert as useful, late, noisy, or unsafe.
- [ ] Fix critical privacy, access, duplicate-delivery, or medical-safety issues immediately.
- [ ] Document validated findings separately from projections.
- [ ] Decide: expand, iterate, or stop based on evidence.

**Exit:** no critical security/safety defects and clear evidence about user value.

## Release gate

- [ ] Cross-family access is denied by API and RLS.
- [ ] Removed members lose access.
- [ ] Secrets are absent from source and browser bundles.
- [ ] Production CORS is restricted.
- [ ] Database backups and restore procedure are tested.
- [ ] FCM failure preserves in-app notifications.
- [ ] Reminder and SOS retries are idempotent.
- [ ] Health score components are explainable.
- [ ] AI never diagnoses or changes medication instructions.
- [ ] Data deletion/export ownership is defined.
- [ ] Monitoring covers API, workers, queue depth, scheduled jobs, and delivery failures.
- [ ] Support and incident contacts are published.

## Beta success criteria

- onboarding completion above 80%;
- no family-isolation or consent failures;
- at least 95% of generated notifications persisted;
- improving useful push-delivery rate;
- day-7 retention target above 70%;
- measurable reminder adherence improvement;
- families answer the five core care questions within 30 seconds;
- elders report feeling supported rather than watched.

Targets are hypotheses until the beta validates them.
