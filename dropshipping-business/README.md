# Dropshipping E-Commerce Business Kit

Everything you need to launch a Shopify dropshipping store: business plan, financial model, research tools, pricing calculators, and a ready-to-deploy store scaffold.

**Budget:** $2,000–$5,000 starting capital
**Platform:** Shopify (recommended)
**Model:** Dropshipping via vetted supplier networks

---

## What's Included

```
dropshipping-business/
├── business-plan/
│   ├── BUSINESS_PLAN.md        Full business plan with strategy & timeline
│   └── financial-model.md      6-month P&L, unit economics, scenario analysis
├── tools/
│   ├── niche-research/
│   │   ├── niche_scorer.py     Score niches 1-100 across 5 dimensions
│   │   ├── product_finder.py   Search supplier catalogs with filters
│   │   ├── competitor_analyzer.py  Analyze competitor Shopify stores
│   │   └── requirements.txt
│   └── pricing-calculator/
│       ├── calculator.py       Interactive pricing & margin calculator
│       ├── bulk_calculator.py  Batch-price a CSV of products
│       └── requirements.txt
├── store/
│   ├── dawn-customizations/
│   │   ├── config/settings_data.json   Theme configuration
│   │   ├── snippets/                   Liquid snippets (trust badges, timers, shipping bar)
│   │   ├── sections/                   Custom homepage sections
│   │   └── assets/                     CSS customizations
│   ├── APP_SETUP_GUIDE.md     App-by-app installation instructions
│   └── LAUNCH_CHECKLIST.md    Pre-launch verification checklist
└── README.md                  You are here
```

---

## Quick Start

### 1. Read the Business Plan

Start with `business-plan/BUSINESS_PLAN.md` to understand the strategy, then review `financial-model.md` for the numbers.

### 2. Install Python Dependencies

```bash
cd tools/niche-research
pip install -r requirements.txt

cd ../pricing-calculator
pip install -r requirements.txt
```

### 3. Score Your Niche Ideas

```bash
# Score the default 5 candidate niches
python tools/niche-research/niche_scorer.py

# Score your own niche ideas
python tools/niche-research/niche_scorer.py -n "smart home" "pet toys" "yoga accessories"

# Offline mode (no API calls, uses heuristics)
python tools/niche-research/niche_scorer.py --offline

# JSON output for scripting
python tools/niche-research/niche_scorer.py --json
```

### 4. Find Products

```bash
# Search for products in your chosen niche
python tools/niche-research/product_finder.py "massage gun"

# Custom filters
python tools/niche-research/product_finder.py "led strip lights" --min-markup 4 --max-cost 10

# Export to CSV for review
python tools/niche-research/product_finder.py "pet bowl" --export products.csv
```

### 5. Analyze Competitors

```bash
# Analyze a competitor's Shopify store
python tools/niche-research/competitor_analyzer.py https://competitor-store.com

# JSON output
python tools/niche-research/competitor_analyzer.py https://competitor-store.com --json
```

### 6. Price Your Products

```bash
# Interactive mode — answer prompts
python tools/pricing-calculator/calculator.py

# Quick calculation
python tools/pricing-calculator/calculator.py --cost 8 --ship 3 --cpa 10 --margin 30

# Bulk pricing from CSV
python tools/pricing-calculator/bulk_calculator.py --generate-sample
python tools/pricing-calculator/bulk_calculator.py sample_products.csv --output priced_catalog.csv
```

### 7. Set Up Your Shopify Store

1. Sign up at [shopify.com](https://www.shopify.com) (Basic plan, $39/mo)
2. Install the Dawn theme (free, already included)
3. Upload the customizations from `store/dawn-customizations/`:
   - Theme settings: `config/settings_data.json`
   - Trust badges: `snippets/trust-badges.liquid`
   - Free shipping bar: `snippets/free-shipping-bar.liquid`
   - Countdown timer: `snippets/countdown-timer.liquid`
   - Featured benefits section: `sections/featured-benefits.liquid`
   - Custom CSS: `assets/custom-dropship.css` and `assets/section-featured-benefits.css`
4. Follow the `store/APP_SETUP_GUIDE.md` for app installation
5. Complete the `store/LAUNCH_CHECKLIST.md` before going live

---

## Tool Reference

### Niche Scorer (`niche_scorer.py`)

Evaluates niches across five weighted dimensions:

| Dimension | Weight | Data Source |
|-----------|--------|-------------|
| Demand Trajectory | 25% | Google Trends API |
| Competition Density | 20% | Google search results |
| Margin Potential | 25% | Product cost vs retail price |
| Shipping Feasibility | 15% | Weight, fragility, warehouse availability |
| Social Virality | 15% | Hashtag analysis |

**Flags:**
- `-n NICHE [NICHE ...]` — Custom niches to evaluate
- `--offline` — Skip API calls, use heuristic scoring
- `--json` — JSON output

### Product Finder (`product_finder.py`)

Searches supplier catalogs and filters by dropshipping viability.

**Flags:**
- `--min-markup N` — Minimum markup multiplier (default: 3.0)
- `--max-cost N` — Maximum product cost in USD (default: 50.0)
- `--min-rating N` — Minimum seller rating (default: 4.5)
- `--min-orders N` — Minimum order count (default: 100)
- `--export FILE` — Export to CSV
- `--no-filter` — Show all results without filtering
- `--json` — JSON output

### Competitor Analyzer (`competitor_analyzer.py`)

Analyzes a Shopify store's products, pricing, apps, and features.

**Flags:**
- `--deep` — More thorough analysis (slower)
- `--json` — JSON output

### Pricing Calculator (`calculator.py`)

Calculates recommended retail price, margins, and models three scenarios.

**Flags:**
- `-i` / `--interactive` — Interactive prompt mode
- `--cost N` — Product cost ($)
- `--ship N` — Shipping cost ($)
- `--cpa N` — Target cost per acquisition ($)
- `--margin N` — Target net margin (%)
- `--json` — JSON output

### Bulk Calculator (`bulk_calculator.py`)

Processes a CSV of products and outputs a priced catalog.

**Flags:**
- `--generate-sample` — Create a sample input CSV
- `--output FILE` — Export priced catalog to CSV
- `--cpa N` — Default CPA for all products
- `--margin N` — Default target margin (%)
- `--json` — JSON output

---

## Execution Timeline

| Phase | Duration | Activities |
|-------|----------|------------|
| Research | Week 1-2 | Run niche scorer, find products, analyze competitors |
| Store Build | Week 3-4 | Shopify setup, add products, configure apps |
| Soft Launch | Week 5-6 | Test orders, organic social content, ad creative |
| Paid Launch | Week 7-10 | Run ads, optimize, scale winners |
| Optimize | Week 11-12 | Retargeting, new products, review financials |

---

## Key Documents

| Document | Purpose |
|----------|---------|
| [BUSINESS_PLAN.md](business-plan/BUSINESS_PLAN.md) | Complete business strategy |
| [financial-model.md](business-plan/financial-model.md) | Financial projections & unit economics |
| [APP_SETUP_GUIDE.md](store/APP_SETUP_GUIDE.md) | Step-by-step app installation |
| [LAUNCH_CHECKLIST.md](store/LAUNCH_CHECKLIST.md) | Pre-launch verification |
