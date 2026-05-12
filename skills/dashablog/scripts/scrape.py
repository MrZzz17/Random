"""
scrape.py - Bulk download files of given extension(s) from a website.

Subcommands:
    scan       Crawl the site and list qualifying files (>= MIN_FILE_SIZE_BYTES)
    download   Fetch the URLs from the previous scan into per-post folders
    crawl      One-shot: scan + download inline (default)
    dedupe     Remove duplicate filenames across folders, prefer post folders
    clean      Remove empty folders and .DS_Store files
    all        crawl --> dedupe --> clean

Common flags:
    --url URL              override START_URL
    --ext EXT[,EXT...]     override FILE_EXTS (e.g. jpg or mp4,webm)
    --depth N              override MAX_DEPTH
    --output PATH          override OUTPUT_DIR
    --min-size-kb N        override MIN_FILE_SIZE_BYTES
    --fresh                disable incremental skipping (re-crawl everything)
    --posts-only           skip files only found on category/tag/page/home pages
    --allow-hosts H[,H...] also download files hosted on these other hosts
                           (e.g. CDN/streamfap.com); crawl stays on START_URL host
    --post-pattern REGEX   regex matched against url.path that marks a page as a
                           post (e.g. '^/t/([^/]+)/\\d+$' for Discourse). Capture
                           group 1, if present, is used as the post-folder slug.

By default crawl/scan run in INCREMENTAL mode: post pages whose destination
folder already exists on disk are skipped (no fetch, no re-download).

Strategy:
    1. BFS crawl from START_URL up to MAX_DEPTH levels deep.
    2. Stay on the same host for *crawling* (no wandering off-site). File URLs
       can come from --allow-hosts.
    3. On each page, find <a href>, <img src/data-*/srcset>, <video src>,
       and <source src/srcset> links.
    4. If a link ends in one of FILE_EXTS -> candidate.
    5. If a link is an HTML page on the same host -> add to crawl queue.
    6. Be polite: delay between requests, sane User-Agent, respect robots.txt.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.robotparser
from collections import Counter, defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse

import requests
from bs4 import BeautifulSoup


START_URL = "https://example.com"
FILE_EXTS: list[str] = ["jpg"]
MAX_DEPTH = 2
OUTPUT_DIR = Path.home() / "Documents" / "Personal"
SCAN_RESULTS_FILE = Path("./scan_results.json")
ALLOW_HOSTS: set[str] = set()
POST_PATTERN: re.Pattern[str] | None = None

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
REQUEST_TIMEOUT = 20
POLITE_DELAY_SEC = 0.2
HEAD_WORKERS = 16
DOWNLOAD_WORKERS = 8
MIN_FILE_SIZE_BYTES = 100 * 1024


def same_host(url: str, root: str) -> bool:
    return urlparse(url).netloc == urlparse(root).netloc


def looks_like_html(url: str) -> bool:
    path = urlparse(url).path.lower()
    if path.endswith("/") or path == "":
        return True
    suffix = Path(path).suffix
    return suffix in {"", ".html", ".htm", ".php", ".asp", ".aspx"}


def has_ext(url: str, exts: str | list[str]) -> bool:
    path = urlparse(url).path.lower()
    if isinstance(exts, str):
        exts = [exts]
    for e in exts:
        if path.endswith(f".{e.lower().lstrip('.')}"):
            return True
    return False


def is_downloadable_host(url: str, root: str) -> bool:
    """File URL is allowed if same host as root, or in ALLOW_HOSTS."""
    host = urlparse(url).netloc
    return host == urlparse(root).netloc or host in ALLOW_HOSTS


_SLUG_SAFE = "-_."


def page_slug(page_url: str) -> str:
    """Derive a folder name from the page URL where an image was found.

    If POST_PATTERN matches and has a capture group, use that group as the slug.
    Otherwise prefer single-segment WordPress post paths (e.g. /kristina-fey-bows03/ -> "kristina-fey-bows03").
    Falls back to a sanitized version of the path/query for category/tag/paginated pages.
    Empty path (homepage) -> "_home".
    """
    parsed = urlparse(page_url)
    if POST_PATTERN is not None:
        m = POST_PATTERN.match(parsed.path)
        if m and m.groups():
            slug = m.group(1)
            cleaned = "".join(ch if ch.isalnum() or ch in _SLUG_SAFE else "-" for ch in slug)
            cleaned = cleaned.strip("-") or "_misc"
            return cleaned[:120]
    path = parsed.path.strip("/")
    if not path and parsed.query:
        slug = parsed.query.replace("=", "-").replace("&", "-")
    elif not path:
        return "_home"
    else:
        slug = path.replace("/", "-")
    cleaned = "".join(ch if ch.isalnum() or ch in _SLUG_SAFE else "-" for ch in slug)
    cleaned = cleaned.strip("-") or "_misc"
    return cleaned[:120]


def is_post_page(page_url: str) -> bool:
    """Heuristic: a single-segment, non-special path looks like an individual post.
    If POST_PATTERN is set, that regex (against url.path) takes precedence."""
    parsed = urlparse(page_url)
    if POST_PATTERN is not None:
        return POST_PATTERN.match(parsed.path) is not None
    path = parsed.path.strip("/")
    if not path or "/" in path:
        return False
    if parsed.query:
        return False
    if path in {"page", "tag", "category", "author", "feed", "wp-admin", "wp-content"}:
        return False
    return True


def post_folder_done(out_dir: Path, page_url: str) -> bool:
    """True if `page_url` looks like a post AND its destination folder already
    exists with at least one file. Used to skip re-crawling already-downloaded posts."""
    if not is_post_page(page_url):
        return False
    parsed = urlparse(page_url)
    folder = out_dir / parsed.netloc / page_slug(page_url)
    if not folder.is_dir():
        return False
    try:
        return any(folder.iterdir())
    except OSError:
        return False


def safe_dest(out_dir: Path, url: str, page_url: str | None = None) -> Path:
    parsed = urlparse(url)
    filename = Path(parsed.path).name or "index"
    folder = page_slug(page_url) if page_url else "_misc"
    # Anchor by the page's host so cross-host files (e.g. CDN, video host)
    # land in the same per-post folder as the page that referenced them.
    if page_url:
        host = urlparse(page_url).netloc or parsed.netloc
    else:
        host = parsed.netloc
    dest = out_dir / host / folder / filename
    dest.parent.mkdir(parents=True, exist_ok=True)
    return dest


def load_robots(
    session: requests.Session, root: str
) -> urllib.robotparser.RobotFileParser:
    rp = urllib.robotparser.RobotFileParser()
    robots_url = urljoin(root, "/robots.txt")
    rp.set_url(robots_url)
    try:
        r = session.get(robots_url, timeout=REQUEST_TIMEOUT)
        if r.status_code == 200:
            rp.parse(r.text.splitlines())
        elif r.status_code in (401, 403):
            rp.disallow_all = True
        else:
            rp.allow_all = True
    except requests.RequestException:
        rp.allow_all = True
    return rp


def extract_candidates(soup: BeautifulSoup) -> list[str]:
    candidates: list[str] = []
    for a in soup.find_all("a", href=True):
        candidates.append(a["href"])
    for img in soup.find_all("img"):
        for attr in ("src", "data-src", "data-lazy-src", "data-original"):
            val = img.get(attr)
            if val:
                candidates.append(val)
        srcset = img.get("srcset")
        if srcset:
            for part in srcset.split(","):
                candidate = part.strip().split(" ")[0]
                if candidate:
                    candidates.append(candidate)
    for video in soup.find_all("video"):
        for attr in ("src", "data-src"):
            val = video.get(attr)
            if val:
                candidates.append(val)
    for source in soup.find_all("source"):
        for attr in ("src", "data-src"):
            val = source.get(attr)
            if val:
                candidates.append(val)
        srcset = source.get("srcset")
        if srcset:
            for part in srcset.split(","):
                candidate = part.strip().split(" ")[0]
                if candidate:
                    candidates.append(candidate)
    return candidates


def crawl_for_files(
    start_url: str,
    exts: str | list[str],
    depth: int,
    incremental_out_dir: Path | None = None,
) -> tuple[dict[str, str], urllib.robotparser.RobotFileParser, requests.Session]:
    """BFS the site and return {file_url: best_page_url} (no size check yet).

    If `incremental_out_dir` is given, post pages whose destination folder already
    exists with content are skipped (no fetch, no link extraction)."""
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT

    robots = load_robots(session, start_url)
    seen_pages: set[str] = set()
    file_to_page: dict[str, str] = {}
    skipped_done = 0
    queue: deque[tuple[str, int]] = deque([(start_url, 0)])

    while queue:
        url, level = queue.popleft()
        url, _ = urldefrag(url)

        if url in seen_pages:
            continue
        seen_pages.add(url)

        if not robots.can_fetch(USER_AGENT, url):
            print(f"[skip:robots] {url}")
            continue

        if incremental_out_dir is not None and post_folder_done(
            incremental_out_dir, url
        ):
            skipped_done += 1
            print(f"[skip:done] {url}")
            continue

        try:
            print(f"[crawl L{level}] {url}")
            r = session.get(url, timeout=REQUEST_TIMEOUT)
        except requests.RequestException as e:
            print(f"[error] {url} -> {e}")
            continue

        time.sleep(POLITE_DELAY_SEC)

        ctype = r.headers.get("content-type", "").lower()
        if "html" not in ctype:
            continue

        soup = BeautifulSoup(r.text, "html.parser")
        page_is_post = is_post_page(url)
        for raw in extract_candidates(soup):
            link = urljoin(url, raw)
            link, _ = urldefrag(link)

            if not link.startswith(("http://", "https://")):
                continue

            if has_ext(link, exts):
                if not is_downloadable_host(link, start_url):
                    continue
                existing = file_to_page.get(link)
                if existing is None or (page_is_post and not is_post_page(existing)):
                    file_to_page[link] = url
            elif (
                level < depth
                and same_host(link, start_url)
                and looks_like_html(link)
                and link not in seen_pages
            ):
                queue.append((link, level + 1))

    ext_label = ",".join(exts) if isinstance(exts, list) else exts
    print(
        f"\nCrawled {len(seen_pages) - skipped_done} pages "
        f"(skipped {skipped_done} already-downloaded posts), "
        f"found {len(file_to_page)} .{ext_label} URLs."
    )
    return file_to_page, robots, session


def head_size(
    session: requests.Session, url: str
) -> int | None:
    """Return Content-Length from HEAD (falling back to a ranged GET). None if unknown."""
    try:
        r = session.head(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        cl = r.headers.get("content-length")
        if cl is not None:
            try:
                return int(cl)
            except ValueError:
                pass
    except requests.RequestException:
        pass

    try:
        r = session.get(
            url,
            timeout=REQUEST_TIMEOUT,
            stream=True,
            headers={"Range": "bytes=0-0"},
        )
        cr = r.headers.get("content-range")
        if cr and "/" in cr:
            total = cr.rsplit("/", 1)[-1]
            if total.isdigit():
                return int(total)
        cl = r.headers.get("content-length")
        if cl is not None and r.status_code == 200:
            try:
                return int(cl)
            except ValueError:
                pass
    except requests.RequestException:
        pass

    return None


def cmd_scan(fresh: bool = False, posts_only: bool = False) -> int:
    file_to_page, _robots, session = crawl_for_files(
        START_URL,
        FILE_EXTS,
        MAX_DEPTH,
        incremental_out_dir=None if fresh else OUTPUT_DIR,
    )
    if posts_only:
        before = len(file_to_page)
        file_to_page = {
            u: p for u, p in file_to_page.items() if is_post_page(p)
        }
        print(
            f"[posts-only] kept {len(file_to_page)}/{before} files "
            f"(dropped {before - len(file_to_page)} from category/tag/page/home)"
        )

    print(
        f"\nProbing sizes for {len(file_to_page)} candidates "
        f"({HEAD_WORKERS} workers in parallel)...\n"
    )
    t0 = time.time()
    sized: list[dict] = []
    done = 0
    total = len(file_to_page)
    with ThreadPoolExecutor(max_workers=HEAD_WORKERS) as pool:
        future_to_url = {
            pool.submit(head_size, session, u): u for u in file_to_page
        }
        for fut in as_completed(future_to_url):
            url = future_to_url[fut]
            try:
                size = fut.result()
            except Exception as e:
                size = None
                print(f"[head-error] {url} -> {e}")

            include = size is None or size >= MIN_FILE_SIZE_BYTES
            if include:
                sized.append(
                    {"url": url, "size": size, "page": file_to_page[url]}
                )
            done += 1
            if done % 50 == 0 or done == total:
                print(f"  probed {done}/{total} (qualifying so far: {len(sized)})")

    elapsed = time.time() - t0
    print(f"\nHEAD probes done in {elapsed:.1f}s.")

    SCAN_RESULTS_FILE.write_text(json.dumps(sized, indent=2))

    folder_counts: Counter[str] = Counter()
    for item in sized:
        folder_counts[page_slug(item["page"])] += 1

    print(
        f"\nQualifying files (>= {MIN_FILE_SIZE_BYTES // 1024} KB or unknown): "
        f"{len(sized)} of {total}\n"
    )
    print("Files per folder:")
    width = max((len(f) for f in folder_counts), default=1)
    for folder, count in sorted(
        folder_counts.items(), key=lambda kv: (-kv[1], kv[0])
    ):
        print(f"  {folder:<{width}}  {count}")

    print(f"\nList written to {SCAN_RESULTS_FILE.resolve()}")
    print(f"Run `python {Path(__file__).name} download` to fetch them.")
    return 0


def cmd_download(posts_only: bool = False) -> int:
    if not SCAN_RESULTS_FILE.exists():
        print(
            f"No {SCAN_RESULTS_FILE} found. Run `scan` first.",
            file=sys.stderr,
        )
        return 1

    items = json.loads(SCAN_RESULTS_FILE.read_text())
    if posts_only:
        before = len(items)
        items = [it for it in items if is_post_page(it.get("page", ""))]
        print(
            f"[posts-only] kept {len(items)}/{before} files "
            f"(dropped {before - len(items)} from category/tag/page/home)"
        )
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    robots = load_robots(session, START_URL)

    print(
        f"Downloading {len(items)} files into {OUTPUT_DIR.resolve()} "
        f"({DOWNLOAD_WORKERS} workers in parallel)\n"
    )
    _parallel_download(
        session,
        [(item["url"], item.get("page")) for item in items],
        OUTPUT_DIR,
        robots,
    )
    return 0


def cmd_crawl(fresh: bool = False, posts_only: bool = False) -> int:
    """Crawl and download inline. By default skips post pages whose folder is
    already on disk (incremental). Pass --fresh to force a full re-crawl.
    Pass --posts-only to skip files that only appear on category/tag/page/home
    listing pages (no category-* / tag-* / page-* / _home folders)."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    mode = "fresh" if fresh else "incremental"
    extra = " posts-only" if posts_only else ""
    ext_label = ",".join(FILE_EXTS)
    print(
        f"Crawling {START_URL} for .{ext_label} files "
        f"(depth={MAX_DEPTH}, mode={mode}{extra})"
    )
    print(f"Saving to {OUTPUT_DIR.resolve()}\n")

    file_to_page, robots, session = crawl_for_files(
        START_URL,
        FILE_EXTS,
        MAX_DEPTH,
        incremental_out_dir=None if fresh else OUTPUT_DIR,
    )
    if posts_only:
        before = len(file_to_page)
        file_to_page = {
            u: p for u, p in file_to_page.items() if is_post_page(p)
        }
        print(
            f"[posts-only] kept {len(file_to_page)}/{before} files "
            f"(dropped {before - len(file_to_page)} from category/tag/page/home)"
        )
    print(
        f"\nDownloading {len(file_to_page)} candidates "
        f"({DOWNLOAD_WORKERS} workers in parallel)...\n"
    )
    _parallel_download(
        session,
        [(url, file_to_page[url]) for url in sorted(file_to_page)],
        OUTPUT_DIR,
        robots,
    )
    return 0


