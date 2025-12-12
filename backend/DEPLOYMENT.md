# StockVision Deployment Guide

## Quick Deploy to Render (Recommended - Free Tier)

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/stockvision.git
git push -u origin main
```

### Step 2: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub

### Step 3: Create Web Service
1. Click **New** → **Web Service**
2. Connect your GitHub repo
3. Configure:
   - **Name**: `stockvision`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn "app:create_app('production')" --bind 0.0.0.0:$PORT`

### Step 4: Add Environment Variables
In Render dashboard, add these:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | Generate: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `FLASK_CONFIG` | `production` |
| `DATABASE_URL` | (Render provides this if you add PostgreSQL) |

### Step 5: Add PostgreSQL Database
1. Click **New** → **PostgreSQL**
2. Name it `stockvision-db`
3. Copy the **Internal Database URL**
4. Add it as `DATABASE_URL` in your web service

### Step 6: Deploy!
Render auto-deploys on git push.

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Flask session encryption key |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `FLASK_CONFIG` | Yes | Set to `production` |
| `TWILIO_ACCOUNT_SID` | No | For real SMS |
| `TWILIO_AUTH_TOKEN` | No | For real SMS |
| `TWILIO_PHONE_NUMBER` | No | For real SMS |

---

## Local Production Test

```bash
# Set environment variables
$env:SECRET_KEY = "test-secret-key"
$env:FLASK_CONFIG = "production"

# Install dependencies
pip install -r requirements.txt

# Run with gunicorn
gunicorn "app:create_app('production')" --bind 127.0.0.1:8000
```

Then visit: http://127.0.0.1:8000
