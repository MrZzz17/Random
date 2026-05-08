#!/usr/bin/env python3
"""
Seeking Alpha Full Article Extractor (Aggressive)

Designed to extract the COMPLETE article text, even from hard paywalled Premium articles.
Uses multiple techniques:
  1. Official undocumented API
  2. Full page scrape looking for React state (window.__PRELOADED_STATE__)
  3. Paywall overlay removal
  4. Content extraction from hidden divs and JSON blobs

Style matches bulk_download_by_ext.py

Usage:
    python seeking_alpha_full_extractor.py "https://seekingalpha.com/article/4891793-bitmine-immersion-ethereum-pivot-driving-hidden-upside"
"""

import sys
import re
import json
import time
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup, NavigableString


USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/134.0.0.0 Safari/537.36"
)

REQUEST_TIMEOUT = 25
POLITE_DELAY = 0.8


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
    raise ValueError(f"Could not parse article ID from: {url_or_id}")


def fetch_with_session(url: str, is_json: bool = False) -> requests.Response:
    """Use a persistent session with realistic browser headers."""
    session = requests.Session()
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json, text/html,application/xhtml+xml" if is_json else "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://seekingalpha.com/",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }
    resp = session.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    time.sleep(POLITE_DELAY)
    return resp


def extract_from_react_state(html: str) -> str | None:
    """Look for full article content inside React state JSON blobs."""
    # Common patterns for Seeking Alpha's React app
    patterns = [
        r'__PRELOADED_STATE__\s*=\s*({.+?});',
        r'window\.__INITIAL_STATE__\s*=\s*({.+?});',
        r'"content":\s*"((?:[^"\\]|\\.)+)"',
        r'"body":\s*"((?:[^"\\]|\\.)+)"',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, html, re.DOTALL)
        for match in matches:
            if isinstance(match, str) and len(match) > 500:
                # Unescape JSON string
                try:
                    cleaned = match.replace('\\"', '"').replace('\\n', '\n')
                    return cleaned
                except:
                    continue
    return None


def remove_paywall_elements(soup: BeautifulSoup):
    """Remove common paywall, login, and overlay elements."""
    selectors_to_remove = [
        "[class*='paywall']", "[class*='Paywall']", "[class*='login']", 
        "[class*='modal']", "[id*='paywall']", ".subscription-wall",
        "div:contains('Go Premium')", "div:contains('Subscribe to continue')",
        ".auth-wall", ".article-paywall"
    ]
    for selector in selectors_to_remove:
        for element in soup.select(selector):
            element.decompose()


def clean_extracted_text(text: str) -> str:
    if not text:
        return ""
    # Basic cleanup
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r' +', ' ', text)
    text = text.replace('\\n', '\n').replace('\\r', '')
    return text.strip()


def main():
    if len(sys.argv) < 2:
        print("Usage: python seeking_alpha_full_extractor.py <URL or Article ID>")
        print("Example: python seeking_alpha_full_extractor.py 4891793")
        sys.exit(1)

    input_arg = sys.argv[1]
    article_id = get_article_id(input_arg)
    article_url = f"https://seekingalpha.com/article/{article_id}"
    
    print(f"🔍 Attempting to extract FULL article: {article_url}")
    print(f"Article ID: {article_id}\n")

    full_text = ""
    title = "Unknown Title"

    try:
        # Method 1: Try API with expanded includes
        print("→ Trying API endpoint...")
        api_url = f"https://seekingalpha.com/api/v3/articles/{article_id}?include=author,primaryTickers,comments"
        resp = fetch_with_session(api_url, is_json=True)
        data = resp.json()
        
        attr = data.get("data", {}).get("attributes", {})
        title = attr.get("title", title)
        content = attr.get("content", "")
        
        if content and len(content) > 800:
            full_text = content
            print("✅ Success via API (full content retrieved)")
        else:
            print("   API only returned preview. Trying full page scrape...")

        # Method 2: Full page scrape with aggressive techniques
        if not full_text:
            print("→ Performing full page scrape with React state extraction...")
            resp = fetch_with_session(article_url)
            html = resp.text
            soup = BeautifulSoup(html, "html.parser")
            
            # Extract title more reliably
            title_tag = soup.find("h1") or soup.find("title")
            if title_tag:
                title = title_tag.get_text(strip=True).split(" | ")[0].strip()
            
            remove_paywall_elements(soup)
            
            # Try React state extraction (most promising for hard paywalls)
            state_content = extract_from_react_state(html)
            if state_content and len(state_content) > len(full_text):
                full_text = state_content
                print("✅ Extracted content from React state blob")
            
            # Fallback: main article body
            if not full_text:
                body = (soup.find("div", {"data-test-id": "article-body"}) or
                       soup.find("article") or
                       soup.find("div", class_=re.compile(r"article-body|content-body|prose", re.I)))
                if body:
                    full_text = str(body)
                    print("✅ Extracted from main article container")
        
        cleaned = clean_extracted_text(full_text)
        
        print("\n" + "="*100)
        print(f"TITLE: {title}")
        print("="*100)
        print(cleaned[:2500])
        if len(cleaned) > 2500:
            print("\n... [truncated - full content saved to file]")
        
        # Save to file
        safe_title = re.sub(r'[^a-z0-9]+', '_', title.lower())[:80]
        output_file = Path(f"SA_FULL_{article_id}_{safe_title}.md")
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n")
            f.write(f"**URL:** {article_url}\n")
            f.write(f"**Extracted:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Full Article\n\n")
            f.write(cleaned or "Failed to extract full content.")
            f.write("\n\n---\n*Extracted using aggressive Seeking Alpha scraper. For personal use only.*\n")
        
        print(f"\n💾 Full output saved to: {output_file}")
        
        if not cleaned or len(cleaned) < 1000:
            print("\n⚠️  Warning: The script could only retrieve a preview.")
            print("   This article appears to use strong server-side paywalling.")
            print("   Consider using a logged-in browser session or premium account for complete access.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
