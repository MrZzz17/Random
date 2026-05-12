"""
streamfap_videos.py - List streamfap.com videos with direct mp4 URLs and exact upload times.

streamfap.com is a video-sharing platform (same CDN that hosts many filtradas.com clips).
Its home page has a 'Recent Videos' section backed by an AJAX endpoint:
    /ajax/load_more_videos.php?offset=N&limit=M
that returns JSON with rendered HTML cards. Each card carries the upload unix timestamp
inside its thumbnail filename (thumb_<hash>_<ts>.jpg), and the playable mp4 lives at
the parallel path /uploads/videos/<hash>_<ts>.mp4 - so no watch-page fetch is needed.

Usage:
    python streamfap_videos.py latest --hours 24
    python streamfap_videos.py latest --limit 30
    python streamfap_videos.py top    --limit 10

Output: a markdown table with columns Age, Posted (UTC), Views, Duration, Title, Tag, Video.

`top` paginates the entire catalogue (the site has no sort=views endpoint) and ranks
by view count. Expect ~40s for a full scan of ~2k videos.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import time
import urllib.error
import urllib.request


BASE = "https://streamfap.com"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
TIMEOUT = 20
FETCH_RETRIES = 6
BATCH_SIZE = 20

CARD_SPLIT_RE = re.compile(r'<div class="group video-card[^"]*"')
ID_RE = re.compile(r'<a href="/w/(\d+)"')
THUMB_RE = re.compile(r'thumb_([a-f0-9]+)_(\d+)\.jpg')
ALT_RE = re.compile(r'<img[^>]+alt="([^"]+)"')
DURATION_RE = re.compile(
    r'<div class="absolute bottom-3 right-3[^"]*">\s*([\d:]+)\s*</div>'
)
VIEWS_RE = re.compile(r'([\d,]+)\s*views', re.I)
TAG_RE = re.compile(
    r'<p class="text-xs text-gray-500[^"]*">\s*([^<]+?)\s*</p>'
)


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json,text/javascript,*/*;q=0.1",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    for attempt in range(FETCH_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt + 1 < FETCH_RETRIES:
                time.sleep(min(2 ** attempt, 32))
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt + 1 < FETCH_RETRIES:
                time.sleep(min(2 ** attempt, 16))
                continue
            raise
    raise RuntimeError("fetch_json retry exhausted")


def cache_bust(url: str) -> str:
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}_={int(dt.datetime.now().timestamp())}"


def parse_cards(html: str) -> list[dict]:
    chunks = CARD_SPLIT_RE.split(html)
    out: list[dict] = []
    # split() returns text before the first delimiter as chunks[0]; skip it.
    for chunk in chunks[1:]:
        m_id = ID_RE.search(chunk)
        m_thumb = THUMB_RE.search(chunk)
        if not (m_id and m_thumb):
            continue
        vid_id = m_id.group(1)
        thumb_hash = m_thumb.group(1)
        ts = int(m_thumb.group(2))
        title = (ALT_RE.search(chunk).group(1) if ALT_RE.search(chunk) else "").strip()
        dur = DURATION_RE.search(chunk)
        views = VIEWS_RE.search(chunk)
        tag = TAG_RE.search(chunk)
        out.append({
            "id": vid_id,
            "ts": ts,
            "title": title,
            "duration": dur.group(1) if dur else "",
            "views": int(views.group(1).replace(",", "")) if views else 0,
            "tag": tag.group(1).strip() if tag else "",
            "page": f"{BASE}/w/{vid_id}",
            "video": f"{BASE}/uploads/videos/{thumb_hash}_{ts}.mp4",
        })
    return out


def fetch_batch(offset: int, limit: int) -> tuple[list[dict], bool]:
    url = cache_bust(
        f"{BASE}/ajax/load_more_videos.php?offset={offset}&limit={limit}"
    )
    data = fetch_json(url)
    if not data.get("success"):
        return [], False
    cards = parse_cards(data.get("html", "") or "")
    return cards, bool(data.get("hasMore", False))


def collect_latest(
    *, max_hours: float | None, hard_limit: int, now: dt.datetime
) -> list[dict]:
    cutoff_ts = (
        int((now - dt.timedelta(hours=max_hours)).timestamp())
        if max_hours is not None
        else None
    )
    out: list[dict] = []
    offset = 0
    max_pages = 50
    for _ in range(max_pages):
        cards, has_more = fetch_batch(offset, BATCH_SIZE)
        if not cards:
            break
        out.extend(cards)
        if cutoff_ts is not None and any(c["ts"] < cutoff_ts for c in cards):
            break
        if len(out) >= hard_limit and max_hours is None:
            break
        if not has_more:
            break
        offset += BATCH_SIZE
    return out


def collect_all(max_pages: int = 500) -> list[dict]:
    """Walk every page until hasMore=False or empty batch. Dedupes by id."""
    seen: set[str] = set()
    out: list[dict] = []
    offset = 0
    for _ in range(max_pages):
        cards, has_more = fetch_batch(offset, BATCH_SIZE)
        if not cards:
            break
        for c in cards:
            if c["id"] not in seen:
                seen.add(c["id"])
                out.append(c)
        if not has_more:
            break
        offset += BATCH_SIZE
    return out


def fmt_age(seconds: float) -> str:
    minutes = seconds / 60.0
    if minutes < 60:
        return f"{int(minutes)}m"
    hours = minutes / 60.0
    if hours < 48:
        return f"{hours:.1f}h"
    return f"{hours / 24:.1f}d"


def _print_table(cards: list[dict], now: dt.datetime) -> None:
    if not cards:
        print("(no videos matched)")
        return
    print("| Age | Posted (UTC) | Views | Duration | Title | Tag | Video |")
    print("|---|---|---|---|---|---|---|")
    for c in cards:
        posted = dt.datetime.fromtimestamp(c["ts"], dt.timezone.utc)
        age = fmt_age((now - posted).total_seconds())
        title = c["title"].replace("|", "\\|")
        tag = c["tag"].replace("|", "\\|") or "-"
        video = c["video"].replace("|", "\\|")
        print(
            f"| {age} | {posted.strftime('%Y-%m-%d %H:%M')} | "
            f"{c['views']} | {c['duration'] or '?'} | "
            f"{title} | {tag} | {video} |"
        )


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_latest = sub.add_parser(
        "latest", help="newest uploads, optionally bounded by --hours"
    )
    p_latest.add_argument(
        "--hours", type=float, default=None,
        help="only include videos uploaded in the last N hours",
    )
    p_latest.add_argument(
        "--limit", type=int, default=50,
        help="hard cap on rows shown (default 50, ignored when --hours set)",
    )

    p_top = sub.add_parser(
        "top", help="most-viewed videos (full-catalogue scan)"
    )
    p_top.add_argument("--limit", type=int, default=10)

    args = ap.parse_args()

    now = dt.datetime.now(dt.timezone.utc)

    if args.cmd == "top":
        cards = collect_all()
        cards.sort(key=lambda c: c["views"], reverse=True)
        cards = cards[: args.limit]
        _print_table(cards, now)
        return

    cards = collect_latest(
        max_hours=args.hours, hard_limit=args.limit, now=now
    )

    if args.hours is not None:
        cutoff_ts = int((now - dt.timedelta(hours=args.hours)).timestamp())
        cards = [c for c in cards if c["ts"] >= cutoff_ts]

    cards.sort(key=lambda c: c["ts"], reverse=True)
    cards = cards[: args.limit]
    _print_table(cards, now)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
