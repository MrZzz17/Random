#!/usr/bin/env python3
"""
patephone_audiobooks.py - Discover and download Russian audiobooks (Patephone).

Full book (default): yt-dlp parallel HLS → remux to QuickTime-compatible .m4a.
Per-chapter: ffmpeg slices (slow). Cookies: PATEPHONE_COOKIE or Chrome via browser_cookie3.

Usage:
    python patephone_audiobooks.py download https://patephone.com/audiobook/52891-...
    python patephone_audiobooks.py download <url> --chapters
    python patephone_audiobooks.py resolve <url>

Requires: requests, ffmpeg, yt-dlp. Optional: mutagen, browser-cookie3.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import requests

BASE = "https://patephone.com"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
TIMEOUT = 30
DEFAULT_OUT = Path.home() / "Documents" / "Personal" / "audiobooks"
ENV_PATH = Path(__file__).resolve().parent / ".env"

PRODUCT_URL_RE = re.compile(
    r"patephone\.com/audiobook/(\d+)(?:-([a-z0-9-]+))?", re.I
)
TIMECODE_RE = re.compile(r"^(\d+):(\d{2}):(\d{2})(?:\.(\d+))?$")


@dataclass
class Chapter:
    index: int
    name: str
    start_sec: float
    end_sec: float | None = None


@dataclass
class Audiobook:
    product_id: int
    slug: str
    title: str
    author: str
    duration_sec: float
    chapters: list[Chapter]
    cover_url: str | None = None
    mp3_preview_url: str | None = None


def load_env() -> dict[str, str]:
    out: dict[str, str] = {}
    if not ENV_PATH.exists():
        return out
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def cookie_from_browser(profile: str = "Profile 1") -> str | None:
    try:
        import browser_cookie3
    except ImportError:
        return None
    path = os.path.expanduser(
        f"~/Library/Application Support/Google/Chrome/{profile}/Cookies"
    )
    if not os.path.exists(path):
        return None
    try:
        cj = browser_cookie3.chrome(domain_name="patephone.com", cookie_file=path)
        pairs = [f"{c.name}={c.value}" for c in cj]
        return "; ".join(pairs) if pairs else None
    except Exception:
        return None


def resolve_cookie(cookie: str | None, browser_profile: str) -> str | None:
    c = cookie or os.environ.get("PATEPHONE_COOKIE") or load_env().get("PATEPHONE_COOKIE")
    if c:
        return c.strip()
    return cookie_from_browser(browser_profile)


def session(cookie: str | None = None, *, browser_profile: str = "Profile 1") -> requests.Session:
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": UA,
            "Accept": "application/json",
            "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
        }
    )
    c = resolve_cookie(cookie, browser_profile)
    if c:
        s.headers["Cookie"] = c
    return s


def parse_product_url(url: str) -> tuple[int, str]:
    m = PRODUCT_URL_RE.search(url)
    if not m:
        raise ValueError(f"Not a patephone audiobook URL: {url}")
    pid = int(m.group(1))
    slug = m.group(2) or str(pid)
    return pid, slug


def parse_timecode(tc: str) -> float:
    m = TIMECODE_RE.match(tc.strip())
    if not m:
        raise ValueError(f"Bad timecode: {tc}")
    h, mi, s, ms = m.groups()
    sec = int(h) * 3600 + int(mi) * 60 + int(s)
    if ms:
        sec += int(ms) / (10 ** len(ms))
    return float(sec)


def slugify(text: str, max_len: int = 80) -> str:
    t = text.lower().strip()
    t = re.sub(r"[^\w\s-]", "", t, flags=re.UNICODE)
    t = re.sub(r"[\s_]+", "-", t, flags=re.UNICODE)
    t = re.sub(r"-+", "-", t).strip("-")
    return (t or "audiobook")[:max_len]


def find_ytdlp() -> str:
    for cand in ("yt-dlp", "/opt/homebrew/bin/yt-dlp", "/usr/local/bin/yt-dlp"):
        if cand == "yt-dlp":
            found = shutil.which("yt-dlp")
            if found:
                return found
        elif os.path.isfile(cand) and os.access(cand, os.X_OK):
            return cand
    sys.exit("ERROR: yt-dlp not found. Install: brew install yt-dlp")


def remux_to_m4a(src: Path, dest: Path) -> None:
    """ADTS/raw AAC → ISO M4A (QuickTime / iPhone compatible)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    _run_ffmpeg(
        ["-i", str(src), "-vn", "-c:a", "copy", "-movflags", "+faststart", str(dest)]
    )


