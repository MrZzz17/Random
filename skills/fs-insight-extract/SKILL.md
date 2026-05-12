---
name: fs-insight-extract
description: >-
  Extract article text and Vimeo video links from Fundstrat Direct (fundstratdirect.com)
  pages. Use when the user asks to extract content, video links, article text, or
  research reports from Fundstrat, FS Insight, or fundstratdirect.com URLs.
---

# FS Insight / Fundstrat Direct Content Extraction

## Key Insight

Fundstrat Direct is a WordPress site. The WP REST API at `/wp-json/wp/v2/posts/{id}`
returns **full unpaywalled content** including rendered HTML, even for gated articles.

## Step 1: Get the WordPress Post ID

From any Fundstrat article URL, fetch the HTML and extract the post ID from the body class:

```bash
curl -s -L "<URL>" | grep -oE 'postid-[0-9]+' | head -1
```

The body tag contains `postid-XXXXXXX`. Extract the numeric ID.

## Step 2: Fetch Full Article via REST API

```bash
curl -s "https://fundstratdirect.com/wp-json/wp/v2/posts/<POST_ID>"
```

Response JSON fields:
- `title.rendered` — article title
- `content.rendered` — full HTML body (unpaywalled)
- `date` — publication date
- `author` — author ID
- `categories` — category IDs
- `meta`, `acf` — custom fields

## Step 3: Extract Clean Text

Use the helper script to convert HTML content to readable markdown-style text:

```bash
curl -s "https://fundstratdirect.com/wp-json/wp/v2/posts/<POST_ID>" \
  | python3 scripts/extract_article.py
```

## Step 4: Extract Vimeo Video Links

**Do not** hand users `https://vimeo.com/{VIDEO_ID}`. Fundstrat embeds are often
embed-only or unlisted on Vimeo’s public site, so that URL frequently returns **404**.
Use the **full iframe `src`** from `content.rendered` — always `player.vimeo.com`
with the full query string (`?h=…` and/or `?dnt=1&app_id=122963`, etc.).

```python
# Prefer parsing <iframe src="https://player.vimeo.com/video/...">
# Helper: ~/.cursor/skills/fs-insight-extract/scripts/vimeo_urls.py → extract_player_embed_urls(html)
```

**Important**: Not all posts have videos. The content categories that typically contain
Vimeo embeds:

| Category         | Slug              | Has Video |
|------------------|-------------------|-----------|
| Comments         | crypto-comments   | Yes — nearly all posts |
| Strategy         | crypto-strategy   | No — text + charts only |
| Macro Minute     | macro-minute      | Yes |
| Webinars         | webinars          | Yes |
| Deep Research    | deep-research     | No |

If no video is found in the target post, search nearby posts in video-enabled categories:

```bash
curl -s "https://fundstratdirect.com/wp-json/wp/v2/posts?categories=10045&per_page=5&orderby=date&order=desc"
```

Category ID `10045` = crypto-comments (most frequent video posts).

## Discovering Categories

```bash
curl -s "https://fundstratdirect.com/wp-json/wp/v2/categories?search=<term>"
```

## Vimeo playback URLs (what actually works)

| Link style | Usually works? |
|------------|------------------|
| `https://vimeo.com/{id}` | **No** — public page missing for embed-only clips |
| Full **`player.vimeo.com/video/{id}?…`** from the post iframe `src` | **Yes** — same URL the site embeds |

Patterns Fundstrat uses (extract from HTML; do not invent):

```
https://player.vimeo.com/video/{VIDEO_ID}?h={HASH}&...
https://player.vimeo.com/video/{VIDEO_ID}?dnt=1&app_id=122963
```

## Utility Scripts

Paths are under `~/.cursor/skills/fs-insight-extract/scripts/`.

- **vimeo_urls.py**: `extract_player_embed_urls(html)` — full working player URLs from post HTML.
- **extract_article.py**: Convert REST API JSON to clean readable text and print **player** Vimeo URLs.
  ```bash
  curl -s "https://fundstratdirect.com/wp-json/wp/v2/posts/<ID>" \
    | python3 extract_article.py
  ```

- **find_videos.py**: Recent posts in a category with **working** `player.vimeo.com` links.
  ```bash
  cd ~/.cursor/skills/fs-insight-extract/scripts
  python3 find_videos.py --category macro-minute --count 10
  python3 find_videos.py --category crypto-comments --count 10
  ```
