SMS/Admin helper server

This small Express server exposes two endpoints useful for testing and for production integration:

- `POST /send-sms` — send an SMS using Twilio, or return the message in the response if Twilio is not configured (useful for local testing).
  - Body: `{ to: string, message: string }`

- `POST /admin-reset` — reset a Firebase user's password using the Firebase Admin SDK. Protect this with a secret.
  - Body: `{ uid: string, newPassword: string, secret: string }`
  - Requires `SERVICE_ACCOUNT_PATH` (service account JSON) and `ADMIN_API_SECRET` set in `.env`.

Setup

1. Copy `.env.example` to `.env` and fill values.
2. If you want real SMS sending, sign up with Twilio and set `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, and `TWILIO_FROM`.
3. If you want `admin-reset` to work, place your Firebase service account JSON file in the server folder and set `SERVICE_ACCOUNT_PATH` to its path.

Install & run

```bash
cd backend/sms_server
npm install
npm start
```

Usage from the frontend

- The frontend currently writes OTPs to Realtime DB and will POST to `/send-sms` with `{to, message}`; configure the server URL accordingly (default http://localhost:3001/send-sms).
- To perform admin password reset (server-side), call `/admin-reset` from a secure admin flow (frontend currently triggers `sendPasswordResetEmail` to use Firebase's secure email reset flow). If you want direct admin-reset after OTP, call `/admin-reset` with the server `ADMIN_API_SECRET`.

Security notes

- Never commit service account JSON or private secrets.
- Protect `/admin-reset` with a strong secret and restrict access to your backend only.
- For production SMS, use Twilio or another provider and keep credentials in environment variables.
