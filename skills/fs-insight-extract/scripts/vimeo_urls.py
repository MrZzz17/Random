"""Extract playable Vimeo *player* URLs from Fundstrat HTML.

Fundstrat uses embed-only or domain-restricted Vimeo clips. The public page
https://vimeo.com/<id> often returns 404; the iframe src on Fundstrat is the
working playback URL (player.vimeo.com/video/... with full query string).
"""
from __future__ import annotations

import re


def extract_player_embed_urls(html: str) -> list[str]:
    """
    Return full https://player.vimeo.com/video/... URLs as embedded on Fundstrat.

    Prefer iframe src; fallback to any player.vimeo.com/video URL in the HTML.
    Dedupe while preserving order.
    """
    html = html.replace("&amp;", "&")
    urls: list[str] = []
    for m in re.finditer(
        r'<iframe[^>]*\bsrc\s*=\s*(["\'])(https://player\.vimeo\.com/video/.*?)\1',
        html,
        re.I | re.DOTALL,
    ):
        urls.append(m.group(2))
    if urls:
        return list(dict.fromkeys(urls))
    bare = re.findall(
        r'https://player\.vimeo\.com/video/\d+(?:\?[a-zA-Z0-9_=&.%+\-]*)?',
        html,
    )
    return list(dict.fromkeys(bare))


def primary_play_url(html: str) -> str | None:
    urls = extract_player_embed_urls(html)
    return urls[0] if urls else None
