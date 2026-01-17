import time
import random
import re
import json
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from models import ProductData, Price

ua = UserAgent()


def scrape_product(url: str) -> ProductData:
    domain = urlparse(url).netloc.lower()
    html = _fetch_html(url)

    if "flipkart.com" in domain:
        return _scrape_flipkart(url, html)
    elif "amazon.in" in domain or "amazon.com" in domain or "amzn.in" in domain:
        return _scrape_amazon(url, html)
    else:
        # LimeRoad, Myntra, Ajio, etc.
        return _scrape_generic(url, html)


def _fetch_html(url: str) -> str:
    headers = {
        "User-Agent": ua.random,
        "Accept-Language": "en-IN,en;q=0.9",
        "Referer": "https://www.google.com/",
    }

    time.sleep(random.uniform(1, 2))

    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.text


# ---------- COMMON HELPERS ----------

def _safe_float(value: str):
    try:
        return float(value)
    except Exception:
        return None


def _extract_price(text: str):
    match = re.search(r"₹\s*([\d,]+(?:\.\d+)?)", text)
    if not match:
        return None
    return _safe_float(match.group(1).replace(",", ""))


def _extract_json_ld_product(soup: BeautifulSoup):
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        try:
            data = json.loads(script.string or script.text or "")
        except Exception:
            continue

        candidates = []
        if isinstance(data, dict):
            candidates = [data]
        elif isinstance(data, list):
            candidates = data

        for item in candidates:
            if not isinstance(item, dict):
                continue
            t = item.get("@type")
            if t == "Product" or (isinstance(t, list) and "Product" in t):
                return item

            if "@graph" in item and isinstance(item["@graph"], list):
                for g in item["@graph"]:
                    if isinstance(g, dict):
                        gt = g.get("@type")
                        if gt == "Product" or (isinstance(gt, list) and "Product" in gt):
                            return g
    return None


# ---------- FLIPKART SCRAPER ----------

def _scrape_flipkart(url: str, html: str) -> ProductData:
    soup = BeautifulSoup(html, "lxml")

    # TITLE
    title_el = (
        soup.select_one("span.B_NuCI")
        or soup.select_one('span[dir="auto"]')
    )
    title = title_el.get_text(strip=True) if title_el else "No title found"

    # PRICE
    mrp = None
    deal = None
    discount_text = None

    deal_el = soup.select_one("div._30jeq3._16Jk6d") or soup.select_one("div._30jeq3")
    if deal_el:
        deal_str = deal_el.get_text(strip=True)
        deal = _extract_price(deal_str)

    mrp_el = soup.select_one("div._3I9_wc._2p6lqe")
    if mrp_el:
        mrp_str = mrp_el.get_text(strip=True)
        possible_mrp = _extract_price(mrp_str)
        if possible_mrp:
            mrp = possible_mrp

    if mrp is None and deal is not None:
        mrp = deal
    if deal is None and mrp is not None:
        deal = mrp

    discount_el = (
        soup.find("div", string=re.compile(r"\d+% off", re.I))
        or soup.find("span", string=re.compile(r"\d+% off", re.I))
    )
    if discount_el:
        discount_text = discount_el.get_text(strip=True)

    if not discount_text and mrp and deal and mrp > deal:
        pct = round((mrp - deal) / mrp * 100)
        discount_text = f"{pct}% off"

    # SELLER (display name)
    seller_display = "Unknown seller"
    seller_label = soup.find("span", string=re.compile(r"Seller", re.I))
    if seller_label:
        parent = seller_label.find_parent()
        if parent:
            seller_name_el = parent.find_next("span")
            if seller_name_el:
                seller_display = seller_name_el.get_text(strip=True)

    # RETURNS (short)
    returns_short = None
    for node in soup.select("span, div, li"):
        txt = node.get_text(strip=True)
        if re.search(r"\b\d+\s*day[s]?\s+(Replacement|Returnable)", txt, re.I):
            returns_short = txt[:120]
            break

    # HIGHLIGHTS as description
    description = None
    highlights = soup.select("li._21Ahn-")
    if highlights:
        items = [li.get_text(" ", strip=True) for li in highlights]
        description = " | ".join(items)[:400]
    else:
        full_text = soup.get_text(separator=" ", strip=True)
        description = full_text[:400] if full_text else None

    # Build structured ProductData
    price_obj = Price(mrp=mrp, deal=deal, discount=discount_text)

    product = ProductData(
        url=url,
        title=title[:150],
        brand=None,  # could be parsed from specs later
        seller=seller_display,
        seller_legal_name=None,
        seller_address=None,
        seller_contact=None,
        importer_details=None,
        price=price_obj,
        total_price=deal,
        taxes_included=None,
        extra_charges=None,
        description=description,
        manufacturer=None,
        net_quantity=None,
        unit=None,
        country_of_origin=None,
        expiry_date=None,
        ingredients=None,
        nutrition_info=None,
        warnings=None,
        usage_instructions=None,
        returns=returns_short,
        return_policy_text=None,
        delivery=None,
        delivery_estimate_text=None,
        warranty=None,
        warranty_text=None,
        grievance_officer_details=None,
        technical_details=None,  # you can later fill with spec table like Amazon
    )

    return product


