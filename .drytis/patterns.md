# MailMind AI — Patterns

## Backend (Python / FastAPI)
- **ORM:** SQLAlchemy 2.0 declarative + `Session` dependency injection via `Depends(get_db)`.
- **Schemas:** Pydantic v2 models (`from_attributes = True` for ORM).
- **Error handling:** custom exception → JSONResponse with `{"detail": "user-friendly message"}`. Never leak tracebacks to client.
- **AI calls:** graceful degradation — if OpenAI fails or no key, fall back to rule-based categorization + template replies so the app still works.
- **Crypto:** Fernet symmetric encryption for email passwords. Key from `EMAIL_ENCRYPTION_KEY` env (auto-generated if absent for dev).
- **Migrations:** `backend/migrations/` — Alembic. Schema changes always via migration, never raw SQL on prod.
- **Naming:** snake_case for Python, PascalCase for SQLAlchemy models, snake_case columns.
- **Config:** all secrets/URLs via `app/config.py` Pydantic Settings reading env vars. No hardcoded credentials.

## Frontend (React / TypeScript)
- **Styling:** Tailwind utility classes; custom palette via tailwind.config. Professional SaaS look.
- **Data fetching:** TanStack Query (`useQuery` / `useMutation`) with the custom `apiFetch` wrapper.
- **State:** server state via React Query; minimal local state.
- **API client:** `src/api/client.ts` — central `apiFetch` with base URL from `VITE_API_BASE_URL`, error normalization.
- **Routing:** React Router v6 with `<Layout>` wrapper (sidebar + topbar).
- **Forms:** controlled components; inline validation; toast on success/error.
- **Toasts:** react-hot-toast.
- **Empty / loading / error states:** every list/page has all three.
- **Confirmation dialogs:** custom `<ConfirmDialog>` for destructive/sensitive actions (delete, send email).
- **Colors:** urgency colors — critical=#dc2626, high=#ea580c, medium=#ca8a04, low=#16a34a.
- **No hardcoded URLs:** all API calls via the client; base URL from env/preview origin.

## Test Conventions
- Backend: pytest against a test DB; seed demo data; test API endpoints via TestClient.
- Frontend: the tester sub-agent runs browser (Playwright) tests against the preview URL.
- Every API endpoint must be reachable and return correct status codes.

## Security
- Never expose DB creds, AI keys, or email passwords in frontend code or API responses.
- Email password fields are write-only (never returned by GET).
- Confirm before sending any email.
- Validate all inputs (Pydantic on backend, inline on frontend).
