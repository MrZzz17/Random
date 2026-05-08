#!/usr/bin/env python3
"""
Seeking Alpha Paywall Bypass Scraper

Replicates the logic used by popular Chrome/Firefox/Tampermonkey extensions:
- Fetches the full page like a real browser
- Removes paywall overlays, modals, backdrops
- Restores and extracts the actual article content (which is often already in the DOM)
- Cleans up the HTML into readable markdown

This is how most "Seeking Alpha Paywall Remover" extensions work.

Usage:
    python seeking_alpha_paywall_bypass.py "https://seekingalpha.com/article/4891793-..."
"""

import sys
import re
import time
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup, NavigableString, Tag


USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/134.0.0.0 Safari/537.36"
)

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


def fetch_full_page(url: str) -> str:
    """Fetch page with browser-like headers."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://seekingalpha.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Cache-Control": "max-age=0",
    }
    
    session = requests.Session()
    resp = session.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text


def remove_paywall_elements(soup: BeautifulSoup):
    """Aggressively remove all known paywall, modal, and overlay elements."""
    # Remove by ID
    for element in soup.find_all(id=re.compile(r'paywall|modal|backdrop|tp-modal|auth', re.I)):
        element.decompose()
    
    # Remove by class
    paywall_classes = [
        'paywall', 'Paywall', 'tp-modal', 'modal', 'backdrop', 'overlay',
        'subscription-wall', 'auth-wall', 'login-wall', 'premium-gate'
    ]
    for cls in paywall_classes:
        for element in soup.find_all(class_=re.compile(cls, re.I)):
            element.decompose()
    
    # Remove elements containing specific text
    for text in ['Go Premium', 'Subscribe to continue', 'Unlock with Premium', 
                 'This article is for Premium members', 'Sign in to continue']:
        for element in soup.find_all(string=re.compile(text, re.I)):
            if element.parent:
                element.parent.decompose()
    
    # Remove common wrapper divs that hide content
    for div in soup.find_all('div'):
        style = div.get('style', '')
        if any(k in style.lower() for k in ['blur', 'overflow: hidden', 'pointer-events: none']):
            div.decompose()


def extract_main_content(soup: BeautifulSoup) -> str:
    """Find the main article content using multiple heuristics."""
    candidates = []
    
    # High confidence selectors
    for selector in [
        'div[data-test-id="article-body"]',
        'article',
        'div.article-body',
        'div.content-body',
        '.prose',
        'div.sa-article-body',
        'div[id*="article"]'
    ]:
        elements = soup.select(selector)
        for el in elements:
            if el and len(str(el)) > 500:
                candidates.append(str(el))
    
    # If nothing good found, take the largest text-containing div
    if not candidates:
        divs = soup.find_all('div')
        for div in sorted(divs, key=lambda x: len(str(x)), reverse=True):
            text = div.get_text(strip=True)
            if len(text) > 800 and 'investment thesis' in text.lower():
                candidates.append(str(div))
                break
    
    if candidates:
        return max(candidates, key=len)
    return ""


def html_to_markdown(html: str, title: str = "") -> str:
    """Convert cleaned HTML to readable markdown."""
    if not html:
        return "Could not extract article content."
    
    soup = BeautifulSoup(html, "html.parser")
    remove_paywall_elements(soup)
    
    # Extract text with better formatting
    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4']):
        tag.insert_before('\n\n')
        tag.insert_after('\n\n')
    
    text = soup.get_text(separator='\n\n')
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    markdown = '\n\n'.join(lines)
    
    # Clean up artifacts
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)
    markdown = re.sub(r'\[.*?\]\(.*?\)', '', markdown)  # remove some links if messy
    
    return f"# {title}\n\n{markdown}" if title else markdown


def main():
    if len(sys.argv) < 2:
        print("Usage: python seeking_alpha_paywall_bypass.py <URL or Article ID>")
        sys.exit(1)

    arg = sys.argv[1]
    article_id = get_article_id(arg)
    url = f"https://seekingalpha.com/article/{article_id}"
    
    print(f"🔧 Running Seeking Alpha Paywall Bypass on:")
    print(f"   {url}\n")
    
    try:
        html = fetch_full_page(url)
        soup = BeautifulSoup(html, "html.parser")
        
        # Get title
        title_tag = soup.find('h1') or soup.find('title')
        title = title_tag.get_text(strip=True).split('|')[0].strip() if title_tag else f"Article {article_id}"
        
        remove_paywall_elements(soup)
        content_html = extract_main_content(soup)
        
        markdown = html_to_markdown(content_html, title)
        
        print("="*90)
        print(title.upper())
        print("="*90)
        print(markdown[:3000])
        if len(markdown) > 3000:
            print("\n... (content continues - full version saved)")
        
        # Save
        safe_name = re.sub(r'[^a-z0-9]+', '_', title.lower())[:80]
        output_path = Path(f"SA_BYPASS_{article_id}_{safe_name}.md")
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown)
            f.write("\n\n---\n")
            f.write(f"**Source:** {url}\n")
            f.write(f"**Bypassed:** {time.strftime('%Y-%m-%d %H:%M')}\n")
            f.write("**Method:** DOM cleanup mimicking browser extension behavior\n")
        
        print(f"\n✅ Full article saved to: {output_path}")
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
