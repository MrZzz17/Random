#!/usr/bin/env python3
"""
Pricing & Margin Calculator — Interactive dropshipping product pricing tool.

Calculates recommended retail price, break-even volume, and models three
scenarios (pessimistic, realistic, optimistic) for any product.

Usage:
  python calculator.py                           # Interactive mode
  python calculator.py --cost 8 --ship 3         # Quick calculation
  python calculator.py --cost 8 --ship 3 --cpa 10 --margin 30
  python calculator.py --cost 8 --ship 3 --json
"""

import argparse
import json
import math
import sys
from dataclasses import dataclass, asdict

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import FloatPrompt, Prompt
    from rich import box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


SHOPIFY_TXN_PCT = 0.029
SHOPIFY_TXN_FLAT = 0.30
DEFAULT_REFUND_RATE = 0.06
MONTHLY_FIXED_COSTS = 83.24  # Shopify + apps (see financial model)


@dataclass
class PricingResult:
    product_name: str
    product_cost: float
    shipping_cost: float
    target_cpa: float
    target_margin_pct: float
    refund_rate: float

    # Calculated fields
    recommended_price: float = 0.0
    txn_fee: float = 0.0
    gross_profit: float = 0.0
    gross_margin_pct: float = 0.0
    net_profit_per_order: float = 0.0
    net_margin_pct: float = 0.0
    markup: float = 0.0
    breakeven_orders_monthly: int = 0
    roas: float = 0.0

    # Scenario modeling
    pessimistic_monthly_orders: int = 0
    pessimistic_monthly_profit: float = 0.0
    realistic_monthly_orders: int = 0
    realistic_monthly_profit: float = 0.0
    optimistic_monthly_orders: int = 0
    optimistic_monthly_profit: float = 0.0


def calculate_recommended_price(
    cost: float,
    shipping: float,
    cpa: float,
    target_margin: float,
    refund_rate: float = DEFAULT_REFUND_RATE,
) -> float:
    """
    Calculate the minimum retail price that achieves the target net margin.

    Price = (cost + shipping + cpa + refund_reserve) / (1 - target_margin - txn_pct)
    Solving for price where:
      net_profit = price - cost - shipping - txn_fee - cpa - refund_reserve
      net_margin = net_profit / price = target_margin
    """
    # price * (1 - target_margin - txn_pct) = cost + shipping + cpa + (price * refund_rate) + txn_flat
    # price * (1 - target_margin - txn_pct - refund_rate) = cost + shipping + cpa + txn_flat
    denominator = 1 - target_margin - SHOPIFY_TXN_PCT - refund_rate
    if denominator <= 0:
        return (cost + shipping) * 5  # Fallback: 5x markup

    price = (cost + shipping + cpa + SHOPIFY_TXN_FLAT) / denominator
    # Round up to .99 pricing
    return math.ceil(price) - 0.01


def calculate_pricing(
    name: str,
    cost: float,
    shipping: float,
    cpa: float,
    target_margin: float,
    refund_rate: float = DEFAULT_REFUND_RATE,
) -> PricingResult:
    """Run full pricing calculation and scenario modeling."""
    result = PricingResult(
        product_name=name,
        product_cost=cost,
        shipping_cost=shipping,
        target_cpa=cpa,
        target_margin_pct=target_margin,
        refund_rate=refund_rate,
    )

    price = calculate_recommended_price(cost, shipping, cpa, target_margin, refund_rate)
    result.recommended_price = price

    # Per-order economics
    result.txn_fee = round(price * SHOPIFY_TXN_PCT + SHOPIFY_TXN_FLAT, 2)
    refund_reserve = round(price * refund_rate, 2)

    result.gross_profit = round(price - cost - shipping - result.txn_fee, 2)
    result.gross_margin_pct = round((result.gross_profit / price) * 100, 1) if price > 0 else 0

    result.net_profit_per_order = round(
        price - cost - shipping - result.txn_fee - cpa - refund_reserve, 2
    )
    result.net_margin_pct = round((result.net_profit_per_order / price) * 100, 1) if price > 0 else 0

    result.markup = round(price / cost, 1) if cost > 0 else 0
    result.roas = round(price / cpa, 2) if cpa > 0 else 0

    # Break-even
    if result.net_profit_per_order > 0:
        result.breakeven_orders_monthly = math.ceil(
            MONTHLY_FIXED_COSTS / result.net_profit_per_order
        )
    else:
        result.breakeven_orders_monthly = -1  # Not viable

    # Scenario modeling (monthly)
    if result.net_profit_per_order > 0:
        result.pessimistic_monthly_orders = max(5, result.breakeven_orders_monthly)
        result.pessimistic_monthly_profit = round(
            result.pessimistic_monthly_orders * result.net_profit_per_order - MONTHLY_FIXED_COSTS, 2
        )

        result.realistic_monthly_orders = result.breakeven_orders_monthly * 3
        result.realistic_monthly_profit = round(
            result.realistic_monthly_orders * result.net_profit_per_order - MONTHLY_FIXED_COSTS, 2
        )

        result.optimistic_monthly_orders = result.breakeven_orders_monthly * 8
        result.optimistic_monthly_profit = round(
            result.optimistic_monthly_orders * result.net_profit_per_order - MONTHLY_FIXED_COSTS, 2
        )

    return result


