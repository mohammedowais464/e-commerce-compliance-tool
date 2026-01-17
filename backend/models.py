from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# Used by Person 2 (Scraper)
class Price(BaseModel):
    mrp: Optional[float] = None
    deal: Optional[float] = None
    discount: Optional[str] = None


class ProductData(BaseModel):
    # Core
    url: str
    title: str
    brand: Optional[str] = None

    # Seller (existing + new structured fields)
    seller: Optional[str] = None                      # existing display name
    seller_legal_name: Optional[str] = None           # legal entity name
    seller_address: Optional[str] = None
    seller_contact: Optional[str] = None              # phone/email combined
    importer_details: Optional[str] = None

    # Price and charges
    price: Price = Price()                            # existing
    total_price: Optional[float] = None               # final price user pays
    taxes_included: Optional[bool] = None             # "inclusive of all taxes"
    extra_charges: Optional[List[str]] = None         # ["delivery fee", "convenience fee"]

    # Product information
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    net_quantity: Optional[str] = None                # "100 ml", "500 g"
    unit: Optional[str] = None                        # "ml", "g", "piece"
    country_of_origin: Optional[str] = None
    expiry_date: Optional[str] = None                 # text; parse later if needed
    ingredients: Optional[str] = None
    nutrition_info: Optional[str] = None
    warnings: Optional[str] = None
    usage_instructions: Optional[str] = None

    # Policies and support
    returns: Optional[str] = None                     # existing short text
    return_policy_text: Optional[str] = None          # full return/refund policy
    delivery: Optional[str] = None                    # existing short text
    delivery_estimate_text: Optional[str] = None
    warranty: Optional[str] = None                    # existing short text
    warranty_text: Optional[str] = None               # full warranty/guarantee
    grievance_officer_details: Optional[str] = None

    # Raw technical details (keep as backup for AI)
    technical_details: Optional[str] = None

    # Metadata
    timestamp: datetime = Field(default_factory=datetime.now)


# Used by Person 3 (Compliance)
class Violation(BaseModel):
    rule_id: str
    severity: str  # HIGH, MEDIUM, LOW
    description: str
    suggestion: str


class TrustIndex(BaseModel):
    score: int
    reasons: List[str]


# AI-normalized product from Gemini
class AiNormalizedProduct(BaseModel):
    category: str | None = None  # "electronics", "food", "health", "all"

    seller: str | None = None
    seller_contact: str | None = None
    seller_address: str | None = None
    price: float | None = None
    charges: str | None = None
    returns: str | None = None
    delivery: str | None = None
    origin: str | None = None
    grievance: str | None = None
    description: str | None = None
    reviews: str | None = None
    title: str | None = None
    brand: str | None = None
    quantity: str | None = None
    images: bool | None = None

    # electronics
    warranty: str | None = None
    specifications: str | None = None
    voltage: str | None = None
    safety: str | None = None
    energy_rating: str | None = None
    model_number: str | None = None
    compatibility: str | None = None

    # food
    expiry: str | None = None
    ingredients: str | None = None
    fssai: str | None = None
    allergen: str | None = None
    veg_nonveg: str | None = None
    storage: str | None = None
    manufacturer: str | None = None
    nutrition: str | None = None

    # health
    disclaimer: str | None = None
    dosage: str | None = None
    guaranteed: str | None = None
    usage: str | None = None
    warning: str | None = None
    age_limit: str | None = None
    prescription_required: str | None = None


class ScanResult(BaseModel):
    id: int | None = None
    timestamp: datetime
    product: ProductData
    risk_score: int
    violations: List[Violation]
    trust_index: TrustIndex
    ai_product: AiNormalizedProduct | None = None


# API Request Model
class ScanRequest(BaseModel):
    url: str


if __name__ == "__main__":
    sample = ProductData(
        url="https://example.com/product",
        title="Sample Product",
        seller="Test Seller",
        price=Price(mrp=1299, deal=999, discount="23% off"),
    )
    print(sample.model_dump_json(indent=2))