# ---------- AMAZON SCRAPER ----------

def _scrape_amazon(url: str, html: str) -> ProductData:
    soup = BeautifulSoup(html, "lxml")

    # ---------- TITLE ----------
    title_el = soup.select_one("#productTitle") or soup.select_one("h1 span")
    if title_el:
        title = title_el.text.strip()
    else:
        ttag = soup.find("title")
        title = ttag.get_text(strip=True) if ttag else "No title found"

    # ---------- PRICE BLOCK (MRP + DEAL) ----------
    mrp_price = None
    deal_price = None

    # 1) MRP / crossed price
    mrp_block = soup.select_one("span.a-price.a-text-price")
    if mrp_block:
        mrp_whole = mrp_block.select_one("span.a-price-whole")
        mrp_frac = mrp_block.select_one("span.a-price-fraction")
        if mrp_whole:
            mrp_str = mrp_whole.text.replace(",", "").strip()
            if mrp_frac:
                mrp_str = f"{mrp_str}.{mrp_frac.text.strip()}"
            mrp_price = _safe_float(mrp_str)

    # 2) Deal price: first non-crossed a-price
    deal_block = None
    for block in soup.select("span.a-price"):
        classes = block.get("class", [])
        if "a-text-price" not in classes:
            deal_block = block
            break

    if deal_block:
        whole = deal_block.select_one("span.a-price-whole")
        frac = deal_block.select_one("span.a-price-fraction")
        if whole:
            deal_str = whole.text.replace(",", "").strip()
            if frac:
                deal_str = f"{deal_str}.{frac.text.strip()}"
            deal_price = _safe_float(deal_str)

    # 3) Fallback generic ₹pattern
    if not mrp_price and not deal_price:
        text = soup.get_text(separator=" ", strip=True)
        generic_price = _extract_price(text)
        if generic_price:
            deal_price = generic_price

    if not mrp_price and deal_price:
        mrp_price = deal_price
    if not deal_price and mrp_price:
        deal_price = mrp_price

    # Discount text
    discount_text = None
    explicit_span = soup.find("span", string=re.compile(r"-?\d+%(\s*off)?", re.I))
    if explicit_span:
        discount_text = explicit_span.get_text(strip=True)
    if not discount_text and mrp_price and deal_price and mrp_price > deal_price:
        pct = round((mrp_price - deal_price) / mrp_price * 100)
        discount_text = f"{pct}% off"

    # ---------- SELLER ----------
    seller_el = soup.select_one("#sellerProfileTriggerId")
    seller_display = seller_el.text.strip() if seller_el else "Amazon"

    # ---------- RETURNS (SHORT) ----------
    returns_short = None
    returns_container = soup.find(
        id=re.compile(r"RETURNS_POLICY|RETURNS-FEATURE", re.I)
    ) or soup.find("div", string=re.compile(r"Returns", re.I))

    if returns_container:
        returns_text = returns_container.get_text(separator=" ", strip=True)
        returns_short = returns_text[:120]
    else:
        for node in soup.select("span, li, div"):
            txt = node.get_text(strip=True)
            if re.search(r"\b\d+\s*-?\s*day[s]?\s+return", txt, re.I):
                returns_short = txt[:120]
                break

    # ---------- TECHNICAL DETAILS (KEY:VALUE LINES) ----------
    technical_details = None
    rows = []

    tech_table = soup.find(
        "table",
        id=re.compile(r"productDetails_techSpec|productDetails_detailBullets", re.I),
    )
    if tech_table:
        for row in tech_table.select("tr"):
            cells = row.find_all(["th", "td"])
            if len(cells) >= 2:
                key = cells[0].get_text(" ", strip=True)
                val = cells[1].get_text(" ", strip=True)
                rows.append(f"{key}: {val}")

    if not rows:
        heading = soup.find(
            lambda tag: tag.name in ["h1", "h2", "h3", "span"]
            and re.search(r"Technical Details|Product Details", tag.get_text(), re.I)
        )
        if heading:
            container = heading.find_parent()
            next_table = container.find_next("table")
            if next_table:
                for row in next_table.select("tr"):
                    cells = row.find_all(["th", "td"])
                    if len(cells) >= 2:
                        key = cells[0].get_text(" ", strip=True)
                        val = cells[1].get_text(" ", strip=True)
                        rows.append(f"{key}: {val}")

    if rows:
        technical_details = " | ".join(rows)

    # ---------- DETAIL BULLETS (FEATURES) ----------
    detail_bullets = []
    for li in soup.select("#feature-bullets li, #feature-bullets span.a-list-item"):
        txt = li.get_text(" ", strip=True)
        if txt:
            detail_bullets.append(txt)
    detail_bullets_text = " | ".join(detail_bullets)[:2000] if detail_bullets else None

    # ---------- POLICY TEXT (RETURNS + DELIVERY) ----------
    policy_chunks = []

    if returns_container:
        policy_chunks.append(returns_container.get_text(" ", strip=True))

    # Delivery / shipping estimate block (common IDs/classes)
    delivery_el = (
        soup.find(id=re.compile(r"deliveryMessage", re.I))
        or soup.find(id=re.compile(r"ddmDeliveryMessage", re.I))
        or soup.select_one("#mir-layout-DELIVERY_BLOCK_SLOT, #deliveryBlockMessage")
    )
    if delivery_el:
        policy_chunks.append(delivery_el.get_text(" ", strip=True))

    policy_text = " | ".join(policy_chunks)[:2000] if policy_chunks else None

    # ---------- FULL PAGE TEXT (FALLBACK, SHORTENED) ----------
    full_text = soup.get_text(separator=" ", strip=True)
    full_page_text = full_text[:4000] if full_text else None

    # ---------- BUILD PRODUCT DATA ----------
    price_obj = Price(
        mrp=mrp_price or deal_price,
        deal=deal_price or mrp_price,
        discount=discount_text,
    )

    product = ProductData(
        url=url,
        title=title[:150],
        brand=None,                 # brand will come later from AI / tech table
        seller=seller_display,
        seller_legal_name=None,
        seller_address=None,
        seller_contact=None,
        importer_details=None,
        price=price_obj,
        total_price=deal_price,
        taxes_included=None,
        extra_charges=None,
        description=detail_bullets_text,    # use bullets as main description for now
        manufacturer=None,
        net_quantity=None,
        unit=None,
        country_of_origin=None,
        expiry_date=None,
        ingredients=None,
        nutrition_info=None,
        warnings=None,
        usage_instructions=None,
        returns=returns_short,
        return_policy_text=policy_text,
        delivery=None,
        delivery_estimate_text=None,
        warranty=None,
        warranty_text=None,
        grievance_officer_details=None,
        technical_details=technical_details,  # still the key:value lines
    )

    # If you want, you can also store full_page_text somewhere later
    # (either add a new field to ProductData, or pass it only to AI).

    return product