def _parallel_download(
    session: requests.Session,
    items: list[tuple[str, str | None]],
    out_dir: Path,
    robots: urllib.robotparser.RobotFileParser,
) -> tuple[int, int, int]:
    saved = skipped = errored = 0
    total = len(items)
    done = 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=DOWNLOAD_WORKERS) as pool:
        futures = [
            pool.submit(download_file, session, url, out_dir, robots, page_url=page)
            for url, page in items
        ]
        for fut in as_completed(futures):
            try:
                result = fut.result()
            except Exception as e:
                result = "error"
                print(f"[error] worker exception: {e}")

            if result == "saved":
                saved += 1
            elif result == "error":
                errored += 1
            else:
                skipped += 1

            done += 1
            if done % 100 == 0 or done == total:
                rate = done / max(time.time() - t0, 0.001)
                print(
                    f"  progress {done}/{total}  "
                    f"saved={saved} skipped={skipped} errored={errored}  "
                    f"({rate:.1f}/s)"
                )

    print(
        f"\nDone. saved={saved}, skipped={skipped}, errored={errored}, "
        f"total={total}"
    )
    return saved, skipped, errored


def download_file(
    session: requests.Session,
    url: str,
    out_dir: Path,
    robots: urllib.robotparser.RobotFileParser,
    page_url: str | None = None,
) -> str:
    if not robots.can_fetch(USER_AGENT, url):
        print(f"[skip:robots] {url}")
        return "skipped"

    dest = safe_dest(out_dir, url, page_url)
    if dest.exists():
        if dest.stat().st_size >= MIN_FILE_SIZE_BYTES:
            print(f"[exists] {dest}")
            return "skipped"
        # tiny leftover from a previous run -> re-fetch
        dest.unlink(missing_ok=True)

    try:
        with session.get(url, stream=True, timeout=REQUEST_TIMEOUT) as r:
            r.raise_for_status()

            cl = r.headers.get("content-length")
            if cl is not None:
                try:
                    if int(cl) < MIN_FILE_SIZE_BYTES:
                        print(f"[skip:small] {url} ({cl} bytes)")
                        return "skipped"
                except ValueError:
                    pass

            written = 0
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if not chunk:
                        continue
                    f.write(chunk)
                    written += len(chunk)

        if written < MIN_FILE_SIZE_BYTES:
            print(f"[skip:small] {url} ({written} bytes)")
            dest.unlink(missing_ok=True)
            return "skipped"

        print(f"[saved]  {dest} ({written} bytes)")
        return "saved"
    except requests.RequestException as e:
        print(f"[error]  {url} -> {e}")
        if dest.exists():
            dest.unlink()
        return "error"


