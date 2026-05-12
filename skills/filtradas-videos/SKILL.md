---
name: filtradas-videos
description: List videos from filtradas.com (a Discourse forum) with direct mp4/webm CDN URLs and English-translated titles. Use when the user asks for the latest, oldest, top, or most-popular videos on filtradas, filtradas.com, or filtradas video links. Always returns direct video URLs (never page links) with English translations and never re-discovers what the site is.
---

# Filtradas Videos

Run the script at `~/Documents/GitHub/Personal/Random/filtradas_videos.py`. It hits filtradas.com's Discourse JSON endpoints, extracts the first embedded video URL from each topic, and translates Spanish titles to English via Google Translate's free public endpoint.

## Rules

- Never explain or re-discover what filtradas.com is — go straight to the script.
- Always emit direct video URLs (mp4 / webm / iframe src), never `/t/<slug>/<id>` page links.
- Always include both the original Spanish title and an English translation.
- Use cache-busted requests (handled by the script) so refresh always shows current data.

## Commands

```bash
# activate venv (requests/bs4 not needed for this script, but venv has python 3.x)
source ~/Documents/GitHub/Personal/Random/.venv/bin/activate

# newest topics in last N hours
python ~/Documents/GitHub/Personal/Random/filtradas_videos.py latest --hours 24

# newest N regardless of age
python ~/Documents/GitHub/Personal/Random/filtradas_videos.py latest --limit 30

# most-viewed all-time (default 10)
python ~/Documents/GitHub/Personal/Random/filtradas_videos.py top --limit 10

# oldest topics on the site
python ~/Documents/GitHub/Personal/Random/filtradas_videos.py oldest --limit 5
```

## Output

The script prints a markdown table directly. Pipe it through to the user verbatim — do not reformat or rewrite. Columns:

`| Age | Views | Likes | Title (ES) | Title (EN) | Video |`

Topics with no embedded video are still listed with `(no video)` in the Video column.

## Mapping user requests to commands

| User says | Command |
|---|---|
| "latest filtradas" / "what's new on filtradas" | `latest --hours 24` |
| "filtradas in the last N hours/days" | `latest --hours <N or N*24>` |
| "newest 30 filtradas videos" | `latest --limit 30` |
| "top / most popular / most viewed filtradas" | `top --limit 10` (or user's number) |
| "oldest filtradas" / "first videos on filtradas" | `oldest --limit 5` |

## Downloading a video

To save a video locally, use plain `curl` with the URL from the table:

```bash
curl -L -o ~/Downloads/<filename>.mp4 "<video URL from table>"
```

For bulk image scrapes of related photo sites (e.g. dashablog.tv galleries), use the separate `bulk-image-scrape` skill instead.
