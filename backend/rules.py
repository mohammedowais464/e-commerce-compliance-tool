"""
rules.py
========
Complete set of machine-checkable compliance rules
mapped to Indian consumer and e-commerce laws.
"""

RULES = [

# =====================================================
# GENERAL E-COMMERCE DISCLOSURE RULES (ALL PRODUCTS)
# Source: E-Commerce Rules, 2020
# =====================================================

{
    "id": "EC-01",
    "title": "Seller name must be disclosed",
    "law": "E-Commerce Rules 2020 – Rule 4(2)(a)",
    "category": "all",
    "severity": "HIGH",
    "required_fields": ["seller"]
},

{
    "id": "EC-02",
    "title": "Seller contact details must be disclosed",
    "law": "E-Commerce Rules 2020 – Rule 4(2)(a)",
    "category": "all",
    "severity": "HIGH",
    "required_fields": ["seller_contact"]
},

{
    "id": "EC-03",
    "title": "Seller address must be disclosed",
    "law": "E-Commerce Rules 2020 – Rule 4(2)(a)",
    "category": "all",
    "severity": "HIGH",
    "required_fields": ["seller_address"]
},

{
    "id": "EC-04",
    "title": "Price must be displayed clearly",
    "law": "E-Commerce Rules 2020 – Rule 4(2)(b)",
    "category": "all",
    "severity": "HIGH",
    "required_fields": ["price"]
},

{
    "id": "EC-05",
    "title": "All charges must be disclosed (tax, delivery, etc.)",
    "law": "E-Commerce Rules 2020 – Rule 4(2)(c)",
    "category": "all",
    "severity": "MEDIUM",
    "required_fields": ["charges"]
},

{
    "id": "EC-06",
    "title": "Return and refund policy must be disclosed",
    "law": "E-Commerce Rules 2020 – Rule 4(2)(d)",
    "category": "all",
    "severity": "HIGH",
    "required_fields": ["returns"]
},

{
    "id": "EC-07",
    "title": "Delivery and shipment details must be disclosed",
    "law": "E-Commerce Rules 2020 – Rule 4(2)(e)",
    "category": "all",
    "severity": "MEDIUM",
    "required_fields": ["delivery"]
},

{
    "id": "EC-08",
    "title": "Country of origin must be mentioned",
    "law": "E-Commerce Rules 2020 – Rule 4(2)(f)",
    "category": "all",
    "severity": "MEDIUM",
    "required_fields": ["origin"]
},

{
    "id": "EC-09",
    "title": "Product description must not be misleading",
    "law": "Consumer Protection Act 2019 – Section 2(28)",
    "category": "all",
    "severity": "HIGH",
    "required_fields": ["description"]
},

{
    "id": "EC-10",
    "title": "Ratings and reviews must not be manipulated",
    "law": "E-Commerce Rules 2020 – Rule 5(3)",
    "category": "all",
    "severity": "MEDIUM",
    "required_fields": ["reviews"]
},

{
    "id": "EC-11",
    "title": "Grievance officer details must be provided",
    "law": "E-Commerce Rules 2020 – Rule 4(5)",
    "category": "all",
    "severity": "HIGH",
    "required_fields": ["grievance"]
},

# =====================================================
# ELECTRONICS RULES
# =====================================================

{
    "id": "EL-01",
    "title": "Warranty or guarantee information must be disclosed",
    "law": "E-Commerce Rules 2020 – Rule 5(3)",
    "category": "electronics",
    "severity": "HIGH",
    "required_fields": ["warranty"]
},

{
    "id": "EL-02",
    "title": "Technical specifications must be disclosed",
    "law": "Consumer Protection Act 2019",
    "category": "electronics",
    "severity": "MEDIUM",
    "required_fields": ["specifications"]
},

{
    "id": "EL-03",
    "title": "Manufacturer / brand details must be disclosed",
    "law": "Legal Metrology Act",
    "category": "electronics",
    "severity": "MEDIUM",
    "required_fields": ["brand"]
},

{
    "id": "EL-04",
    "title": "Electrical safety / power rating must be mentioned",
    "law": "Legal Metrology Rules",
    "category": "electronics",
    "severity": "LOW",
    "required_fields": ["voltage"]
},

# =====================================================
# FOOD RULES (FSSAI)
# =====================================================

{
    "id": "FD-01",
    "title": "Expiry or best-before date must be disclosed",
    "law": "FSSAI Regulations",
    "category": "food",
    "severity": "HIGH",
    "required_fields": ["expiry"]
},

{
    "id": "FD-02",
    "title": "Ingredients list must be disclosed",
    "law": "FSSAI Regulations",
    "category": "food",
    "severity": "HIGH",
    "required_fields": ["ingredients"]
},

{
    "id": "FD-03",
    "title": "FSSAI license number must be displayed",
    "law": "FSSAI Act, 2006",
    "category": "food",
    "severity": "HIGH",
    "required_fields": ["fssai"]
},

{
    "id": "FD-04",
    "title": "Allergen warning must be disclosed",
    "law": "FSSAI Regulations",
    "category": "food",
    "severity": "MEDIUM",
    "required_fields": ["allergen"]
},

{
    "id": "FD-05",
    "title": "Net quantity must be mentioned",
    "law": "Legal Metrology (Packaged Commodities) Rules",
    "category": "food",
    "severity": "MEDIUM",
    "required_fields": ["quantity"]
},

# =====================================================
# HEALTH / MEDICAL RULES
# =====================================================

{
    "id": "HL-01",
    "title": "Medical disclaimer must be present",
    "law": "Drugs & Magic Remedies Act, 1954",
    "category": "health",
    "severity": "HIGH",
    "required_fields": ["disclaimer"]
},

{
    "id": "HL-02",
    "title": "Dosage or usage instructions must be provided",
    "law": "Drugs & Cosmetics Act, 1940",
    "category": "health",
    "severity": "HIGH",
    "required_fields": ["dosage"]
},

{
    "id": "HL-03",
    "title": "Guaranteed cure claims are prohibited",
    "law": "Drugs & Magic Remedies Act, 1954",
    "category": "health",
    "severity": "HIGH",
    "required_fields": ["guaranteed", "100%"]
},

{
    "id": "HL-04",
    "title": "Manufacturer details must be disclosed",
    "law": "Drugs & Cosmetics Act, 1940",
    "category": "health",
    "severity": "MEDIUM",
    "required_fields": ["manufacturer"]
}

]