"""
Find Vimeo video links from recent Fundstrat Direct posts in a given category.

Usage (run from this directory so imports resolve):
  cd "$(dirname "$0")"
  python3 find_videos.py --category crypto-comments --count 10
  python3 find_videos.py --category-id 10045 --count 5
"""
import argparse
import json
import pathlib
import ssl
import sys
import urllib.request

_SCRIPTS = pathlib.Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from vimeo_urls import extract_player_embed_urls


BASE = "https://fundstratdirect.com/wp-json/wp/v2"
_SSL_CTX = ssl.create_default_context()

KNOWN_CATEGORIES = {
    "crypto-comments": 10045,
    "crypto-strategy": 4593,
    "crypto-research": 10428,
    "macro-minute": 10041,
    "macro-videos": 48,
    "webinars": 10457,
}


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=_SSL_CTX, timeout=60) as resp:
        return json.loads(resp.read())


def resolve_category_id(slug):
    if slug in KNOWN_CATEGORIES and KNOWN_CATEGORIES[slug]:
        return KNOWN_CATEGORIES[slug]
    cats = fetch_json(f"{BASE}/categories?slug={slug}")
    if cats:
        return cats[0]["id"]
    cats = fetch_json(f"{BASE}/categories?search={slug}")
    if cats:
        return cats[0]["id"]
    return None


def find_videos(category_id, count):
    posts = fetch_json(
        f"{BASE}/posts?categories={category_id}&per_page={count}"
        f"&orderby=date&order=desc"
    )
    results = []
    for post in posts:
        content = post.get("content", {}).get("rendered", "")
        player_urls = extract_player_embed_urls(content)
        title = post.get("title", {}).get("rendered", "")
        date = post.get("date", "")
        pid = post["id"]
        link = post.get("link", "")
        results.append({
            "id": pid,
            "title": title,
            "date": date,
            "link": link,
            "player_urls": player_urls,
        })
    return results


def main():
    parser = argparse.ArgumentParser(description="Find Vimeo links in Fundstrat posts")
    parser.add_argument("--category", type=str, help="Category slug")
    parser.add_argument("--category-id", type=int, help="Category ID (overrides slug)")
    parser.add_argument("--count", type=int, default=10, help="Number of posts to check")
    args = parser.parse_args()

    cat_id = args.category_id
    if not cat_id and args.category:
        cat_id = resolve_category_id(args.category)
    if not cat_id:
        print("ERROR: Could not resolve category. Use --category-id directly.")
        print("\nKnown categories:")
        for slug, cid in KNOWN_CATEGORIES.items():
            print(f"  {slug}: {cid}")
        return

    print(f"Searching category ID {cat_id}, last {args.count} posts...\n")
    results = find_videos(cat_id, args.count)

    for r in results:
        has_video = "VIDEO" if r["player_urls"] else "no video"
        print(f"[{r['date'][:10]}] [{has_video}] {r['title']}")
        if r["player_urls"]:
            for v in r["player_urls"]:
                print(f"  -> {v}")
        print(f"  {r['link']}")
        print()


if __name__ == "__main__":
    main()
