# Finance

Personal finance tracking: bank accounts, budgeting, and crypto.

## Structure

```
finance/
├── bank/           # Bank transaction exports and analysis scripts
├── budgeting/      # Monthly budget templates and tracking
├── crypto/         # Crypto portfolio tracking
└── scripts/        # Shared finance utilities
```

## Bank Accounts

Uses [Plaid](https://plaid.com) to pull transactions programmatically.
Raw exports (CSV/OFX) are gitignored — only scripts and templates are committed.

```bash
# Fetch last 30 days of transactions across all linked accounts
python scripts/fetch_transactions.py --days 30

# Categorize and export to CSV
python scripts/categorize.py --out finance/bank/transactions_$(date +%Y-%m).csv
```

## Budgeting

Monthly budget lives in a Google Sheet (see `../google/sheets/`).
Scripts here sync local exports → the sheet.

```bash
python scripts/sync_budget.py --month 2026-04
```

## Crypto

Pulls prices from CoinGecko (free, no key required for basic use).

```bash
python crypto/portfolio.py
```

## ⚠️ Security Notes

- Never commit real transaction files, bank statements, or account numbers
- All sensitive exports are covered by `.gitignore`
- Use environment variables (`.env`) for API keys — never hardcode them
