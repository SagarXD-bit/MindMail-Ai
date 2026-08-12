# Task: Build MailMind AI — Full Application

## Files to Create
### Backend (`/workspace/backend/`)
- `requirements.txt`, `app/__init__.py`, `app/main.py`, `app/config.py`, `app/database.py`
- `app/models.py`, `app/schemas.py`, `app/crypto.py`
- `app/ai_service.py`, `app/imap_service.py`, `app/smtp_service.py`, `app/seed_data.py`
- `app/routers/` — health, settings, accounts, emails, replies, follow_ups, analytics
- `tests/` — pytest tests for API + AI fallback

### Frontend (`/workspace/frontend/`)
- `package.json`, `vite.config.ts`, `tsconfig.json`, `tailwind.config.js`, `postcss.config.js`, `index.html`
- `src/main.tsx`, `src/App.tsx`, `src/index.css`, `src/types.ts`
- `src/api/client.ts`, `src/api/*.ts`
- `src/components/` — Layout, Sidebar, Toast, ConfirmDialog, EmailListItem, etc.
- `src/pages/` — Dashboard, Inbox, EmailDetail, FollowUps, Analytics, Settings
- `src/hooks/` — react-query hooks

## Acceptance Criteria

### Infrastructure
- [ ] Backend runs on :8000 via `uvicorn`, registered as background service.
- [ ] Frontend built and served on :3000 via `serve`, registered as background service.
- [ ] Caddy reverse-proxies `/api/*` → :8000 and `/` → :3000.
- [ ] All env vars via backend env-keys tool; no hardcoded creds.
- [ ] DB migrations apply on setup; seed data loads on first run.

### Backend API
- [ ] `GET /api/health` returns `{status: "ok"}`.
- [ ] `POST /api/sync` fetches demo emails if no IMAP account, or real IMAP if configured.
- [ ] `GET /api/emails` supports search, category/urgency/status/follow-up filters, sort, pagination.
- [ ] `GET /api/emails/{id}` returns email + classification + replies + follow-ups.
- [ ] `PATCH /api/emails/{id}/classification` updates category/urgency, records feedback.
- [ ] `POST /api/emails/{id}/replies` generates AI reply in requested tone.
- [ ] `PATCH /api/emails/{id}/replies/{rid}` edits / marks used / discards.
- [ ] `POST /api/emails/{id}/send` sends reply via SMTP (requires confirm flag).
- [ ] `GET/POST/PATCH/DELETE /api/follow-ups` full CRUD + complete/snooze.
- [ ] `GET /api/analytics` returns all required metrics + distributions.
- [ ] `GET/PUT /api/settings` persists user prefs.
- [ ] AI service gracefully falls back to rule-based if OpenAI unavailable.

### Frontend
- [ ] Sidebar navigation: Dashboard, Inbox, Follow-ups, Analytics, Settings.
- [ ] Dashboard: KPI cards, urgent emails, pending replies, upcoming follow-ups, recent emails, category chart, quick actions.
- [ ] Inbox: list with search, filters (category/urgency/status/follow-up), sort; refresh/sync button.
- [ ] Email Detail: full content, metadata, AI confidence, suggested replies (3 tones), follow-up controls.
- [ ] Follow-ups: create, complete, snooze, overdue/upcoming views.
- [ ] Analytics: charts (by category, by urgency), response metrics, avg response time, AI accuracy, reply usage.
- [ ] Settings: IMAP config, AI prefs, default tone, categorization prefs, notifications, privacy.
- [ ] Loading/empty/error states on all pages.
- [ ] Toast notifications for actions.
- [ ] Confirmation dialogs for send/delete.
- [ ] Responsive (desktop + mobile).

### Security & Privacy
- [ ] No credentials in frontend code or API responses.
- [ ] Email passwords encrypted at rest (Fernet).
- [ ] Never auto-send replies without explicit confirmation.
- [ ] All secrets via env vars.

### Demo Mode
- [ ] Seeded with realistic emails across all 11 categories and 4 urgency levels.
- [ ] Demo data clearly flagged (is_demo badge).
- [ ] Full workflow demonstrable: sync → categorize → reply → follow-up → analytics.

## Tests
- pytest: API endpoints, AI fallback categorization, email parsing, analytics aggregation.
- Playwright (tester): navigation, inbox filters, email detail, reply generation, follow-up create/complete, analytics render.
