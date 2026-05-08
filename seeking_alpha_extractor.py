#!/usr/bin/env python3
"""
Seeking Alpha Full Article + Comments Extractor (v2)

This version:
1. Tries the JSON API first (fast when it works)
2. Falls back to full page scraping when content is paywalled
3. Fetches top comments
4. Better cleaning and formatting

Usage:
    python seeking_alpha_extractor.py "https://seekingalpha.com/article/4891793-bitmine-immersion-ethereum-pivot-driving-hidden-upside"
"""

import sys
import re
import json
import requests
from bs4 import BeautifulSoup, NavigableString
from urllib.parse import urlparse
from pathlib import Path
from datetime import datetime


def get_article_id(url_or_id: str) -> str:
    s = str(url_or_id).strip()
    if re.match(r'^\d+$', s):
        return s
    match = re.search(r'/article/(\d+)', s)
    if match:
        return match.group(1)
    match = re.search(r'(\d{6,})', s)
    if match:
        return match.group(1)
    raise ValueError(f"Could not extract article ID from: {url_or_id}")


def fetch_api(article_id: str) -> dict:
    """Try API first - works for many articles."""
    url = f"https://seekingalpha.com/api/v3/articles/{article_id}"
    params = {
        "include": "author,primaryTickers,secondaryTickers,otherTags,author.authorResearch,comments",
        "fields[articles]": "title,content,summary,publishOn,isPaywalled,commentCount"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
        "Referer": "https://seekingalpha.com/",
    }
    resp = requests.get(url, params=params, headers=headers, timeout=20)
    if resp.status_code == 200:
        return resp.json()
    return None


def scrape_full_page(url: str) -> dict:
    """Aggressive full page scrape looking for content in React state and main article blocks."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml",
        "Referer": "https://seekingalpha.com/",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    html = resp.text
    soup = BeautifulSoup(html, "html.parser")
    
    title_tag = soup.find("h1") or soup.find("title")
    title_text = title_tag.get_text(strip=True).split("|")[0].strip() if title_tag else "Unknown Title"
    
    content = ""
    
    # Look for main article content containers (common SA classes)
    selectors = [
        "div[data-test-id='article-body']",
        "article",
        "div[class*='article-body']",
        "div[class*='content-body']",
        "div.prose",
        ".sa-article-body"
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        if elements:
            for el in elements:
                content += str(el)
            break
    
    # If still empty, try to find large paragraph blocks
    if not content or len(content) < 300:
        paragraphs = soup.find_all("p")
        long_paras = [str(p) for p in paragraphs if len(str(p)) > 50]
        if long_paras:
            content = "\n\n".join(long_paras[:30])
    
    # Try to extract from JSON state in script tags (common in React SPAs)
    scripts = soup.find_all("script")
    for script in scripts:
        if script.string and any(k in script.string.lower() for k in ["content", "body", "articlebody", "__preloaded", "initialstate"]):
            # Look for large JSON containing the full text
            match = re.search(r'("content":\s*")(.*?)(?<!\\)"', script.string, re.DOTALL)
            if match:
                potential_content = match.group(2).replace('\\"', '"')
                if len(potential_content) > len(content):
                    content = potential_content
                    break
    
    return {
        "title": title_text,
        "content_html": content,
        "html_length": len(html)
    }


def fetch_comments(article_id: str, limit: int = 20) -> list:
    """Fetch comments for the article."""
    url = "https://seekingalpha.com/api/v3/comments"
    params = {
        "filter[article_id]": article_id,
        "page[size]": limit,
        "sort": "-createdAt",
        "include": "author"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            comments = []
            for item in data.get("data", []):
                attr = item.get("attributes", {})
                comments.append({
                    "author": attr.get("authorName", "Anonymous"),
                    "created": attr.get("createdAt", ""),
                    "body": attr.get("body", ""),
                    "likes": attr.get("likeCount", 0)
                })
            return comments
    except:
        pass
    return []


def clean_content(html_content: str) -> str:
    if not html_content:
        return "Full content could not be extracted. This article appears to be Premium only."
    
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Remove scripts, styles, ads, etc.
    for tag in soup.find_all(["script", "style", "nav", "header", "footer", "aside", "button"]):
        tag.decompose()
    
    text = soup.get_text(separator="\n\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned = "\n\n".join(lines)
    
    # Clean up common artifacts
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = re.sub(r' +', ' ', cleaned)
    cleaned = cleaned.replace('\n \n', '\n\n')
    
    return cleaned.strip()


def main():
    if len(sys.argv) < 2:
        print("Usage: python seeking_alpha_extractor.py <URL or Article ID>")
        sys.exit(1)
    
    input_arg = sys.argv[1]
    article_id = get_article_id(input_arg)
    article_url = f"https://seekingalpha.com/article/{article_id}"
    
    print(f"Fetching full article: {article_url}")
    print(f"Article ID: {article_id}\n")
    
    # Try API first
    data = fetch_api(article_id)
    content = ""
    title = ""
    is_paywalled = True
    
    if data and "data" in data:
        attr = data["data"].get("attributes", {})
        title = attr.get("title", "Untitled")
        content = attr.get("content", "")
        is_paywalled = attr.get("isPaywalled", True)
        print(f"Title: {title}")
        print(f"API Paywalled: {is_paywalled}\n")
    
    # Fallback to full page scrape if API gave little content
    if not content or len(content) < 500:
        print("API returned limited content. Scraping full page...")
        page_data = scrape_full_page(article_url)
        title = page_data.get("title", title)
        content = page_data.get("content_html", content)
        print(f"Used full page scrape. Title: {title}\n")
    
    clean_text = clean_content(content)
    
    print("="*90)
    print("FULL ARTICLE")
    print("="*90)
    print(clean_text[:2000] + "\n\n..." if len(clean_text) > 2000 else clean_text)
    
    # Fetch comments
    print("\n" + "="*90)
    print("TOP COMMENTS")
    print("="*90)
    comments = fetch_comments(article_id, limit=15)
    
    if comments:
        for i, c in enumerate(comments, 1):
            print(f"{i}. {c['author']} ({c.get('created', '')[:10]}) [+{c['likes']}]")
            print(f"   {c['body'][:280]}...\n")
    else:
        print("No comments found or comments are also behind login.")
    
    # Save to file
    safe_title = re.sub(r'[^a-zA-Z0-9\-_]', '_', title.lower()[:60])
    output_path = Path(f"sa_full_{article_id}_{safe_title}.md")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        f.write(f"**Source:** {article_url}\n")
        f.write(f"**Extracted:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write("## Full Article\n\n")
        f.write(clean_text)
        f.write("\n\n---\n\n")
        f.write("## Comments\n\n")
        for c in comments:
            f.write(f"**{c['author']}**  [+{c['likes']}]\n")
            f.write(f"{c['body']}\n\n---\n\n")
        f.write("\n*Extracted using Seeking Alpha API + page scraping. For personal research only.*")
    
    print(f"\n💾 Full article + comments saved to: {output_path}")


if __name__ == "__main__":
    main()