FALLBACK_PREFIXES = ("category-", "tag-", "page-", "_")


def _folder_score(folder_name: str) -> int:
    """Higher score = preferred location for keeping a duplicate."""
    if folder_name.startswith("_"):
        return 0
    if folder_name.startswith("page-"):
        return 1
    if folder_name.startswith("tag-"):
        return 2
    if folder_name.startswith("category-"):
        return 3
    return 10


def _file_hash(p: Path, chunk: int = 65536) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(chunk), b""):
            h.update(blk)
    return h.hexdigest()


# Matches WordPress-style resolution / scaled variants.
# Examples that collapse to the same base:
#   foo-1152x1536.jpg  foo-1536x2048.jpg  foo-scaled.jpg  foo.jpg  -> base "foo.jpg"
_VARIANT_RE = re.compile(r"^(.+?)(?:-\d+x\d+|-scaled)$")


def _variant_base(filename: str) -> str:
    """Strip a WordPress -<W>x<H> or -scaled suffix from the stem."""
    stem, dot, ext = filename.rpartition(".")
    if not dot:
        return filename
    m = _VARIANT_RE.match(stem)
    if not m:
        return filename
    return f"{m.group(1)}.{ext}"


def _dedupe_variants_in_folder(folder: Path, ext: str) -> tuple[int, int]:
    """Within one folder, collapse resolution variants to the largest file.
    Returns (deleted_count, deleted_bytes)."""
    groups: dict[str, list[Path]] = defaultdict(list)
    for p in folder.iterdir():
        if p.is_file() and p.suffix.lower() == f".{ext.lower()}":
            groups[_variant_base(p.name)].append(p)

    deleted = 0
    bytes_freed = 0
    for base, paths in groups.items():
        if len(paths) < 2:
            continue
        # Keep largest; delete the rest.
        ranked = sorted(paths, key=lambda p: p.stat().st_size, reverse=True)
        for loser in ranked[1:]:
            bytes_freed += loser.stat().st_size
            loser.unlink()
            deleted += 1
    return deleted, bytes_freed


