"""
vk_videos.py - Search VK Videos via the official VK API.

One-time setup:
  1. Sign in at https://vk.com  2. Create a Standalone app: https://vk.com/editapp?act=create
     - Type: Standalone application
     - Note the App ID (e.g. 1234567)
  3. Get a user access token via Implicit Flow. Open this URL in a browser
     while logged into VK (replace <APP_ID>):

       https://oauth.vk.com/authorize?client_id=<APP_ID>&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=video,offline&response_type=token&v=5.199

     After clicking Allow, the address bar will redirect to something like:

       https://oauth.vk.com/blank.html#access_token=vk1.a.XXXXXX&expires_in=0&user_id=...

     Copy the value between "access_token=" and "&". With the `offline` scope,
     `expires_in=0` means the token never expires.

  4. Save the token in ~/Documents/GitHub/Personal/Random/.env:
       VK_ACCESS_TOKEN=vk1.a.XXXXXX

Usage:
    python vk_videos.py search "query" --sort date --days 30 --sort-by-views
    python vk_videos.py search "интервью" --days 30 --sort-by-views --count 20
    python vk_videos.py search "музыка" --sort date --days 30 --sort-by-views
    python vk_videos.py search "casting hairy" --count 30
    python vk_videos.py get <owner_id>_<video_id>

New options for finding popular recent videos:
    --days N          Only include videos uploaded in last N days
    --sort-by-views   Sort results by view count (highest first)
    trending          New command: best-effort "most popular in last N days"

Output: a markdown table with columns Date, Duration, Views, Title, Page URL, Player URL.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


API_BASE = "https://api.vk.com/method"
API_VERSION = "5.199"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
TIMEOUT = 20

ENV_PATH = Path(__file__).resolve().parent / ".env"


def load_env() -> dict[str, str]:
    out: dict[str, str] = {}
    if not ENV_PATH.exists():
        return out
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def get_token() -> str:
    token = os.environ.get("VK_ACCESS_TOKEN") or load_env().get("VK_ACCESS_TOKEN", "")
    if not token:
        sys.exit(
            "ERROR: VK_ACCESS_TOKEN not found.\n"
            "Set it in ~/Documents/GitHub/Personal/Random/.env or export it.\n"
            "See the docstring at the top of this file for setup steps."
        )
    return token


def call(method: str, **params) -> dict:
    params.setdefault("v", API_VERSION)
    params.setdefault("access_token", get_token())
    url = f"{API_BASE}/{method}"
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        body = json.load(r)
    if "error" in body:
        err = body["error"]
        sys.exit(f"VK API error {err.get('error_code')}: {err.get('error_msg')}")
    return body.get("response", {})


def try_vk_call(method: str, **params) -> dict:
    """Same as `call` but return {} on API error (no sys.exit) — for `trending` fan-out."""
    try:
        params.setdefault("v", API_VERSION)
        params.setdefault("access_token", get_token())
        url = f"{API_BASE}/{method}"
        data = urllib.parse.urlencode(params).encode()
        req = urllib.request.Request(url, data=data, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            body = json.load(r)
        if "error" in body:
            return {}
        return body.get("response", {}) or {}
    except (OSError, json.JSONDecodeError, ValueError, urllib.error.HTTPError):
        return {}


def fmt_duration(secs: int) -> str:
    if not secs:
        return "?"
    h, rem = divmod(int(secs), 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def fmt_date(unix_ts: int) -> str:
    if not unix_ts:
        return "?"
    return dt.datetime.fromtimestamp(unix_ts, tz=dt.timezone.utc).strftime("%Y-%m-%d")


def fmt_count(n: int) -> str:
    n = int(n or 0)
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(n)


def page_url(item: dict) -> str:
    oid = item.get("owner_id")
    vid = item.get("id")
    return f"https://vkvideo.ru/video{oid}_{vid}"


def best_thumb(item: dict) -> str:
    """Return the largest thumbnail URL, or empty string."""
    images = item.get("image") or []
    if isinstance(images, list) and images:
        best = max(
            (img for img in images if isinstance(img, dict) and img.get("url")),
            key=lambda i: i.get("width", 0) * i.get("height", 0),
            default=None,
        )
        if best:
            return best.get("url", "")
    return ""


def video_quality(item: dict) -> int:
    """Return max available video height (e.g. 720, 1080), or 0 if unknown.

    VK returns either an explicit `height` field or a `files` dict with keys
    like `mp4_240`, `mp4_360`, `mp4_720`, `mp4_1080`. We prefer the files dict
    because `height` is sometimes the player canvas, not the source.
    """
    files = item.get("files", {}) or {}
    max_h = 0
    for key in files.keys():
        if key.startswith("mp4_"):
            try:
                v = int(key.split("_")[1])
                if v > max_h:
                    max_h = v
            except (ValueError, IndexError):
                pass
    if max_h:
        return max_h
    h = item.get("height", 0) or 0
    return int(h) if h else 0


def fmt_quality(h: int) -> str:
    if not h:
        return "?"
    if h >= 2160:
        return "4K"
    if h >= 1440:
        return "1440p"
    if h >= 1080:
        return "1080p"
    if h >= 720:
        return "720p"
    if h >= 480:
        return "480p"
    if h >= 360:
        return "360p"
    if h >= 240:
        return "240p"
    return f"{h}p"


def filter_by_quality(items: list[dict], min_q: int) -> list[dict]:
    if not min_q:
        return items
    return [it for it in items if video_quality(it) >= min_q]


def filter_by_days(items: list[dict], days: int) -> list[dict]:
    """Filter videos to only those uploaded within the last N days."""
    if not days or days <= 0:
        return items
    cutoff = int((dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).timestamp())
    return [item for item in items if item.get("date", 0) >= cutoff]


def paginate_owner_videos(owner_id: int, max_pages: int) -> list[dict]:
    """Return recent videos for one owner (community or user) via video.get.

    See cmd_user: VK may return ~90-100 items per call; advance offset by
    len(page_items). Stops at empty page or max_pages.
    """
    out: list[dict] = []
    seen: set[tuple[int, int]] = set()
    offset = 0
    for _ in range(max_pages):
        resp = try_vk_call(
            "video.get",
            owner_id=owner_id,
            count=200,
            offset=offset,
            extended=1,
        )
        page_items = resp.get("items", []) or []
        if not page_items:
            break
        for it in page_items:
            key = (it.get("owner_id", 0), it.get("id", 0))
            if key in seen:
                continue
            seen.add(key)
            out.append(it)
        offset += len(page_items)
    return out


def render(items: list[dict], verbose: bool = False) -> None:
    """Render markdown table.

    verbose=True adds Description (truncated) and Thumb columns — useful when
    multiple results have ambiguous titles and the user needs to cross-check
    with a description or visual thumbnail.
    """
    if not items:
        print("(no results)")
        return
    if verbose:
        print("| Date | Quality | Duration | Views | Title | Description | Thumb | Page |")
        print("|---|---|---|---|---|---|---|---|")
    else:
        print("| Date | Quality | Duration | Views | Title | Page | Player |")
        print("|---|---|---|---|---|---|---|")
    for it in items:
        title = (it.get("title") or "").replace("|", "\\|").replace("\n", " ").strip()[:120]
        q = fmt_quality(video_quality(it))
        if verbose:
            desc = (it.get("description") or "").replace("|", "\\|").replace("\n", " ").strip()[:200]
            thumb = best_thumb(it)
            print(
                f"| {fmt_date(it.get('date', 0))} "
                f"| {q} "
                f"| {fmt_duration(it.get('duration', 0))} "
                f"| {fmt_count(it.get('views', 0))} "
                f"| {title} "
                f"| {desc or '(none)'} "
                f"| {thumb or '(none)'} "
                f"| {page_url(it)} |"
            )
        else:
            player = (it.get("player") or "").replace("|", "\\|")
            print(
                f"| {fmt_date(it.get('date', 0))} "
                f"| {q} "
                f"| {fmt_duration(it.get('duration', 0))} "
                f"| {fmt_count(it.get('views', 0))} "
                f"| {title} "
                f"| {page_url(it)} "
                f"| {player or '(none)'} |"
            )


SORT_MAP = {"date": 0, "duration": 1, "relevance": 2, "popularity": 2}


def cmd_search(args) -> None:
    sort = SORT_MAP.get(args.sort, 2)
    resp = call(
        "video.search",
        q=args.query,
        sort=sort,
        hd=1 if args.hd else 0,
        adult=1 if args.adult else 0,
        count=min(args.count, 200),
        offset=args.offset,
        extended=1,
    )
    items = resp.get("items", []) or []
    if args.count_only:
        print(resp.get("count", 0))
        return

    raw = len(items)
    items = filter_by_quality(items, args.min_quality)
    items = filter_by_days(items, getattr(args, "days", 0))

    # Sort by views if requested (after date/quality filtering)
    if getattr(args, "sort_by_views", False):
        items.sort(key=lambda x: x.get("views", 0), reverse=True)
    elif getattr(args, "sort_by_quality", False):
        items.sort(key=lambda x: video_quality(x), reverse=True)

    print(
        f"<!-- {resp.get('count', 0)} total results, "
        f"{raw} returned, {len(items)} after filters "
        f"(days={getattr(args, 'days', 0)}, min_quality={args.min_quality}) -->"
    )
    render(items)


def cmd_trending(args) -> None:
    """Best-effort: most popular uploads in a time window.

    1) video.search — multiple queries with date and relevance sorts + offsets.
    2) groups.search — large public pages, then video.get per owner (like a
       channel's "Videos" tab) — this is how 500k+ recent hits surface.
    3) discover — Brave-indexed VK URLs, enriched via video.get.
    """
    days = args.days
    min_views = args.min_views
    target_count = args.count
    min_q = getattr(args, "min_quality", 0) or 0
    max_groups = getattr(args, "max_groups", 15)
    max_pages = getattr(args, "max_pages", 6)
    no_groups = getattr(args, "no_groups", False)

    print(
        f"<!-- trending: last {days}d, min {min_views} views, "
        f"max_groups={max_groups} max_pages/owner={max_pages} -->"
    )

    queries = [
        "",
        "интервью OR сатир OR мизулина",
        "КВН OR пародия",
        "новости OR политика",
        "токшоу OR подкаст",
    ]

    all_items: list[dict] = []
    seen: set[tuple[object, object]] = set()

    def _merge(items: list[dict]) -> None:
        for item in items:
            item = filter_by_quality([item], min_q)
            if not item:
                continue
            item = item[0]
            key = (item.get("owner_id"), item.get("id"))
            if key in seen:
                continue
            if int(item.get("views", 0) or 0) < min_views:
                continue
            seen.add(key)
            all_items.append(item)

    # --- Path A: global search (date + relevance, paginated) ---
    for q in queries:
        for sort_key in (0, 2):  # 0=date, 2=relevance/popularity
            for offset in (0, 100):
                resp = try_vk_call(
                    "video.search",
                    q=q,
                    sort=sort_key,
                    count=100,
                    offset=offset,
                    adult=1,
                    extended=1,
                )
                items = resp.get("items", []) or []
                if not items:
                    break
                for it in items:
                    if not filter_by_days([it], days):
                        continue
                    _merge([it])

    # --- Path B: high-subscriber group pages = channel-scale views ---
    if not no_groups and max_groups > 0:
        group_phrases = [
            "осторожно",
            "собчак",
            "интервью",
            "телеканал",
            "дудь",
            "страна",
            "новости",
        ]
        group_meta: dict[int, tuple[str, int]] = {}
        for phrase in group_phrases:
            resp = try_vk_call("groups.search", q=phrase, count=20, type="page")
            if not resp:
                continue
            for it in resp.get("items", []) or []:
                gid = -int(it.get("id", 0) or 0)
                if not gid:
                    continue
                mcount = int(it.get("members_count", 0) or 0)
                name = (it.get("name") or "")[:80]
                if gid not in group_meta or mcount > group_meta[gid][1]:
                    group_meta[gid] = (name, mcount)

        for owner_id, (gname, members) in sorted(
            group_meta.items(),
            key=lambda x: -x[1][1],
        )[:max_groups]:
            raw = paginate_owner_videos(owner_id, max_pages)
            if not raw and members > 0:
                print(
                    f"<!-- group {owner_id} {gname[:30]!r}: no video list (private/blocked) -->"
                )
            kept = 0
            for it in raw:
                if not filter_by_days([it], days):
                    continue
                _merge([it])
                kept += 1
            print(
                f"<!-- group {owner_id} {gname[:40]!r} ~{members} members: "
                f"scanned {len(raw)} videos, {kept} in window -->"
            )

    # --- Path C: Brave discover (optional coverage) ---
    try:
        pairs = brave_search_vk(
            "интервью site:vkvideo.ru OR site:vk.com/video",
            max_pages=3,
        )
        if pairs:
            videos_arg = ",".join(f"{o}_{v}" for o, v in pairs[:50])
            resp = try_vk_call("video.get", videos=videos_arg, extended=1)
            for it in resp.get("items", []) or []:
                if not filter_by_days([it], days):
                    continue
                _merge([it])
    except (OSError, Exception) as e:
        print(f"<!-- discover: {e} -->")

    all_items.sort(
        key=lambda x: (int(x.get("views", 0) or 0), int(x.get("date", 0) or 0)),
        reverse=True,
    )
    print(f"<!-- after merge: {len(all_items)} qualifying, showing {target_count} -->")
    render(all_items[: target_count])


def cmd_get(args) -> None:
    resp = call("video.get", videos=args.video_id, extended=1)
    items = resp.get("items", []) or []
    render(items, verbose=getattr(args, "verbose", False))


def cmd_user(args) -> None:
    """Paginate through an owner's full library, deduping by video id.

    VK's video.get returns ~90-100 items per call regardless of `count`,
    and adjacent pages occasionally overlap. We dedupe by (owner_id, id)
    and stop when no new items are added or we hit limits.
    """
    items: list[dict] = []
    seen: set[tuple[int, int]] = set()
    offset = args.offset
    total = None
    pages = 0
    while True:
        resp = call(
            "video.get",
            owner_id=args.owner_id,
            count=200,
            offset=offset,
            extended=1,
        )
        page_items = resp.get("items", []) or []
        if total is None:
            total = resp.get("count", 0) or 0
        if not page_items:
            break
        new_in_page = 0
        for it in page_items:
            key = (it.get("owner_id", 0), it.get("id", 0))
            if key in seen:
                continue
            seen.add(key)
            items.append(it)
            new_in_page += 1
            if len(items) >= args.count:
                break
        pages += 1
        offset += len(page_items)
        if (
            len(items) >= args.count
            or new_in_page == 0
            or (total and len(items) >= total)
            or pages >= 50
        ):
            break
    items = filter_by_quality(items, getattr(args, "min_quality", 0))
    if getattr(args, "sort_by_quality", False):
        items.sort(key=lambda x: video_quality(x), reverse=True)
    print(
        f"<!-- {total} total videos, showing {len(items)} unique "
        f"(paginated across {pages} call(s)) -->"
    )
    render(items[: args.count])


VIDEO_URL_RE = re.compile(r"https?://(?:vk\.com|vkvideo\.ru|m\.vk\.com)/video(-?\d+)_(\d+)")


def _brave_fetch(url: str) -> str:
    """GET a Brave Search URL with one retry on 429."""
    import time
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return r.read().decode("utf-8", errors="ignore")
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt == 0:
                time.sleep(4)
                continue
            return ""
        except Exception:
            return ""
    return ""


def brave_search_vk(query: str, max_pages: int = 3) -> list[tuple[int, int]]:
    """Return list of (owner_id, video_id) tuples discovered via Brave Search.

    Tries site:vk.com/video first (indexes NSFW community uploads that VK's
    own video.search endpoint hides), then site:vkvideo.ru as a top-up.
    """
    import time
    seen: set[tuple[int, int]] = set()
    results: list[tuple[int, int]] = []
    for site in ("vk.com/video", "vkvideo.ru"):
        for page in range(max_pages):
            offset = page * 20
            q = urllib.parse.quote_plus(f"{query} site:{site}")
            url = f"https://search.brave.com/search?q={q}&offset={offset}"
            html = _brave_fetch(url)
            if not html:
                time.sleep(2)
                continue
            page_hits = VIDEO_URL_RE.findall(html)
            if not page_hits:
                break
            new_this_page = 0
            for owner_str, vid_str in page_hits:
                key = (int(owner_str), int(vid_str))
                if key not in seen:
                    seen.add(key)
                    results.append(key)
                    new_this_page += 1
            if new_this_page == 0:
                break
            time.sleep(1)
    return results


def cmd_discover(args) -> None:
    """Use Brave Search to find VK videos, then enrich via VK API.
    
    Bypasses VK's video.search adult-content filter by relying on third-party
    indexing of public video pages.
    """
    print(f"<!-- discover '{args.query}' via Brave Search -->", flush=True)
    pairs = brave_search_vk(args.query, max_pages=args.pages)
    if not pairs:
        print("(no Brave results)")
        return
    pairs = pairs[: args.count]
    videos_arg = ",".join(f"{o}_{v}" for o, v in pairs)
    resp = call("video.get", videos=videos_arg, extended=1)
    items = resp.get("items", []) or []
    by_owner: dict[int, int] = {}
    for it in items:
        by_owner[it.get("owner_id", 0)] = by_owner.get(it.get("owner_id", 0), 0) + 1
    items = filter_by_quality(items, getattr(args, "min_quality", 0))
    if getattr(args, "sort_by_quality", False):
        items.sort(key=lambda x: video_quality(x), reverse=True)
    print(f"<!-- {len(pairs)} URLs from Brave, {len(items)} resolved by VK API -->")
    print(f"<!-- owners discovered: " + ", ".join(
        f"{oid} ({n})" for oid, n in sorted(by_owner.items(), key=lambda x: -x[1])
    ) + " -->")
    render(items)


KNOWN_OWNERS_PATH = Path(__file__).resolve().parent / "vk_known_owners.json"


def load_known_owners() -> dict[str, dict]:
    if not KNOWN_OWNERS_PATH.exists():
        return {}
    try:
        return json.loads(KNOWN_OWNERS_PATH.read_text())
    except Exception:
        return {}


def save_known_owners(data: dict) -> None:
    KNOWN_OWNERS_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def search_one_owner(
    owner_id: int, needle: str, max_pages: int, max_matches: int
) -> tuple[list[dict], int, int, str]:
    """Returns (matches, total_videos_scanned, total_count, error_msg)."""
    matches: list[dict] = []
    scanned = 0
    offset = 0
    pages = 0
    total = None
    err = ""
    while True:
        try:
            resp = call(
                "video.get",
                owner_id=owner_id,
                count=200,
                offset=offset,
                extended=1,
            )
        except SystemExit as e:
            err = str(e)
            break
        items = resp.get("items", []) or []
        if total is None:
            total = resp.get("count", 0) or 0
        if not items:
            break
        for it in items:
            scanned += 1
            hay = ((it.get("title") or "") + " " + (it.get("description") or "")).lower()
            if needle in hay:
                matches.append(it)
                if len(matches) >= max_matches:
                    break
        pages += 1
        offset += len(items)
        if (
            len(matches) >= max_matches
            or pages >= max_pages
            or (total and scanned >= total)
        ):
            break
    return matches, scanned, total or 0, err


def cmd_owner_search(args) -> None:
    """Paginate one owner's library and filter titles client-side by keyword.

    VK's video.get returns ~90-100 items per call regardless of the count
    parameter, so we advance offset by len(items), not by a fixed page size,
    and stop only when (a) we've reached the reported total count,
    (b) the API returns 0 items, or (c) we've hit max_pages.
    """
    needle = args.query.lower()
    matches: list[dict] = []
    scanned = 0
    offset = 0
    pages = 0
    total = None
    while True:
        resp = call(
            "video.get",
            owner_id=args.owner_id,
            count=200,
            offset=offset,
            extended=1,
        )
        items = resp.get("items", []) or []
        if total is None:
            total = resp.get("count", 0) or 0
        if not items:
            break
        for it in items:
            scanned += 1
            hay = ((it.get("title") or "") + " " + (it.get("description") or "")).lower()
            if needle in hay:
                matches.append(it)
                if len(matches) >= args.count:
                    break
        pages += 1
        offset += len(items)
        if (
            len(matches) >= args.count
            or pages >= args.max_pages
            or (total and scanned >= total)
        ):
            break
    matches = filter_by_quality(matches, getattr(args, "min_quality", 0))
    if getattr(args, "sort_by_quality", False):
        matches.sort(key=lambda x: video_quality(x), reverse=True)
    print(
        f"<!-- scanned {scanned}/{total} videos in owner {args.owner_id} "
        f"across {pages} page(s), {len(matches)} matches for '{args.query}' -->"
    )
    render(matches[: args.count])


def cmd_multi_search(args) -> None:
    """Run owner_search across many communities and aggregate results."""
    if args.owners:
        owners = [int(x.strip()) for x in args.owners.split(",") if x.strip()]
        labels = {oid: "" for oid in owners}
    else:
        known = load_known_owners()
        if not known:
            sys.exit(
                "No known owners. Add some with `owners_add` first or pass --owners."
            )
        owners = [int(k) for k in known.keys()]
        labels = {int(k): v.get("name", "") for k, v in known.items()}

    needle = args.query.lower()
    all_matches: list[dict] = []
    seen_ids: set[tuple[int, int]] = set()
    summary: list[tuple[int, str, int, int, int, str]] = []

    for oid in owners:
        if len(all_matches) >= args.total_cap:
            break
        per_owner_quota = min(args.count, args.total_cap - len(all_matches))
        matches, scanned, total, err = search_one_owner(
            oid, needle, args.max_pages, per_owner_quota
        )
        new_count = 0
        for m in matches:
            key = (m.get("owner_id", 0), m.get("id", 0))
            if key not in seen_ids:
                seen_ids.add(key)
                all_matches.append(m)
                new_count += 1
        summary.append((oid, labels.get(oid, ""), total, scanned, new_count, err))

    print(
        f"<!-- multi_search '{args.query}' across {len(summary)} owner(s); "
        f"{sum(s[3] for s in summary):,} videos scanned; "
        f"{len(all_matches)} unique matches -->"
    )
    print("<!-- per-owner: -->")
    for oid, label, total, scanned, hits, err in summary:
        suffix = f" ERR:{err}" if err else ""
        print(f"<!--   {oid} ({label[:50]}): {hits} hits in {scanned}/{total}{suffix} -->")
    all_matches = filter_by_quality(all_matches, getattr(args, "min_quality", 0))
    if getattr(args, "sort_by_quality", False):
        all_matches.sort(key=lambda x: video_quality(x), reverse=True)
    else:
        all_matches.sort(key=lambda x: x.get("date", 0), reverse=True)
    print(f"<!-- after quality filter: {len(all_matches)} -->")
    render(all_matches[: args.total_cap])


def cmd_owners_add(args) -> None:
    known = load_known_owners()
    new_ids = [int(x.strip()) for x in args.owner_ids.split(",") if x.strip()]
    for oid in new_ids:
        try:
            resp = call("video.get", owner_id=oid, count=1, extended=1)
            total = resp.get("count", 0) or 0
            sample = ""
            items = resp.get("items") or []
            if items:
                sample = (items[0].get("title") or "")[:80]
        except SystemExit as e:
            total = 0
            sample = f"ERR: {e}"
        known[str(oid)] = {
            "name": sample,
            "total_videos": total,
            "added_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        }
        print(f"+ {oid}: {total} videos | {sample[:60]}")
    save_known_owners(known)
    print(f"\nSaved {len(known)} owners to {KNOWN_OWNERS_PATH}")


def cmd_owners_list(args) -> None:
    known = load_known_owners()
    if not known:
        print("(no known owners; use `owners_add <ids>` to add)")
        return
    rows = sorted(
        known.items(), key=lambda kv: kv[1].get("total_videos", 0), reverse=True
    )
    print("| Owner ID | Videos | Sample / Name |")
    print("|---|---|---|")
    for oid, info in rows:
        n = info.get("total_videos", 0)
        name = (info.get("name") or "").replace("|", "\\|")[:80]
        print(f"| {oid} | {n} | {name} |")
    print(f"\nTotal: {sum(v.get('total_videos', 0) for v in known.values()):,} videos across {len(known)} communities")


def cmd_resolve(args) -> None:
    """Bulk-resolve VK video URLs/IDs from arbitrary pasted text.

    Reads from stdin if no positional arg given. Accepts any messy mix of
    URLs, ids, search-result snippets, etc. — extracts every (owner_id,
    video_id) pair, dedupes, calls video.get to enrich, renders a markdown
    table, and (unless --no-add) auto-adds discovered owners to
    vk_known_owners.json.
    """
    text = args.text or sys.stdin.read()
    pairs: list[tuple[int, int]] = []
    seen: set[tuple[int, int]] = set()
    pattern = re.compile(
        r"(?:video|video[›\s])\s*(-?\d+)[_\s]+(\d+)|"
        r"(?:vk\.com|vkvideo\.ru|m\.vk\.com)[/\s]+video(-?\d+)_(\d+)",
        re.IGNORECASE,
    )
    for m in pattern.finditer(text):
        oid = int(m.group(1) or m.group(3))
        vid = int(m.group(2) or m.group(4))
        key = (oid, vid)
        if key not in seen:
            seen.add(key)
            pairs.append(key)
    if not pairs:
        print("(no VK video URLs found in input)")
        return
    print(f"<!-- extracted {len(pairs)} unique video IDs -->", flush=True)
    videos_arg = ",".join(f"{o}_{v}" for o, v in pairs)
    BATCH = 100
    items: list[dict] = []
    for i in range(0, len(pairs), BATCH):
        batch_arg = ",".join(f"{o}_{v}" for o, v in pairs[i : i + BATCH])
        resp = call("video.get", videos=batch_arg, extended=1)
        items.extend(resp.get("items", []) or [])
    by_owner: dict[int, int] = {}
    for it in items:
        oid = it.get("owner_id", 0)
        by_owner[oid] = by_owner.get(oid, 0) + 1
    print(
        f"<!-- resolved {len(items)} videos via VK API; "
        f"{len(by_owner)} unique owners -->"
    )
    print("<!-- owners discovered: " + ", ".join(
        f"{oid} ({n})" for oid, n in sorted(by_owner.items(), key=lambda x: -x[1])
    ) + " -->")
    items.sort(key=lambda x: x.get("date", 0), reverse=True)
    render(items, verbose=getattr(args, "verbose", False))
    if not args.no_add and by_owner:
        known = load_known_owners()
        new_count = 0
        for oid, n in by_owner.items():
            if str(oid) not in known:
                sample_title = ""
                for it in items:
                    if it.get("owner_id") == oid:
                        sample_title = (it.get("title") or "")[:80]
                        break
                try:
                    r = call("video.get", owner_id=oid, count=1, extended=1)
                    total = r.get("count", 0) or 0
                except SystemExit:
                    total = n
                known[str(oid)] = {
                    "name": sample_title,
                    "total_videos": total,
                    "added_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                }
                new_count += 1
        if new_count:
            save_known_owners(known)
            print(f"<!-- added {new_count} new owners to known list -->")


def cmd_groups_search(args) -> None:
    resp = call("groups.search", q=args.query, count=args.count, type="page")
    items = resp.get("items", []) or []
    print(f"<!-- {resp.get('count', 0)} total groups, showing {len(items)} -->")
    print("| Owner ID | Members | Name |")
    print("|---|---|---|")
    for it in items:
        gid = -it.get("id", 0)
        members = it.get("members_count", "?")
        name = (it.get("name") or "").replace("|", "\\|")[:100]
        print(f"| {gid} | {members} | {name} |")


def add_quality_args(p):
    p.add_argument(
        "--min-quality",
        type=int,
        default=0,
        metavar="HEIGHT",
        help="filter out videos below this height (e.g. 480, 720, 1080)",
    )
    p.add_argument(
        "-Q",
        "--sort-by-quality",
        action="store_true",
        help="sort results by max-available quality (highest first)",
    )


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_s = sub.add_parser("search", help="search all of VK Video")
    p_s.add_argument("query", help='search query, e.g. "casting hairy"')
    p_s.add_argument("--count", type=int, default=30, help="max results (1-200)")
    p_s.add_argument("--offset", type=int, default=0)
    p_s.add_argument(
        "--sort",
        choices=["date", "duration", "relevance", "popularity"],
        default="relevance",
    )
    p_s.add_argument("--hd", action="store_true", help="HD only (VK-side filter)")
    p_s.add_argument(
        "--adult", action="store_true", help="include 18+ results (default off)"
    )
    p_s.add_argument(
        "--count-only", action="store_true", help="only print total result count"
    )
    p_s.add_argument(
        "--days",
        type=int,
        default=0,
        help="only include videos uploaded in the last N days (client-side filter)",
    )
    p_s.add_argument(
        "--sort-by-views",
        action="store_true",
        help="sort results by view count descending (after date filtering)",
    )
    add_quality_args(p_s)
    p_s.set_defaults(func=cmd_search)

    p_g = sub.add_parser("get", help="get info for one video by id like -12345_67890")
    p_g.add_argument("video_id")
    p_g.add_argument(
        "-v", "--verbose", action="store_true",
        help="include description + thumbnail URL columns",
    )
    p_g.set_defaults(func=cmd_get)

    p_u = sub.add_parser(
        "user_videos", help="list videos uploaded by a user/community owner_id"
    )
    p_u.add_argument("owner_id", help="user id (positive) or community id (negative)")
    p_u.add_argument("--count", type=int, default=30)
    p_u.add_argument("--offset", type=int, default=0)
    add_quality_args(p_u)
    p_u.set_defaults(func=cmd_user)

    p_d = sub.add_parser(
        "discover",
        help="search by keyword via Brave Search (bypasses VK's adult-content filter)",
    )
    p_d.add_argument("query", help='free-text query, e.g. "woodman casting x"')
    p_d.add_argument("--count", type=int, default=30, help="max videos to enrich")
    p_d.add_argument("--pages", type=int, default=3, help="Brave result pages to scan")
    add_quality_args(p_d)
    p_d.set_defaults(func=cmd_discover)

    p_os = sub.add_parser(
        "owner_search",
        help="filter one owner's full library by keyword (client-side)",
    )
    p_os.add_argument("owner_id", help="user id (positive) or community id (negative)")
    p_os.add_argument("query", help='keyword to find in titles/descriptions')
    p_os.add_argument("--count", type=int, default=30, help="max matches to return")
    p_os.add_argument(
        "--max-pages", type=int, default=20, help="hard cap on pages scanned"
    )
    add_quality_args(p_os)
    p_os.set_defaults(func=cmd_owner_search)

    p_m = sub.add_parser(
        "multi_search",
        help="filter MANY owners' libraries by keyword and aggregate results",
    )
    p_m.add_argument("query", help='keyword to find in titles/descriptions')
    p_m.add_argument(
        "--owners",
        help="comma-separated owner IDs; defaults to vk_known_owners.json",
    )
    p_m.add_argument("--count", type=int, default=100, help="max matches per owner")
    p_m.add_argument("--max-pages", type=int, default=60, help="hard cap per owner")
    p_m.add_argument("--total-cap", type=int, default=500, help="overall match cap")
    add_quality_args(p_m)
    p_m.set_defaults(func=cmd_multi_search)

    p_oa = sub.add_parser(
        "owners_add",
        help="add owner_ids to vk_known_owners.json (with auto-fetched names)",
    )
    p_oa.add_argument("owner_ids", help="comma-separated owner IDs to add")
    p_oa.set_defaults(func=cmd_owners_add)

    p_ol = sub.add_parser("owners_list", help="show known owners and video totals")
    p_ol.set_defaults(func=cmd_owners_list)

    p_gs = sub.add_parser(
        "groups_search", help="search VK groups/communities by name"
    )
    p_gs.add_argument("query")
    p_gs.add_argument("--count", type=int, default=50)
    p_gs.set_defaults(func=cmd_groups_search)

    p_r = sub.add_parser(
        "resolve",
        help="bulk-extract VK video IDs from arbitrary pasted text and enrich",
    )
    p_r.add_argument(
        "text",
        nargs="?",
        help="text to parse (omit to read from stdin)",
    )
    p_r.add_argument(
        "--no-add",
        action="store_true",
        help="don't add discovered owners to vk_known_owners.json",
    )
    p_r.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="include description + thumbnail URL columns for cross-checking",
    )
    add_quality_args(p_r)
    p_r.set_defaults(func=cmd_resolve)

    p_t = sub.add_parser(
        "trending",
        help="best-effort most popular videos in last N days (tries multiple strategies)",
    )
    p_t.add_argument("--days", type=int, default=30, help="number of days to look back")
    p_t.add_argument("--count", type=int, default=15, help="max results to return")
    p_t.add_argument(
        "--min-views", type=int, default=1000, help="minimum views to include"
    )
    p_t.add_argument(
        "--max-groups",
        type=int,
        default=15,
        help="top N communities by members to scan (group library path)",
    )
    p_t.add_argument(
        "--max-pages",
        type=int,
        default=6,
        help="max video.get pages per group (~100 videos/page on VK)",
    )
    p_t.add_argument(
        "--no-groups",
        action="store_true",
        help="skip groups.search + owner library scan (search + discover only)",
    )
    add_quality_args(p_t)
    p_t.set_defaults(func=cmd_trending)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
