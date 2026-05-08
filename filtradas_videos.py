"""
filtradas_videos.py - List filtradas.com videos with direct video URLs and English titles.

The site is a known Discourse forum hosting embedded mp4/webm videos (mostly on
streamfap.com and videj.com CDNs). This script never re-discovers what the site is;
it just hits the Discourse JSON endpoints directly, extracts the first video URL
from each topic's first post, and translates the Spanish title to English.

Usage:
    python filtradas_videos.py latest --hours 24
    python filtradas_videos.py latest --limit 30
    python filtradas_videos.py top   --limit 10
    python filtradas_videos.py oldest --limit 5

Output: a markdown table with columns Age, Views, Likes, Title (ES), Title (EN), Video.
Topics with no embedded video (image-only / promo posts) are still listed with "(no video)".
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor


BASE = "https://filtradas.com"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
TIMEOUT = 20
WORKERS = 3
FETCH_RETRIES = 6

VIDEO_RE = re.compile(r'https?://[^\s"\'<>]+?\.(?:mp4|webm|m3u8)(?:\?[^\s"\'<>]*)?', re.I)
IFRAME_RE = re.compile(r'<iframe[^>]+src="([^"]+)"', re.I)


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Cache-Control": "no-cache", "Pragma": "no-cache"},
    )
    for attempt in range(FETCH_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt + 1 < FETCH_RETRIES:
                time.sleep(min(2**attempt, 32))
                continue
            raise
    raise RuntimeError("fetch_json retry exhausted")


def cache_bust(url: str) -> str:
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}_={int(dt.datetime.now().timestamp())}"


def hours_since(iso_ts: str, now: dt.datetime) -> float:
    try:
        when = dt.datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
    except Exception:
        return float("inf")
    return (now - when).total_seconds() / 3600.0


def list_topics(
    mode: str,
    *,
    max_hours: float | None = None,
    now: dt.datetime | None = None,
    max_pages: int = 80,
) -> list[dict]:
    """mode: 'latest' | 'top' | 'oldest'.

    For 'latest', when max_hours is set, paginate until all topics on a page are older
    than max_hours (Discourse returns newest-first per page).
    """
    if mode == "latest":
        tz_now = now or dt.datetime.now(dt.timezone.utc)
        acc: list[dict] = []
        for page in range(max_pages):
            url = cache_bust(
                f"{BASE}/latest.json?order=created&ascending=false&page={page}"
            )
            data = fetch_json(url)
            batch = data.get("topic_list", {}).get("topics", []) or []
            if not batch:
                break
            acc.extend(batch)
            if max_hours is not None:
                oldest = batch[-1].get("created_at", "")
                if hours_since(oldest, tz_now) > max_hours:
                    break
        return acc
    if mode == "oldest":
        url = cache_bust(f"{BASE}/latest.json?order=created&ascending=true&page=0")
    elif mode == "top":
        url = cache_bust(f"{BASE}/top.json?period=all")
    else:
        raise ValueError(f"unknown mode: {mode}")
    data = fetch_json(url)
    return data.get("topic_list", {}).get("topics", []) or []


def extract_video(tid: int, slug: str) -> str:
    url = f"{BASE}/t/{slug}/{tid}.json"
    try:
        data = fetch_json(url)
    except Exception as e:
        return f"ERROR: {e}"
    posts = data.get("post_stream", {}).get("posts", [])
    if not posts:
        return "(no video)"
    cooked = posts[0].get("cooked", "") or ""
    seen: set[str] = set()
    out: list[str] = []
    for v in VIDEO_RE.findall(cooked):
        if v not in seen:
            seen.add(v)
            out.append(v)
    for ifr in IFRAME_RE.findall(cooked):
        if ifr not in seen:
            seen.add(ifr)
            out.append(ifr)
    return " | ".join(out) if out else "(no video)"


_TRANSLATE_CACHE: dict[str, str] = {}


def translate_es_en(text: str) -> str:
    """Best-effort ES->EN via Google Translate's free public endpoint.

    Falls back to the original text on any error so the script never breaks."""
    if not text.strip():
        return text
    if text in _TRANSLATE_CACHE:
        return _TRANSLATE_CACHE[text]
    q = urllib.parse.quote(text)
    url = (
        "https://translate.googleapis.com/translate_a/single"
        f"?client=gtx&sl=es&tl=en&dt=t&q={q}"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            data = json.load(r)
        # data[0] is a list of [translated_chunk, original_chunk, ...] arrays
        en = "".join(seg[0] for seg in (data[0] or []) if seg and seg[0])
        en = en.strip()
        if not en:
            en = text
    except Exception:
        en = text
    _TRANSLATE_CACHE[text] = en
    return en


def fmt_age(hours: float) -> str:
    if hours < 1:
        return f"{int(hours * 60)}m"
    if hours < 48:
        return f"{hours:.1f}h"
    return f"{hours / 24:.1f}d"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_latest = sub.add_parser("latest", help="newest topics, optionally bounded by --hours")
    p_latest.add_argument("--hours", type=float, default=None, help="only include topics from the last N hours")
    p_latest.add_argument("--limit", type=int, default=50, help="hard cap on topics returned (default 50)")

    p_top = sub.add_parser("top", help="most-viewed topics (all time)")
    p_top.add_argument("--limit", type=int, default=10)

    p_old = sub.add_parser("oldest", help="oldest topics on the site")
    p_old.add_argument("--limit", type=int, default=5)

    args = ap.parse_args()

    now = dt.datetime.now(dt.timezone.utc)
    max_hours = args.hours if args.cmd == "latest" else None
    topics = list_topics(args.cmd, max_hours=max_hours, now=now)

    if args.cmd == "latest":
        topics.sort(key=lambda t: t.get("created_at", ""), reverse=True)
        if args.hours is not None:
            topics = [
                t
                for t in topics
                if hours_since(t.get("created_at", ""), now) <= args.hours
            ]
        topics = topics[: args.limit]
    elif args.cmd == "top":
        topics.sort(key=lambda t: t.get("views", 0), reverse=True)
        topics = topics[: args.limit]
    elif args.cmd == "oldest":
        topics.sort(key=lambda t: t.get("created_at", ""))
        topics = topics[: args.limit]

    if not topics:
        print("(no topics matched)")
        return

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        videos = list(pool.map(lambda t: extract_video(t["id"], t["slug"]), topics))
        translations = list(pool.map(lambda t: translate_es_en(t.get("title", "")), topics))

    print("| Age | Views | Likes | Title (ES) | Title (EN) | Video |")
    print("|---|---|---|---|---|---|")
    for t, vid, en in zip(topics, videos, translations):
        age = fmt_age(hours_since(t.get("created_at", ""), now))
        title_es = (t.get("title") or "").replace("|", "\\|")
        title_en = (en or "").replace("|", "\\|")
        vid_cell = vid.replace("|", "\\|")
        print(
            f"| {age} | {t.get('views', 0)} | {t.get('like_count', 0)} | "
            f"{title_es} | {title_en} | {vid_cell} |"
        )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
