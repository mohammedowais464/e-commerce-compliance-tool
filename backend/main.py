from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime

# Import your own modules
from models import ScanRequest, ScanResult, ProductData, Violation
from database import get_db, init_db, ScanRecord

# --- INTEGRATION STUBS (Placeholders for Person 2 & 3) ---
# Once Person 2 finishes, change this to: from scrapers.extractor import extract_product
def mock_extract_product(url: str) -> ProductData:
    # Simulates what Person 2 will give you
    return ProductData(
        url=url, 
        title="Sample Product", 
        price="₹500", 
        description="Limited time offer!"
    )

# Once Person 3 finishes, change this to: from compliance.engine import run_compliance_check
def mock_compliance_check(product: ProductData) -> dict:
    # Simulates what Person 3 will give you
    return {
        "score": 65,
        "violations": [
            Violation(rule_id="R1", severity="HIGH", description="Missing Country of Origin", suggestion="Add manufacture details"),
            Violation(rule_id="R2", severity="MEDIUM", description="False Urgency", suggestion="Remove 'Limited Time' tag")
        ]
    }
# ---------------------------------------------------------

app = FastAPI(title="Compliance API")

# Setup CORS for Person 5 (Frontend)
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

@app.post("/scan", response_model=ScanResult)
def scan_endpoint(request: ScanRequest, db: Session = Depends(get_db)):
    # 1. Call Person 2's Logic (or your mock)
    product = mock_extract_product(request.url)
    
    # 2. Call Person 3's Logic (or your mock)
    compliance_result = mock_compliance_check(product)
    
    # 3. Create Result Object
    result = ScanResult(
        timestamp=datetime.utcnow(),
        product=product,
        risk_score=compliance_result["score"],
        violations=compliance_result["violations"]
    )
    
    # 4. Save to Database (Your Logic)
    db_record = ScanRecord(
        url=request.url,
        risk_score=result.risk_score,
        product_data=product.dict(),
        violations_data=[v.dict() for v in result.violations]
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    result.id = db_record.id
    
    return result

@app.get("/history")
def get_history(db: Session = Depends(get_db)):
    return db.query(ScanRecord).order_by(ScanRecord.timestamp.desc()).all()