def cmd_dedupe(host: str | None = None, variants: bool = True) -> int:
    """Within OUTPUT_DIR/<host> (or each host if not given), find files with the
    same name in multiple folders and delete the duplicates, preferring real
    post folders over fallback folders (category-*, tag-*, page-*, _*).
    Only deletes when content is byte-identical (verified via SHA-256)."""
    targets: list[Path] = []
    if host:
        targets.append(OUTPUT_DIR / host)
    else:
        targets.extend(p for p in OUTPUT_DIR.iterdir() if p.is_dir())

    grand_deleted = 0
    grand_bytes = 0
    grand_skipped = 0
    grand_variant_deleted = 0
    grand_variant_bytes = 0
    for root in targets:
        if not root.is_dir():
            continue
        print(f"\nDedupe scan: {root}")

        # Pass 1: same filename across multiple folders -> prefer post folders,
        # only delete if byte-identical.
        groups: dict[str, list[Path]] = defaultdict(list)
        for ext in FILE_EXTS:
            for p in root.rglob(f"*.{ext}"):
                if p.is_file():
                    groups[p.name].append(p)
        dups = {n: paths for n, paths in groups.items() if len(paths) > 1}
        print(
            f"  [cross-folder] unique={len(groups)}, "
            f"duplicated={len(dups)}, "
            f"files-in-dup-groups={sum(len(v) for v in dups.values())}"
        )

        deleted = 0
        deleted_bytes = 0
        skipped = 0
        for paths in dups.values():
            ranked = sorted(
                paths,
                key=lambda p: (_folder_score(p.parent.name), p.stat().st_size),
                reverse=True,
            )
            keeper = ranked[0]
            keeper_size = keeper.stat().st_size
            keeper_hash: str | None = None
            for loser in ranked[1:]:
                loser_size = loser.stat().st_size
                if loser_size != keeper_size:
                    skipped += 1
                    continue
                if keeper_hash is None:
                    keeper_hash = _file_hash(keeper)
                if _file_hash(loser) != keeper_hash:
                    skipped += 1
                    continue
                deleted_bytes += loser_size
                loser.unlink()
                deleted += 1

        print(
            f"    deleted={deleted} ({deleted_bytes / 1024 / 1024:.1f} MB), "
            f"skipped={skipped} (different content)"
        )
        grand_deleted += deleted
        grand_bytes += deleted_bytes
        grand_skipped += skipped

        # Pass 2: WordPress resolution variants in each folder
        # (foo-1152x1536.jpg, foo-1536x2048.jpg, foo-scaled.jpg, foo.jpg ...)
        # -> keep the largest file; delete the rest. Opt out via --keep-variants.
        if variants:
            variant_deleted = 0
            variant_bytes = 0
            for ext in FILE_EXTS:
                folders = {
                    p.parent for p in root.rglob(f"*.{ext}") if p.is_file()
                }
                for folder in folders:
                    d, b = _dedupe_variants_in_folder(folder, ext)
                    variant_deleted += d
                    variant_bytes += b
            print(
                f"  [resolution-variants] deleted={variant_deleted} "
                f"({variant_bytes / 1024 / 1024:.1f} MB)"
            )
            grand_variant_deleted += variant_deleted
            grand_variant_bytes += variant_bytes

    print(
        f"\nDedupe done. "
        f"cross-folder: deleted={grand_deleted} "
        f"({grand_bytes / 1024 / 1024:.1f} MB), skipped_unsafe={grand_skipped}"
    )
    if variants:
        print(
            f"               variants:     deleted={grand_variant_deleted} "
            f"({grand_variant_bytes / 1024 / 1024:.1f} MB)"
        )
    return 0


