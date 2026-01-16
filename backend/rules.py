RULES = [

# =====================================================
# GENERAL E-COMMERCE RULES (15)
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
    "title": "Product price must be clearly displayed",
    "law": "E-Commerce Rules 2020 – Rule 4(2)(b)",
    "category": "all",
    "severity": "HIGH",
    "required_fields": ["price"]
},

{
    "id": "EC-05",
    "title": "All taxes and charges must be disclosed",
    "law": "E-Commerce Rules 2020 – Rule 4(2)(c)",
    "category": "all",
    "severity": "MEDIUM",
    "required_fields": ["charges"]
},

{
    "id": "EC-06",
    "title": "Return and refund policy must be available",
    "law": "E-Commerce Rules 2020 – Rule 4(2)(d)",
    "category": "all",
    "severity": "HIGH",
    "required_fields": ["returns"]
},

{
    "id": "EC-07",
    "title": "Delivery and shipping details must be provided",
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
    "title": "Grievance officer details must be disclosed",
    "law": "E-Commerce Rules 2020 – Rule 4(5)",
    "category": "all",
    "severity": "HIGH",
    "required_fields": ["grievance"]
},

{
    "id": "EC-10",
    "title": "Product description must not be misleading",
    "law": "Consumer Protection Act 2019 – Section 2(28)",
    "category": "all",
    "severity": "HIGH",
    "required_fields": ["description"]
},

{
    "id": "EC-11",
    "title": "Ratings and reviews must not be manipulated",
    "law": "E-Commerce Rules 2020 – Rule 5(3)",
    "category": "all",
    "severity": "MEDIUM",
    "required_fields": ["reviews"]
},

{
    "id": "EC-12",
    "title": "Product title must be clearly mentioned",
    "law": "Consumer Protection Act 2019",
    "category": "all",
    "severity": "LOW",
    "required_fields": ["title"]
},

{
    "id": "EC-13",
    "title": "Brand or manufacturer name must be disclosed",
    "law": "Legal Metrology Act",
    "category": "all",
    "severity": "LOW",
    "required_fields": ["brand"]
},

{
    "id": "EC-14",
    "title": "Net quantity must be mentioned",
    "law": "Legal Metrology Rules",
    "category": "all",
    "severity": "MEDIUM",
    "required_fields": ["quantity"]
},

{
    "id": "EC-15",
    "title": "Product images must be provided",
    "law": "Consumer Protection Act 2019",
    "category": "all",
    "severity": "LOW",
    "required_fields": ["images"]
},

# =====================================================
# ELECTRONICS RULES (8)
# =====================================================

{
    "id": "EL-01",
    "title": "Warranty or guarantee must be disclosed",
    "law": "E-Commerce Rules 2020 – Rule 5(3)",
    "category": "electronics",
    "severity": "HIGH",
    "required_fields": ["warranty"]
},

{
    "id": "EL-02",
    "title": "Technical specifications must be provided",
    "law": "Consumer Protection Act 2019",
    "category": "electronics",
    "severity": "MEDIUM",
    "required_fields": ["specifications"]
},

{
    "id": "EL-03",
    "title": "Brand or manufacturer must be disclosed",
    "law": "Legal Metrology Act",
    "category": "electronics",
    "severity": "MEDIUM",
    "required_fields": ["brand"]
},

{
    "id": "EL-04",
    "title": "Power rating or voltage details must be mentioned",
    "law": "Legal Metrology Rules",
    "category": "electronics",
    "severity": "LOW",
    "required_fields": ["voltage"]
},

{
    "id": "EL-05",
    "title": "Safety instructions or warnings must be provided",
    "law": "Consumer Protection Act 2019",
    "category": "electronics",
    "severity": "MEDIUM",
    "required_fields": ["safety"]
},

{
    "id": "EL-06",
    "title": "Energy efficiency rating must be disclosed if applicable",
    "law": "BEE Guidelines",
    "category": "electronics",
    "severity": "LOW",
    "required_fields": ["energy_rating"]
},

{
    "id": "EL-07",
    "title": "Model number must be disclosed",
    "law": "Consumer Protection Act 2019",
    "category": "electronics",
    "severity": "LOW",
    "required_fields": ["model_number"]
},

