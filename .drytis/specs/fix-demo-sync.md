# Fix Demo Mode Sync & IMAP Error Handling

## Problem
When an errored/placeholder IMAP account exists in the DB, clicking "Sync Emails" attempts a real IMAP connection even though the account never connected successfully. The resulting raw error (`[Errno -2] Name or service not known`) gets appended to the demo-mode message, confusing users.

## Files to Change
1. `backend/app/routers/accounts.py` — `sync_emails()` + `_seed_demo_emails()`
2. `backend/app/imap_service.py` — `test_imap_connection()` + `fetch_emails()` error messages
3. `backend/tests/test_demo_sync.py` — new test file

## Acceptance Criteria
- [ ] `sync_emails` does NOT attempt IMAP when no account exists OR account status is not "connected" — goes straight to demo mode
- [ ] When demo emails already exist, sync returns a clean message without any IMAP error appended
- [ ] When an account with status "error" exists, sync clearly tells the user the account needs attention, without showing a raw OS error
- [ ] `test_imap_connection` and `fetch_emails` return user-friendly error messages (no raw `[Errno -2]` strings)
- [ ] Real IMAP functionality still works: a valid connected account syncs via IMAP
- [ ] `force_demo=True` always goes to demo mode regardless of account status
- [ ] All existing tests pass
- [ ] New tests cover: demo-only sync (no account), sync with errored account, sync with connected account (mocked IMAP)