def cmd_clean(host: str | None = None) -> int:
    """Remove empty folders and stray .DS_Store files under OUTPUT_DIR (or
    OUTPUT_DIR/<host> if specified)."""
    if host:
        roots = [OUTPUT_DIR / host]
    else:
        roots = [p for p in OUTPUT_DIR.iterdir() if p.is_dir()]

    ds_removed = 0
    empty_removed: list[Path] = []
    for root in roots:
        if not root.is_dir():
            continue
        for p in root.rglob(".DS_Store"):
            if p.is_file():
                p.unlink()
                ds_removed += 1
        for d in sorted([p for p in root.rglob("*") if p.is_dir()], reverse=True):
            try:
                if not any(d.iterdir()):
                    d.rmdir()
                    empty_removed.append(d)
            except OSError:
                pass

    print(f".DS_Store files removed: {ds_removed}")
    print(f"Empty folders removed:   {len(empty_removed)}")
    for r in empty_removed[:10]:
        print(f"  - {r.relative_to(OUTPUT_DIR)}")
    if len(empty_removed) > 10:
        print(f"  ... and {len(empty_removed) - 10} more")
    return 0


def _apply_overrides(args: argparse.Namespace) -> None:
    global START_URL, FILE_EXTS, MAX_DEPTH, OUTPUT_DIR, MIN_FILE_SIZE_BYTES
    global ALLOW_HOSTS, POST_PATTERN
    if args.url:
        START_URL = args.url
    if args.ext:
        FILE_EXTS = [
            e.lstrip(".").lower()
            for e in args.ext.split(",")
            if e.strip()
        ]
    if args.depth is not None:
        MAX_DEPTH = args.depth
    if args.output:
        OUTPUT_DIR = Path(args.output).expanduser()
    if args.min_size_kb is not None:
        MIN_FILE_SIZE_BYTES = args.min_size_kb * 1024
    if args.allow_hosts:
        ALLOW_HOSTS = {
            h.strip().lower()
            for h in args.allow_hosts.split(",")
            if h.strip()
        }
    if args.post_pattern:
        POST_PATTERN = re.compile(args.post_pattern)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="crawl",
        choices=["scan", "download", "crawl", "dedupe", "clean", "all"],
        help="scan/download/crawl run the scrape; dedupe and clean are "
             "post-processing; `all` = crawl + dedupe + clean (default: crawl)",
    )
    parser.add_argument("--url", help="override START_URL (e.g. https://example.com)")
    parser.add_argument(
        "--ext",
        help="override FILE_EXTS. Single ext (jpg) or comma-separated list "
             "(mp4,webm). No leading dot.",
    )
    parser.add_argument("--depth", type=int, help="override MAX_DEPTH")
    parser.add_argument("--output", help="override OUTPUT_DIR")
    parser.add_argument(
        "--min-size-kb",
        type=int,
        help="override MIN_FILE_SIZE_BYTES (in KB; default 100)",
    )
    parser.add_argument(
        "--host",
        help="for dedupe/clean: limit to a single host folder under OUTPUT_DIR "
             "(defaults to inferring from --url, otherwise all hosts)",
    )
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Disable incremental skipping. Re-crawl every page even if its "
             "destination folder already exists on disk.",
    )
    parser.add_argument(
        "--keep-variants",
        action="store_true",
        help="For dedupe: do NOT collapse WordPress resolution variants "
             "(foo-1152x1536.jpg, foo-scaled.jpg, etc.) to the largest file.",
    )
    parser.add_argument(
        "--posts-only",
        action="store_true",
        help="Only download files that are reachable from an individual post "
             "page (single-segment WordPress-style path, or matching "
             "--post-pattern). Skips files whose only known source is a "
             "category/tag/page/home listing, so no category-* / tag-* / "
             "page-* / _home folders get created.",
    )
    parser.add_argument(
        "--allow-hosts",
        help="Comma-separated extra hostnames whose files may be downloaded "
             "(e.g. a CDN or video host like 'streamfap.com'). Crawling still "
             "stays on START_URL host; this only affects which file URLs are "
             "kept as candidates.",
    )
    parser.add_argument(
        "--post-pattern",
        help="Regex matched against url.path that marks a page as an "
             "individual post (overrides the single-segment heuristic). If the "
             "regex has a capture group, group 1 is used as the post-folder "
             "slug. Example for Discourse: '^/t/([^/]+)/\\d+$'",
    )
    args = parser.parse_args()
    _apply_overrides(args)

    host = args.host or (urlparse(START_URL).netloc if args.url else None)
    do_variants = not args.keep_variants

    if args.command == "scan":
        return cmd_scan(fresh=args.fresh, posts_only=args.posts_only)
    if args.command == "download":
        return cmd_download(posts_only=args.posts_only)
    if args.command == "dedupe":
        return cmd_dedupe(host=host, variants=do_variants)
    if args.command == "clean":
        return cmd_clean(host=host)
    if args.command == "all":
        rc = cmd_crawl(fresh=args.fresh, posts_only=args.posts_only)
        if rc == 0:
            cmd_dedupe(
                host=host or urlparse(START_URL).netloc, variants=do_variants
            )
            cmd_clean(host=host or urlparse(START_URL).netloc)
        return rc
    return cmd_crawl(fresh=args.fresh, posts_only=args.posts_only)


if __name__ == "__main__":
    sys.exit(main())
