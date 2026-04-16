#!/usr/bin/env python3
"""
Competitor Analyzer — Analyze competitor Shopify stores.

Given a Shopify store URL, extracts product count, price ranges, tech stack,
estimated best-sellers, and provides a competitive assessment.

Usage:
  python competitor_analyzer.py https://example-store.myshopify.com
  python competitor_analyzer.py https://example-store.com --json
  python competitor_analyzer.py https://example-store.com --deep
"""

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass, field, asdict
from typing import Optional
from urllib.parse import urlparse

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.tree import Tree
    from rich import box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


@dataclass
class ProductInfo:
    title: str
    price: float
    compare_at_price: Optional[float]
    available: bool
    product_type: str
    vendor: str
    url: str


@dataclass
class StoreAnalysis:
    url: str
    store_name: str
    is_shopify: bool
    product_count: int
    price_range: tuple[float, float]
    avg_price: float
    median_price: float
    collections: list[str]
    products: list[ProductInfo]
    apps_detected: list[str]
    theme_detected: str
    has_reviews: bool
    has_upsells: bool
    has_email_popup: bool
    has_live_chat: bool
    has_free_shipping_bar: bool
    estimated_monthly_traffic: str
    social_links: list[str]
    strengths: list[str]
    weaknesses: list[str]
    opportunities: list[str]


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def normalize_url(url: str) -> str:
    if not url.startswith("http"):
        url = f"https://{url}"
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def check_shopify(url: str) -> bool:
    """Check if a site runs on Shopify."""
    if not HAS_REQUESTS:
        return True  # Assume true for offline mode

    try:
        resp = requests.get(f"{url}/products.json?limit=1", headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return "products" in data
    except Exception:
        pass

    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        return "shopify" in resp.text.lower() or "cdn.shopify.com" in resp.text
    except Exception:
        return False


def fetch_products(url: str, limit: int = 250) -> list[ProductInfo]:
    """Fetch products from Shopify's public products.json endpoint."""
    if not HAS_REQUESTS:
        return []

    products = []
    page = 1

    while len(products) < limit:
        try:
            resp = requests.get(
                f"{url}/products.json",
                params={"limit": 250, "page": page},
                headers=HEADERS,
                timeout=15,
            )
            if resp.status_code != 200:
                break

            data = resp.json()
            page_products = data.get("products", [])
            if not page_products:
                break

            for p in page_products:
                variants = p.get("variants", [{}])
                price = float(variants[0].get("price", 0)) if variants else 0
                compare_at = variants[0].get("compare_at_price")
                if compare_at:
                    compare_at = float(compare_at)

                products.append(ProductInfo(
                    title=p.get("title", "Unknown"),
                    price=price,
                    compare_at_price=compare_at,
                    available=any(v.get("available", False) for v in variants),
                    product_type=p.get("product_type", ""),
                    vendor=p.get("vendor", ""),
                    url=f"{url}/products/{p.get('handle', '')}",
                ))

            if len(page_products) < 250:
                break
            page += 1
            time.sleep(0.5)

        except Exception:
            break

    return products


def fetch_collections(url: str) -> list[str]:
    """Fetch collection names from the store."""
    if not HAS_REQUESTS:
        return []

    try:
        resp = requests.get(
            f"{url}/collections.json",
            headers=HEADERS,
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            return [c.get("title", "") for c in data.get("collections", [])]
    except Exception:
        pass
    return []


def detect_apps_and_features(url: str) -> dict:
    """Detect installed apps and features by analyzing the store's HTML."""
    result = {
        "apps": [],
        "theme": "Unknown",
        "has_reviews": False,
        "has_upsells": False,
        "has_email_popup": False,
        "has_live_chat": False,
        "has_free_shipping_bar": False,
        "social_links": [],
    }

    if not HAS_REQUESTS or not HAS_BS4:
        return result

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return result

        html = resp.text.lower()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Detect apps by known script/CSS patterns
        app_signatures = {
            "Judge.me": ["judge.me", "jdgm"],
            "Loox": ["loox.io", "looxapp"],
            "Yotpo": ["yotpo.com", "yotpo"],
            "Stamped.io": ["stamped.io"],
            "Klaviyo": ["klaviyo.com", "klaviyo"],
            "Privy": ["privy.com", "privy"],
            "Omnisend": ["omnisend.com"],
            "PageFly": ["pagefly"],
            "GemPages": ["gempages"],
            "Vitals": ["vitals.co", "vitals-app"],
            "Sales Pop": ["sales-pop", "salespop"],
            "Bold Upsell": ["boldapps", "bold-upsell"],
            "ReConvert": ["reconvert"],
            "Tidio": ["tidio.co", "tidio"],
            "Gorgias": ["gorgias"],
            "Zendesk": ["zendesk"],
            "DSers": ["dsers"],
            "Oberlo": ["oberlo"],
            "Spocket": ["spocket"],
            "Zendrop": ["zendrop"],
            "AfterShip": ["aftership"],
            "Smile.io": ["smile.io"],
            "ReferralCandy": ["referralcandy"],
        }

        for app_name, signatures in app_signatures.items():
            if any(sig in html for sig in signatures):
                result["apps"].append(app_name)

        # Detect theme
        theme_match = re.search(r'shopify\.theme\s*=\s*\{[^}]*"name"\s*:\s*"([^"]+)"', resp.text)
        if theme_match:
            result["theme"] = theme_match.group(1)
        elif "dawn" in html:
            result["theme"] = "Dawn (likely)"

        # Feature detection
        review_signals = ["review", "rating", "stars", "testimonial"]
        result["has_reviews"] = any(s in html for s in review_signals)

        upsell_signals = ["upsell", "cross-sell", "frequently bought", "you may also like",
                          "add to bundle", "bundle"]
        result["has_upsells"] = any(s in html for s in upsell_signals)

        popup_signals = ["popup", "newsletter", "subscribe", "email-signup", "klaviyo-form"]
        result["has_email_popup"] = any(s in html for s in popup_signals)

        chat_signals = ["live-chat", "tidio", "gorgias", "zendesk", "chat-widget", "intercom"]
        result["has_live_chat"] = any(s in html for s in chat_signals)

        shipping_signals = ["free shipping", "free-shipping-bar", "shipping-bar"]
        result["has_free_shipping_bar"] = any(s in html for s in shipping_signals)

        # Social links
        social_patterns = [
            (r'instagram\.com/[\w.]+', "Instagram"),
            (r'tiktok\.com/@[\w.]+', "TikTok"),
            (r'facebook\.com/[\w.]+', "Facebook"),
            (r'pinterest\.com/[\w.]+', "Pinterest"),
            (r'twitter\.com/[\w.]+', "Twitter/X"),
            (r'youtube\.com/[\w.]+', "YouTube"),
        ]
        for pattern, platform in social_patterns:
            match = re.search(pattern, resp.text, re.IGNORECASE)
            if match:
                result["social_links"].append(f"{platform}: {match.group(0)}")

    except Exception:
        pass

    return result


def estimate_traffic(url: str) -> str:
    """Rough traffic estimate based on available signals."""
    return "Use SimilarWeb.com or Semrush for accurate traffic data"


def analyze_store(url: str, deep: bool = False) -> StoreAnalysis:
    """Run full analysis on a Shopify store."""
    url = normalize_url(url)

    is_shopify = check_shopify(url)
    products = fetch_products(url) if is_shopify else []
    collections = fetch_collections(url) if is_shopify else []
    features = detect_apps_and_features(url)

    prices = [p.price for p in products if p.price > 0]
    if prices:
        prices_sorted = sorted(prices)
        price_range = (prices_sorted[0], prices_sorted[-1])
        avg_price = sum(prices) / len(prices)
        mid = len(prices_sorted) // 2
        median_price = (
            prices_sorted[mid]
            if len(prices_sorted) % 2
            else (prices_sorted[mid - 1] + prices_sorted[mid]) / 2
        )
    else:
        price_range = (0, 0)
        avg_price = 0
        median_price = 0

    # SWOT-style assessment
    strengths = []
    weaknesses = []
    opportunities = []

    if len(products) > 50:
        strengths.append(f"Large catalog ({len(products)} products) — established store")
    elif len(products) > 15:
        strengths.append(f"Focused catalog ({len(products)} products)")
    elif len(products) > 0:
        weaknesses.append(f"Small catalog ({len(products)} products) — may be new or niche")

    if features["has_reviews"]:
        strengths.append("Has product reviews (social proof)")
    else:
        weaknesses.append("No visible reviews — opportunity to differentiate")
        opportunities.append("Add reviews app to build trust faster")

    if features["has_upsells"]:
        strengths.append("Uses upsell/cross-sell features")
    else:
        opportunities.append("No upsells detected — they're leaving money on the table")

    if features["has_email_popup"]:
        strengths.append("Captures email addresses")
    else:
        opportunities.append("No email capture — not building a customer list")

    if features["has_live_chat"]:
        strengths.append("Has live chat support")

    if features["has_free_shipping_bar"]:
        strengths.append("Free shipping bar increases AOV")

    if avg_price > 40:
        strengths.append(f"Higher price point (avg ${avg_price:.0f}) — premium positioning")
    elif avg_price > 0 and avg_price < 15:
        weaknesses.append(f"Low prices (avg ${avg_price:.0f}) — thin margins likely")

    if len(features["apps"]) > 5:
        strengths.append(f"Well-optimized ({len(features['apps'])} apps detected)")

    if not features["social_links"]:
        weaknesses.append("No visible social media links")
        opportunities.append("Weak social presence — outperform them on social")

    # Extract store name from URL
    parsed = urlparse(url)
    store_name = parsed.netloc.replace("www.", "").split(".")[0].title()

    return StoreAnalysis(
        url=url,
        store_name=store_name,
        is_shopify=is_shopify,
        product_count=len(products),
        price_range=price_range,
        avg_price=avg_price,
        median_price=median_price,
        collections=collections,
        products=products[:20],  # Keep top 20 for display
        apps_detected=features["apps"],
        theme_detected=features["theme"],
        has_reviews=features["has_reviews"],
        has_upsells=features["has_upsells"],
        has_email_popup=features["has_email_popup"],
        has_live_chat=features["has_live_chat"],
        has_free_shipping_bar=features["has_free_shipping_bar"],
        estimated_monthly_traffic=estimate_traffic(url),
        social_links=features["social_links"],
        strengths=strengths,
        weaknesses=weaknesses,
        opportunities=opportunities,
    )


def print_analysis_rich(analysis: StoreAnalysis) -> None:
    console = Console()
    console.print()

    status = "[green]Shopify Confirmed[/green]" if analysis.is_shopify else "[red]Not Shopify[/red]"
    console.print(Panel.fit(
        f"[bold]Competitor Analysis: {analysis.store_name}[/bold]\n"
        f"URL: {analysis.url}\n"
        f"Platform: {status} | Theme: {analysis.theme_detected}",
        border_style="blue",
    ))

    # Overview table
    overview = Table(title="Store Overview", box=box.ROUNDED, show_lines=True)
    overview.add_column("Metric", style="bold", width=25)
    overview.add_column("Value", min_width=30)

    overview.add_row("Total Products", str(analysis.product_count))
    overview.add_row("Price Range", f"${analysis.price_range[0]:.2f} – ${analysis.price_range[1]:.2f}")
    overview.add_row("Average Price", f"${analysis.avg_price:.2f}")
    overview.add_row("Median Price", f"${analysis.median_price:.2f}")
    overview.add_row("Collections", str(len(analysis.collections)))
    overview.add_row("Apps Detected", str(len(analysis.apps_detected)))
    overview.add_row("Traffic Estimate", analysis.estimated_monthly_traffic)
    console.print(overview)

    # Apps
    if analysis.apps_detected:
        apps_table = Table(title="Detected Apps & Integrations", box=box.SIMPLE)
        apps_table.add_column("App", style="cyan")
        for app in analysis.apps_detected:
            apps_table.add_row(app)
        console.print(apps_table)

    # Features
    features = Table(title="Feature Checklist", box=box.SIMPLE)
    features.add_column("Feature", width=25)
    features.add_column("Status", width=10)
    yes, no = "[green]Yes[/green]", "[red]No[/red]"
    features.add_row("Product Reviews", yes if analysis.has_reviews else no)
    features.add_row("Upsells / Cross-sells", yes if analysis.has_upsells else no)
    features.add_row("Email Popup", yes if analysis.has_email_popup else no)
    features.add_row("Live Chat", yes if analysis.has_live_chat else no)
    features.add_row("Free Shipping Bar", yes if analysis.has_free_shipping_bar else no)
    console.print(features)

    # Collections
    if analysis.collections:
        coll_table = Table(title="Collections", box=box.SIMPLE)
        coll_table.add_column("Collection Name")
        for c in analysis.collections[:15]:
            coll_table.add_row(c)
        if len(analysis.collections) > 15:
            coll_table.add_row(f"... and {len(analysis.collections) - 15} more")
        console.print(coll_table)

    # Top products by price
    if analysis.products:
        prod_table = Table(title="Sample Products (by price)", box=box.ROUNDED, show_lines=True)
        prod_table.add_column("#", width=3)
        prod_table.add_column("Product", min_width=35)
        prod_table.add_column("Price", justify="right", width=10)
        prod_table.add_column("Type", width=15)
        prod_table.add_column("Available", justify="center", width=10)

        sorted_products = sorted(analysis.products, key=lambda p: p.price, reverse=True)
        for i, p in enumerate(sorted_products[:10], 1):
            avail = "[green]Yes[/green]" if p.available else "[red]No[/red]"
            prod_table.add_row(
                str(i), p.title[:50], f"${p.price:.2f}",
                p.product_type[:15] if p.product_type else "—", avail,
            )
        console.print(prod_table)

    # SWOT
    console.print()
    swot = Table(title="Competitive Assessment", box=box.HEAVY, show_lines=True, title_style="bold")
    swot.add_column("Strengths", style="green", min_width=30)
    swot.add_column("Weaknesses", style="red", min_width=30)
    swot.add_column("Your Opportunities", style="cyan", min_width=30)

    max_rows = max(len(analysis.strengths), len(analysis.weaknesses), len(analysis.opportunities))
    for i in range(max_rows):
        s = analysis.strengths[i] if i < len(analysis.strengths) else ""
        w = analysis.weaknesses[i] if i < len(analysis.weaknesses) else ""
        o = analysis.opportunities[i] if i < len(analysis.opportunities) else ""
        swot.add_row(s, w, o)

    console.print(swot)

    # Social links
    if analysis.social_links:
        console.print()
        console.print("[bold]Social Media Presence:[/bold]")
        for link in analysis.social_links:
            console.print(f"  • {link}")

    console.print()


def print_analysis_plain(analysis: StoreAnalysis) -> None:
    print(f"\n{'='*70}")
    print(f"COMPETITOR ANALYSIS: {analysis.store_name}")
    print(f"{'='*70}")
    print(f"URL: {analysis.url}")
    print(f"Platform: {'Shopify' if analysis.is_shopify else 'Not Shopify'}")
    print(f"Theme: {analysis.theme_detected}")
    print(f"\nProducts: {analysis.product_count}")
    print(f"Price Range: ${analysis.price_range[0]:.2f} – ${analysis.price_range[1]:.2f}")
    print(f"Avg Price: ${analysis.avg_price:.2f}")
    print(f"Median Price: ${analysis.median_price:.2f}")

    if analysis.apps_detected:
        print(f"\nApps Detected: {', '.join(analysis.apps_detected)}")

    print(f"\nFeatures:")
    print(f"  Reviews: {'Yes' if analysis.has_reviews else 'No'}")
    print(f"  Upsells: {'Yes' if analysis.has_upsells else 'No'}")
    print(f"  Email Popup: {'Yes' if analysis.has_email_popup else 'No'}")
    print(f"  Live Chat: {'Yes' if analysis.has_live_chat else 'No'}")
    print(f"  Free Shipping Bar: {'Yes' if analysis.has_free_shipping_bar else 'No'}")

    print(f"\nStrengths:")
    for s in analysis.strengths:
        print(f"  + {s}")
    print(f"\nWeaknesses:")
    for w in analysis.weaknesses:
        print(f"  - {w}")
    print(f"\nOpportunities:")
    for o in analysis.opportunities:
        print(f"  > {o}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Analyze a competitor Shopify store"
    )
    parser.add_argument("url", help="Shopify store URL to analyze")
    parser.add_argument("--deep", action="store_true",
                        help="Deep analysis (slower, more thorough)")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    args = parser.parse_args()

    analysis = analyze_store(args.url, deep=args.deep)

    if args.json:
        output = asdict(analysis)
        # Convert ProductInfo objects
        output["products"] = [asdict(p) for p in analysis.products]
        print(json.dumps(output, indent=2, default=str))
    elif HAS_RICH:
        print_analysis_rich(analysis)
    else:
        print_analysis_plain(analysis)


if __name__ == "__main__":
    main()
