"""
Back up your Spotify Liked Songs to playlists/liked.json.
Usage: python backup_liked.py
"""

import os
import json
from datetime import datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv("../../../.env")

SCOPE = "user-library-read"
OUTPUT_FILE = "../playlists/liked.json"


def get_client():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback"),
        scope=SCOPE,
    ))


def fetch_liked_songs(sp: spotipy.Spotify) -> list[dict]:
    tracks = []
    offset = 0
    limit = 50
    while True:
        resp = sp.current_user_saved_tracks(limit=limit, offset=offset)
        items = resp.get("items", [])
        if not items:
            break
        for item in items:
            track = item["track"]
            tracks.append({
                "id": track["id"],
                "name": track["name"],
                "artist": ", ".join(a["name"] for a in track["artists"]),
                "album": track["album"]["name"],
                "added_at": item["added_at"],
                "uri": track["uri"],
            })
        offset += limit
        if resp["next"] is None:
            break
    return tracks


def main():
    sp = get_client()
    print("Fetching liked songs...")
    tracks = fetch_liked_songs(sp)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    output = {
        "exported_at": datetime.utcnow().isoformat() + "Z",
        "total": len(tracks),
        "tracks": tracks,
    }
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Saved {len(tracks)} liked songs → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
