# Sodai — Daily Chaldal.com Grocery Scraper

Scrapes [chaldal.com](https://chaldal.com) every day, builds a complete category tree, and fetches all products from every leaf category.

## Output

- **`Grocery.json`** — Full nested JSON with 15 top-level categories, ~100 leaf categories, ~2,000 products with prices, images, and country of origin
- **GitHub Pages** — Browseable web interface at `https://boktiarshakil.github.io/sodai/`

## How it works

1. Scrapes homepage for the category sidebar (15 top-level categories)
2. Visits each category page to extract subcategories (up to 3 levels deep)
3. For every leaf category, extracts products from React SSR state (`window.__reactAsyncStatePacket`)
4. Runs daily via GitHub Actions

## Files

| File | Description |
|------|-------------|
| `chaldal_scraper.py` | The scraper script |
| `requirements.txt` | Python dependencies |
| `.github/workflows/scrape.yml` | GitHub Action — runs daily |
| `docs/index.html` | Static frontend that displays Grocery.json |
