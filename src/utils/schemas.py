"""
JSON schemas for data validation.

This module provides JSON schemas for all data models:
- Requirements
- Risks
- Drafts
- RFPs

Used for validating imported data and API responses.
"""

# ============================================================================
# Requirement Schema
# ============================================================================

REQUIREMENT_SCHEMA = {
    "type": "object",
    "required": ["description", "category", "priority", "confidence"],
    "properties": {
        "id": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100
        },
        "description": {
            "type": "string",
            "minLength": 10,
            "maxLength": 1000
        },
        "category": {
            "type": "string",
            "enum": ["Technical", "Functional", "Timeline", "Budget", "Compliance"]
        },
        "priority": {
            "type": "string",
            "enum": ["Critical", "High", "Medium", "Low"]
        },
        "confidence": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0
        },
        "page_number": {
            "type": "integer",
            "minimum": 1
        },
        "verified": {
            "type": "boolean"
        },
        "source": {
            "type": "string",
            "enum": ["AI", "Manual", "Pattern"]
        }
    }
}


# ============================================================================
# Risk Schema
# ============================================================================

RISK_SCHEMA = {
    "type": "object",
    "required": ["clause_text", "category", "severity", "confidence"],
    "properties": {
        "id": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100
        },
        "clause_text": {
            "type": "string",
            "minLength": 10,
            "maxLength": 2000
        },
        "category": {
            "type": "string",
            "enum": ["Legal", "Financial", "Timeline", "Technical", "Compliance"]
        },
        "severity": {
            "type": "string",
            "enum": ["Critical", "High", "Medium", "Low"]
        },
        "confidence": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0
        },
        "page_number": {
            "type": "integer",
            "minimum": 1
        },
        "recommendation": {
            "type": "string",
            "maxLength": 1000
        },
        "alternative_language": {
            "type": "string",
            "maxLength": 2000
        },
        "acknowledged": {
            "type": "boolean"
        }
    }
}


# ============================================================================
# Draft Schema
# ============================================================================

DRAFT_SCHEMA = {
    "type": "object",
    "required": ["id", "rfp_id", "content", "status"],
    "properties": {
        "id": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100
        },
        "rfp_id": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100
        },
        "content": {
            "type": "string",
            "minLength": 10
        },
        "status": {
            "type": "string",
            "enum": ["Draft", "Review", "Approved", "Submitted"]
        },
        "generated_by": {
            "type": "string",
            "enum": ["AI", "Manual"]
        },
        "word_count": {
            "type": "integer",
            "minimum": 0
        },
        "section_count": {
            "type": "integer",
            "minimum": 0
        },
        "completeness_score": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0
        }
    }
}


# ============================================================================
# RFP Schema
# ============================================================================

RFP_SCHEMA = {
    "type": "object",
    "required": ["id", "file_name", "client_name"],
    "properties": {
        "id": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100
        },
        "file_name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 255
        },
        "client_name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 255
        },
        "extracted_text": {
            "type": "string"
        },
        "page_count": {
            "type": "integer",
            "minimum": 1
        },
        "deadline": {
            "type": "string",
            "format": "date-time"
        },
        "upload_date": {
            "type": "string",
            "format": "date-time"
        }
    }
}


# ============================================================================
# Collection Schemas
# ============================================================================

REQUIREMENTS_LIST_SCHEMA = {
    "type": "array",
    "items": REQUIREMENT_SCHEMA,
    "minItems": 0
}

RISKS_LIST_SCHEMA = {
    "type": "array",
    "items": RISK_SCHEMA,
    "minItems": 0
}

