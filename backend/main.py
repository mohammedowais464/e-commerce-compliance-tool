from datetime import datetime
import json
import os
import requests

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from evaluator import infer_product_category
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

from datetime import datetime
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session



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


<<<<<<< HEAD

def ai_normalize_product(product: ProductData) -> AiNormalizedProduct:
    """
    Call Gemini HTTP API to normalize ProductData into AiNormalizedProduct.
    Uses ALL scraped text (especially technical_details and description).
    Falls back to scraped fields if missing or on HTTP errors.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
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

    url = (
        "https://generativelanguage.googleapis.com/v1/"
        "models/gemini-2.0-flash:generateContent"
    )

    # Build a lighter JSON for the prompt
    product_json = {
        "url": product.url,
        "title": product.title,
        "brand": product.brand,
        "seller": product.seller,
        "price": product.price.model_dump() if product.price else None,
        "returns": product.returns,
        "delivery": product.delivery,
        "description": product.description,
        "manufacturer": product.manufacturer,
        "country_of_origin": product.country_of_origin,
        "technical_details": product.technical_details,
    }

    prompt = (
        "You are a compliance assistant for Indian e-commerce rules.\n"
        "You are given a ProductData JSON scraped from an e-commerce site.\n"
        "Use ALL of these fields, especially 'technical_details' and 'description', "
        "to fill an AiNormalizedProduct JSON.\n\n"
        "From this data, extract when possible:\n"
        "- brand (e.g. 'LAKMÉ').\n"
        "- quantity as a string, including unit when obvious (e.g. '100 ml').\n"
        "- expiry as text (e.g. '05 MAY 2027').\n"
        "- ingredients: a comma-separated list of ingredients if present.\n"
        "- usage: short description of how to use or key benefits.\n"
        "- warning: short safety warnings.\n"
        "- seller: main seller name.\n"
        "- seller_contact: manufacturer/importer contact or phone/email.\n"
        "- seller_address: address from manufacturer/importer/packer if clearly present.\n"
        "- origin: country of origin (e.g. 'India').\n"
        "- returns: short return/returnable text.\n"
        "- delivery: short phrase like 'Free delivery'.\n"
        "- grievance: long manufacturer/importer/grievance contact.\n"
        "- manufacturer: manufacturer name.\n"
        "- nutrition: nutrition information for food items.\n"
        "- category: 'electronics' for phones/laptops/TVs; 'food' for snacks/drinks; "
        "  'health' for medicines/supplements/cosmetics; otherwise 'all'.\n\n"
        "VERY IMPORTANT RULES:\n"
        "- Only use text present in the ProductData JSON.\n"
        "- Do NOT invent values. If something is not clearly present, set it to null.\n"
        "- If multiple candidates exist, pick the clearest or most complete.\n\n"
        "OUTPUT FORMAT (THIS IS CRITICAL):\n"
        "- Return ONLY one JSON object with exactly these keys:\n"
        "  category, seller, seller_contact, seller_address, price, charges,\n"
        "  returns, delivery, origin, grievance, description, reviews, title,\n"
        "  brand, quantity, images, warranty, specifications, voltage, safety,\n"
        "  energy_rating, model_number, compatibility, expiry, ingredients,\n"
        "  fssai, allergen, veg_nonveg, storage, manufacturer, nutrition,\n"
        "  disclaimer, dosage, guaranteed, usage, warning, age_limit,\n"
        "  prescription_required.\n"
        "- All keys must be present. If a value is unknown, set it to null.\n"
        "- Do NOT wrap the JSON in markdown. No ``` fences.\n\n"
        f"ProductData JSON:\n{json.dumps(product_json, ensure_ascii=False)}\n"
    )

    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    params = {"key": api_key}
    headers = {"Content-Type": "application/json"}

    try:
        resp = requests.post(url, params=params, headers=headers, json=body, timeout=20)
        print("GEMINI STATUS:", resp.status_code)
        print("GEMINI BODY:", resp.text[:1000])
        resp.raise_for_status()
    except requests.HTTPError as e:
        print("GEMINI ERROR:", e)
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

    result = resp.json()
    try:
        text = result["candidates"]["content"]["parts"]["text"].strip()
    except Exception as e:
        print("GEMINI PARSE ERROR:", e, result)
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

    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()

    print("GEMINI RAW TEXT:", repr(text[:500]))

    data = json.loads(text)
    return AiNormalizedProduct(**data)



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

    # Returns and delivery (AI may refine short text)
    if ai.returns:
        data.returns = ai.returns
    if ai.delivery:
        data.delivery = ai.delivery

    # Price (if AI parsed numeric price)
    if ai.price is not None:
        # keep mrp as-is, but override deal / total_price with AI if present
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
=======
def run_compliance_check(product: ProductData) -> dict:
    product_category = infer_product_category(product)
    field_values = build_field_index(product)

>>>>>>> 5a5c19f1d898072ecfb9197fedb2fe34be61a204
    violations: list[Violation] = []

    category = (ai_product.category or "all").lower()
    is_electronics = category == "electronics"
    is_food = category == "food"
    is_health = category == "health"

    for rule in RULES:
<<<<<<< HEAD
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
=======
        rule_category = rule.get("category", "all")

        # 🔥 CATEGORY FILTER (THIS IS THE FIX)
        if rule_category != "all" and rule_category != product_category:
            continue

        missing = []
        for f in rule.get("required_fields", []):
            if not field_values.get(f, False):
                missing.append(f)

        if missing:
>>>>>>> 5a5c19f1d898072ecfb9197fedb2fe34be61a204
            violations.append(
                Violation(
                    rule_id=rule["id"],
                    severity=rule["severity"],
                    description=(
                        f"{rule['title']} – missing or unclear: "
                        f"{', '.join(missing)}"
                    ),
                    suggestion=(
                        f"Ensure the following field(s) are clearly disclosed: "
                        f"{', '.join(missing)}."
                    ),
                )
            )

<<<<<<< HEAD
=======
    # score calculation stays the same
>>>>>>> 5a5c19f1d898072ecfb9197fedb2fe34be61a204
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

    # 1.5 AI-normalized product (Gemini)
    ai_product = ai_normalize_product(product)
    print("AI PRODUCT:", ai_product.dict())

    # 1.6 Merge AI into product for rich view
    normalized_product = merge_ai_into_product(product, ai_product)

    # 2. Rule-based compliance using rules.py (with AI normalization)
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

    # 4. Risk score from violations
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

    # 6. Build result (IMPORTANT: use normalized_product here)
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
