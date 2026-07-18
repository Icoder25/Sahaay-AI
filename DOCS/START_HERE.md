# Sahaay Documentation

Sahaay v1.0 is a responsive web care platform for families and elderly loved ones. It is not a WhatsApp/Twilio bot.

## Source of truth

[Sahaay_Real_PRD.md](Sahaay_Real_PRD.md) is the canonical product requirements document. It defines:

- Next.js web experience;
- FastAPI `/api/v1` backend;
- Supabase Auth and Postgres with RLS;
- Redis/Celery scheduling;
- FCM and in-app notifications;
- Claude, Exa, and ElevenLabs;
- families, elders, reminders, wellness, health scores, dashboards, summaries, SOS, analytics, and three-language support.

If another document conflicts with it, follow the PRD.

## Important rebuild boundary

The backend rebuild replaces the anonymous session/demo architecture with authenticated, family-scoped care workflows. The existing `frontend/` is unchanged by this rebuild; backend contracts are built to support it without redesigning frontend code.

## Documents

1. **[Sahaay_Real_PRD.md](Sahaay_Real_PRD.md)**
   Product vision, roles, complete MVP scope, data model, architecture, security, metrics, and acceptance.

2. **[Sahaay_User_Journeys.md](Sahaay_User_Journeys.md)**
   Family setup, elder day, reminders, escalation, AI, health trends, multi-elder privacy, and SOS.

3. **[Sahaay_Implementation_Guide.md](Sahaay_Implementation_Guide.md)**
   Runtime architecture, setup, authorization, API domains, worker commands, integrations, tests, and deployment.

4. **[Sahaay_30Day_Launch_Checklist.md](Sahaay_30Day_Launch_Checklist.md)**
   Four-week path from security foundation to a closed beta and release gate.

5. **[Sahaay_GTM_and_Research.md](Sahaay_GTM_and_Research.md)**
   Narrow launch segment, interviews, beta phases, evidence standards, trust, metrics, and pricing research.

6. **[Sahaay_Pitch_Deck_Outline.md](Sahaay_Pitch_Deck_Outline.md)**
   Ten-slide web-first story with explicit safeguards against presenting projections as traction.

7. **[Sahaay_Quick_Reference.txt](Sahaay_Quick_Reference.txt)**
   One-page product, stack, safety, commands, and reading order.

8. **[../README.md](../README.md)**
   Repository architecture and developer quickstart.

## Recommended reading paths

**Product/design:** PRD → User Journeys → GTM/Research
**Engineering:** PRD sections 5–8 → Implementation Guide → root README
**Beta operations:** Launch Checklist → User Journeys → GTM/Research
**Pitching:** PRD summary → Pitch Deck → Quick Reference

## Terminology

- **Reminder:** recurring care instruction.
- **Occurrence/completion:** one due instance and its outcome.
- **Activity:** durable event shown in the timeline.
- **Health score:** explainable daily routine/wellness indicator, not a diagnosis.
- **Escalation:** family notification after configured evidence or repeated miss.
- **SOS:** elder-triggered urgent family alert; not emergency-service dispatch.
- **In-app notification:** durable product record independent of push delivery.

## Evidence rules

Older materials contained useful qualitative insights alongside projected traction, market, and financial numbers. Current documents preserve compatible insights but treat targets as hypotheses. Before external publication:

- cite market facts;
- label projections;
- report only measured traction;
- obtain permission for quotes;
- avoid clinical outcome claims.

## Start now

1. Read the canonical PRD.
2. Configure local backend services using the Implementation Guide.
3. Verify authentication and family isolation.
4. Complete the end-to-end reminder, wellness, summary, and SOS journeys.
5. Use the 30-Day Checklist for beta readiness.
