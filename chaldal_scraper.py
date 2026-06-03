"""
Chaldal.com Grocery Scraper
============================
Builds the full category tree from the current live sidebar (multi-pass),
then fetches all products from every leaf category.
Output: Grocery.json with the complete nested structure
"""

import re, json, sys, time
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://chaldal.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
}

session = requests.Session()
session.headers.update(HEADERS)

URL_OVERRIDES = {
    "popular": "popular", "flash sales": "flash-sales", "food": "food",
    "cleaning supplies": "cleaning", "home & kitchen": "home-kitchen",
    "fashion & lifestyle": "fashion-lifestyle", "baby care": "babycare",
    "personal care": "personal-care", "stationery & office": "stationery-office",
    "pet care": "pet-care", "toys & sports": "toys-sports",
    "beauty & makeup": "beauty-makeup", "health & wellness": "health-and-wellness",
    "vehicle essentials": "vehicle-essentials", "new arrival": "new-arrival",
    "premium care": "premium-care", "fruits & vegetables": "fruits-vegetables",
    "fresh vegetables": "fresh-vegetable", "fresh fruits": "fresh-fruit",
    "meat & fish": "meat-fish", "chicken & poultry": "chicken-poultry",
    "dried fish": "dried-fish", "tofu & meat alternatives": "tofu-meat-alternatives",
    "cooking": "cooking", "spices": "spices", "salt & sugar": "salt-sugar",
    "rice": "rices", "dal or lentil": "dal-lentil", "ready mix": "ready-mix",
    "shemai & suji": "shemai-suji", "special ingredients": "special-ingredients",
    "oil": "oils", "colors & flavours": "colors-flavours", "ghee": "ghee",
    "premium ingredients": "premium-ingredients", "sauces & pickles": "sauces-pickles",
    "tomato sauces": "tomato-sauce", "other sauces": "other-sauce", "pickles": "pickles",
    "salad dressing": "salad-dressing", "dairy & eggs": "dairy", "eggs": "eggs",
    "milk": "milk", "butter & sour cream": "butter-sour-cream", "cheese": "cheese",
    "yogurt & sweet": "yogurt-sweet", "powder milk & creamer": "powder-milk-creamer",
    "condensed milk": "condensed-milk", "breakfast": "breakfast", "bread": "breads",
    "local breakfast": "local-breakfast", "tea & coffee": "tea-coffee", "cereals": "cereals",
    "honey": "honey", "spreads": "spreads", "oats": "oats",
    "candy & chocolate": "candy-chocolate", "chocolates": "chocolates", "wafers": "wafers",
    "candies": "candies", "gums, mints & mouth fresheners": "gums-mints-mouth-fresheners",
    "jellies & marshmallows": "jellies-marshmallows", "snacks": "snacks", "noodles": "noodles",
    "chips & pretzels": "chips-pretzels", "biscuits": "biscuits", "cookies": "cookies",
    "local snacks": "local-snacks", "popcorn & nuts": "popcorn-nuts", "chanachur": "chanachur",
    "canned & preserved": "canned-preserved", "beverages": "beverages", "tea": "tea",
    "soft drinks": "soft-drinks", "coffee": "coffee", "syrups & powder drinks": "syrups-powder-drinks",
    "juice": "juice", "water": "water", "baking": "baking", "flour": "flour",
    "baking tools & accessories": "baking-tools-accessories", "baking ingredients": "baking-ingredients",
    "yeast & baking powder": "yeast-baking-powder", "frozen & canned": "frozen-canned",
    "frozen snacks": "frozen-snacks", "frozen fish & meat": "frozen-fish-meat",
    "canned food": "canned-food", "diabetic food": "diabetic-food", "ice cream": "ice-cream",
    "tub ice cream": "tub-ice-cream", "stick & cone ice cream": "stick-cone-ice-cream",
    "ice cream cakes": "ice-cream-cakes", "dishwashing supplies": "dishwashing-supplies",
    "laundry": "laundry", "toilet cleaners": "toilet-cleaner", "napkins & paper products": "napkins-paper-products",
    "pest control": "pest-control", "floor & glass cleaners": "floor-glass-cleaner",
    "cleaning accessories": "cleaning-accessories", "air fresheners": "air-fresheners",
    "disposables & trash bags": "disposables-trash-bags", "shoe care": "shoe-care",
    "trash bin & basket": "trash-bin-basket", "kitchen appliances": "kitchen-appliances",
    "kitchen tools & accessories": "kitchen-tools-accessories", "cookware & bakeware": "cookware-bakeware",
    "tableware & serveware": "tableware-serveware", "storage & organizers": "storage-organizers",
    "home decor & furnishing": "home-decor-furnishing", "hardware & electrical": "hardware-electrical",
    "light bulbs & batteries": "light-bulbs-batteries", "gardening": "gardening",
    "men's fashion": "mens-fashion", "women's fashion": "womens-fashion",
    "boys' fashion": "boys-fashion", "girls' fashion": "girls-fashion",
    "bags & luggage": "bags-luggage", "socks & innerwear": "socks-innerwear",
    "footwear": "footwear", "jewelry & accessories": "jewelry-accessories",
    "diapers": "diaper", "baby food": "babyfood", "baby skincare": "baby-skin-care",
    "wipes": "wipes", "baby oral care": "baby-oral-care", "newborn essentials": "newborn-essentials",
    "baby accessories": "baby-accessories", "feeders": "feeders",
    "writing & drawing": "writing-drawing", "paper & notebooks": "paper-notebooks",
    "office supplies": "office-supplies", "files & organizers": "files-organizers",
    "scissors & adhesives": "scissors-adhesives", "calculators & electronic items": "calculators-electronic-items",
    "cat food": "cat-food", "dog food": "dog-food", "bird & other pet food": "bird-other-pet-food",
    "pet accessories & toys": "pet-accessories-toys", "pet grooming & hygiene": "pet-grooming-hygiene",
    "toys": "toys", "sports & fitness": "sports-fitness", "games & puzzles": "games-puzzles",
    "outdoor play & ride-ons": "outdoor-play-ride-ons", "skin care": "skin-care",
    "hair care": "hair-care", "oral care": "oral-care", "bath & body": "bath-body",
    "perfumes & deodorants": "perfumes-deodorants", "feminine hygiene": "feminine-hygiene",
    "men's grooming": "mens-grooming", "makeup": "makeup", "car care": "car-care",
    "motorcycle care": "motorcycle-care", "helmets & safety gear": "helmets-safety-gear",
    "vehicle accessories & parts": "vehicle-accessories-parts", "meat": "meat", "fish": "fish",
}

