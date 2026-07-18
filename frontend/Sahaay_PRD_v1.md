# Product Requirements Document (PRD)

# Sahaay – AI Care Companion for Elderly

**Version:** 1.0 (MVP)

**Status:** Draft

**Product Type:** AI-powered Digital Caregiving Platform

**Frontend:** Next.js

**Backend:** FastAPI

**Notifications:** Firebase Cloud Messaging (FCM)

**AI:** LLM-powered Care Companion

**Target Platform:** Responsive Web Application

---

## 1. Executive Summary

Sahaay is an AI-powered caregiving platform designed to help families remotely care for elderly loved ones. Unlike traditional reminder applications, Sahaay actively engages with seniors through intelligent conversations, personalized reminders, routine monitoring, and proactive health insights while keeping family members informed through a centralized dashboard.

## 2. Vision

> To make distance irrelevant by enabling families to care for elderly loved ones through AI-powered companionship, intelligent reminders, and proactive health insights.

## 3. Mission

Build a digital companion that reminds, listens, learns, encourages, and informs families instead of functioning as another notification app.

## 4. Problem Statement

Millions of elderly people live independently while their children work or study elsewhere. Existing reminder solutions do not provide companionship, routine understanding, proactive monitoring, or meaningful family insights.

## 5. Target Audience

### Primary
- Adult children living away from parents
- Working professionals
- Students
- NRIs

### Secondary
- Elderly living independently
- Families
- Future: caregivers and doctors

## 6. Unique Value Proposition

> Unlike reminder apps, Sahaay helps families remotely care for elderly loved ones instead of simply sending reminders.

## 7. Core MVP Features

- Email/password authentication
- Family management with invitations
- Elder profiles
- Medicine, meal, sleep, and appointment reminders
- AI companion with proactive conversations
- Daily wellness questions
- Activity timeline
- AI-generated health score
- Family dashboard
- Elder dashboard
- Calendar
- Firebase Cloud Messaging (FCM)
- SOS button
- English, Hindi, and Gujarati support

## 8. AI Features

- Proactive conversations
- Personalized memory
- Routine learning
- Missed reminder detection
- Health score generation
- Daily summaries
- Risk detection
- Family insights

## 9. Reminder Workflow

```text
Reminder Time
      ↓
Push Notification
      ↓
Website Notification
      ↓
AI Follow-up Conversation
      ↓
Task Completed?
      ↓
No → Repeat Reminder
      ↓
Threshold Reached
      ↓
Notify Family
```

## 10. High-Level Database

- User
- Family
- FamilyMember
- ElderProfile
- Reminder
- Activity
- WellnessCheck
- AIConversation
- Notification
- HealthScore

## 11. Tech Stack

### Frontend
- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui

### Backend
- FastAPI
- PostgreSQL
- SQLAlchemy
- Redis

### AI
- OpenAI API

### Notifications
- Firebase Cloud Messaging (FCM)

## 12. Roadmap

### MVP
- Core reminders
- AI companion
- Family dashboard
- Health score
- Activity tracking

### Phase 2
- Voice input/output
- Smarter AI memory
- Better analytics

### Phase 3
- Doctor portal
- Wearables
- Smartwatch support
- Smart home integrations

## 13. Success Criteria

A family member should be able to answer within 30 seconds:

- Did my parent take today's medicines?
- Did they eat?
- How are they feeling?
- Is anything unusual today?
- Do they need my attention?
