# YouTube

Scripts for managing your YouTube subscriptions, watch history, and downloads.

## Features

- Export your subscriptions list
- Search and filter your watch history (via Google Takeout)
- Download videos for offline use with `yt-dlp`

## Setup

```bash
pip install google-auth google-auth-oauthlib google-api-python-client yt-dlp python-dotenv
```

For the YouTube Data API:
- Reuses `YOUTUBE_API_KEY` or Google OAuth from `.env`
- Enable YouTube Data API v3 in your Google Cloud Console project

## Scripts

| Script                          | What it does                                       |
|---------------------------------|----------------------------------------------------|
| `scripts/export_subscriptions.py` | Export all subscriptions to `subscriptions/list.json` |
| `scripts/download.py`           | Download a video or playlist with `yt-dlp`         |

## Downloading Videos

```bash
# Download a single video (best quality)
python scripts/download.py --url "https://youtube.com/watch?v=VIDEO_ID"

# Download an entire playlist
python scripts/download.py --url "https://youtube.com/playlist?list=PLAYLIST_ID"

# Audio only (mp3)
python scripts/download.py --url "..." --audio-only
```

Downloads go to `downloads/` (gitignored).

## Watch History

Export your watch history via [Google Takeout](https://takeout.google.com):
1. Select "YouTube and YouTube Music" → "History"
2. Download and place `watch-history.json` in `subscriptions/`
3. Run `python scripts/analyze_history.py` for stats
