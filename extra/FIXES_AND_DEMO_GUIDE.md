# Checkpoint 3 Fixes & Demo Notes

## Things we fixed

### 1. UUID Bug
**Issue**: The `generate_uuid()` function was making UUIDs with hyphens, but our database wanted them without hyphens (SQLite format).
**Fix**: We changed `database.py` to use `.hex` so it matches what SQLite expects.

### 2. Error Messages
**Issue**: When something went wrong (like a duplicate email), it just said "Failed" without saying why.
**Fix**: We added try-catch blocks in `app.py` so now it tells you if the email is taken or if a field is missing.

### 3. Frontend Errors
**Issue**: The frontend wasn't showing the error messages from the backend properly.
**Fix**: Fixed `apiCall()` in `app.js` to actually show the error text in the toast notification.

## Testing Results

- Creating users works now (UUIDs are correct).
- Duplicate emails show a proper error message.
- All the CRUD stuff gives better feedback now.

## Files We Changed

1. `web-ui/backend/database.py` (UUID fix)
2. `web-ui/backend/app.py` (Error handling)
3. `web-ui/frontend/app.js` (Showing errors)

## Presentation Notes (Dec 7)

**Intro (3 mins):**
- "This is a Stock Exchange Management System."
- "Brokers can manage users, accounts, and trades."
- Show the ER diagram and the 7 tables.
- Mention we used SQLite, Flask, and vanilla JS.

**Demo (5 mins):**
1. **Dashboard**: Show the stats.
2. **Create User**: Make a new user (e.g., "Sarah").
3. **Create Account**: Give Sarah an account.
4. **Search**: Look for "AAPL".
5. **Trade**: Buy 10 shares of AAPL.
6. **Holdings**: Show that she owns it now.
7. **Analytics**: Show the portfolio value.

**Questions (2 mins):**
- Be ready to explain the relationships (M:N, etc.).

## How to Run for Demo

**Terminal 1 (Backend):**
```bash
cd web-ui/backend
python3 app.py
```

**Terminal 2 (Frontend):**
```bash
cd web-ui/frontend
open index.html
```
(Or use `python3 -m http.server 8000` if you want to be safe).

It meets all the Checkpoint 3 requirements (Interactive, CRUD, Parametrized queries, GUI).
