---
name: dashablog
description: List the latest galleries from dashablog.tv (and similar WordPress/RSS gallery sites like gravureblog.tv, latinblog.tv, modelblog.asia, marvelblog.asia, tokyoblog.asia, amateurblog.tv, xblog.tv) with cache-busted refresh, and bulk-download any gallery as JPGs into per-post folders under ~/Documents/Personal. Always refreshes from origin (never cached). Use when the user asks for the latest dashablog uploads, latest galleries, newest sets, or wants to download/scrape a gallery, mirror images, dedupe a folder, or refresh existing image scrapes.
---

# Dashablog (and friends)

Two operating modes against the same script (`Random/bulk_download_by_ext.py`):

1. **List latest galleries** — read the site's RSS feed (cache-busted) and print a markdown table.
2. **Download a specific gallery** — bulk-download every JPG from a post into a per-post folder under `~/Documents/Personal/<host>/<post-slug>/`.

The script defaults to `~/Documents/Personal` (intentionally outside any git repo).

## Setup (first run only)

```bash
cd ~/Documents/GitHub/Personal/Random
python3 -m venv .venv
source .venv/bin/activate
pip install requests beautifulsoup4
```

Subsequent runs:

```bash
source ~/Documents/GitHub/Personal/Random/.venv/bin/activate
```

---

## Mode 1: List latest galleries

Always cache-busted — pulls fresh data from origin every time.

```bash
# latest in last 24h on dashablog
python ~/Documents/GitHub/Personal/Random/bulk_download_by_ext.py latest \
  --url https://dashablog.tv/ --hours 24

# newest 30 regardless of age
python ~/Documents/GitHub/Personal/Random/bulk_download_by_ext.py latest \
  --url https://dashablog.tv/ --limit 30

# any other RSS-enabled gallery site
python ~/Documents/GitHub/Personal/Random/bulk_download_by_ext.py latest \
  --url https://gravureblog.tv/ --hours 12
```

Output is a markdown table: `Age | Posted (UTC) | Title | Link`. Pipe verbatim to the user.

### Mapping user requests to commands

| User says | Command |
|---|---|
| "latest dashablog" / "what's new on dashablog" / "latest uploads to dashablog" | `latest --url https://dashablog.tv/ --hours 24` |
| "dashablog in the last N hours" | `latest --url https://dashablog.tv/ --hours <N>` |
| "newest 30 dashablog galleries" | `latest --url https://dashablog.tv/ --limit 30` |
| "latest gravureblog / latinblog / modelblog / marvelblog / tokyoblog / amateurblog / xblog" | swap host in `--url` |

---

## Mode 2: Download a specific gallery

For a single known post URL, use `--depth 0 --fresh` for the fastest, most focused run (skips BFS into the homepage / category pages, which would otherwise queue up many other posts):

```bash
python ~/Documents/GitHub/Personal/Random/bulk_download_by_ext.py all \
  --url https://dashablog.tv/sweet-dolls-set-12/ \
  --ext jpg --depth 0 --fresh
```

For a full site refresh (incremental — skips posts whose folder already exists with content):

```bash
python ~/Documents/GitHub/Personal/Random/bulk_download_by_ext.py all \
  --url https://dashablog.tv/ --ext jpg
```

After download, optionally open the folder:

```bash
open ~/Documents/Personal/dashablog.tv/<post-slug>/
```

### Subcommands

| Command | Purpose |
|---|---|
| `latest` | List newest RSS posts (no download). Cache-busted. Supports `--hours` and `--limit`. |
| `scan` | BFS crawl + HEAD-probe; writes `scan_results.json` and per-folder count. No downloads. |
| `download` | Parallel download from `scan_results.json`. |
| `crawl` | BFS + parallel download in a single pass. Default if no command given. |
| `dedupe` | (1) Cross-folder: same filename in multiple folders, keep the post-folder copy, delete others (only if byte-identical via SHA-256). (2) Resolution variants: collapse `foo.jpg`, `foo-1152x1536.jpg`, `foo-scaled.jpg` to the largest. Pass `--keep-variants` to disable pass 2. |
| `clean` | Remove `.DS_Store` and any empty folders. |
| `all` | `crawl` then `dedupe` then `clean`. |

### Flags

| Flag | Description | Default |
|---|---|---|
| `--url URL` | Starting URL (post page, category, or site root) | required per run |
| `--ext EXT` | File extension(s), comma-separated, no dot | `jpg` |
| `--depth N` | BFS max depth from start. Use `0` for single-post focused runs. | `2` |
| `--output PATH` | Root output dir | `~/Documents/Personal` |
| `--min-size-kb N` | Skip files smaller than N KB | `100` |
| `--fresh` | Disable incremental skip; re-crawl every page | off |
| `--posts-only` | Only save files reachable from a post page; skip category/tag/page/home | off |
| `--allow-hosts H[,H...]` | Extra hostnames whose files may be downloaded (e.g. video CDN) | empty |
| `--post-pattern REGEX` | Regex against `url.path` marking a post (overrides single-segment heuristic). Capture group 1 = folder slug. | none |
| `--hours N` | (latest only) Only show posts newer than N hours | none |
| `--limit N` | (latest only) Cap on rows shown | 50 |

---

## How downloads are organized

Saved as `~/Documents/Personal/<host>/<post-slug>/<filename>`. Slug is derived from the post page where the image was first seen, preferring real post pages over fallback pages (`category/`, `tag/`, `page/N/`, home).

## Incremental mode

By default the BFS skips fetching a post page entirely when `~/Documents/Personal/<host>/<post-slug>/` already exists with content. Refresh runs are fast — skips fetch AND download for previously-completed posts. Use `--fresh` to disable.

## Common workflow

```
Task progress:
- [ ] 1. latest      - show the user the cache-busted list of new galleries
- [ ] 2. (review)    - user picks one (or asks for "all new")
- [ ] 3. all (post)  - --depth 0 --fresh against the chosen post URL
- [ ] 4. open        - open the folder in Finder
```

For routine refresh of all new galleries on a site, just run `all` against the site root — incremental mode handles the skip logic.

## Stopping background runs

If the script is killed mid-run, check for zombies before re-running:

```bash
ps aux | grep "python.*bulk_download" | grep -v grep
# kill survivors with `kill -9 <pid> ...` before starting fresh
```

## Anti-patterns

- Don't store scraped output inside a git repo — default `~/Documents/Personal` is intentionally outside the user's GitHub trees.
- Don't run `all` against a single post URL without `--depth 0 --fresh` — BFS will hop to the homepage and start downloading every other recent post.
- Don't `mkdir` an empty target folder before running — incremental mode treats it as "already has content" only if it has files, but creating it manually can confuse later refreshes.