def download_full_ytdlp(
    m3u8_url: str,
    out_m4a: Path,
    *,
    referer: str,
    browser_profile: str,
    concurrent_fragments: int,
    log_path: Path,
) -> None:
    ytdlp = find_ytdlp()
    out_dir = out_m4a.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    raw = out_dir / "complete.raw"
    for old in (raw, out_dir / "complete.mp4", out_m4a):
        if old.exists() and old != out_m4a:
            pass
    cmd = [
        ytdlp,
        "--referer",
        referer,
        "--cookies-from-browser",
        f"chrome:{browser_profile}",
        "--concurrent-fragments",
        str(concurrent_fragments),
        "--fragment-retries",
        "20",
        "--retries",
        "50",
        "--no-part",
        "-o",
        str(raw) + ".%(ext)s",
        m3u8_url,
    ]
    print(f"Downloading HLS (yt-dlp, {concurrent_fragments} threads) → {out_m4a.name}")
    with log_path.open("w", encoding="utf-8") as logf:
        subprocess.run(cmd, check=True, stdout=logf, stderr=subprocess.STDOUT)
    downloaded = None
    for ext in ("mp4", "m4a", "aac", "mkv"):
        cand = out_dir / f"complete.raw.{ext}"
        if cand.exists() and cand.stat().st_size > 0:
            downloaded = cand
            break
    if not downloaded:
        for f in out_dir.glob("complete.raw*"):
            if f.is_file() and f.stat().st_size > 0 and not f.suffix == ".part":
                downloaded = f
                break
    if not downloaded:
        raise RuntimeError("yt-dlp finished but no output file found")
    print(f"Remuxing → {out_m4a.name} (QuickTime-compatible M4A)...")
    remux_to_m4a(downloaded, out_m4a)
    if downloaded != out_m4a:
        downloaded.unlink(missing_ok=True)
    for frag in out_dir.glob("complete.raw*"):
        if frag.is_file():
            frag.unlink(missing_ok=True)




def ffmeta_escape(s: str) -> str:
    return (
        s.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace("#", "\\#")
        .replace("=", "\\=")
        .replace("\n", " ")
    )
def build_bound_m4b(out_dir: Path, meta: dict, *, audio_m4a: Path | None = None) -> Path:
    """Build complete.m4b with chapters, cover, title/author for Bound / OneDrive import."""
    src = audio_m4a or (out_dir / "complete.m4a")
    cover = out_dir / "cover.jpg"
    dest = out_dir / "complete.m4b"
    if not src.exists():
        raise FileNotFoundError(f"Missing audio: {src}")
    dur = float(
        subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "csv=p=0",
                str(src),
            ],
            text=True,
        ).strip()
    )
    dur_ms = int(dur * 1000)
    title = meta.get("title") or "Audiobook"
    author = meta.get("author") or "Unknown"
    chapters = meta.get("chapters") or []
    lines = [
        ";FFMETADATA1",
        f"title={ffmeta_escape(title)}",
        f"artist={ffmeta_escape(author)}",
        f"album={ffmeta_escape(title)}",
    ]
    for i, ch in enumerate(chapters):
        start_ms = int(ch["start_sec"] * 1000)
        end_ms = int(ch["end_sec"] * 1000) if ch.get("end_sec") is not None else dur_ms
        if i == len(chapters) - 1:
            end_ms = dur_ms
        lines += [
            "[CHAPTER]",
            "TIMEBASE=1/1000",
            f"START={start_ms}",
            f"END={end_ms}",
            f"title={ffmeta_escape(ch['name'])}",
        ]
    ffmeta = out_dir / "chapters.ffmeta"
    ffmeta.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Building {dest.name} ({len(chapters)} chapters, Bound-ready)...")
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "warning",
        "-y",
        "-i",
        str(src),
    ]
    if cover.exists():
        cmd += ["-i", str(cover)]
    cmd += [
        "-i",
        str(ffmeta),
        "-map",
        "0:a",
    ]
    if cover.exists():
        cmd += ["-map", "1:v", "-c:v", "mjpeg", "-disposition:v:0", "attached_pic"]
    cmd += [
        "-map_metadata",
        "2" if cover.exists() else "1",
        "-map_chapters",
        "2" if cover.exists() else "1",
        "-c:a",
        "copy",
        "-movflags",
        "+faststart",
        str(dest),
    ]
    subprocess.run(cmd, check=True)
    ffmeta.unlink(missing_ok=True)
    return dest


