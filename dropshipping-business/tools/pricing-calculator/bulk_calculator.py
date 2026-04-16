#!/usr/bin/env python3
"""
Bulk Pricing Calculator — Process a CSV of products and output a priced catalog.

Reads a CSV with product cost and shipping data, calculates recommended
retail prices, margins, and viability for each product.

Input CSV format:
  name, cost, shipping, [target_cpa], [target_margin]

Usage:
  python bulk_calculator.py products.csv
  python bulk_calculator.py products.csv --output priced_catalog.csv
  python bulk_calculator.py products.csv --cpa 12 --margin 25
  python bulk_calculator.py --generate-sample   # Create a sample input CSV

Example:
  python bulk_calculator.py --generate-sample
  python bulk_calculator.py sample_products.csv --output priced.csv
"""

import argparse
import csv
import json
import sys
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

from calculator import calculate_pricing, PricingResult


SAMPLE_PRODUCTS = [
    {"name": "LED Strip Lights 5M RGB", "cost": 4.50, "shipping": 2.00},
    {"name": "Massage Gun Mini Portable", "cost": 12.30, "shipping": 3.50},
    {"name": "Slow Feeder Dog Bowl", "cost": 3.80, "shipping": 2.50},
    {"name": "Resistance Bands Set 5-Pack", "cost": 3.50, "shipping": 1.80},
    {"name": "Monitor Stand with USB Hub", "cost": 12.00, "shipping": 4.00},
    {"name": "Bamboo Desk Organizer", "cost": 7.50, "shipping": 3.00},
    {"name": "Smart Plug WiFi 2-Pack", "cost": 5.00, "shipping": 2.00},
    {"name": "Foldable Travel Dog Bowl", "cost": 2.10, "shipping": 1.50},
    {"name": "Cable Management Box", "cost": 5.50, "shipping": 2.50},
    {"name": "Ergonomic Wrist Rest", "cost": 4.00, "shipping": 2.00},
    {"name": "Ring Light 10-inch", "cost": 8.00, "shipping": 3.50},
    {"name": "Foam Roller 18-inch", "cost": 6.20, "shipping": 4.00},
    {"name": "Reusable Shopping Bags 6-Pack", "cost": 3.00, "shipping": 1.50},
    {"name": "Phone Stand Adjustable", "cost": 2.50, "shipping": 1.50},
    {"name": "Yoga Mat Towel Non-Slip", "cost": 5.00, "shipping": 2.50},
]


def generate_sample(filepath: str = "sample_products.csv") -> str:
    """Generate a sample input CSV file."""
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "cost", "shipping"])
        writer.writeheader()
        writer.writerows(SAMPLE_PRODUCTS)
    return filepath


def read_input_csv(filepath: str) -> list[dict]:
    """Read product data from input CSV."""
    products = []
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            product = {
                "name": row.get("name", "Unknown"),
                "cost": float(row.get("cost", 0)),
                "shipping": float(row.get("shipping", 0)),
            }
            if "target_cpa" in row and row["target_cpa"]:
                product["target_cpa"] = float(row["target_cpa"])
            if "target_margin" in row and row["target_margin"]:
                product["target_margin"] = float(row["target_margin"]) / 100.0
            products.append(product)
    return products


def process_products(
    products: list[dict],
    default_cpa: float = 10.0,
    default_margin: float = 0.30,
) -> list[PricingResult]:
    """Calculate pricing for all products."""
    results = []
    for p in products:
        cpa = p.get("target_cpa", default_cpa)
        margin = p.get("target_margin", default_margin)
        result = calculate_pricing(p["name"], p["cost"], p["shipping"], cpa, margin)
        results.append(result)
    return results


def export_csv(results: list[PricingResult], filepath: str) -> None:
    """Export priced catalog to CSV."""
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Product", "Cost", "Shipping", "Recommended Price", "Markup",
            "Gross Profit", "Gross Margin %", "CPA", "Net Profit",
            "Net Margin %", "ROAS", "Break-Even Orders/Mo",
            "Realistic Monthly Orders", "Realistic Monthly Profit", "Viable",
        ])
        for r in results:
            viable = "Yes" if r.net_profit_per_order > 0 else "No"
            writer.writerow([
                r.product_name, r.product_cost, r.shipping_cost,
                r.recommended_price, r.markup, r.gross_profit,
                r.gross_margin_pct, r.target_cpa, r.net_profit_per_order,
                r.net_margin_pct, r.roas, r.breakeven_orders_monthly,
                r.realistic_monthly_orders, r.realistic_monthly_profit, viable,
            ])


