---
name: russian-audiobooks
description: Find and download Russian audiobooks from patephone.com. Search by title, download full books as complete.m4b (chapters, cover, title/author) to ~/Documents/Personal/audiobooks/ for Bound app via OneDrive. Uses yt-dlp + ffmpeg. Use when the user asks for Russian audiobooks, patephone, Bound, скачать аудиокнигу, or offline iPhone listening.
---

# Russian audiobooks (Patephone → Bound)

Script: `~/Documents/GitHub/Personal/Random/patephone_audiobooks.py`  
Output: `~/Documents/Personal/audiobooks/<book-slug>/` (outside git)

Patephone streams **HLS (AAC, ~10s segments)**. Chapters API is public. Full book needs a **logged-in session** (cookies).

## Final output (what the user gets)

After `download`, each book folder should contain **only**:

| File | Required | Used by Bound |
| --- | --- | --- |
| **`complete.m4b`** | Yes | **Import this** — audio + 33 chapter markers + embedded cover + title/author |
| **`cover.jpg`** | Yes (if available) | Optional backup; cover is already inside `.m4b` |
| **`metadata.json`** | Yes (written by script) | No — reference / re-export only |

**Do not leave** in the folder: `complete.m4a`, `complete.mp4`, `download*.log`, `download.pid`, `chapters.ffmeta`, partial files.

### How `complete.m4b` is built

1. **yt-dlp** — parallel HLS download → remux to `complete.m4a` (fixes raw ADTS `.mp4` from yt-dlp).
2. **`build_bound_m4b()`** — ffmpeg: chapter markers from `metadata.json` + embed `cover.jpg` + title/author tags → `complete.m4b`.
3. **`finalize_audiobook_folder()`** — delete `complete.m4a` and all logs/temp files.

## Quick start

```bash
cd ~/Documents/GitHub/Personal/Random
python3 -m venv .venv && source .venv/bin/activate
pip install requests mutagen browser-cookie3
brew install ffmpeg yt-dlp

alias pab='python ~/Documents/GitHub/Personal/Random/patephone_audiobooks.py'
```

## Decision tree

```
User wants a Russian audiobook
├── Has patephone.com /audiobook/ URL?
│   → pab info <url>
│   → pab download <url>              # → complete.m4b (default)
│   → pab download <url> --chapters   # per-chapter .m4a (rare; slow)
│   → pab export <url>                # rebuild m4b from existing folder
├── Title/author only?
│   → pab search "query" → download
└── Popular?
    → pab latest --limit 20
```

## Commands

| Command | Purpose |
| --- | --- |
| `search "<query>"` | Catalog search |
| `info <url>` | Metadata + stream mode (`preview` / `ad` / `full`) |
| `resolve <url>` | Verify HLS endpoints and durations |
| **`download <url>`** | Full book → **`complete.m4b`** (yt-dlp + finalize) |
| `download <url> --chapters` | Per-chapter `.m4a` files (no single m4b) |
| **`export <url>`** | Build **`complete.m4b`** from existing folder (has `metadata.json` + `complete.m4a` or rebuild m4b only) |
| **`export /path/to/folder`** | Same, by folder path |
| `latest [--limit N]` | Chart list |

### Download flags

| Flag | Default | Description |
| --- | --- | --- |
| `-o DIR` | `~/Documents/Personal/audiobooks` | Output root |
| `--chapters` | off | Per-chapter `.m4a` instead of `complete.m4b` |
| `--preview` | off | ~21 min sample only |
| `--force` | off | Re-download / rebuild |
| `--cookie "..."` | env | Override `PATEPHONE_COOKIE` |
| `--browser-profile` | `Profile 1` | Chrome profile for cookies |
| `--concurrent-fragments` | 32 | yt-dlp parallelism |
| `--ffmpeg-only` | off | Sequential ffmpeg (slow) |

## Stream modes (API)

| Mode | Endpoint | Auth |
| --- | --- | --- |
| **preview** | `/api/product/{id}/preview/hls` | None (~21 min) |
| **ad** | `/api/ad/stream/{id}` | Logged in free (~full book) |
| **full** | `/api/product/{id}/stream/hls` | Paid (ad-free) |

Order: **full** → **ad** → **preview**.

## Download workflow (agent must follow)

1. `pab info <url>` — confirm `ad` or `full`, not preview-only.
2. `pab download <url>` — wait for completion.
3. Verify folder: **`complete.m4b`** exists; no logs or stray `.m4a`.
4. Tell user: upload folder to **OneDrive** → import **`complete.m4b`** in **Bound**.

**Speed:** yt-dlp ~6–10 min for a 21h book; m4b build ~1 min (stream copy).

**While downloading:** `tail -f <out-dir>/download-ytdlp.log` (log removed after finalize).

**Re-export only:** `pab export <url>` or `pab export ~/Documents/Personal/audiobooks/<slug>`

## Bound app (primary target)

- User imports via **OneDrive** (or Files) into **Bound** — not Apple Books.
- Bound reads **embedded** metadata and **chapter markers** in `.m4b` / `.m4a`.
- Bound does **not** read `metadata.json` or sidecar `cover.jpg` for listing (cover is embedded in m4b).
- If multiple audio files in a folder, Bound may split/group wrong — keep folder to **one** `complete.m4b` (+ optional `cover.jpg`, `metadata.json`).

## Cookies

**Auto:** `browser_cookie3` from Chrome `--browser-profile "Profile 1"`.

**Manual:** `PATEPHONE_COOKIE` in `~/Documents/GitHub/Personal/Random/.env`.

## Ads

- Cannot strip ads during merge — no ad segments in HLS manifest.
- Browser ads are often player-only; downloaded audio may be continuous.
- Ad-free source: paid **full** stream.

## Example (verified)

```bash
pab download "https://patephone.com/audiobook/52891-odin-na-odin-s-zhiznyu-kniga-kotoraya-pomozhet-naiti-smysl"
# → ~/Documents/Personal/audiobooks/odin-na-odin-s-zhiznyu-.../
#      complete.m4b   (~904 MB, ~21h, 33 chapters, Латыпов)
#      cover.jpg
#      metadata.json
```

## Output rules

- Pipe **`search` / `latest` / `resolve` tables** verbatim.
- **Deliverable is always `complete.m4b`** for default download (unless `--chapters`).
- After download, folder must be **clean** (no logs, no intermediate audio).
- Never claim full book if stream mode was `preview` only.
- Patephone only unless user extends sources.

## Common gotchas

- `user_not_found` = no session cookie.
- Paid HLS URL may 402 on manifest — use **ad** stream when logged in free.
- yt-dlp raw output is ADTS named `.mp4` — never give that to the user; remux to `.m4a` then `.m4b`.
- Chapter times come from `/api/product/{id}/chapters` in `metadata.json`.
- Russian search terms work better than transliteration.
- `metadata.json` `stream_mode` may say `preview` from an early run; if `complete.m4b` is ~21h, the audio is the full book.

## Dependencies

| Tool | Role |
| --- | --- |
| **yt-dlp** | Parallel HLS download |
| **ffmpeg** | Remux m4a; build m4b with chapters + cover |
| **browser-cookie3** | Chrome cookies (macOS) |
| **mutagen** | Optional tags for `--chapters` mp3 mode |
