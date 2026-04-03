# Spotify

Scripts for managing and backing up your Spotify library.

## Features

- Export all your playlists (names, tracks, metadata)
- Backup liked songs
- Discover and filter recommendations

## Setup

1. Go to https://developer.spotify.com/dashboard and create an app
2. Set Redirect URI to `http://localhost:8888/callback`
3. Add `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, and `SPOTIFY_USERNAME` to `.env`

```bash
pip install spotipy python-dotenv
```

## Scripts

| Script                        | What it does                                  |
|-------------------------------|-----------------------------------------------|
| `scripts/export_playlists.py` | Export all playlists to JSON                  |
| `scripts/backup_liked.py`     | Save your Liked Songs to `playlists/liked.json` |
| `scripts/recommendations.py`  | Get recommendations based on a seed playlist  |

## Usage

```bash
# Back up all playlists
python scripts/export_playlists.py

# Back up liked songs
python scripts/backup_liked.py
```

## Playlist Backups

Exported playlists are saved to `playlists/` as JSON files.
These are committed to git so you have a history of your library over time.
Cache files are gitignored.
