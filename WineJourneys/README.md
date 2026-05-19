# Wine Journeys — A & J Wine Journeys

Premium bilingual landing site for private wine tours around Melbourne, Australia.

## Live site

- **Current:** [https://mrzzz17.github.io/Random/WineJourneys/](https://mrzzz17.github.io/Random/WineJourneys/)
- **Legacy redirect:** [https://mrzzz17.github.io/Random/wine-tours/](https://mrzzz17.github.io/Random/wine-tours/) → WineJourneys

GitHub Pages publishes from `Random/docs/`; `docs/WineJourneys` is a symlink to this folder.

## Structure

```
WineJourneys/
├── index.html          # Main page (inline + linked CSS)
├── editorial.css       # Editorial / cinematic sections
├── translations.js     # RU / EN copy
├── i18n.js             # Language switcher
├── nav.js              # Mobile nav
├── tours.js            # Regions, tour cards, booking flow
├── editorial.js        # Scroll reveal, parallax
├── img/                # Optimized production images (webp + png)
├── artefacts/
│   ├── mockups/        # Design references from Cursor session
│   └── source-downloads/  # Original ChatGPT / export PNGs
└── README.md
```

## Local preview

```bash
cd WineJourneys
python3 -m http.server 8080
# open http://localhost:8080
```

## Deploy

From repo root (`Random`):

```bash
git add WineJourneys docs/WineJourneys docs/wine-tours
git commit -m "…"
git push
```

Pages rebuilds from `main` / `docs` automatically.
