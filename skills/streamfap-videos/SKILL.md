---
name: streamfap-videos
description: List videos from streamfap.com (the CDN/platform that also hosts most filtradas.com clips) with direct mp4 URLs, English titles, exact upload timestamps, view counts, and duration. Supports newest-first (`latest`) and most-viewed (`top`). Use when the user asks for the latest, newest, top, most-popular, or most-viewed videos on streamfap or streamfap.com.
---

# StreamFap Videos

Run the script at `~/Documents/GitHub/Personal/Random/streamfap_videos.py`. It hits the site's single AJAX endpoint (`/ajax/load_more_videos.php?offset=N&limit=M`), parses the returned HTML cards, and outputs a markdown table. Stdlib-only (no extra deps).

The site exposes only one machine-readable endpoint and it is recency-ordered, but every card carries the exact unix upload timestamp inside its thumbnail filename, and the playable mp4 is at a parallel path that uses the same hash + timestamp. So one batch request gives full metadata, with no need to fetch the watch page.

## Rules

- Never re-discover what streamfap.com is — go straight to the script.
- Always emit direct mp4 URLs (`/uploads/videos/<hash>_<ts>.mp4`), never `/w/<id>` watch-page links.
- The upload timestamp comes from the thumbnail filename (`thumb_<hash>_<ts>.jpg`); the script already extracts it and shows both `Age` and `Posted (UTC)`.
- For `top`, the entire catalogue is paginated (no sort-by-views server endpoint exists; `/trending.php` returns 500, `/recommended.php` returns 404). Expect ~20-40s; warn the user only if they ask for `top --limit` greater than ~100.
- Pipe the script's table output verbatim. Don't reformat columns or summarize rows.

## Commands

```bash
# activate venv (stdlib-only but keeps PATH consistent with sibling scrapers)
source ~/Documents/GitHub/Personal/Random/.venv/bin/activate

# newest videos in last N hours
python ~/Documents/GitHub/Personal/Random/streamfap_videos.py latest --hours 24

# newest N regardless of age
python ~/Documents/GitHub/Personal/Random/streamfap_videos.py latest --limit 30

# top N by all-time view count (full-catalogue scan, ~20-40s)
python ~/Documents/GitHub/Personal/Random/streamfap_videos.py top --limit 10
```

## Output

Markdown table, piped verbatim to the user. Columns:

`| Age | Posted (UTC) | Views | Duration | Title | Tag | Video |`

- **Age** — relative (`28m`, `4.5h`, `2.1d`)
- **Posted (UTC)** — exact upload moment from the thumbnail-filename timestamp
- **Views** — view count
- **Duration** — `mm:ss` from the card overlay
- **Title** — already English (taken from the card's `alt=` attribute)
- **Tag** — primary category shown under the uploader (`Teen`, `Blonde`, `Latina`, ...)
- **Video** — direct mp4 URL (200-OK Cloudflare-fronted CDN)

## Mapping user requests to commands

| User says | Command |
|---|---|
| "latest streamfap" / "what's new on streamfap" | `latest --hours 24` |
| "streamfap in the last N hours/days" | `latest --hours <N or N*24>` |
| "newest 30 streamfap videos" | `latest --limit 30` |
| "top / most popular / most viewed streamfap" | `top --limit 10` (or user's number) |

## Downloading a video

Use plain `curl` with the URL from the table:

```bash
curl -L -o ~/Downloads/<filename>.mp4 "<video URL from table>"
```

## Relationship to filtradas-videos

Many filtradas.com posts embed streamfap-hosted mp4s, so the two scrapers complement each other:

- **filtradas** = forum-style index with Spanish titles (translated to English by the script). Source of "what's being shared right now in the Spanish-language scene."
- **streamfap** = direct platform with English titles, view counts, and the actual files. Source of truth for "what's actually on the CDN."

Same machine, same venv, similar output shape — both pipe markdown tables verbatim.
