# Bank

Scripts for pulling and analyzing bank transactions via Plaid.

## Setup

1. Create a free Plaid account at https://dashboard.plaid.com
2. Add your `PLAID_CLIENT_ID`, `PLAID_SECRET`, and `PLAID_ENV` to `.env`
3. Run the link flow once to get your `access_token` for each bank
4. Store `access_token` values in `.env` — never commit them

## Files

- `fetch_transactions.py` — pull transactions from Plaid and export locally
- `categorize.py` — tag transactions by merchant/category

## Raw Exports

If you prefer manual exports over Plaid:
1. Download OFX/CSV from your bank's website
2. Drop files here (they are gitignored)
3. Run `python categorize.py --file transactions.csv`

## Supported Banks

Most major US banks support Plaid. For banks that don't, use manual CSV export.