# ---------- GENERIC SCRAPER ----------

def _scrape_generic(url: str, html: str) -> ProductData:
    soup = BeautifulSoup(html, "lxml")

    # JSON-LD first (if present)
    ld_product = _extract_json_ld_product(soup)

    title = None
    brand = None
    description = None
    seller_legal_name = None
    manufacturer = None
    total_price = None

    if ld_product:
        title = ld_product.get("name") or ld_product.get("headline")
        description = ld_product.get("description")

        brand_field = ld_product.get("brand")
        if isinstance(brand_field, dict):
            brand = brand_field.get("name")
        elif isinstance(brand_field, str):
            brand = brand_field

        offers = ld_product.get("offers")
        if isinstance(offers, dict):
            price_value = offers.get("price")
            try:
                total_price = float(price_value)
            except (TypeError, ValueError):
                total_price = None

            seller_obj = offers.get("seller")
            if isinstance(seller_obj, dict):
                seller_legal_name = seller_obj.get("name")

        manufacturer_field = ld_product.get("manufacturer")
        if isinstance(manufacturer_field, dict):
            manufacturer = manufacturer_field.get("name")
        elif isinstance(manufacturer_field, str):
            manufacturer = manufacturer_field

    # TITLE fallback
    if not title:
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title["content"].strip()
    if not title and soup.title and soup.title.string:
        title = soup.title.string.strip()
    if not title:
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(strip=True)
    if not title:
        title = "No title found"

    # PRICE (mrp/deal)
    mrp = None
    deal = None
    discount_text = None

    full_text = soup.get_text(separator=" ", strip=True)

    deal = _extract_price(full_text)
    mrp = deal

    prices = re.findall(r"₹\s*([\d,]+(?:\.\d+)?)", full_text)
    if len(prices) >= 2:
        nums = [_safe_float(p.replace(",", "")) for p in prices]
        nums = [n for n in nums if n is not None]
        if len(nums) >= 2:
            high = max(nums)
            low = min(nums)
            mrp, deal = high, low

    m = re.search(r"(\d+)%\s*off", full_text, re.I)
    if m:
        discount_text = f"{m.group(1)}% off"

    if not discount_text and mrp and deal and mrp > deal:
        pct = round((mrp - deal) / mrp * 100)
        discount_text = f"{pct}% off"

    # SELLER display
    seller_display = "Unknown seller"
    seller_label = soup.find(string=re.compile(r"Brand|Seller|Sold by", re.I))
    if seller_label:
        parent = seller_label.find_parent()
        if parent:
            cand = parent.find_next(["strong", "span", "div"])
            if cand:
                seller_display = cand.get_text(strip=True)

    # RETURNS short
    returns_short = None
    for node in soup.select("span, div, li"):
        txt = node.get_text(strip=True)
        if re.search(r"\b\d+\s*day[s]?\s+(return|refund|replacement|returnable)", txt, re.I):
            returns_short = txt[:120]
            break

    # DESCRIPTION
    if not description:
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            description = meta_desc["content"].strip()

    if not description:
        desc_div = (
            soup.find("div", id=re.compile(r"productDescription|description", re.I))
            or soup.find("div", class_=re.compile(r"description|prod-desc|product-info", re.I))
        )
        if desc_div:
            description = desc_div.get_text(" ", strip=True)

    if not description:
        for p in soup.find_all("p"):
            txt = p.get_text(" ", strip=True)
            if len(txt) > 50:
                description = txt
                break

    if not description and full_text:
        description = full_text

    if description:
        description = description[:400]

    price_obj = Price(mrp=mrp, deal=deal, discount=discount_text)

    product = ProductData(
        url=url,
        title=title[:150],
        brand=brand,
        seller=seller_display,
        seller_legal_name=seller_legal_name,
        seller_address=None,
        seller_contact=None,
        importer_details=None,
        price=price_obj,
        total_price=total_price or deal,
        taxes_included=None,
        extra_charges=None,
        description=description,
        manufacturer=manufacturer,
        net_quantity=None,
        unit=None,
        country_of_origin=None,
        expiry_date=None,
        ingredients=None,
        nutrition_info=None,
        warnings=None,
        usage_instructions=None,
        returns=returns_short,
        return_policy_text=None,
        delivery=None,
        delivery_estimate_text=None,
        warranty=None,
        warranty_text=None,
        grievance_officer_details=None,
        technical_details=None,
    )

    return product


if __name__ == "__main__":
    test_urls = [
        "https://amzn.in/d/9ZX3RdP",
        "https://amzn.in/d/2sgbIfs",
    ]
    for u in test_urls:
        try:
            print(f"\nTesting {u}")
            p = scrape_product(u)
            print(p.model_dump_json(indent=2))
        except Exception as e:
            print(f"Error for {u}: {e}")