def print_results_rich(results: list[PricingResult]) -> None:
    console = Console()
    console.print()
    console.print(Panel.fit(
        f"[bold]Bulk Pricing Calculator[/bold]\n"
        f"{len(results)} products analyzed",
        border_style="blue",
    ))

    # Sort by net profit descending
    sorted_results = sorted(results, key=lambda r: r.net_profit_per_order, reverse=True)

    table = Table(
        title="Priced Product Catalog",
        box=box.ROUNDED,
        show_lines=True,
        title_style="bold cyan",
    )
    table.add_column("#", width=3)
    table.add_column("Product", min_width=25)
    table.add_column("Cost", justify="right", width=8)
    table.add_column("Price", justify="right", width=8)
    table.add_column("Markup", justify="center", width=7)
    table.add_column("Gross", justify="right", width=9)
    table.add_column("CPA", justify="right", width=7)
    table.add_column("Net", justify="right", width=9)
    table.add_column("Margin", justify="center", width=8)
    table.add_column("ROAS", justify="center", width=6)
    table.add_column("B/E", justify="center", width=5)

    for i, r in enumerate(sorted_results, 1):
        viable_color = "green" if r.net_profit_per_order > 0 else "red"
        table.add_row(
            str(i),
            r.product_name[:30],
            f"${r.product_cost:.2f}",
            f"${r.recommended_price:.2f}",
            f"{r.markup:.1f}x",
            f"${r.gross_profit:.2f}",
            f"${r.target_cpa:.0f}",
            f"[{viable_color}]${r.net_profit_per_order:.2f}[/{viable_color}]",
            f"[{viable_color}]{r.net_margin_pct:.0f}%[/{viable_color}]",
            f"{r.roas:.1f}x",
            str(r.breakeven_orders_monthly),
        )
    console.print(table)

    # Summary
    viable = [r for r in results if r.net_profit_per_order > 0]
    avg_margin = sum(r.net_margin_pct for r in viable) / len(viable) if viable else 0
    avg_profit = sum(r.net_profit_per_order for r in viable) / len(viable) if viable else 0
    best = max(viable, key=lambda r: r.net_profit_per_order) if viable else None

    console.print()
    summary = Table(title="Summary", box=box.SIMPLE_HEAVY, show_lines=True)
    summary.add_column("Metric", style="bold", width=25)
    summary.add_column("Value", width=20)
    summary.add_row("Total Products", str(len(results)))
    summary.add_row("Viable Products", f"[green]{len(viable)}[/green] / {len(results)}")
    summary.add_row("Avg Net Profit/Order", f"${avg_profit:.2f}")
    summary.add_row("Avg Net Margin", f"{avg_margin:.1f}%")
    if best:
        summary.add_row("Best Product", f"{best.product_name}")
        summary.add_row("Best Net Profit", f"${best.net_profit_per_order:.2f}/order")
    console.print(summary)
    console.print()


def print_results_plain(results: list[PricingResult]) -> None:
    print(f"\n{'='*80}")
    print(f"BULK PRICING CALCULATOR — {len(results)} Products")
    print(f"{'='*80}")
    print(f"{'#':<3} {'Product':<30} {'Cost':>7} {'Price':>8} {'Markup':>7} "
          f"{'Net':>8} {'Margin':>7} {'ROAS':>5}")
    print("-" * 80)

    sorted_results = sorted(results, key=lambda r: r.net_profit_per_order, reverse=True)
    for i, r in enumerate(sorted_results, 1):
        print(f"{i:<3} {r.product_name[:30]:<30} ${r.product_cost:>5.2f} "
              f"${r.recommended_price:>6.2f} {r.markup:>5.1f}x "
              f"${r.net_profit_per_order:>6.2f} {r.net_margin_pct:>5.1f}% "
              f"{r.roas:>4.1f}x")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Bulk calculate pricing for a CSV of products"
    )
    parser.add_argument("input_csv", nargs="?", help="Input CSV file path")
    parser.add_argument("--output", "-o", help="Output CSV file path")
    parser.add_argument("--cpa", type=float, default=10.0,
                        help="Default CPA for all products (default: 10.0)")
    parser.add_argument("--margin", type=float, default=30.0,
                        help="Default target net margin %% (default: 30)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--generate-sample", action="store_true",
                        help="Generate a sample input CSV")
    args = parser.parse_args()

    if args.generate_sample:
        path = generate_sample()
        print(f"Sample CSV generated: {path}")
        print("Edit it with your products, then run:")
        print(f"  python bulk_calculator.py {path} --output priced.csv")
        return

    if not args.input_csv:
        print("Error: Please provide an input CSV file or use --generate-sample")
        print("Usage: python bulk_calculator.py products.csv")
        sys.exit(1)

    if not Path(args.input_csv).exists():
        print(f"Error: File not found: {args.input_csv}")
        sys.exit(1)

    products = read_input_csv(args.input_csv)
    results = process_products(products, args.cpa, args.margin / 100.0)

    if args.output:
        export_csv(results, args.output)
        print(f"Exported {len(results)} priced products to {args.output}")

    if args.json:
        from dataclasses import asdict
        output = [asdict(r) for r in results]
        print(json.dumps(output, indent=2))
    elif HAS_RICH:
        print_results_rich(results)
    else:
        print_results_plain(results)


if __name__ == "__main__":
    main()