def fetch_html(url):
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    return resp.text

def strip_name(raw):
    return re.sub(r'\s+', ' ', raw).strip()

def name_to_slug(name):
    key = name.strip().lower()
    if key in URL_OVERRIDES:
        return URL_OVERRIDES[key]
    slug = key.replace(' & ', '-').replace('&', '-').replace("'", "")
    slug = re.sub(r'[^a-z0-9-]', '-', slug)
    slug = re.sub(r'-+', '-', slug).strip('-')
    return slug

def resolve_url(name):
    slug = name_to_slug(name)
    url = f"{BASE_URL}/{slug}"
    try:
        r = session.head(url, timeout=10, allow_redirects=True)
        if r.status_code == 200:
            return url
    except requests.RequestException:
        pass
    alt = slug[:-1] if slug.endswith('s') and len(slug) > 3 else slug + 's'
    if alt != slug:
        try:
            r = session.head(f"{BASE_URL}/{alt}", timeout=10, allow_redirects=True)
            if r.status_code == 200:
                return f"{BASE_URL}/{alt}"
        except requests.RequestException:
            pass
    return None

def parse_sidebar_li(li):
    name_el = li.select_one('div.category-menu-vertical div.category-name')
    if not name_el:
        return None
    name = strip_name(name_el.text)
    if not name:
        return None
    return {"name": name, "cid": li.get('data-cid'), "has_arrow": li.select_one('.arrow-right') is not None}

def get_top_level_categories():
    html = fetch_html(BASE_URL)
    soup = BeautifulSoup(html, 'lxml')
    level0 = soup.select_one('ul.level-0')
    if not level0:
        raise Exception("Could not find category sidebar")
    cats = []
    for li in level0.find_all('li', recursive=False):
        p = parse_sidebar_li(li)
        if p:
            p["url"] = resolve_url(p["name"])
            p["subcategories"] = []
            cats.append(p)
    return cats

