"""
Simple crypto portfolio tracker using CoinGecko (no API key needed).
Edit HOLDINGS below with your actual coins and amounts.

Usage: python portfolio.py
"""

import requests

# --- Edit this section ---
HOLDINGS = {
    "bitcoin": 0.0,
    "ethereum": 0.0,
    "solana": 0.0,
    # Add more CoinGecko coin IDs here
}
CURRENCY = "usd"
# -------------------------

COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"


def fetch_prices(coin_ids: list[str], vs_currency: str) -> dict:
    resp = requests.get(
        COINGECKO_URL,
        params={"ids": ",".join(coin_ids), "vs_currencies": vs_currency},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def main():
    coins = [c for c, amt in HOLDINGS.items() if amt > 0]
    if not coins:
        print("No holdings configured. Edit HOLDINGS in portfolio.py.")
        return

    prices = fetch_prices(coins, CURRENCY)

    total = 0.0
    print(f"\n{'Coin':<15} {'Amount':>12} {'Price':>12} {'Value':>12}")
    print("-" * 55)
    for coin, amount in HOLDINGS.items():
        if amount <= 0:
            continue
        price = prices.get(coin, {}).get(CURRENCY, 0)
        value = price * amount
        total += value
        print(f"{coin:<15} {amount:>12.6f} ${price:>11,.2f} ${value:>11,.2f}")

    print("-" * 55)
    print(f"{'TOTAL':<15} {'':<12} {'':<12} ${total:>11,.2f}")


if __name__ == "__main__":
    main()
