from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Used by Person 2 (Scraper)
class ProductData(BaseModel):
    url: str
    title: Optional[str] = None
    price: Optional[str] = None
    description: Optional[str] = None
    seller_info: Optional[str] = None
    image_url: Optional[str] = None

# Used by Person 3 (Compliance)
class Violation(BaseModel):
    rule_id: str
    severity: str  # HIGH, MEDIUM, LOW
    description: str
    suggestion: str

class ScanResult(BaseModel):
    id: Optional[int] = None
    timestamp: datetime
    product: ProductData
    risk_score: int
    violations: List[Violation]

# API Request Model
class ScanRequest(BaseModel):
    url: str
