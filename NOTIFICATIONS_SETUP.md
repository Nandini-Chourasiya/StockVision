# StockVision - SMS & Push Notifications Setup Guide

This guide walks you through setting up **Twilio SMS** and **Web Push** notifications for StockVision.

---

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables (see below)
3. Run the backend: `flask run`
4. Enable notifications in your browser when prompted
5. Add your phone number in your profile for SMS alerts

---

## 1. Twilio SMS Setup

### Create a Twilio Account

1. Go to [twilio.com](https://www.twilio.com/) and sign up for a free trial
2. Verify your phone number
3. Get a Twilio phone number (free trial includes one)

### Get Your Credentials

From the [Twilio Console](https://console.twilio.com/):

- **Account SID**: Found on your dashboard
- **Auth Token**: Found on your dashboard (click to reveal)
- **Phone Number**: Your Twilio phone number in E.164 format (e.g., `+15551234567`)

### Set Environment Variables (Windows)

**Option A: Command Prompt (temporary)**
```cmd
set TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
set TWILIO_AUTH_TOKEN=your_auth_token_here
set TWILIO_PHONE_NUMBER=+15551234567
```

**Option B: PowerShell (temporary)**
```powershell
$env:TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
$env:TWILIO_AUTH_TOKEN="your_auth_token_here"
$env:TWILIO_PHONE_NUMBER="+15551234567"
```

**Option C: Permanent (System Environment Variables)**
1. Press `Win + X` → "System"
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Under "User variables", click "New" for each:
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_PHONE_NUMBER`

### Add Your Phone Number

1. Login to StockVision
2. Go to your **Profile** page
3. Enter your phone number in E.164 format: `+919876543210`
4. Save your profile

---

## 2. Web Push Notifications Setup

### Generate VAPID Keys

Run this command to generate VAPID keys:

```bash
npx web-push generate-vapid-keys
```

This outputs:
```
=======================================

Public Key:
BPxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

Private Key:
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

=======================================
```

### Set VAPID Environment Variables

```cmd
set VAPID_PUBLIC_KEY=BPxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
set VAPID_PRIVATE_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
set VAPID_CLAIMS_EMAIL=mailto:your@email.com
```

### Enable in Browser

1. Open the StockVision dashboard
2. Your browser will ask for notification permission
3. Click **Allow**
4. Check the console for `[Push] Subscribed successfully`

---

## 3. Running the Backend

```bash
cd backend
pip install -r requirements.txt
flask run
```

The server starts at `http://127.0.0.1:5000/`

---

## 4. Testing Notifications

### Test Browser Alerts

1. Login to your account
2. Go to the **Dashboard**
3. Set a price alert (e.g., RELIANCE High > 3000)
4. Wait 5-10 seconds - the mock ticker runs every 5 seconds
5. When triggered, you'll see:
   - Browser notification popup
   - Console log: `[Alert] Backend trigger results`

### Test SMS (Twilio Trial)

> **Note**: Twilio trial accounts can only send SMS to verified numbers.

1. Verify your phone number at [Twilio Verified Caller IDs](https://console.twilio.com/us1/develop/phone-numbers/manage/verified)
2. Add that number to your StockVision profile
3. Trigger an alert
4. Check your phone for the SMS

---

## 5. API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/vapid-public-key` | GET | Get VAPID public key for push subscription |
| `/api/push/subscribe` | POST | Save push subscription |
| `/api/push/unsubscribe` | POST | Remove push subscription |
| `/api/push/send` | POST | Send push notification |
| `/api/sms/send` | POST | Send SMS to user's phone |
| `/api/alert/trigger` | POST | Trigger both SMS and Push |

### Example: Trigger Alert

```javascript
fetch('/api/alert/trigger', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: 'RELIANCE crossed above ₹3000!' })
});
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "VAPID keys not configured" | Set `VAPID_PUBLIC_KEY` and `VAPID_PRIVATE_KEY` environment variables |
| "Twilio credentials not configured" | Set all 3 Twilio environment variables |
| "No phone number on file" | Add phone number in your profile |
| Notifications not showing | Check browser permissions in Settings → Site Settings |
| SMS not received (trial) | Verify phone number at Twilio console |

---

## Security Notes

- **Never** commit credentials to git
- Use environment variables for all secrets
- The service worker (`sw.js`) must be served from the same origin
- Phone numbers must be in E.164 format (+CountryCodeNumber)
