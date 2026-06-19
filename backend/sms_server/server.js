require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(bodyParser.json());

const PORT = process.env.PORT || 3001;

// Optional Twilio setup
const TWILIO_SID = process.env.TWILIO_ACCOUNT_SID;
const TWILIO_TOKEN = process.env.TWILIO_AUTH_TOKEN;
const TWILIO_FROM = process.env.TWILIO_FROM;
let twilioClient = null;
if (TWILIO_SID && TWILIO_TOKEN) {
  const twilio = require('twilio');
  twilioClient = twilio(TWILIO_SID, TWILIO_TOKEN);
}

// Optional Firebase Admin setup (for admin password reset)
let admin = null;
if (process.env.SERVICE_ACCOUNT_PATH) {
  admin = require('firebase-admin');
  const serviceAccount = require(process.env.SERVICE_ACCOUNT_PATH);
  admin.initializeApp({
    credential: admin.credential.cert(serviceAccount),
    databaseURL: process.env.FIREBASE_DATABASE_URL || undefined
  });
}

app.get('/', (req, res) => res.json({ ok: true, message: 'SMS/Admin server' }));

// POST /send-sms { to, message }
app.post('/send-sms', async (req, res) => {
  const { to, message } = req.body || {};
  if (!to || !message) return res.status(400).json({ error: 'Missing to or message' });

  if (twilioClient && TWILIO_FROM) {
    try {
      const resp = await twilioClient.messages.create({ to, from: TWILIO_FROM, body: message });
      return res.json({ ok: true, sid: resp.sid });
    } catch (e) {
      console.error('Twilio error', e);
      return res.status(500).json({ ok: false, error: e.message || String(e) });
    }
  }

  // No Twilio configured: return success but include the OTP in response for testing
  console.warn('Twilio not configured — returning message in response for testing (do not use in production)');
  return res.json({ ok: true, test: true, to, message });
});

// POST /admin-reset { uid, newPassword, secret }
// This endpoint uses Firebase Admin SDK to change a user's password. Protect with SECRET.
app.post('/admin-reset', async (req, res) => {
  const { uid, newPassword, secret } = req.body || {};
  if (!admin) return res.status(500).json({ error: 'Firebase Admin not configured on server' });
  if (!uid || !newPassword) return res.status(400).json({ error: 'Missing uid or newPassword' });
  if (!process.env.ADMIN_API_SECRET || secret !== process.env.ADMIN_API_SECRET) return res.status(401).json({ error: 'Unauthorized' });

  try {
    await admin.auth().updateUser(uid, { password: newPassword });
    return res.json({ ok: true });
  } catch (e) {
    console.error('admin-reset error', e);
    return res.status(500).json({ ok: false, error: e.message || String(e) });
  }
});

// POST /admin-reset-token { token, newPassword }
// Validates a one-time token stored in Realtime DB at /passwordResetTokens/{token}
app.post('/admin-reset-token', async (req, res) => {
  if (!admin) return res.status(500).json({ error: 'Firebase Admin not configured on server' });
  const { token, newPassword } = req.body || {};
  if (!token || !newPassword) return res.status(400).json({ error: 'Missing token or newPassword' });

  try {
    const db = admin.database();
    const tokenRef = db.ref(`passwordResetTokens/${token}`);
    const snap = await tokenRef.get();
    if (!snap.exists()) return res.status(400).json({ error: 'Invalid or expired token' });
    const data = snap.val();
    if (Date.now() > (data.expiresAt || 0)) {
      await tokenRef.remove();
      return res.status(400).json({ error: 'Token expired' });
    }

    const uid = data.uid || null;
    if (!uid) return res.status(400).json({ error: 'No uid associated with token' });

    // perform password update
    await admin.auth().updateUser(uid, { password: newPassword });

    // cleanup DB entries
    await tokenRef.remove();
    const key = data.key;
    if (key) await db.ref(`passwordResets/${key}`).remove();

    return res.json({ ok: true });
  } catch (e) {
    console.error('admin-reset-token error', e);
    return res.status(500).json({ error: e.message || String(e) });
  }
});

app.listen(PORT, () => console.log(`SMS/Admin server running on http://localhost:${PORT}`));