def get_subcategories(category):
    url = category.get("url")
    if not url:
        return
    try:
        html = fetch_html(url)
    except requests.RequestException:
        return
    soup = BeautifulSoup(html, 'lxml')
    cid = category.get("cid")
    li = soup.select_one(f'li[data-cid="{cid}"]') if cid else None
    if not li:
        return
    depth = 0
    p = li.find_parent('ul')
    if p:
        for cls in (p.get('class') or []):
            if cls.startswith('level-'):
                try: depth = int(cls.split('-')[1])
                except ValueError: pass
    next_level = f'level-{depth + 1}'
    nested_ul = li.find('ul', class_=lambda c: c and next_level in (c or ''))
    if not nested_ul:
        nested_ul = li.find('ul', class_=lambda c: c and 'level' in (c or ''))
    if not nested_ul:
        return
    children = []
    for child_li in nested_ul.find_all('li', recursive=False):
        p = parse_sidebar_li(child_li)
        if p:
            p["url"] = resolve_url(p["name"])
            p["subcategories"] = []
            children.append(p)
    category["subcategories"] = children

def scrape_full_tree():
    cats = get_top_level_categories()
    for cat in cats:
        get_subcategories(cat)
    def process_deep(node):
        for child in node.get("subcategories", []):
            if child.get("has_arrow"):
                get_subcategories(child)
                process_deep(child)
    for cat in cats:
        process_deep(cat)
    return cats

def extract_react_state(html):
    idx = html.find('window.__reactAsyncStatePacket')
    if idx == -1: return None
    eq_idx = html.find('=', idx)
    if eq_idx == -1: return None
    start = eq_idx + 1; depth = 0; in_str = False; escape = False
    for i in range(start, len(html)):
        ch = html[i]
        if escape: escape = False; continue
        if ch == '\\' and in_str: escape = True; continue
        if ch == '"' and not escape: in_str = not in_str; continue
        if not in_str:
            if ch == '{': depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return json.loads(html[start:i+1])
    return None

def extract_products(state):
    if not state: return None
    for v in state.values():
        if isinstance(v, dict) and 'products' in v:
            prod = v['products']
            if isinstance(prod, dict) and 'items' in prod: return prod['items']
            if isinstance(prod, list): return prod
    return None

def clean_product(p):
    price_raw = p.get("Price") or {}
    disc_raw = p.get("DiscountedPrice") or {}
    pics = p.get("PictureUrls") or []
    return {
        "id": p.get("ProductVariantId"),
        "name": p.get("Name", ""),
        "subtext": p.get("SubText", ""),
        "slug": p.get("Slug", ""),
        "price": price_raw.get("Lo") if isinstance(price_raw, dict) else price_raw,
        "discounted_price": disc_raw.get("Lo") if isinstance(disc_raw, dict) else disc_raw,
        "image_url": pics[0] if pics else None,
        "category_ids": p.get("AllCategoryIds", []),
        "is_age_restricted": p.get("IsAgeRestricted", False),
        "country_of_origin": p.get("CountryOriginCode"),
    }

def scrape_products(category_url, category_name):
    try:
        html = fetch_html(category_url)
    except requests.RequestException:
        return []
    state = extract_react_state(html)
    items = extract_products(state)
    if items:
        return [clean_product(p) for p in items if p.get("ProductVariantId")]
    return []

def build_output(categories):
    output = {
        "store": "chaldal", "base_url": BASE_URL,
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "categories": categories,
    }
    total = 0; leaf_count = 0
    def process(node):
        nonlocal total, leaf_count
        subs = node.get("subcategories", [])
        if not subs:
            url = node.get("url")
            if url:
                products = scrape_products(url, node["name"])
                node["products"] = products
                total += len(products); leaf_count += 1
            else:
                node["products"] = []
        else:
            for c in subs: process(c)
    for cat in categories: process(cat)
    output["_meta"] = {"leaf_categories": leaf_count, "total_products": total}
    return output

def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "Grocery.json"
    categories = scrape_full_tree()
    output = build_output(categories)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"Done: {output['_meta']['total_products']} products from {output['_meta']['leaf_categories']} leaf categories")
    print(f"Output: {out}")

if __name__ == "__main__":
    main()
