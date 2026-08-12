# MailMind AI — Specification

## Overview
AI Email Automation Tool. Connects to email (IMAP), categorizes incoming emails by type & urgency via AI, generates context-aware reply suggestions, tracks follow-ups, and shows response analytics.

## Tech Stack
- **Frontend:** React 18 + Vite + TypeScript, Tailwind CSS, Recharts, React Router, TanStack Query, lucide-react, react-hot-toast
- **Backend:** Python FastAPI + SQLAlchemy 2.0 + Pydantic v2 + PyMySQL
- **Database:** MySQL (auto-provisioned)
- **AI:** OpenAI-compatible API (structured JSON: categorization + replies)
- **Email:** IMAP via imaplib + email parsing; Demo Mode fallback

## Key Decisions
- Single-tenant app (one primary user/email account) — all tables scoped by user_id.
- Demo Mode seeded with realistic emails across all categories/urgencies. AI processes live so full workflow is demonstrable.
- Email account passwords stored encrypted (Fernet) in DB; encryption key from env.
- AI returns structured JSON (category, urgency, confidence, explanation) for categorization; tone-based reply text for replies.
- Never auto-send replies — all sends require explicit user confirmation.
- Frontend served as built static assets; Caddy reverse-proxies `/api/*` to FastAPI.

## Categories (11)
Work, Personal, Customer Support, Sales, Finance, Meeting, Application/Recruitment, Newsletter, Notification, Spam, Other

## Urgency Levels (4)
Critical, High, Medium, Low

## Reply Tones
Professional, Friendly, Concise