def finalize_audiobook_folder(out_dir: Path, meta: dict) -> Path:
    """m4a → m4b, drop logs and intermediate audio."""
    m4a = out_dir / "complete.m4a"
    if m4a.exists():
        m4b = build_bound_m4b(out_dir, meta, audio_m4a=m4a)
        m4a.unlink(missing_ok=True)
    elif (out_dir / "complete.m4b").exists():
        m4b = out_dir / "complete.m4b"
    else:
        raise FileNotFoundError("No complete.m4a or complete.m4b in output folder")
    for junk in (
        "download-ytdlp.log",
        "download.log",
        "download.pid",
        "complete.mp4",
        "complete.partial.ffmpeg.m4a",
        "chapters.ffmeta",
    ):
        (out_dir / junk).unlink(missing_ok=True)
    return m4b

def require_ffmpeg() -> str:
    ff = shutil.which("ffmpeg")
    if not ff:
        sys.exit(
            "ERROR: ffmpeg not found on PATH.\n"
            "Install: brew install ffmpeg\n"
            "ffmpeg is required to download HLS streams and split chapters."
        )
    return ff


def fetch_page_book(sess: requests.Session, url: str, product_id: int) -> dict:
    r = sess.get(url, headers={"Accept": "text/html"}, timeout=TIMEOUT)
    r.raise_for_status()
    if not r.encoding or r.encoding.lower() in ("iso-8859-1", "latin-1"):
        r.encoding = r.apparent_encoding or "utf-8"
    html = r.text
    m = re.search(r"const data = (\[.*?\]);\s*\n", html, re.DOTALL)
    if not m:
        raise RuntimeError("Could not find embedded page data (site layout changed?)")
    blob = m.group(1)
    # Book record is keyed by id:N
    needle = f"id:{product_id},"
    idx = blob.find(needle)
    if idx < 0:
        raise RuntimeError(f"Product {product_id} not found in page data")
    chunk = blob[idx : idx + 12000]
    title_m = re.search(r'title:"((?:\\.|[^"\\])*)"', chunk)
    title = title_m.group(1) if title_m else f"audiobook-{product_id}"
    if "\\u" in title:
        title = title.encode("utf-8").decode("unicode_escape")
    dur_m = re.search(r"duration:(\d+(?:\.\d+)?)", chunk)
    duration = float(dur_m.group(1)) if dur_m else 0.0
    author = ""
    fn_m = re.search(
        r'authors:\[\{[^}]*firstName:"([^"]*)"[^}]*lastName:"([^"]*)"[^}]*role:\{name:"Автор"',
        chunk,
    )
    if fn_m:
        author = f"{fn_m.group(1)} {fn_m.group(2)}".strip()
    cover_m = re.search(r'image_640",url:"([^"]+)"', chunk)
    preview_m = re.search(r'mp3PreviewUrl:"([^"]+)"', chunk)
    web_m = re.search(r'webId:"(\d+-[^"]+)"', chunk)
    return {
        "title": title,
        "author": author,
        "duration": duration,
        "cover_url": cover_m.group(1) if cover_m else None,
        "mp3_preview_url": preview_m.group(1) if preview_m else None,
        "web_id": web_m.group(1) if web_m else f"{product_id}",
    }


