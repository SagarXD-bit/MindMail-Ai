# MailMind AI — AI Email Automation Tool

AI-powered email automation that connects to your inbox, categorizes emails by type and urgency, generates context-aware reply suggestions, tracks follow-ups, and provides response analytics.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, TypeScript, Tailwind CSS, Recharts, TanStack Query |
| Backend | Python FastAPI, SQLAlchemy 2.0, Pydantic v2 |
| Database | MySQL |
| AI | OpenAI-compatible API (structured categorization + reply generation) |
| Email | IMAP via `imaplib` with Demo Mode fallback |

## Features

- **AI Email Categorization** — 11 categories, 4 urgency levels, confidence scores, explanations
- **AI Reply Engine** — Professional / Friendly / Concise tones, edit, regenerate, copy, send
- **Follow-up Tracker** — Reminders, snooze, complete, overdue tracking
- **Response Analytics** — Charts, response rates, avg response time, AI accuracy metrics
- **Dashboard** — KPI cards, charts, quick actions
- **Search & Filter** — By sender, subject, category, urgency, status, follow-up
- **IMAP Integration** — Secure email fetching with graceful error handling
- **Demo Mode** — 22 realistic sample emails across all categories
- **Responsive** — Desktop and mobile SaaS interface

## Local Development

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up environment variables (see backend/.env example below)
# Start the server:
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Environment Variables

Create `backend/.env`:

```
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/mailmind
OPENAI_API_KEY=your-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
EMAIL_ENCRYPTION_KEY=your-fernet-key
APP_ENV=development
CORS_ORIGINS=*
```

Create `frontend/.env`:

```
VITE_API_BASE_URL=http://localhost:8000/api
```

## Testing

```bash
cd backend
source venv/bin/activate
python -m pytest tests/ -v
```

36 tests covering API endpoints, AI categorization, reply generation, and analytics.

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive Swagger docs.

## Deployment

### Frontend (Vercel / Netlify)

The frontend is a static Vite build. Point your deployment platform to the `frontend/` directory.

### Backend (Railway / Render / Fly.io)

The FastAPI backend needs a persistent server with MySQL access. See `backend/requirements.txt`.

## Security

- Email passwords encrypted at rest (Fernet encryption)
- API keys stored in environment variables only
- No credentials exposed in frontend code or API responses
- Replies never sent without explicit user confirmation
