# MailMind AI — Production Deployment Guide

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   FRONTEND       │     │    BACKEND        │     │   DATABASE       │
│   (Vercel)       │────▶│   (Render/Koyeb)  │────▶│   (Aiven/TiDB)   │
│   React build    │     │   FastAPI + uvicorn│     │   MySQL          │
│   Free tier      │     │   Free tier       │     │   Free tier      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## Free-Tier Deployment (All 100% Free)

### 1. Database — Aiven MySQL (Free)
- Sign up at https://aiven.io
- Create a free MySQL service (1 free plan available)
- Note: host, port, database name, username, password
- Connection string: `mysql+pymysql://USER:PASS@HOST:PORT/DBNAME`

### 2. Backend — Render (Free)
- Sign up at https://render.com with your GitHub
- Create new → **Web Service** → connect your `MailMind-AI` repo
- **Build Command:** `cd backend && pip install -r requirements.txt`
- **Start Command:** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Add environment variables (see below)
- Free tier: spins down after 15 min inactivity (first request takes ~30s to wake)

### 3. Frontend — Vercel (Free)
- Sign up at https://vercel.com with your GitHub
- Import your `MailMind-AI` repo
- **Root Directory:** `frontend`
- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- Add environment variable: `VITE_API_BASE_URL` = your Render backend URL + `/api`

### Alternative Free Hosts

| Component | Vercel | Netlify | Cloudflare Pages | Render | Koyeb | Railway | Fly.io |
|-----------|--------|---------|-----------------|--------|-------|---------|--------|
| Frontend  | ✅ Free | ✅ Free | ✅ Free | — | — | — | — |
| Backend   | — | — | — | ✅ Free* | ✅ Free | Trial only | ✅ Free* |
| Database  | — | — | — | PostgreSQL free | — | Trial only | — |

*Render free web services spin down after inactivity. Koyeb has a generous free tier.

## Backend Environment Variables (for Render/Koyeb)

```
DATABASE_URL=mysql+pymysql://USER:PASSWORD@HOST:PORT/DATABASE
OPENAI_API_KEY=your-openai-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
EMAIL_ENCRYPTION_KEY=<generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">
APP_ENV=production
CORS_ORIGINS=https://your-app.vercel.app
```

## Frontend Environment Variables (for Vercel)

```
VITE_API_BASE_URL=https://your-backend.onrender.com/api
```

## Important Notes

- The backend creates database tables automatically on first boot
- Demo data seeds automatically if the database is empty
- The AI fallback system works even without an OpenAI key (rule-based categorization + template replies)
- Email passwords are encrypted with Fernet — generate your own key, don't reuse the dev one
- Never commit `.env` files — they are in `.gitignore`
