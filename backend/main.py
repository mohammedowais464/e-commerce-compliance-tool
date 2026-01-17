from datetime import datetime
import json
import os
import re

from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from scraper import scrape_product, _fetch_html
from dark_patterns import detect_dark_patterns
from models import (
    ScanRequest,
    ScanResult,
    ProductData,
    Violation,
    AiNormalizedProduct,
)
from database import get_db, init_db, ScanRecord
from rules import RULES

load_dotenv()

# We still call ai_normalize_product, but it is now heuristic-only (no external AI)
USE_AI = True


app = FastAPI(title="Compliance API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


def build_field_index(product: ProductData) -> dict:
    """
    Legacy helper (not used by the new AI-based engine, kept for reference).
    """
    tech = (product.technical_details or "").lower()

    field_values: dict[str, bool] = {
        "seller": bool(product.seller),
        "seller_contact": False,
        "seller_address": False,
        "price": bool(product.price),
        "charges": "convenience fee" in tech or "handling fee" in tech,
        "returns": bool(product.returns),
        "delivery": bool(product.delivery),
        "origin": "country of origin" in tech,
        "grievance": "grievance" in tech,
        "description": bool(getattr(product, "description", None) or tech),
        "reviews": "reviews" in tech or "rating" in tech,
        "title": bool(product.title),
        "brand": bool(product.brand) or "brand name" in tech,
        "quantity": (
            "net quantity" in tech
            or "unit count" in tech
            or " g" in tech
            or " kg" in tech
        ),
        "images": True,
        # electronics
        "warranty": bool(product.warranty) or "warranty" in tech,
        "specifications": bool(product.technical_details),
        "voltage": "volt" in tech or " w" in tech,
        "safety": "safety" in tech or "warning" in tech,
        "energy_rating": "star" in tech or "energy" in tech,
        "model_number": "model" in tech,
        "compatibility": "compatible" in tech,
        # food
        "expiry": "expiry" in tech or "best before" in tech,
        "ingredients": "ingredients" in tech,
        "fssai": "fssai" in tech,
        "allergen": "allergen" in tech,
        "veg_nonveg": "vegetarian" in tech or "non-vegetarian" in tech,
        "storage": "store in" in tech or "storage" in tech,
        "manufacturer": "manufacturer" in tech,
        "nutrition": "nutrition" in tech or "nutritional" in tech,
        # health
        "disclaimer": "disclaimer" in tech,
        "dosage": "dosage" in tech or "dose" in tech,
        "guaranteed": "guaranteed" in tech,
        "100%": "100%" in tech,
        "usage": "usage" in tech or "use:" in tech,
        "warning": "warning" in tech,
        "age_limit": "age" in tech,
        "prescription_required": "prescription" in tech,
    }

    return field_values


def parse_technical_details(tech: str) -> dict:
    """
    Parse 'Key: Value | Key2: Value2' style technical_details into a dict.
    Very simple heuristic split.
    """
    result: dict[str, str] = {}
    if not tech:
        return result

    # Your scraper joins entries with " | "
    parts = [p.strip() for p in tech.split("|") if p.strip()]

    for part in parts:
        if ":" in part:
            key, val = part.split(":", 1)
            key = key.strip().lower()
            val = val.strip()
            if key and val:
                result[key] = val

    return result


def fallback_ai(product: ProductData) -> AiNormalizedProduct:
    """
    Minimal normalized object if technical details are missing.
    """
    return AiNormalizedProduct(
        category="all",
        seller=product.seller,
        price=product.price.deal if product.price else None,
        returns=product.returns,
        delivery=product.delivery,
        origin=product.country_of_origin,
        brand=product.brand,
        quantity=None,
        images=True,
    )


def ai_normalize_product(product: ProductData) -> AiNormalizedProduct:
    """
    Heuristic 'AI' using only scraped data:
    - parses technical_details for known keys
    - fills AiNormalizedProduct fields accordingly
    """
    tech_map = parse_technical_details(product.technical_details or "")

    # Brand
    brand = product.brand
    if not brand:
        brand = tech_map.get("brand") or tech_map.get("brand name")

    # Origin
    origin = product.country_of_origin
    if not origin:
        origin = tech_map.get("country of origin") or tech_map.get("country as labeled")

    # Manufacturer
    manufacturer = product.manufacturer
    if not manufacturer:
        manufacturer = tech_map.get("manufacturer")

    # Model number
    model_number = tech_map.get("item model number") or tech_map.get("model number")

    # Quantity: try to detect "100 ml", "50 g", etc.
    quantity = None
    text_for_qty = (product.technical_details or "") + " " + (product.description or "")
    m_qty = re.search(r"(\d+(\.\d+)?)\s*(ml|g|kg|l|L)", text_for_qty)
    if m_qty:
        quantity = f"{m_qty.group(1)} {m_qty.group(3)}"

    # Basic category guess from title
    title_lower = (product.title or "").lower()
    if any(w in title_lower for w in ["laptop", "phone", "tv", "headphone", "earbud"]):
        category = "electronics"
    elif any(w in title_lower for w in ["biscuit", "chips", "juice", "chocolate", "snack"]):
        category = "food"
    elif any(w in title_lower for w in ["sunscreen", "cream", "lotion", "tablet", "capsule", "syrup"]):
        category = "health"
    else:
        category = "all"

    return AiNormalizedProduct(
        category=category,
        seller=product.seller,
        seller_contact=None,
        seller_address=None,
        price=product.price.deal if product.price else None,
        charges=None,
        returns=product.returns,
        delivery=product.delivery,
        origin=origin,
        grievance=None,
        description=product.description,
        reviews=None,
        title=product.title,
        brand=brand,
        quantity=quantity,
        images=True,
        warranty=product.warranty,
        specifications=product.technical_details,
        voltage=None,
        safety=None,
        energy_rating=None,
        model_number=model_number,
        compatibility=None,
        expiry=None,
        ingredients=None,
        fssai=None,
        allergen=None,
        veg_nonveg=None,
        storage=None,
        manufacturer=manufacturer,
        nutrition=None,
        disclaimer=None,
        dosage=None,
        guaranteed=None,
        usage=None,
        warning=None,
        age_limit=None,
        prescription_required=None,
    )


def merge_ai_into_product(product: ProductData, ai: AiNormalizedProduct) -> ProductData:
    """
    Combine raw scraped ProductData with AI-normalized fields to get a richer,
    'ideal' ProductData for UI and risk explanation.
    Does NOT change fields where AI returned null.
    """
    data = product.model_copy(deep=True)

    # Brand and origin
    if ai.brand:
        data.brand = ai.brand
    if ai.origin:
        data.country_of_origin = ai.origin

    # Quantity: e.g. "100 ml" or "500 g"
    if ai.quantity:
        parts = ai.quantity.split()
        if len(parts) >= 2:
            data.net_quantity = parts[0]
            data.unit = parts[1]
        else:
            data.net_quantity = ai.quantity

    # Usage, warnings, expiry, ingredients, manufacturer
    if ai.usage:
        data.usage_instructions = ai.usage
    if ai.warning:
        data.warnings = ai.warning
    if ai.expiry:
        data.expiry_date = ai.expiry
    if ai.ingredients:
        data.ingredients = ai.ingredients
    if ai.manufacturer:
        data.manufacturer = ai.manufacturer

    # Seller / contact / grievance
    if ai.seller:
        data.seller = ai.seller
    if ai.seller_contact:
        data.seller_contact = ai.seller_contact
    if ai.seller_address:
        data.seller_address = ai.seller_address
    if ai.grievance:
        data.grievance_officer_details = ai.grievance

    # Returns and delivery
    if ai.returns:
        data.returns = ai.returns
    if ai.delivery:
        data.delivery = ai.delivery

    # Price
    if ai.price is not None:
        if data.price is not None:
            data.price.deal = ai.price
        data.total_price = ai.price

    return data


def build_field_index_ai(product: ProductData, ai: AiNormalizedProduct) -> dict:
    """
    Build field index using AI-normalized product, but fall back to raw scraped data
    where AI fields are missing.
    """
    tech = (product.technical_details or "").lower()

    seller = ai.seller or product.seller
    price = ai.price if ai.price is not None else (product.price.deal if product.price else None)
    returns = ai.returns or product.returns
    delivery = ai.delivery or product.delivery
    origin = ai.origin
    brand = ai.brand or product.brand
    quantity = ai.quantity
    images = ai.images if ai.images is not None else True

    return {
        "seller": bool(seller),
        "seller_contact": bool(ai.seller_contact),
        "seller_address": bool(ai.seller_address),
        "price": price is not None,
        "charges": bool(ai.charges),
        "returns": bool(returns),
        "delivery": bool(delivery),
        "origin": bool(origin),
        "grievance": bool(ai.grievance),
        "description": bool(ai.description or product.title or tech),
        "reviews": bool(ai.reviews),
        "title": bool(ai.title or product.title),
        "brand": bool(brand),
        "quantity": bool(quantity),
        "images": bool(images),
        # electronics
        "warranty": bool(ai.warranty or product.warranty or ("warranty" in tech)),
        "specifications": bool(ai.specifications or product.technical_details),
        "voltage": bool(ai.voltage),
        "safety": bool(ai.safety),
        "energy_rating": bool(ai.energy_rating),
        "model_number": bool(ai.model_number),
        "compatibility": bool(ai.compatibility),
        # food
        "expiry": bool(ai.expiry),
        "ingredients": bool(ai.ingredients),
        "fssai": bool(ai.fssai),
        "allergen": bool(ai.allergen),
        "veg_nonveg": bool(ai.veg_nonveg),
        "storage": bool(ai.storage),
        "manufacturer": bool(ai.manufacturer or ("manufacturer" in tech)),
        "nutrition": bool(ai.nutrition),
        # health
        "disclaimer": bool(ai.disclaimer),
        "dosage": bool(ai.dosage),
        "guaranteed": bool(ai.guaranteed),
        "100%": "100%" in (ai.guaranteed or ""),
        "usage": bool(ai.usage),
        "warning": bool(ai.warning),
        "age_limit": bool(ai.age_limit),
        "prescription_required": bool(ai.prescription_required),
    }


def run_compliance_check(product: ProductData, ai_product: AiNormalizedProduct) -> dict:
    """
    Apply RULES from rules.py to the product, using AI-normalized fields.
    Filter rules by category from AI (electronics/food/health/all).
    """
    field_values = build_field_index_ai(product, ai_product)
    violations: list[Violation] = []

    category = (ai_product.category or "all").lower()
    is_electronics = category == "electronics"
    is_food = category == "food"
    is_health = category == "health"

    for rule in RULES:
        rule_id = rule["id"]
        severity = rule["severity"]
        title_text = rule["title"]
        required_fields = rule.get("required_fields", [])
        rule_cat = rule.get("category", "all")

        if rule_cat == "electronics" and not is_electronics:
            continue
        if rule_cat == "food" and not is_food:
            continue
        if rule_cat == "health" and not is_health:
            continue

        missing = [f for f in required_fields if not field_values.get(f, False)]

        if missing:
            description = f"{title_text} – missing or unclear: {', '.join(missing)}"
            suggestion = f"Ensure the following field(s) are clearly disclosed: {', '.join(missing)}."
            violations.append(
                Violation(
                    rule_id=rule_id,
                    severity=severity,
                    description=description,
                    suggestion=suggestion,
                )
            )

    score = 100
    for v in violations:
        if v.severity.upper() == "HIGH":
            score -= 20
        elif v.severity.upper() == "MEDIUM":
            score -= 10
        elif v.severity.upper() == "LOW":
            score -= 5

    score = max(0, score)
    return {"score": score, "violations": violations}


def compute_trust_index(product: ProductData, violations: list[Violation]) -> dict:
    score = 100
    reasons: list[str] = []

    tech = (product.technical_details or "").lower()

    if "country of origin" not in tech:
        score -= 15
        reasons.append("Country of origin not found in technical details.")

    if not product.seller:
        score -= 10
        reasons.append("Seller name missing.")

    if not product.returns:
        score -= 15
        reasons.append("No returns information visible.")

    if not product.warranty and "warranty" not in tech:
        score -= 10
        reasons.append("Warranty not specified.")

    if not product.price or getattr(product.price, "deal", None) is None:
        score -= 20
        reasons.append("Deal price not clearly extracted.")

    for v in violations:
        if v.severity.upper() == "HIGH":
            score -= 10
        elif v.severity.upper() == "MEDIUM":
            score -= 5

    score = max(0, min(score, 100))
    return {"score": score, "reasons": reasons}


@app.post("/scan", response_model=ScanResult)
def scan_endpoint(request: ScanRequest, db: Session = Depends(get_db)):
    url = request.url

    # 1. Scrape real product data
    html = _fetch_html(url)
    product = scrape_product(url)

    # 1.5 Heuristic-normalized product
    if USE_AI:
        ai_product = ai_normalize_product(product)
    else:
        ai_product = fallback_ai(product)

    print("AI PRODUCT:", ai_product.dict())

    # 1.6 Merge into product for rich view
    normalized_product = merge_ai_into_product(product, ai_product)

    # 2. Rule-based compliance
    compliance_result = run_compliance_check(product, ai_product)
    base_violations = compliance_result["violations"]

    # 3. Dark patterns
    dark_findings = detect_dark_patterns(product, html)
    dark_violations: list[Violation] = [
        Violation(
            rule_id=f.code,
            severity=f.severity,
            description=f.message,
            suggestion="Review pricing/UX for potential dark pattern.",
        )
        for f in dark_findings
    ]

    all_violations = base_violations + dark_violations

    # 4. Risk score
    risk = 100
    for v in all_violations:
        if v.severity.upper() == "HIGH":
            risk -= 20
        elif v.severity.upper() == "MEDIUM":
            risk -= 10
        elif v.severity.upper() == "LOW":
            risk -= 5
    risk = max(0, risk)

    # 5. Trust index
    trust_index = compute_trust_index(product, all_violations)

    # 6. Build result
    result = ScanResult(
        timestamp=datetime.utcnow(),
        product=normalized_product,
        risk_score=risk,
        violations=all_violations,
        trust_index=trust_index,
        ai_product=ai_product,
    )

    # 7. Save to DB
    product_dict = normalized_product.model_dump()
    product_dict.pop("timestamp", None)

    db_record = ScanRecord(
        url=url,
        risk_score=result.risk_score,
        product_data=product_dict,
        violations_data=[v.model_dump() for v in result.violations],
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    result.id = db_record.id

    return result


@app.get("/history")
def get_history(db: Session = Depends(get_db)):
    return db.query(ScanRecord).order_by(ScanRecord.timestamp.desc()).all()
