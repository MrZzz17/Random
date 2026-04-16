#!/usr/bin/env python3
"""
Niche Scorer — Evaluate dropshipping niches on a 1-100 scale.

Scores each niche across five weighted dimensions:
  - Demand trajectory (Google Trends)   25%
  - Competition density                 20%
  - Margin potential                    25%
  - Shipping feasibility               15%
  - Social virality                    15%

Usage:
  python niche_scorer.py                          # Score default niches
  python niche_scorer.py -n "smart home" "pet"    # Score custom niches
  python niche_scorer.py --json                   # Output as JSON
"""

import argparse
import json
import sys
import time
from dataclasses import dataclass, field, asdict
from typing import Optional

try:
    from pytrends.request import TrendReq
    HAS_PYTRENDS = True
except ImportError:
    HAS_PYTRENDS = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


DEFAULT_NICHES = [
    {
        "name": "Smart Home Accessories",
        "keywords": ["smart home accessories", "led strip lights", "smart plug"],
        "avg_product_cost": 6.0,
        "avg_retail_price": 30.0,
        "avg_weight_kg": 0.3,
        "fragile": False,
        "us_warehouse_available": True,
        "social_hashtags": ["#smarthome", "#ledlights", "#homedecor"],
    },
    {
        "name": "Sustainable Daily Products",
        "keywords": ["eco friendly products", "reusable bags", "bamboo utensils"],
        "avg_product_cost": 4.0,
        "avg_retail_price": 22.0,
        "avg_weight_kg": 0.2,
        "fragile": False,
        "us_warehouse_available": True,
        "social_hashtags": ["#ecofriendly", "#sustainable", "#zerowaste"],
    },
    {
        "name": "Pet Wellness & Accessories",
        "keywords": ["pet accessories", "slow feeder dog bowl", "pet calming bed"],
        "avg_product_cost": 7.0,
        "avg_retail_price": 35.0,
        "avg_weight_kg": 0.8,
        "fragile": False,
        "us_warehouse_available": True,
        "social_hashtags": ["#dogsofinstagram", "#petproducts", "#dogmom"],
    },
    {
        "name": "Desk / WFH Productivity",
        "keywords": ["desk accessories", "monitor stand", "cable management"],
        "avg_product_cost": 8.0,
        "avg_retail_price": 32.0,
        "avg_weight_kg": 0.6,
        "fragile": False,
        "us_warehouse_available": True,
        "social_hashtags": ["#desksetup", "#workfromhome", "#deskaccessories"],
    },
    {
        "name": "Portable Fitness & Recovery",
        "keywords": ["resistance bands", "massage gun", "foam roller"],
        "avg_product_cost": 10.0,
        "avg_retail_price": 45.0,
        "avg_weight_kg": 1.0,
        "fragile": False,
        "us_warehouse_available": True,
        "social_hashtags": ["#fitness", "#homegym", "#recovery"],
    },
]


@dataclass
class NicheScore:
    name: str
    demand_score: float = 0.0
    competition_score: float = 0.0
    margin_score: float = 0.0
    shipping_score: float = 0.0
    social_score: float = 0.0
    total_score: float = 0.0
    demand_detail: str = ""
    competition_detail: str = ""
    margin_detail: str = ""
    shipping_detail: str = ""
    social_detail: str = ""
    grade: str = ""


WEIGHTS = {
    "demand": 0.25,
    "competition": 0.20,
    "margin": 0.25,
    "shipping": 0.15,
    "social": 0.15,
}