{
    "id": "EL-08",
    "title": "Compatibility details must be provided",
    "law": "Consumer Protection Act 2019",
    "category": "electronics",
    "severity": "LOW",
    "required_fields": ["compatibility"]
},

# =====================================================
# FOOD RULES (10)
# =====================================================

{
    "id": "FD-01",
    "title": "Expiry or best-before date must be mentioned",
    "law": "FSSAI Labelling Regulations",
    "category": "food",
    "severity": "HIGH",
    "required_fields": ["expiry"]
},

{
    "id": "FD-02",
    "title": "Ingredients list must be disclosed",
    "law": "FSSAI Labelling Regulations",
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
    "title": "Allergen information must be disclosed",
    "law": "FSSAI Regulations",
    "category": "food",
    "severity": "MEDIUM",
    "required_fields": ["allergen"]
},

{
    "id": "FD-05",
    "title": "Vegetarian or non-vegetarian symbol must be shown",
    "law": "FSSAI Regulations",
    "category": "food",
    "severity": "MEDIUM",
    "required_fields": ["veg_nonveg"]
},

{
    "id": "FD-06",
    "title": "Net quantity or weight must be mentioned",
    "law": "Legal Metrology Rules",
    "category": "food",
    "severity": "MEDIUM",
    "required_fields": ["quantity"]
},

{
    "id": "FD-07",
    "title": "Storage instructions must be mentioned",
    "law": "FSSAI Regulations",
    "category": "food",
    "severity": "LOW",
    "required_fields": ["storage"]
},

{
    "id": "FD-08",
    "title": "Manufacturer or packer details must be disclosed",
    "law": "FSSAI Regulations",
    "category": "food",
    "severity": "MEDIUM",
    "required_fields": ["manufacturer"]
},

{
    "id": "FD-09",
    "title": "Nutritional information must be provided",
    "law": "FSSAI Regulations",
    "category": "food",
    "severity": "LOW",
    "required_fields": ["nutrition"]
},

{
    "id": "FD-10",
    "title": "No false health claims allowed on food products",
    "law": "Consumer Protection Act 2019",
    "category": "food",
    "severity": "HIGH",
    "required_fields": ["description"]
},

# =====================================================
# HEALTH RULES (10)
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
    "title": "Guaranteed cure or 100% result claims are prohibited",
    "law": "Drugs & Magic Remedies Act, 1954",
    "category": "health",
    "severity": "HIGH",
    "required_fields": ["guaranteed", "100%"]
},

{
    "id": "HL-04",
    "title": "Disease cure or prevention claims must not be misleading",
    "law": "Drugs & Magic Remedies Act, 1954",
    "category": "health",
    "severity": "HIGH",
    "required_fields": ["description"]
},

{
    "id": "HL-05",
    "title": "Manufacturer or marketer details must be disclosed",
    "law": "Drugs & Cosmetics Act, 1940",
    "category": "health",
    "severity": "MEDIUM",
    "required_fields": ["manufacturer"]
},

{
    "id": "HL-06",
    "title": "Intended use or purpose must be mentioned",
    "law": "Consumer Protection Act 2019",
    "category": "health",
    "severity": "MEDIUM",
    "required_fields": ["usage"]
},

{
    "id": "HL-07",
    "title": "Warnings or side effects must be disclosed",
    "law": "Drugs & Cosmetics Act, 1940",
    "category": "health",
    "severity": "MEDIUM",
    "required_fields": ["warning"]
},

{
    "id": "HL-08",
    "title": "Age restriction must be disclosed where applicable",
    "law": "Drugs & Cosmetics Act, 1940",
    "category": "health",
    "severity": "LOW",
    "required_fields": ["age_limit"]
},

{
    "id": "HL-09",
    "title": "Prescription-only products must indicate prescription requirement",
    "law": "Drugs & Cosmetics Act, 1940",
    "category": "health",
    "severity": "HIGH",
    "required_fields": ["prescription_required"]
},

{
    "id": "HL-10",
    "title": "Misleading medical testimonials are prohibited",
    "law": "Consumer Protection Act 2019 – Section 2(28)",
    "category": "health",
    "severity": "HIGH",
    "required_fields": ["reviews"]
}

]
