"""
Extract clean readable text from a Fundstrat Direct WP REST API JSON response.

Usage:
  curl -s "https://fundstratdirect.com/wp-json/wp/v2/posts/<ID>" | python3 extract_article.py
"""
import pathlib
import sys

_SCRIPTS = pathlib.Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import json
import re
import html as htmlmod

from vimeo_urls import extract_player_embed_urls


def html_to_text(raw_html):
    text = raw_html
    text = re.sub(r"<figcaption[^>]*>(.*?)</figcaption>", r"[Caption: \1]", text)
    text = re.sub(r"<figure[^>]*>.*?</figure>", "\n[Chart]\n", text, flags=re.DOTALL)
    text = re.sub(r"<h1[^>]*>(.*?)</h1>", r"\n\n# \1\n", text)
    text = re.sub(r"<h2[^>]*>(.*?)</h2>", r"\n\n## \1\n", text)
    text = re.sub(r"<h3[^>]*>(.*?)</h3>", r"\n\n### \1\n", text)
    text = re.sub(r"<li>(.*?)</li>", r"- \1", text, flags=re.DOTALL)
    text = re.sub(r"<p>(.*?)</p>", r"\1\n", text, flags=re.DOTALL)
    text = re.sub(r"<strong>(.*?)</strong>", r"**\1**", text)
    text = re.sub(r"<em>(.*?)</em>", r"*\1*", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = htmlmod.unescape(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def main():
    data = json.loads(sys.stdin.read())
    title = data.get("title", {}).get("rendered", "Untitled")
    date = data.get("date", "")
    author_id = data.get("author", "")
    categories = data.get("categories", [])
    content_html = data.get("content", {}).get("rendered", "")

    print(f"# {title}")
    print(f"Date: {date}")
    print(f"Author ID: {author_id}")
    print(f"Categories: {categories}")

    vimeo = extract_player_embed_urls(content_html)
    if vimeo:
        print("\nVimeo (use player URLs below; https://vimeo.com/<id> often 404s):")
        for url in vimeo:
            print(f"  {url}")

    print("=" * 80)
    print(html_to_text(content_html))


if __name__ == "__main__":
    main()