def score_demand(keywords: list[str], use_api: bool = True) -> tuple[float, str]:
    """Score demand trajectory using Google Trends data (0-100)."""
    if not use_api or not HAS_PYTRENDS:
        return _score_demand_heuristic(keywords)

    try:
        pytrends = TrendReq(hl="en-US", tz=360)
        primary_kw = keywords[0]
        pytrends.build_payload([primary_kw], timeframe="today 12-m", geo="US")
        interest = pytrends.interest_over_time()

        if interest.empty or primary_kw not in interest.columns:
            return _score_demand_heuristic(keywords)

        values = interest[primary_kw].values
        n = len(values)
        if n < 10:
            return _score_demand_heuristic(keywords)

        first_half_avg = values[: n // 2].mean()
        second_half_avg = values[n // 2 :].mean()
        current_level = values[-4:].mean()

        if first_half_avg == 0:
            trend_ratio = 1.0
        else:
            trend_ratio = second_half_avg / first_half_avg

        # Trend direction contributes up to 50 points
        if trend_ratio >= 1.3:
            trend_pts = 50
            direction = "Strong uptrend"
        elif trend_ratio >= 1.1:
            trend_pts = 40
            direction = "Moderate uptrend"
        elif trend_ratio >= 0.9:
            trend_pts = 25
            direction = "Stable"
        elif trend_ratio >= 0.7:
            trend_pts = 10
            direction = "Declining"
        else:
            trend_pts = 0
            direction = "Sharp decline"

        # Absolute interest level contributes up to 50 points
        level_pts = min(50, current_level * 0.7)

        score = min(100, trend_pts + level_pts)
        detail = f"{direction} ({trend_ratio:.2f}x), interest level {current_level:.0f}/100"
        return score, detail

    except Exception:
        return _score_demand_heuristic(keywords)


def _score_demand_heuristic(keywords: list[str]) -> tuple[float, str]:
    """Fallback heuristic scoring when Google Trends API is unavailable."""
    high_demand = [
        "smart home", "led", "pet", "fitness", "eco", "sustainable",
        "wireless", "organizer", "massage", "resistance", "yoga",
    ]
    score = 40
    matches = sum(1 for k in keywords for hd in high_demand if hd in k.lower())
    score += min(40, matches * 15)
    return score, f"Heuristic estimate ({matches} high-demand keyword matches)"


def score_competition(keywords: list[str], use_api: bool = True) -> tuple[float, str]:
    """
    Score competition density (0-100, higher = LESS competition = better).
    Uses Google search result count as a proxy.
    """
    if not use_api or not HAS_REQUESTS:
        return _score_competition_heuristic(keywords)

    try:
        query = f'"{keywords[0]}" shopify store'
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        resp = requests.get(
            "https://www.google.com/search",
            params={"q": query},
            headers=headers,
            timeout=10,
        )

        if resp.status_code != 200:
            return _score_competition_heuristic(keywords)

        text = resp.text.lower()
        # Extract approximate result count
        import re
        match = re.search(r"about ([\d,]+) results", text)
        if match:
            count = int(match.group(1).replace(",", ""))
        else:
            return _score_competition_heuristic(keywords)

        # Fewer results = less competition = higher score
        if count < 100_000:
            score = 90
            level = "Very low competition"
        elif count < 500_000:
            score = 75
            level = "Low competition"
        elif count < 2_000_000:
            score = 55
            level = "Moderate competition"
        elif count < 10_000_000:
            score = 35
            level = "High competition"
        else:
            score = 15
            level = "Very high competition"

        return score, f"{level} (~{count:,} search results)"

    except Exception:
        return _score_competition_heuristic(keywords)


def _score_competition_heuristic(keywords: list[str]) -> tuple[float, str]:
    """Fallback heuristic for competition scoring."""
    saturated = ["phone case", "t-shirt", "jewelry", "fitness", "pet"]
    emerging = ["smart home", "eco", "sustainable", "wfh", "desk setup", "recovery"]

    primary = keywords[0].lower()
    for kw in saturated:
        if kw in primary:
            return 35, f"Heuristic: '{kw}' is a saturated category"
    for kw in emerging:
        if kw in primary:
            return 70, f"Heuristic: '{kw}' is an emerging category"
    return 55, "Heuristic: moderate estimated competition"


def score_margin(avg_cost: float, avg_price: float) -> tuple[float, str]:
    """Score margin potential (0-100) based on markup ratio."""
    if avg_cost <= 0:
        return 0, "Invalid cost data"

    markup = avg_price / avg_cost
    margin_pct = ((avg_price - avg_cost) / avg_price) * 100

    if markup >= 5.0:
        score = 95
    elif markup >= 4.0:
        score = 85
    elif markup >= 3.0:
        score = 70
    elif markup >= 2.5:
        score = 55
    elif markup >= 2.0:
        score = 35
    else:
        score = 15

    detail = f"{markup:.1f}x markup, {margin_pct:.0f}% margin (${avg_cost:.2f} → ${avg_price:.2f})"
    return score, detail


def score_shipping(weight_kg: float, fragile: bool, us_warehouse: bool) -> tuple[float, str]:
    """Score shipping feasibility (0-100)."""
    score = 50
    details = []

    if weight_kg <= 0.3:
        score += 25
        details.append("lightweight")
    elif weight_kg <= 0.8:
        score += 15
        details.append("moderate weight")
    elif weight_kg <= 2.0:
        score += 5
        details.append("heavier item")
    else:
        score -= 10
        details.append("heavy — high shipping cost")

    if fragile:
        score -= 15
        details.append("fragile — damage risk")
    else:
        score += 10
        details.append("durable")

    if us_warehouse:
        score += 15
        details.append("US warehouse available")
    else:
        score -= 5
        details.append("China shipping only")

    score = max(0, min(100, score))
    return score, "; ".join(details)


def score_social(hashtags: list[str], use_api: bool = True) -> tuple[float, str]:
    """Score social media virality potential (0-100)."""
    viral_indicators = [
        "smarthome", "ledlights", "homedecor", "desksetup", "workfromhome",
        "fitness", "homegym", "recovery", "yoga", "ecofriendly", "sustainable",
        "zerowaste", "dogsofinstagram", "catsofinstagram", "petproducts",
        "dogmom", "catmom", "tiktok", "viral", "unboxing", "satisfying",
    ]

    clean_tags = [h.replace("#", "").lower() for h in hashtags]
    viral_matches = sum(1 for tag in clean_tags if tag in viral_indicators)

    base_score = 30
    score = base_score + (viral_matches * 20)
    score = min(100, score)

    if viral_matches >= 3:
        virality = "High virality potential"
    elif viral_matches >= 2:
        virality = "Moderate virality potential"
    else:
        virality = "Low virality — needs strong content strategy"

    return score, f"{virality} ({viral_matches}/{len(hashtags)} viral hashtags)"


def calculate_grade(score: float) -> str:
    if score >= 85:
        return "A+"
    elif score >= 75:
        return "A"
    elif score >= 65:
        return "B+"
    elif score >= 55:
        return "B"
    elif score >= 45:
        return "C+"
    elif score >= 35:
        return "C"
    else:
        return "D"


def evaluate_niche(niche: dict, use_api: bool = True) -> NicheScore:
    """Evaluate a single niche and return its scores."""
    result = NicheScore(name=niche["name"])

    result.demand_score, result.demand_detail = score_demand(
        niche["keywords"], use_api
    )
    result.competition_score, result.competition_detail = score_competition(
        niche["keywords"], use_api
    )
    result.margin_score, result.margin_detail = score_margin(
        niche["avg_product_cost"], niche["avg_retail_price"]
    )
    result.shipping_score, result.shipping_detail = score_shipping(
        niche["avg_weight_kg"], niche["fragile"], niche["us_warehouse_available"]
    )
    result.social_score, result.social_detail = score_social(
        niche["social_hashtags"], use_api
    )

    result.total_score = (
        result.demand_score * WEIGHTS["demand"]
        + result.competition_score * WEIGHTS["competition"]
        + result.margin_score * WEIGHTS["margin"]
        + result.shipping_score * WEIGHTS["shipping"]
        + result.social_score * WEIGHTS["social"]
    )

    result.grade = calculate_grade(result.total_score)
    return result


def print_results_rich(results: list[NicheScore]) -> None:
    """Display results using rich tables."""
    console = Console()

    console.print()
    console.print(
        Panel.fit(
            "[bold]Dropshipping Niche Scorer[/bold]\n"
            "Evaluating niches across 5 weighted dimensions",
            border_style="blue",
        )
    )

    # Summary table
    table = Table(
        title="Niche Rankings",
        box=box.ROUNDED,
        show_lines=True,
        title_style="bold cyan",
    )
    table.add_column("Rank", style="bold", width=5)
    table.add_column("Niche", style="bold white", min_width=25)
    table.add_column("Demand\n(25%)", justify="center", width=10)
    table.add_column("Compet.\n(20%)", justify="center", width=10)
    table.add_column("Margin\n(25%)", justify="center", width=10)
    table.add_column("Ship\n(15%)", justify="center", width=10)
    table.add_column("Social\n(15%)", justify="center", width=10)
    table.add_column("Total", justify="center", style="bold", width=8)
    table.add_column("Grade", justify="center", style="bold", width=6)

    for i, r in enumerate(results, 1):
        grade_color = (
            "green" if r.grade.startswith("A") else
            "yellow" if r.grade.startswith("B") else
            "red"
        )
        table.add_row(
            str(i),
            r.name,
            f"{r.demand_score:.0f}",
            f"{r.competition_score:.0f}",
            f"{r.margin_score:.0f}",
            f"{r.shipping_score:.0f}",
            f"{r.social_score:.0f}",
            f"{r.total_score:.1f}",
            f"[{grade_color}]{r.grade}[/{grade_color}]",
        )

    console.print(table)

    # Detailed breakdown for the top niche
    top = results[0]
    detail_table = Table(
        title=f"Top Pick: {top.name}",
        box=box.SIMPLE_HEAVY,
        show_lines=True,
        title_style="bold green",
    )
    detail_table.add_column("Dimension", style="bold", width=20)
    detail_table.add_column("Score", justify="center", width=8)
    detail_table.add_column("Details", min_width=40)

    detail_table.add_row("Demand Trajectory", f"{top.demand_score:.0f}", top.demand_detail)
    detail_table.add_row("Competition", f"{top.competition_score:.0f}", top.competition_detail)
    detail_table.add_row("Margin Potential", f"{top.margin_score:.0f}", top.margin_detail)
    detail_table.add_row("Shipping", f"{top.shipping_score:.0f}", top.shipping_detail)
    detail_table.add_row("Social Virality", f"{top.social_score:.0f}", top.social_detail)

    console.print()
    console.print(detail_table)
    console.print()


def print_results_plain(results: list[NicheScore]) -> None:
    """Plain text fallback output."""
    print("\n" + "=" * 70)
    print("DROPSHIPPING NICHE SCORER — RANKINGS")
    print("=" * 70)
    print(
        f"{'Rank':<5} {'Niche':<30} {'Demand':<8} {'Comp.':<8} "
        f"{'Margin':<8} {'Ship':<8} {'Social':<8} {'Total':<8} {'Grade':<6}"
    )
    print("-" * 70)

    for i, r in enumerate(results, 1):
        print(
            f"{i:<5} {r.name:<30} {r.demand_score:<8.0f} {r.competition_score:<8.0f} "
            f"{r.margin_score:<8.0f} {r.shipping_score:<8.0f} {r.social_score:<8.0f} "
            f"{r.total_score:<8.1f} {r.grade:<6}"
        )

    print("\n" + "-" * 70)
    top = results[0]
    print(f"TOP PICK: {top.name} (Score: {top.total_score:.1f}, Grade: {top.grade})")
    print(f"  Demand:      {top.demand_score:.0f}/100 — {top.demand_detail}")
    print(f"  Competition: {top.competition_score:.0f}/100 — {top.competition_detail}")
    print(f"  Margin:      {top.margin_score:.0f}/100 — {top.margin_detail}")
    print(f"  Shipping:    {top.shipping_score:.0f}/100 — {top.shipping_detail}")
    print(f"  Social:      {top.social_score:.0f}/100 — {top.social_detail}")
    print()


def build_niche_from_name(name: str) -> dict:
    """Build a niche config dict from just a name, using reasonable defaults."""
    kw = name.lower().strip()
    return {
        "name": name.title(),
        "keywords": [kw, f"{kw} products", f"best {kw}"],
        "avg_product_cost": 8.0,
        "avg_retail_price": 35.0,
        "avg_weight_kg": 0.5,
        "fragile": False,
        "us_warehouse_available": True,
        "social_hashtags": [f"#{kw.replace(' ', '')}", f"#{kw.split()[0]}"],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Score dropshipping niches on a 1-100 scale"
    )
    parser.add_argument(
        "-n", "--niches",
        nargs="+",
        help="Custom niche names to evaluate (e.g., 'smart home' 'pet toys')",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Use heuristic scoring only (no API calls)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    args = parser.parse_args()

    if args.niches:
        niches = [build_niche_from_name(n) for n in args.niches]
    else:
        niches = DEFAULT_NICHES

    use_api = not args.offline

    results: list[NicheScore] = []
    for niche in niches:
        result = evaluate_niche(niche, use_api=use_api)
        results.append(result)
        if use_api:
            time.sleep(1)  # Rate limiting for API calls

    results.sort(key=lambda r: r.total_score, reverse=True)

    if args.json:
        output = [asdict(r) for r in results]
        print(json.dumps(output, indent=2))
    elif HAS_RICH:
        print_results_rich(results)
    else:
        print_results_plain(results)


if __name__ == "__main__":
    main()
