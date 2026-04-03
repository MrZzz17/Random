# Gmail Filters

Store your Gmail filter rules here for backup and version control.

## Export Filters from Gmail

1. Open Gmail → Settings → See all settings → Filters and Blocked Addresses
2. Select all filters → Export
3. Save the downloaded `mailFilters.xml` here

## Files

- `mailFilters.xml` — Gmail's native export format (re-importable)
- `filters.json` — Human-readable source of truth; edit this, then regenerate XML

## Categories to Filter

| Label               | Criteria                              |
|---------------------|---------------------------------------|
| `finance/bank`      | From your bank's notification address |
| `finance/receipts`  | Subject contains "receipt" or "order" |
| `subscriptions`     | Newsletters, subscription services    |
| `social`            | Social network notifications          |
| `spam-adjacent`     | Promotions you still want but rarely  |
