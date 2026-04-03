# Personal Automation & Management Hub

A centralized repo for managing, automating, and backing up personal digital life — Gmail, Google services, finances, Spotify, YouTube, Chrome, and more.

## Structure

```
.
├── gmail/              # Gmail filters, scripts, and templates
├── google/             # Calendar, Drive, Sheets, Contacts automation
├── finance/            # Bank tracking, budgeting, crypto
├── media/              # Spotify and YouTube tools
├── browser/            # Chrome bookmarks, extensions, profiles
├── scripts/            # General automation, utilities, cron jobs
├── docs/               # Setup guides and personal documentation
└── config/             # Shared config files and constants
```

## Setup

1. Copy `.env.example` → `.env` and fill in your credentials
2. Install dependencies for the service you want to use (see each subfolder's `README.md`)
3. Never commit `.env` or any file containing real credentials

## Services Covered

| Category   | Services                                      |
|------------|-----------------------------------------------|
| Email      | Gmail                                         |
| Productivity | Google Calendar, Drive, Sheets, Contacts    |
| Finance    | Bank accounts, budgeting, crypto tracking     |
| Media      | Spotify, YouTube                              |
| Browser    | Chrome bookmarks, extensions, profiles        |
| Automation | Cron jobs, shell utilities                    |
