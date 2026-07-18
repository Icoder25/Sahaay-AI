# Sahaay v1.0 User Journeys

These journeys translate the canonical web-first PRD into observable product behavior. Names are representative personas; research quotes and outcome figures require validation before external use.

## 1. Family owner: Anjali sets up care

**Context:** Anjali lives in another city and wants visibility without calling her father about every task.

1. Anjali opens the responsive Next.js app and registers with email/password.
2. Supabase sends email verification; she signs in and creates the “Sharma Family.”
3. She creates Rajesh's elder profile with timezone, Hindi preference, emergency contact, and relevant notes.
4. She adds recurring BP medicine, meals, sleep, and an upcoming appointment.
5. She invites her brother as a Family Member.
6. The dashboard shows today's tasks, upcoming appointment, and “not enough data yet” instead of inventing a health trend.

**Success:** Setup is understandable, access is explicit, and Anjali can answer what is due today.

## 2. Elder: Rajesh completes his day

1. Rajesh signs in to a large, simplified elder dashboard.
2. At 8:00 AM, FCM and the in-app center show “Time for BP medicine.”
3. Rajesh taps **Done**. The occurrence, activity timeline, adherence, and family dashboard update once.
4. The morning wellness check asks about mood, sleep, breakfast, pain, and water in Hindi.
5. Rajesh answers with large controls and optionally adds a note.
6. His calendar shows lunch and the doctor's appointment without exposing family administration.

**Success:** Rajesh feels supported, not monitored; Anjali sees completion without making a check-in call.

## 3. Missed reminder and escalation

1. A medicine occurrence becomes due and is persisted before delivery.
2. FCM delivery fails temporarily; the notification remains visible in-app and a retry is queued.
3. Rajesh does not complete the reminder. At the configured interval, Sahaay sends one gentle follow-up.
4. After the escalation threshold, authorized family members receive: what was missed, when, prior follow-up state, and a suggested action.
5. Anjali contacts Rajesh and records the outcome; the alert becomes acknowledged/resolved.

**Success:** No duplicate incidents, no notification storm, and family receives an actionable exception.

## 4. AI companion and grounded guidance

1. Rajesh opens **AI Chat** and writes in Hindi.
2. Claude responds in Hindi using his approved preferences and recent routine context.
3. When he asks for current general wellness information, Exa supplies relevant sources and Sahaay shows citations.
4. If enabled, ElevenLabs provides an audio version.
5. If Rajesh asks whether to change a dose, Sahaay declines to prescribe and directs him to his doctor or caregiver.

**Success:** The answer is supportive, language-appropriate, transparent about sources, and medically bounded.

## 5. Daily summary and health trend

1. The scheduled worker calculates a deterministic daily health score from completed medicines/meals, wellness, activity, and data completeness.
2. It stores both the total and component values.
3. The evening summary states what happened, what was missed, how Rajesh reported feeling, and what is scheduled tomorrow.
4. Anjali sees a trend with an explanation such as “lower today because one medicine is pending and wellness was not answered.”

**Success:** The score helps interpretation without claiming diagnosis or treating missing data as illness.

## 6. SOS

1. Rajesh presses the persistent SOS button and confirms.
2. Sahaay immediately creates one durable SOS incident, timeline event, audit record, and family notification fan-out.
3. The screen tells Rajesh to contact local emergency services when immediate danger exists.
4. Anjali receives push and in-app alerts, acknowledges the incident, and calls him.
5. The family records resolution; timestamps support later review.

**Success:** Authorized family is alerted quickly, retries do not duplicate the incident, and Sahaay never implies it replaces emergency services.

## 7. Multiple elders and family privacy

1. Anjali switches between her parents from the family dashboard.
2. Each elder has separate reminders, wellness, conversations, scores, and timelines.
3. A member only sees families and elders granted by membership.
4. A signed-in user from another family receives no data, even if they guess an identifier.
5. Removing a member immediately removes API and database access.

**Success:** The interface scales to multiple elders while JWT, RBAC, and RLS preserve boundaries.

## 8. Important experience moments

- **First reminder:** delivery and completion must be fast and obvious.
- **First missing data:** explain “not enough information”; do not show a false low score.
- **First escalation:** include context and a clear next action.
- **First AI refusal:** remain warm while enforcing medical safety.
- **First family invite:** explain the recipient's access before acceptance.
- **Push disabled:** retain full in-app behavior and show how to enable notifications.

## 9. Journey metrics

- setup and invite completion;
- time to first elder and reminder;
- reminder completion and response time;
- wellness and AI conversation completion;
- notification delivery/retry rate;
- escalation usefulness and false-alert feedback;
- dashboard time-to-understanding;
- SOS acknowledgment time;
- elder comfort and caregiver confidence.
