# MailMind AI — Scope

## In Scope
1. **Inbox & IMAP Integration** — configure account, secure fetch, refresh/sync, graceful failures, demo-mode fallback.
2. **AI Categorization** — category (11), urgency (4), confidence, explanation; manual override.
3. **Reply Engine** — professional/friendly/concise tones, edit, regenerate, copy, send-via-SMTP (confirm), discard.
4. **Follow-up Tracker** — create, date/time, notes, complete, snooze, overdue/upcoming views, AI-suggested follow-ups.
5. **Response Analytics** — totals, by category/urgency, response rates, avg response time, follow-up completion, AI accuracy, reply usage.
6. **Dashboard** — KPI cards, urgent emails, pending replies, upcoming follow-ups, recent emails, category chart, quick actions.
7. **Email Detail** — full content, metadata, AI confidence, replies, follow-up controls, conversation/thread history.
8. **Search & Filter** — sender/subject/content search, category/urgency/status/follow-up filters, sort options.
9. **Privacy & Security** — env-based secrets, encrypted password storage, no frontend credential exposure, confirm before send.
10. **UI/UX** — responsive SaaS design, sidebar nav, loading/empty/error states, toasts, confirmation dialogs.

## Out of Scope
- Real-time push notifications (websockets) — use polling + manual sync.
- Multi-account support (single primary account for v1).
- Calendar integration.
- Full OAuth email providers (Gmail/Outlook) — IMAP password auth only for v1.
- Mobile native apps (responsive web only).

## Phases
1. **Scaffold** — backend + frontend skeletons, env, DB models, migrations, seed data.
2. **Backend Services** — AI (categorize + replies), IMAP sync, analytics; full REST API.
3. **Frontend** — layout, dashboard, inbox, detail, follow-ups, analytics, settings.
4. **Integration & Verification** — Infrastructure Gate, reviewer + tester, fixes, final verification.
