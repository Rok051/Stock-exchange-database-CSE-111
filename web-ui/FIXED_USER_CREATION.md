# User Creation Fix

We finally fixed the "Failed to create user" error!

## What was wrong

1. **Port Conflict**: Turns out macOS AirPlay uses port 5000, so our Flask backend was getting blocked.
2. **File Protocol**: We were opening `index.html` directly (file://), which blocked the API calls.

## How we fixed it

- **Backend**: Moved Flask to **port 5001** so it doesn't clash with AirPlay.
- **Frontend**: Running it on a local server (**port 8000**) instead of just opening the file.
- **API**: Updated the code to talk to `localhost:5001`.

## How to run it now

### 1. Start Backend (Terminal 1)
```bash
cd web-ui/backend
python3 app.py
```
It should say it's running on **port 5001**.

### 2. Start Frontend (Terminal 2)
```bash
cd web-ui/frontend
python3 -m http.server 8000
```

### 3. Open in Browser
Go to **http://localhost:8000**
(Don't just double-click the html file!)

## Testing it

We tested it with `curl` and it works now. You can create users, accounts, and everything else through the UI.

## For the Presentation (Dec 7)

Just remember:
- Use **two terminals**.
- Go to **http://localhost:8000**.
- Backend is on **5001**.

Everything else should work fine.

---

**Troubleshooting:**
If it breaks, check if both terminals are running and make sure you aren't using `file://` in the browser.
