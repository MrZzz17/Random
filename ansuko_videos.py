"""
ansuko_videos.py - List ansuko.net videos with direct mp4 URLs and English titles.

ansuko.net is a WordPress voyeur-clip site that self-hosts mp4 files on the
ansuko2.getducked.xyz CDN. The latest items are exposed via the standard
WordPress RSS feed (/feed/). For each item we fetch the post page and pull
the <source src=".../*.mp4"> URL out of the <video> tag.

Usage:
    python ansuko_videos.py latest --limit 10

Output: markdown table with columns Age, Title (JA), Title (EN), Video.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor


BASE = "https://ansuko.net"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
TIMEOUT = 25
WORKERS = 8

# self-hosted player markup: <source src="https://ansuko2.getducked.xyz/videos/<id>.mp4" type="video/mp4" ...>
SOURCE_MP4_RE = re.compile(
    r'<source[^>]+src="(https?://[^"]+\.mp4[^"]*)"[^>]*type="video/mp4"',
    re.I,
)
# external embed: <iframe id="video-iframe" src="https://gdplayer.to/embed2/...">
IFRAME_RE = re.compile(
    r'<iframe[^>]+id="video-iframe"[^>]+src="([^"]+)"',
    re.I,
)
# alt-player JS map: const players = { "GD1": "...", "lulu": "..." };
PLAYERS_MAP_RE = re.compile(
    r'const\s+players\s*=\s*\{([^}]+)\}',
    re.I,
)
PLAYER_PAIR_RE = re.compile(r'"([^"]+)"\s*:\s*"([^"]+)"')

# any direct media url (excluding trailers / thumbnails)
ANY_VIDEO_RE = re.compile(
    r'https?://[^\s"\'<>]+?\.(?:mp4|webm|m3u8)(?:\?[^\s"\'<>]*)?',
    re.I,
)


def _request(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Cache-Control": "no-cache", "Pragma": "no-cache"},
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read()


def cache_bust(url: str) -> str:
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}_={int(dt.datetime.now().timestamp())}"


def list_feed_items() -> list[dict]:
    raw = _request(cache_bust(f"{BASE}/feed/"))
    root = ET.fromstring(raw)
    channel = root.find("channel")
    if channel is None:
        return []
    items: list[dict] = []
    for it in channel.findall("item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        pub = (it.findtext("pubDate") or "").strip()
        items.append({"title": title, "link": link, "pubDate": pub})
    return items


def _decode_html_entities(s: str) -> str:
    # the WP markup HTML-encodes ampersands inside iframe srcs (`&#038;`)
    return s.replace("&#038;", "&").replace("&amp;", "&")


def _unescape_js_url(url: str) -> str:
    return _decode_html_entities(url).replace("\\/", "/")


# Preferred host order for which iframe to pick. luluvdoo first because it's
# the only one whose packed JS we can reliably unpack to a direct stream URL.
HOST_PREFERENCE = ("luluvdoo.com", "vide0.net", "savefiles.com", "gdplayer.to")

PACKER_HEAD = "eval(function(p,a,c,k,e,d)"


def _find_packed_eval(html: str) -> str | None:
    """Locate the full `eval(function(p,a,c,k,e,d){...}(...))` block via paren counting."""
    i = html.find(PACKER_HEAD)
    if i < 0:
        return None
    depth = 0
    for j in range(i, len(html)):
        ch = html[j]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return html[i : j + 1]
    return None


def _unpack_packer(eval_call: str) -> str:
    """Decode Dean-Edwards-style packed JS used by luluvdoo et al."""
    inner = eval_call.find("}(")
    if inner < 0:
        return ""
    depth = 0
    args_end = -1
    for j in range(inner + 1, len(eval_call)):
        if eval_call[j] == "(":
            depth += 1
        elif eval_call[j] == ")":
            depth -= 1
            if depth == 0:
                args_end = j
                break
    if args_end < 0:
        return ""
    args = eval_call[inner + 2 : args_end]
    m = re.match(
        r"'((?:[^'\\]|\\.)*)'\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*'((?:[^'\\]|\\.)*)'\.split",
        args,
        re.S,
    )
    if not m:
        return ""
    payload, base_s, count_s, words_blob = m.groups()
    base = int(base_s)
    count = int(count_s)
    payload = payload.encode().decode("unicode_escape")
    words = words_blob.split("|")

    chars = "0123456789abcdefghijklmnopqrstuvwxyz"

    def base_n(num: int) -> str:
        if num == 0:
            return "0"
        out = ""
        while num > 0:
            out = chars[num % base] + out
            num //= base
        return out

    for i in range(count - 1, -1, -1):
        if i < len(words) and words[i]:
            payload = re.sub(r"\b" + re.escape(base_n(i)) + r"\b", words[i], payload)
    return payload


def resolve_luluvdoo(embed_url: str) -> str | None:
    """Fetch a luluvdoo.com /e/<id> page and pull the underlying m3u8/mp4."""
    try:
        html = _request(embed_url).decode("utf-8", errors="replace")
    except Exception:
        return None
    packed = _find_packed_eval(html)
    if not packed:
        return None
    unpacked = _unpack_packer(packed)
    if not unpacked:
        return None
    # jwplayer setup contains: sources:[{file:"https://...m3u8"}]
    m = re.search(r'file:\s*"(https?://[^"]+\.(?:m3u8|mp4)[^"]*)"', unpacked)
    if m:
        return m.group(1)
    for url in ANY_VIDEO_RE.findall(unpacked):
        return url
    return None


def extract_video(page_url: str, resolve: bool = True) -> str:
    try:
        html = _request(page_url).decode("utf-8", errors="replace")
    except Exception as e:
        return f"ERROR: {e}"

    # 1) self-hosted mp4 wins
    m = SOURCE_MP4_RE.search(html)
    if m:
        return m.group(1)

    # 2) collect iframe candidates
    candidates: list[str] = []
    em = IFRAME_RE.search(html)
    if em:
        candidates.append(_decode_html_entities(em.group(1)))
    pm = PLAYERS_MAP_RE.search(html)
    if pm:
        for _label, url in PLAYER_PAIR_RE.findall(pm.group(1)):
            candidates.append(_unescape_js_url(url))

    seen: set[str] = set()
    uniq: list[str] = []
    for u in candidates:
        if u not in seen:
            seen.add(u)
            uniq.append(u)

    def host_rank(u: str) -> int:
        host = urllib.parse.urlparse(u).netloc
        try:
            return HOST_PREFERENCE.index(host)
        except ValueError:
            return len(HOST_PREFERENCE)

    uniq.sort(key=host_rank)

    if resolve:
        for u in uniq:
            if "luluvdoo.com" in u:
                resolved = resolve_luluvdoo(u)
                if resolved:
                    return resolved

    if uniq:
        # mark non-direct embed URLs so the user knows it's not a raw stream
        return f"[embed] {uniq[0]}"

    # 3) last-ditch
    for url in ANY_VIDEO_RE.findall(html):
        if "/trailers/" in url:
            continue
        return url

    return "(no video)"


_TRANSLATE_CACHE: dict[str, str] = {}


def translate_ja_en(text: str) -> str:
    """Best-effort JA->EN via Google Translate's free public endpoint."""
    if not text.strip():
        return text
    if text in _TRANSLATE_CACHE:
        return _TRANSLATE_CACHE[text]
    q = urllib.parse.quote(text)
    url = (
        "https://translate.googleapis.com/translate_a/single"
        f"?client=gtx&sl=ja&tl=en&dt=t&q={q}"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            data = json.load(r)
        en = "".join(seg[0] for seg in (data[0] or []) if seg and seg[0]).strip()
        if not en:
            en = text
    except Exception:
        en = text
    _TRANSLATE_CACHE[text] = en
    return en


def parse_pubdate(s: str) -> dt.datetime | None:
    # RFC 822: "Tue, 09 Dec 2025 04:02:15 +0000"
    try:
        return dt.datetime.strptime(s, "%a, %d %b %Y %H:%M:%S %z")
    except Exception:
        return None


def fmt_age(hours: float) -> str:
    if hours < 1:
        return f"{int(hours * 60)}m"
    if hours < 48:
        return f"{hours:.1f}h"
    return f"{hours / 24:.1f}d"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_latest = sub.add_parser("latest", help="newest videos from the RSS feed")
    p_latest.add_argument("--limit", type=int, default=10)
    p_latest.add_argument(
        "--no-resolve",
        action="store_true",
        help="don't follow iframe embeds (faster but returns embed URLs instead of m3u8)",
    )

    args = ap.parse_args()

    items = list_feed_items()
    items = items[: args.limit]

    if not items:
        print("(no items)")
        return

    now = dt.datetime.now(dt.timezone.utc)
    do_resolve = not getattr(args, "no_resolve", False)

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        videos = list(pool.map(lambda it: extract_video(it["link"], resolve=do_resolve), items))
        translations = list(pool.map(lambda it: translate_ja_en(it["title"]), items))

    print("| Age | Title (JA) | Title (EN) | Video |")
    print("|---|---|---|---|")
    for it, vid, en in zip(items, videos, translations):
        when = parse_pubdate(it["pubDate"])
        age = fmt_age((now - when).total_seconds() / 3600.0) if when else "?"
        title_ja = (it["title"] or "").replace("|", "\\|")
        title_en = (en or "").replace("|", "\\|")
        vid_cell = vid.replace("|", "\\|")
        print(f"| {age} | {title_ja} | {title_en} | {vid_cell} |")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
