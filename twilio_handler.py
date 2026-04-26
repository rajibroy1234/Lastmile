# twilio_handler.py
# Handles sending SMS alerts via Twilio
# Credentials are read from environment variables (safe for Render.com deployment)

import os
from twilio.rest import Client

# ── CREDENTIALS FROM ENV VARS ─────────────────────────────
# Set these in Render dashboard → Environment → Add Environment Variable
ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
AUTH_TOKEN  = os.environ.get('TWILIO_AUTH_TOKEN', '')
FROM_NUMBER = os.environ.get('TWILIO_FROM_NUMBER', '')
TO_NUMBER   = os.environ.get('TWILIO_TO_NUMBER', '')

def send_alert(area_name, crisis_type, severity):
    """
    Send SMS alert to authority when a HIGH severity report comes in.
    Called automatically from app.py when severity == 3
    """
    if severity < 3:
        return  # Only alert for HIGH severity

    if not ACCOUNT_SID or not AUTH_TOKEN:
        print("⚠️  Twilio credentials not set — skipping SMS alert")
        return None

    try:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        body = (
            f"🚨 LASTMILE ALERT\n"
            f"Crisis: {crisis_type.upper()}\n"
            f"Area: {area_name}\n"
            f"Severity: HIGH\n"
            f"Action required immediately."
        )
        message = client.messages.create(
            body=body,
            from_=FROM_NUMBER,
            to=TO_NUMBER
        )
        print(f"✅ SMS Alert sent: {message.sid}")
        return message.sid
    except Exception as e:
        print(f"❌ SMS Alert failed: {e}")
        return None


def receive_sms_webhook(form_data):
    """
    Processes incoming SMS from Twilio webhook.
    Twilio sends POST to /api/sms with form fields:
      Body = SMS text content
      From = sender's phone number

    HOW TO SET UP ON RENDER:
    1. Deploy this app on Render
    2. Go to Twilio console → Phone Numbers → Your Number → Configure
    3. Webhook URL: https://YOUR-APP-NAME.onrender.com/api/sms
    4. Method: HTTP POST
    """
    body = form_data.get('Body', '').strip()
    sender = form_data.get('From', 'Unknown')
    print(f"📱 SMS received from {sender}: {body}")
    return body


# ── RENDER SETUP GUIDE ────────────────────────────────────
"""
SETTING UP TWILIO ON RENDER:

1. Go to your Render service → Environment tab
2. Add these environment variables:
   TWILIO_ACCOUNT_SID   = ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN    = your_auth_token
   TWILIO_FROM_NUMBER   = +1XXXXXXXXXX   (your Twilio number)
   TWILIO_TO_NUMBER     = +91XXXXXXXXXX  (admin number)

3. For SMS receiving webhook, set in Twilio console:
   https://YOUR-APP-NAME.onrender.com/api/sms

4. Test SMS: text  FLOOD KAROLBAGH HIGH  to your Twilio number
"""