def fetch_chapters(sess: requests.Session, product_id: int) -> list[Chapter]:
    r = sess.get(f"{BASE}/api/product/{product_id}/chapters", timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    if not data.get("success"):
        raise RuntimeError(data.get("code") or "chapters API failed")
    raw = data.get("list") or []
    starts: list[tuple[str, float]] = []
    for row in raw:
        starts.append((row["name"], parse_timecode(row["timecode"])))
    chapters: list[Chapter] = []
    for i, (name, start) in enumerate(starts):
        end = starts[i + 1][1] if i + 1 < len(starts) else None
        chapters.append(Chapter(index=i + 1, name=name, start_sec=start, end_sec=end))
    return chapters


def pick_hls_url(sess: requests.Session, product_id: int, *, preview_only: bool) -> tuple[str, str]:
    """Return (m3u8_url, mode) where mode is full | ad | preview."""
    referer = f"{BASE}/audiobook/{product_id}"

    def try_endpoint(path: str) -> str | None:
        r = sess.get(
            f"{BASE}{path}",
            headers={"Referer": referer},
            timeout=TIMEOUT,
        )
        if r.status_code == 403:
            return None
        r.raise_for_status()
        data = r.json()
        if not data.get("success"):
            return None
        urls = []
        if data.get("url"):
            urls.append(data["url"])
        urls.extend(data.get("alternativeUrls") or [])
        for u in urls:
            if _probe_m3u8(sess, u, referer):
                return u
        return None

    if not preview_only:
        full = try_endpoint(f"/api/product/{product_id}/stream/hls")
        if full:
            return full, "full"
        ad = try_endpoint(f"/api/ad/stream/{product_id}")
        if ad:
            return ad, "ad"

    prev = try_endpoint(f"/api/product/{product_id}/preview/hls")
    if prev:
        return prev, "preview"
    raise RuntimeError(
        "No playable HLS URL. Full book needs PATEPHONE_COOKIE from a logged-in browser "
        "(DevTools → Application → Cookies → patephone.com). Preview also failed."
    )


def _probe_m3u8(sess: requests.Session, url: str, referer: str) -> bool:
    try:
        r = sess.get(
            url,
            headers={"Referer": referer, "Accept": "*/*"},
            timeout=15,
        )
        return r.status_code == 200 and "#EXTM3U" in r.text[:200]
    except requests.RequestException:
        return False


def cmd_search(args: argparse.Namespace) -> None:
    sess = session(args.cookie, browser_profile=args.browser_profile)
    params = {"query": args.query}
    if args.product_type:
        params["productType"] = args.product_type
    r = sess.get(f"{BASE}/api/search/products", params=params, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    rows = data.get("page") or []
    print("| Title | Author | Duration | ID | URL |")
    print("| --- | --- | --- | --- | --- |")
    for row in rows[: args.limit]:
        title = (row.get("title") or "").replace("|", "/")
        author = ""
        for p in row.get("persons") or row.get("authors") or []:
            if p.get("role", {}).get("abbr") == "author" or "author" in (p.get("roles") or []):
                author = p.get("fullName") or ""
                break
        dur = row.get("duration") or 0
        dur_s = f"{int(dur // 3600)}:{int((dur % 3600) // 60):02d}:{int(dur % 60):02d}"
        pid = row.get("id")
        web = row.get("webId") or f"{pid}"
        url = f"{BASE}/audiobook/{web}"
        print(f"| {title} | {author} | {dur_s} | {pid} | {url} |")
    paging = data.get("paging") or {}
    print(f"\n_{paging.get('countAll', len(rows))} hits (showing {min(len(rows), args.limit)})_")


def cmd_info(args: argparse.Namespace) -> None:
    pid, slug = parse_product_url(args.url)
    sess = session(args.cookie)
    meta = fetch_page_book(sess, args.url, pid)
    chapters = fetch_chapters(sess, pid)
    try:
        _, mode = pick_hls_url(sess, pid, preview_only=False)
    except RuntimeError as e:
        mode = f"unavailable ({e})"
    print(f"**{meta['title']}**")
    if meta["author"]:
        print(f"- Author: {meta['author']}")
    print(f"- Product ID: {pid}")
    print(f"- Slug: {slug}")
    print(f"- Duration: {meta['duration']:.0f}s ({meta['duration']/3600:.1f}h)")
    print(f"- Chapters: {len(chapters)}")
    print(f"- Stream: {mode}")
    print(f"- URL: {args.url}")
    if meta.get("cover_url"):
        print(f"- Cover: {meta['cover_url']}")


def _run_ffmpeg(args: list[str]) -> None:
    ff = require_ffmpeg()
    cmd = [ff, "-hide_banner", "-loglevel", "error", "-y", *args]
    subprocess.run(cmd, check=True)


def download_hls(
    m3u8_url: str,
    out_path: Path,
    *,
    referer: str,
    start_sec: float | None = None,
    end_sec: float | None = None,
    audio_format: str = "m4a",
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    headers = f"Referer: {referer}\r\nUser-Agent: {UA}\r\n"
    inp = ["-headers", headers, "-i", m3u8_url]
    if start_sec is not None:
        inp.extend(["-ss", str(start_sec)])
    if end_sec is not None:
        inp.extend(["-to", str(end_sec)])
    if audio_format == "mp3":
        inp.extend(["-c:a", "libmp3lame", "-q:a", "2", str(out_path)])
    elif audio_format == "aac":
        inp.extend(["-c", "copy", str(out_path)])
    else:
        inp.extend(["-vn", "-c:a", "copy", "-movflags", "+faststart", str(out_path)])
    _run_ffmpeg(inp)


def tag_mp3(path: Path, title: str, artist: str, album: str, track: int) -> None:
    try:
        from mutagen.id3 import ID3, TIT2, TPE1, TALB, TRCK
        from mutagen.mp3 import MP3
    except ImportError:
        return
    try:
        audio = MP3(path)
        tags = audio.tags or ID3()
        tags.add(TIT2(encoding=3, text=title))
        tags.add(TPE1(encoding=3, text=artist))
        tags.add(TALB(encoding=3, text=album))
        tags.add(TRCK(encoding=3, text=str(track)))
        audio.tags = tags
        audio.save()
    except Exception:
        pass


def cmd_download(args: argparse.Namespace) -> None:
    sess = session(args.cookie, browser_profile=args.browser_profile)

    if not args.m3u8 and not args.url:
        sys.exit("download requires a patephone audiobook URL (or --m3u8)")

    if args.m3u8:
        out_dir = Path(args.output)
        out_dir.mkdir(parents=True, exist_ok=True)
        dest = out_dir / "audiobook.m4a"
        raw = out_dir / "audiobook.raw.m4a"
        print(f"Downloading HLS → {dest.name}")
        download_hls(
            args.m3u8,
            raw,
            referer=args.referer or BASE,
            audio_format="m4a",
        )
        remux_to_m4a(raw, dest)
        raw.unlink(missing_ok=True)
        print(f"Done: {dest}")
        return

    pid, url_slug = parse_product_url(args.url)
    meta = fetch_page_book(sess, args.url, pid)
    chapters = fetch_chapters(sess, pid)
    # URL slug is stable ASCII; title slug is fallback for non-patephone URLs.
    book_slug = url_slug if url_slug and not url_slug.isdigit() else slugify(meta["title"])
    if len(book_slug) < 4:
        book_slug = f"audiobook-{pid}"
    out_dir = Path(args.output) / book_slug
    out_dir.mkdir(parents=True, exist_ok=True)

    preview_only = args.preview
    m3u8, mode = pick_hls_url(sess, pid, preview_only=preview_only)
    referer = args.url

    meta_path = out_dir / "metadata.json"
    meta_doc = {
        "product_id": pid,
        "title": meta["title"],
        "author": meta["author"],
        "source_url": args.url,
        "stream_mode": mode,
        "m3u8_url": m3u8,
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
        "chapters": [
            {"index": c.index, "name": c.name, "start_sec": c.start_sec, "end_sec": c.end_sec}
            for c in chapters
        ],
    }
    meta_path.write_text(json.dumps(meta_doc, ensure_ascii=False, indent=2), encoding="utf-8")

    if meta.get("cover_url") and not (out_dir / "cover.jpg").exists():
        try:
            cr = sess.get(meta["cover_url"], timeout=TIMEOUT)
            cr.raise_for_status()
            (out_dir / "cover.jpg").write_bytes(cr.content)
        except requests.RequestException:
            pass

    if mode == "preview":
        print(
            "WARNING: Only preview stream available (~20 min sample). "
            "Log into patephone.com (cookies) for the full book."
        )

    complete_m4a = out_dir / "complete.m4a"
    if not args.chapters:
        m4b_done = out_dir / "complete.m4b"
        if m4b_done.exists() and m4b_done.stat().st_size > 1_000_000 and not args.force:
            print(f"Exists: {m4b_done} ({m4b_done.stat().st_size / 1e6:.0f} MB)")
            return
        if args.ffmpeg_only:
            print(f"Downloading {meta['title']} ({mode}, ffmpeg) → {complete_m4a}")
            raw = out_dir / "complete.ffmpeg.raw.m4a"
            cookie = resolve_cookie(args.cookie, args.browser_profile)
            hdr = f"Referer: {referer}\r\nUser-Agent: {UA}\r\n"
            if cookie:
                hdr += f"Cookie: {cookie}\r\n"
            _run_ffmpeg(["-headers", hdr, "-i", m3u8, "-vn", "-c:a", "copy", str(raw)])
            remux_to_m4a(raw, complete_m4a)
            raw.unlink(missing_ok=True)
        else:
            download_full_ytdlp(
                m3u8,
                complete_m4a,
                referer=referer,
                browser_profile=args.browser_profile,
                concurrent_fragments=args.concurrent_fragments,
                log_path=out_dir / "download-ytdlp.log",
            )
        m4b = finalize_audiobook_folder(out_dir, meta_doc)
        mb = m4b.stat().st_size / 1e6
        print(f"\nFinished: {m4b} ({mb:.0f} MB, stream={mode}, {len(chapters)} chapters)")
        print("Import complete.m4b into Bound (OneDrive / Files).")
        return

    ext = "m4a"
    todo = chapters
    if args.max_chapters > 0:
        todo = chapters[: args.max_chapters]
    print(f"Downloading {meta['title']} ({mode}, {len(todo)} chapters) → {out_dir}")

    for c in todo:
        end = c.end_sec
        if mode == "preview" and end is not None:
            # Preview manifest is short; skip chapters entirely beyond sample.
            try:
                prev_dur = _preview_duration(sess, m3u8, referer)
            except Exception:
                prev_dur = 1260.0
            if c.start_sec >= prev_dur:
                print(f"  skip ch {c.index:02d} (beyond preview)")
                continue
            if end > prev_dur:
                end = prev_dur

        fname = f"{c.index:02d} - {slugify(c.name, max_len=60)}.{ext}"
        dest = out_dir / fname
        if dest.exists() and dest.stat().st_size > 1000 and not args.force:
            print(f"  exists {fname}")
            continue
        print(f"  [{c.index}/{len(todo)}] {c.name[:70]}...")
        t0 = time.time()
        download_hls(
            m3u8,
            dest,
            referer=referer,
            start_sec=c.start_sec,
            end_sec=end,
            audio_format=ext,
        )
        tag_mp3(dest, c.name, meta["author"] or "Unknown", meta["title"], c.index)
        print(f"       done {dest.name} ({time.time()-t0:.0f}s)")

    print(f"\nFinished: {out_dir}")
    if mode == "preview":
        print("For the full 21h book, export cookies after logging into patephone.com:")
        print("  echo 'PATEPHONE_COOKIE=...' >> ~/Documents/GitHub/Personal/Random/.env")


def _preview_duration(sess: requests.Session, m3u8: str, referer: str) -> float:
    r = sess.get(m3u8, headers={"Referer": referer}, timeout=TIMEOUT)
    r.raise_for_status()
    total = 0.0
    for line in r.text.splitlines():
        if line.startswith("#EXTINF:"):
            total += float(line.split(":")[1].rstrip(","))
    return total


def cmd_resolve(args: argparse.Namespace) -> None:
    """Print verified direct URLs (curl-checked), FS-Insight style."""
    sess = session(args.cookie)
    url = args.url
    pid, slug = parse_product_url(url)
    meta = fetch_page_book(sess, url, pid)
    chapters = fetch_chapters(sess, pid)

    print(f"## {meta['title']}")
    if meta["author"]:
        print(f"- **Author:** {meta['author']}")
    print(f"- **Catalog duration:** {meta['duration']:.0f}s ({meta['duration']/3600:.1f}h)")
    print(f"- **Chapters (API):** {len(chapters)}")
    print()

    rows: list[tuple[str, str, str, str]] = []

    # Full stream (usually blocked without session)
    for label, path in [
        ("Full HLS (API)", f"/api/product/{pid}/stream/hls"),
        ("Ad-supported HLS (API)", f"/api/ad/stream/{pid}"),
    ]:
        r = sess.get(f"{BASE}{path}", headers={"Referer": url}, timeout=TIMEOUT)
        if r.status_code == 200:
            data = r.json()
            u = data.get("url") or (data.get("alternativeUrls") or [None])[0]
            dur = _m3u8_duration(sess, u, url) if u else 0
            rows.append((label, "yes" if u else "no", f"{dur/60:.0f} min" if dur else "?", u or ""))
        else:
            code = r.json().get("code", r.status_code) if r.headers.get("content-type", "").startswith("application/json") else r.status_code
            rows.append((label, "no", str(code), ""))

    # Preview HLS (no login)
    prev = sess.get(f"{BASE}/api/product/{pid}/preview/hls", headers={"Referer": url}, timeout=TIMEOUT)
    if prev.status_code == 200 and prev.json().get("success"):
        data = prev.json()
        urls = [data["url"]] + list(data.get("alternativeUrls") or [])
        best = urls[0]
        dur = _m3u8_duration(sess, best, url)
        rows.append(("Preview HLS (API, no login)", "yes", f"{dur/60:.1f} min", best))
        for alt in urls[1:]:
            rows.append(("Preview HLS (mirror)", "yes", f"{dur/60:.1f} min", alt))
    else:
        rows.append(("Preview HLS", "no", "failed", ""))

    # Litres trial MP3 (separate catalog id on affiliate pages)
    litres_id = "71329981"
    trial = f"https://www.litres.ru/get_mp3_trial/{litres_id}.mp3"
    try:
        hr = sess.head(trial, headers={"Referer": "https://www.litres.ru/"}, timeout=TIMEOUT, allow_redirects=True)
        size = int(hr.headers.get("content-length", 0))
        rows.append(("Litres trial MP3", "yes" if hr.status_code == 200 else "no", f"{size/1e6:.1f} MB", trial))
    except requests.RequestException:
        rows.append(("Litres trial MP3", "no", "error", trial))

    print("| Source | Verified | Duration/size | URL |")
    print("| --- | --- | --- | --- |")
    for label, ok, dur, link in rows:
        print(f"| {label} | {ok} | {dur} | {link} |")

    print()
    if not any(r[1] == "yes" and "Full" in r[0] for r in rows):
        print(
            "_Full patephone book is not available without a session cookie. "
            "The site player shows catalog duration (21h) even when only the preview stream is unlocked._"
        )
        print()
        print("**Download max without login:**")
        print("```bash")
        print(f"python {Path(__file__).name} download {url}")
        print("```")


def _m3u8_duration(sess: requests.Session, m3u8: str, referer: str) -> float:
    try:
        return _preview_duration(sess, m3u8, referer)
    except Exception:
        return 0.0


def cmd_discover(args: argparse.Namespace) -> None:
    """Brave-search mirrors; list candidate URLs (verify separately)."""
    q = urllib.parse.quote_plus(f"{args.query} аудиокнига mp3 скачать")
    r = requests.get(
        f"https://search.brave.com/search?q={q}",
        headers={"User-Agent": UA, "Accept-Encoding": "gzip"},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    html = r.text
    seen: set[str] = set()
    print("| Site | URL |")
    print("| --- | --- |")
    for m in re.finditer(r'href="(https?://[^"]+)"', html):
        u = m.group(1)
        if u in seen:
            continue
        seen.add(u)
        if not any(
            d in u.lower()
            for d in [
                "patephone",
                "litres",
                "youtube",
                "vk.com",
                "all-books",
                "knig",
                "coollib",
                "flibusta",
                "mybook",
                "readrate",
            ]
        ):
            continue
        host = urllib.parse.urlparse(u).netloc
        print(f"| {host} | {u} |")
    print(f"\n_{len(seen)} links; run `resolve` on a patephone URL for curl-verified streams._")




def cmd_export(args: argparse.Namespace) -> None:
    """Build complete.m4b + cleanup from existing download folder."""
    path = Path(args.url)
    if path.is_dir():
        out_dir = path
        meta_path = out_dir / "metadata.json"
        if not meta_path.exists():
            sys.exit(f"No metadata.json in {out_dir}")
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    else:
        _, url_slug = parse_product_url(args.url)
        out_dir = Path(args.output) / url_slug
        meta_path = out_dir / "metadata.json"
        if not meta_path.exists():
            sys.exit(f"Folder not found or missing metadata: {out_dir}")
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    m4b = finalize_audiobook_folder(out_dir, meta)
    print(f"Done: {m4b}")

def cmd_latest(args: argparse.Namespace) -> None:
    """Top chart / recent audiobooks from public chart API."""
    sess = session(args.cookie)
    r = sess.get(f"{BASE}/api/products/chart/now", timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    rows = (data.get("list") or data.get("page") or [])[: args.limit]
    print("| Title | Author | ID | URL |")
    print("| --- | --- | --- | --- |")
    for row in rows:
        title = (row.get("title") or "").replace("|", "/")
        author = ""
        for p in row.get("persons") or []:
            if p.get("defaultPersonRoleAbbr") == "author":
                author = p.get("fullName") or ""
        pid = row.get("id")
        web = row.get("webId") or pid
        print(f"| {title} | {author} | {pid} | {BASE}/audiobook/{web} |")


def main() -> None:
    p = argparse.ArgumentParser(description="Patephone.com audiobook search & download")
    p.add_argument("--cookie", help="Cookie header value (overrides PATEPHONE_COOKIE)")
    p.add_argument(
        "--browser-profile",
        default="Profile 1",
        help='Chrome profile for cookies (default: "Profile 1")',
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="Search audiobooks by title/author")
    s.add_argument("query")
    s.add_argument("--limit", type=int, default=20)
    s.add_argument("--product-type", default="audiobooks")
    s.set_defaults(func=cmd_search)

    i = sub.add_parser("info", help="Show book metadata and stream availability")
    i.add_argument("url")
    i.set_defaults(func=cmd_info)

    d = sub.add_parser(
        "download",
        help="Download audiobook as complete.m4a (default) or per-chapter files",
    )
    d.add_argument("url", nargs="?", help="patephone audiobook URL")
    d.add_argument("--m3u8", help="Direct HLS manifest URL (skip book page)")
    d.add_argument("--referer", help="Referer for --m3u8")
    d.add_argument("--output", "-o", default=str(DEFAULT_OUT))
    d.add_argument("--preview", action="store_true", help="Force preview stream only")
    d.add_argument(
        "--chapters",
        action="store_true",
        help="Per-chapter .m4a files (slow); default is single complete.m4a",
    )
    d.add_argument(
        "--ffmpeg-only",
        action="store_true",
        help="Use ffmpeg instead of yt-dlp (much slower)",
    )
    d.add_argument(
        "--concurrent-fragments",
        type=int,
        default=32,
        help="yt-dlp parallel fragment downloads",
    )
    d.add_argument("--force", action="store_true", help="Re-download existing files")
    d.add_argument(
        "--max-chapters",
        type=int,
        default=0,
        help="With --chapters: limit chapter count (0 = all)",
    )
    d.set_defaults(func=cmd_download)

    r = sub.add_parser("resolve", help="Verify stream URLs and durations")
    r.add_argument("url")
    r.set_defaults(func=cmd_resolve)

    x = sub.add_parser("discover", help="Brave search for mirror links")
    x.add_argument("query")
    x.set_defaults(func=cmd_discover)

    e = sub.add_parser("export", help="Build complete.m4b from existing folder")
    e.add_argument("url", help="Original patephone URL (for slug) or path to book folder")
    e.add_argument("--output", "-o", default=str(DEFAULT_OUT))
    e.set_defaults(func=cmd_export)

    l = sub.add_parser("latest", help="List charting audiobooks")
    l.add_argument("--limit", type=int, default=20)
    l.set_defaults(func=cmd_latest)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
