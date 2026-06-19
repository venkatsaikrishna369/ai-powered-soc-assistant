Forgot server (Flask)

This small Flask server accepts SMS send requests and performs admin password resets using Firebase Admin SDK.

Endpoints:
- POST /send-sms { to, message }
  - Uses Twilio if configured, otherwise returns the message in the JSON response for local testing.
- POST /admin-reset-token { token, newPassword }
  - Validates the one-time token in Realtime DB at `/passwordResetTokens/{token}` and uses Firebase Admin SDK to update the user's password. Removes token and `passwordResets/{key}` on success.

Setup
1. Copy `.env.example` to `.env` and fill values.
2. Place your Firebase service account JSON at `SERVICE_ACCOUNT_PATH` (or adjust path).
3. Install dependencies and run:

```bash
cd backend/forgot_server
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Notes
- Keep your service account JSON and secrets out of source control.
- The frontend expects this server at `http://localhost:3001` by default. If you run Flask on 3002, set `window.SMS_SERVER_URL` in the browser devtools or edit the frontend JS.