def print_result_rich(result: PricingResult) -> None:
    console = Console()
    console.print()
    console.print(Panel.fit(
        f"[bold]Pricing Calculator[/bold]\n"
        f"Product: {result.product_name}",
        border_style="blue",
    ))

    # Input summary
    inputs = Table(title="Inputs", box=box.SIMPLE, show_lines=False)
    inputs.add_column("Parameter", style="bold", width=25)
    inputs.add_column("Value", width=15)
    inputs.add_row("Product Cost", f"${result.product_cost:.2f}")
    inputs.add_row("Shipping Cost", f"${result.shipping_cost:.2f}")
    inputs.add_row("Target CPA (ad cost)", f"${result.target_cpa:.2f}")
    inputs.add_row("Target Net Margin", f"{result.target_margin_pct * 100:.0f}%")
    inputs.add_row("Refund Rate", f"{result.refund_rate * 100:.0f}%")
    console.print(inputs)

    # Recommended price
    color = "green" if result.net_profit_per_order > 0 else "red"
    console.print(Panel(
        f"[bold {color}]Recommended Retail Price: ${result.recommended_price:.2f}[/bold {color}]\n"
        f"Markup: {result.markup:.1f}x  |  ROAS: {result.roas:.1f}x",
        border_style=color,
    ))

    # Per-order breakdown
    breakdown = Table(title="Per-Order Economics", box=box.ROUNDED, show_lines=True)
    breakdown.add_column("Line Item", style="bold", width=30)
    breakdown.add_column("Amount", justify="right", width=12)
    breakdown.add_column("% of Price", justify="right", width=12)

    p = result.recommended_price
    breakdown.add_row("Revenue", f"${p:.2f}", "100.0%")
    breakdown.add_row("Product Cost", f"-${result.product_cost:.2f}",
                      f"{(result.product_cost/p)*100:.1f}%")
    breakdown.add_row("Shipping", f"-${result.shipping_cost:.2f}",
                      f"{(result.shipping_cost/p)*100:.1f}%")
    breakdown.add_row("Transaction Fee", f"-${result.txn_fee:.2f}",
                      f"{(result.txn_fee/p)*100:.1f}%")
    breakdown.add_row("[bold]Gross Profit[/bold]", f"[bold]${result.gross_profit:.2f}[/bold]",
                      f"[bold]{result.gross_margin_pct:.1f}%[/bold]")
    breakdown.add_row("Ad Cost (CPA)", f"-${result.target_cpa:.2f}",
                      f"{(result.target_cpa/p)*100:.1f}%")
    refund_amt = round(p * result.refund_rate, 2)
    breakdown.add_row("Refund Reserve", f"-${refund_amt:.2f}",
                      f"{result.refund_rate*100:.1f}%")
    breakdown.add_row(
        f"[bold {color}]Net Profit[/bold {color}]",
        f"[bold {color}]${result.net_profit_per_order:.2f}[/bold {color}]",
        f"[bold {color}]{result.net_margin_pct:.1f}%[/bold {color}]",
    )
    console.print(breakdown)

    # Break-even
    if result.breakeven_orders_monthly > 0:
        console.print(f"\n  Break-even: [bold]{result.breakeven_orders_monthly}[/bold] "
                      f"orders/month (covers ${MONTHLY_FIXED_COSTS:.2f} fixed costs)")
    else:
        console.print("\n  [red bold]Not viable — net profit per order is negative.[/red bold]")

    # Scenarios
    if result.net_profit_per_order > 0:
        scenarios = Table(title="Monthly Scenario Modeling", box=box.ROUNDED, show_lines=True)
        scenarios.add_column("Scenario", style="bold", width=15)
        scenarios.add_column("Orders/Mo", justify="center", width=12)
        scenarios.add_column("Revenue", justify="right", width=12)
        scenarios.add_column("Total Ad Spend", justify="right", width=14)
        scenarios.add_column("Net Profit", justify="right", width=12)

        for label, orders, profit in [
            ("Pessimistic", result.pessimistic_monthly_orders, result.pessimistic_monthly_profit),
            ("Realistic", result.realistic_monthly_orders, result.realistic_monthly_profit),
            ("Optimistic", result.optimistic_monthly_orders, result.optimistic_monthly_profit),
        ]:
            rev = orders * result.recommended_price
            ad_spend = orders * result.target_cpa
            profit_color = "green" if profit > 0 else "red"
            scenarios.add_row(
                label,
                str(orders),
                f"${rev:,.0f}",
                f"${ad_spend:,.0f}",
                f"[{profit_color}]${profit:,.0f}[/{profit_color}]",
            )
        console.print(scenarios)

    console.print()


