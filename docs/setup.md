# Setup Guide

Complete setup instructions for getting everything running from scratch.

## Prerequisites

- Python 3.11+
- `pip` / `venv`
- Google account (Gmail address in `.env`)
- Spotify account + developer app
- (Optional) Plaid account for bank integration

## 1. Clone & Environment

```bash
git clone https://github.com/<your-username>/personal-automation.git
cd personal-automation

python -m venv .venv
source .venv/bin/activate      # macOS/Linux
# .venv\Scripts\activate       # Windows

pip install -r requirements.txt

cp .env.example .env
# Open .env and fill in your credentials
```

## 2. Google / Gmail

1. Go to https://console.cloud.google.com
2. Create a new project (e.g. "Personal Automation")
3. Enable APIs: **Gmail API**, **Google Calendar API**, **Google Drive API**, **Google Sheets API**, **People API**, **YouTube Data API v3**
4. Create OAuth 2.0 credentials → Desktop app
5. Download `credentials.json` → place in `config/` (gitignored)
6. Run any script — it will open a browser for one-time OAuth consent
7. Token saved to `config/token.json` (gitignored)

## 3. Spotify

1. Go to https://developer.spotify.com/dashboard
2. Create an app → note Client ID and Client Secret
3. Add `http://localhost:8888/callback` as a Redirect URI
4. Add values to `.env`

## 4. Finance (Plaid — optional)

1. Sign up at https://dashboard.plaid.com
2. Create an app → get Client ID and Secret
3. Run the Plaid Link flow to connect your bank → save the `access_token` to `.env`
4. Set `PLAID_ENV=development` once you want real data (sandbox uses fake data)

## 5. Cron Jobs

```bash
# Preview what will be scheduled
cat scripts/cron/crontab.example

# Install
crontab scripts/cron/crontab.example
```

## 6. Verify Everything Works

```bash
# Gmail triage
python gmail/scripts/triage.py

# Crypto portfolio
python finance/crypto/portfolio.py

# Chrome extensions list
python browser/scripts/list_extensions.py

# Spotify liked songs backup
python media/spotify/scripts/backup_liked.py
```
