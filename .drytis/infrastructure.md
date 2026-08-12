# MailMind AI — Infrastructure

## Proxy Routes (Caddy)
| Path | Type | Target | Notes |
|------|------|--------|-------|
| `/` | php_server? NO → reverse_proxy | frontend `dist` via `serve` on :3000 | React SPA |
| `/api/*` | reverse_proxy | FastAPI uvicorn on :8000 | backend API |

**Routing approach:** Single Vite build served by `serve -s dist -l 3000`. Caddy reverse-proxies `/api/*` to FastAPI (:8000) and everything else to the Node serve (:3000).

## Background Services
| Name | Command | Port |
|------|---------|------|
| backend | `cd /workspace/backend && uvicorn app.main:app --host 0.0.0.0 --port 8000` | 8000 |
| frontend | `cd /workspace/frontend && serve -s dist -l 3000` | 3000 |

## Env Files
- `/workspace/backend/.env` — DB creds, AI key, AI base URL, encryption key, app config
- `/workspace/frontend/.env` — `VITE_API_BASE_URL=/api` (relative, so preview domain works)

## Env Keys (backend)
- `DATABASE_URL` — mysql+pymysql connection string
- `OPENAI_API_KEY` — secret, from create_openai_api_key
- `OPENAI_BASE_URL` — from create_openai_api_key
- `OPENAI_MODEL` — model name (default: gpt-4o-mini)
- `EMAIL_ENCRYPTION_KEY` — Fernet key for password encryption
- `APP_ENV` — development/production
- `CORS_ORIGINS` — allowed origins

## Ports
- 3000 → frontend (serve)
- 8000 → backend (FastAPI/uvicorn)