def print_result_plain(result: PricingResult) -> None:
    print(f"\n{'='*50}")
    print(f"PRICING CALCULATOR — {result.product_name}")
    print(f"{'='*50}")
    print(f"Product Cost:     ${result.product_cost:.2f}")
    print(f"Shipping:         ${result.shipping_cost:.2f}")
    print(f"Target CPA:       ${result.target_cpa:.2f}")
    print(f"Target Margin:    {result.target_margin_pct*100:.0f}%")
    print(f"\nRecommended Price: ${result.recommended_price:.2f}")
    print(f"Markup:           {result.markup:.1f}x")
    print(f"ROAS:             {result.roas:.1f}x")
    print(f"\nGross Profit:     ${result.gross_profit:.2f} ({result.gross_margin_pct:.1f}%)")
    print(f"Net Profit:       ${result.net_profit_per_order:.2f} ({result.net_margin_pct:.1f}%)")
    print(f"Break-even:       {result.breakeven_orders_monthly} orders/month")
    print(f"\nScenarios (monthly):")
    print(f"  Pessimistic: {result.pessimistic_monthly_orders} orders → ${result.pessimistic_monthly_profit:,.0f}")
    print(f"  Realistic:   {result.realistic_monthly_orders} orders → ${result.realistic_monthly_profit:,.0f}")
    print(f"  Optimistic:  {result.optimistic_monthly_orders} orders → ${result.optimistic_monthly_profit:,.0f}")
    print()


def interactive_mode() -> None:
    """Run the calculator in interactive mode with prompts."""
    if HAS_RICH:
        console = Console()
        console.print(Panel.fit("[bold]Interactive Pricing Calculator[/bold]", border_style="blue"))
        name = Prompt.ask("Product name", default="My Product")
        cost = FloatPrompt.ask("Product cost from supplier ($)", default=8.0)
        shipping = FloatPrompt.ask("Shipping cost ($)", default=3.0)
        cpa = FloatPrompt.ask("Target CPA / ad cost per sale ($)", default=10.0)
        margin_input = FloatPrompt.ask("Target net margin (%)", default=30.0)
    else:
        name = input("Product name [My Product]: ").strip() or "My Product"
        cost = float(input("Product cost from supplier ($) [8.00]: ").strip() or "8.0")
        shipping = float(input("Shipping cost ($) [3.00]: ").strip() or "3.0")
        cpa = float(input("Target CPA / ad cost per sale ($) [10.00]: ").strip() or "10.0")
        margin_input = float(input("Target net margin (%) [30]: ").strip() or "30")

    margin = margin_input / 100.0
    result = calculate_pricing(name, cost, shipping, cpa, margin)

    if HAS_RICH:
        print_result_rich(result)
    else:
        print_result_plain(result)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate dropshipping product pricing and margins"
    )
    parser.add_argument("--name", default="Product", help="Product name")
    parser.add_argument("--cost", type=float, help="Product cost from supplier ($)")
    parser.add_argument("--ship", type=float, default=3.0, help="Shipping cost ($)")
    parser.add_argument("--cpa", type=float, default=10.0, help="Target CPA ($)")
    parser.add_argument("--margin", type=float, default=30.0, help="Target net margin (%%)")
    parser.add_argument("--refund-rate", type=float, default=6.0, help="Expected refund rate (%%)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    args = parser.parse_args()

    if args.interactive or args.cost is None:
        interactive_mode()
        return

    margin = args.margin / 100.0
    refund = args.refund_rate / 100.0
    result = calculate_pricing(
        args.name, args.cost, args.ship, args.cpa, margin, refund
    )

    if args.json:
        print(json.dumps(asdict(result), indent=2))
    elif HAS_RICH:
        print_result_rich(result)
    else:
        print_result_plain(result)


if __name__ == "__main__":
    main()
