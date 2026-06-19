from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import time

load_dotenv()

TWILIO_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_FROM = os.getenv('TWILIO_FROM')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')
SERVICE_ACCOUNT_PATH = os.getenv('SERVICE_ACCOUNT_PATH')
FIREBASE_DATABASE_URL = os.getenv('FIREBASE_DATABASE_URL')
ADMIN_API_SECRET = os.getenv('ADMIN_API_SECRET')
PORT = int(os.getenv('PORT', '3002'))

app = Flask(__name__)
CORS(app)

# Optional clients (initialized lazily)
_twilio_client = None
_firebase_admin = None
_db = None
_auth_admin = None

def init_twilio():
    global _twilio_client
    if _twilio_client is not None:
        return _twilio_client
    if not (TWILIO_SID and TWILIO_TOKEN and TWILIO_FROM):
        return None
    try:
        from twilio.rest import Client
        _twilio_client = Client(TWILIO_SID, TWILIO_TOKEN)
        return _twilio_client
    except Exception as e:
        print('Twilio init error:', e)
        _twilio_client = None
        return None


_sns_client = None
def init_sns():
    global _sns_client
    if _sns_client is not None:
        return _sns_client
    # require AWS credentials and region
    if not (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_REGION):
        return None
    try:
        import boto3
        _sns_client = boto3.client('sns',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION)
        return _sns_client
    except Exception as e:
        print('SNS init error:', e)
        _sns_client = None
        return None

def init_firebase_admin():
    global _firebase_admin, _db, _auth_admin
    if _firebase_admin is not None:
        return True
    if not SERVICE_ACCOUNT_PATH:
        return False
    if not os.path.exists(SERVICE_ACCOUNT_PATH):
        print(f'Firebase service account not found at: {SERVICE_ACCOUNT_PATH}')
        return False
    try:
        import firebase_admin as _fa
        from firebase_admin import credentials, db as _db_mod, auth as _auth_mod
        cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
        _fa.initialize_app(cred, {'databaseURL': FIREBASE_DATABASE_URL})
        _firebase_admin = _fa
        _db = _db_mod
        _auth_admin = _auth_mod
        return True
    except Exception as e:
        print('Firebase Admin init error:', e)
        _firebase_admin = None
        _db = None
        _auth_admin = None
        return False

def safe_delete(ref):
    try:
        # Preferred delete() if available
        delete_fn = getattr(ref, 'delete', None)
        if callable(delete_fn):
            delete_fn()
            return
    except Exception:
        pass
    try:
        # Fallback to set(None)
        ref.set(None)
    except Exception:
        pass

@app.route('/')
def index():
    return jsonify({'ok': True, 'message': 'Forgot server running'})

@app.route('/send-sms', methods=['POST'])
def send_sms():
    data = request.get_json() or {}
    to = data.get('to')
    message = data.get('message')
    if not to or not message:
        return jsonify({'error': 'missing to or message'}), 400
    client = init_twilio()
    if client and TWILIO_FROM:
        try:
            msg = client.messages.create(body=message, from_=TWILIO_FROM, to=to)
            return jsonify({'ok': True, 'sid': msg.sid})
        except Exception as e:
            print('Twilio error', e)
            return jsonify({'ok': False, 'error': str(e)}), 500
    # Try AWS SNS if available
    sns = init_sns()
    if sns:
        try:
            # AWS SNS expects E.164 phone numbers; ensure `to` is formatted correctly.
            resp = sns.publish(PhoneNumber=to, Message=message)
            return jsonify({'ok': True, 'messageId': resp.get('MessageId')})
        except Exception as e:
            print('SNS error', e)
            return jsonify({'ok': False, 'error': str(e)}), 500

    # fallback: return the message in response for local testing
    return jsonify({'ok': True, 'test': True, 'to': to, 'message': message})

@app.route('/admin-reset-token', methods=['POST'])
def admin_reset_token():
    if not init_firebase_admin():
        return jsonify({'error': 'Firebase Admin not configured on server'}), 500
    body = request.get_json() or {}
    token = body.get('token')
    new_password = body.get('newPassword') or body.get('new_password')
    if not token or not new_password:
        return jsonify({'error': 'missing token or newPassword'}), 400
    try:
        # look up token in database
        ref = _db.reference(f'passwordResetTokens/{token}')
        data = ref.get()
        if not data:
            return jsonify({'error': 'invalid or expired token'}), 400
        expires_at = data.get('expiresAt') or data.get('expires_at')
        if expires_at and int(time.time()*1000) > int(expires_at):
            safe_delete(ref)
            return jsonify({'error': 'token expired'}), 400
        uid = data.get('uid')
        if not uid:
            return jsonify({'error': 'no uid associated with token'}), 400
        # perform password update
        _auth_admin.update_user(uid, password=new_password)
        # cleanup
        safe_delete(ref)
        key = data.get('key')
        if key:
            safe_delete(_db.reference(f'passwordResets/{key}'))
        return jsonify({'ok': True})
    except Exception as e:
        print('admin-reset-token error', e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print(f"Starting forgot_server on port {PORT}")
    print(f"Twilio configured: {'yes' if (TWILIO_SID and TWILIO_TOKEN and TWILIO_FROM) else 'no'}")
    print(f"Firebase Admin available: {'yes' if SERVICE_ACCOUNT_PATH else 'no'}")
    try:
        app.run(host='0.0.0.0', port=PORT)
    except Exception as e:
        print('Server failed to start:', e)
