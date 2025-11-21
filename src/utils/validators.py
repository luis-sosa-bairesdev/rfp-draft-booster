"""
Input validation functions using JSON schemas.

This module provides validation for:
- JSON imports (requirements, risks, drafts)
- RFP uploads (file validation)
- Individual data models (requirements, risks)
"""

import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

import jsonschema
from jsonschema import validate, ValidationError as JSONSchemaValidationError

from src.utils.schemas import (
    REQUIREMENT_SCHEMA,
    RISK_SCHEMA,
    DRAFT_SCHEMA,
    RFP_SCHEMA,
    REQUIREMENTS_LIST_SCHEMA,
    RISKS_LIST_SCHEMA
)
from src.utils.error_handler import ValidationError

logger = logging.getLogger(__name__)


# ============================================================================
# JSON Validation
# ============================================================================

def validate_json_import(
    data: Dict[str, Any],
    schema: Dict[str, Any]
) -> Tuple[bool, str]:
    """
    Validate imported JSON against schema.
    
    Args:
        data: JSON data to validate
        schema: JSON schema to validate against
    
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    try:
        validate(instance=data, schema=schema)
        logger.debug(f"JSON validation successful")
        return True, ""
    except JSONSchemaValidationError as e:
        # Build user-friendly error message
        path = ".".join(str(p) for p in e.path) if e.path else "root"
        error_msg = f"Validation error at '{path}': {e.message}"
        logger.warning(f"JSON validation failed: {error_msg}")
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected validation error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return False, error_msg


def validate_requirements_json(data: list) -> Tuple[bool, str]:
    """Validate requirements list JSON."""
    return validate_json_import(data, REQUIREMENTS_LIST_SCHEMA)


def validate_risks_json(data: list) -> Tuple[bool, str]:
    """Validate risks list JSON."""
    return validate_json_import(data, RISKS_LIST_SCHEMA)


def validate_draft_json(data: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate draft JSON."""
    return validate_json_import(data, DRAFT_SCHEMA)


def validate_rfp_json(data: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate RFP JSON."""
    return validate_json_import(data, RFP_SCHEMA)


# ============================================================================
# RFP Upload Validation
# ============================================================================

def validate_rfp_upload(
    file,
    title: str,
    client: str,
    deadline: Optional[datetime] = None
) -> Tuple[bool, str]:
    """
    Validate RFP upload inputs.
    
    Args:
        file: Uploaded file object (with .name, .size attributes)
        title: RFP title
        client: Client name
        deadline: Submission deadline (optional)
    
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    # File validation
    if not file:
        return False, "No file uploaded"
    
    if not hasattr(file, 'size'):
        return False, "Invalid file object"
    
    if file.size == 0:
        return False, "PDF file is empty (0 bytes)"
    
    if file.size > 50 * 1024 * 1024:  # 50MB
        size_mb = file.size / (1024 * 1024)
        return False, f"PDF file too large ({size_mb:.1f}MB). Maximum 50MB."
    
    # File type validation
    if hasattr(file, 'name'):
        if not file.name.lower().endswith('.pdf'):
            return False, f"Invalid file type. Only PDF files are supported."
    
    # Title validation
    if not title or title.strip() == "":
        return False, "RFP title is required"
    
    if len(title.strip()) < 5:
        return False, "RFP title must be at least 5 characters"
    
    if len(title) > 255:
        return False, "RFP title must be less than 255 characters"
    
    # Client validation
    if not client or client.strip() == "":
        return False, "Client name is required"
    
    if len(client.strip()) < 2:
        return False, "Client name must be at least 2 characters"
    
    if len(client) > 255:
        return False, "Client name must be less than 255 characters"
    
    # Deadline validation (optional)
    if deadline:
        if not isinstance(deadline, datetime):
            return False, "Deadline must be a valid datetime object"
        
        if deadline < datetime.now():
            return False, "Deadline must be in the future"
    
    return True, ""


# ============================================================================
# Individual Model Validation
# ============================================================================

def validate_requirement(req: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate a single requirement.
    
    Args:
        req: Requirement dictionary
    
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    # Description validation
    if not req.get("description") or req["description"].strip() == "":
        return False, "Description is required"
    
    if len(req["description"]) < 10:
        return False, "Description must be at least 10 characters"
    
    if len(req["description"]) > 1000:
        return False, "Description must be less than 1000 characters"
    
    # Category validation
    valid_categories = ["Technical", "Functional", "Timeline", "Budget", "Compliance"]
    if req.get("category") not in valid_categories:
        return False, f"Category must be one of: {', '.join(valid_categories)}"
    
    # Priority validation
    valid_priorities = ["Critical", "High", "Medium", "Low"]
    if req.get("priority") not in valid_priorities:
        return False, f"Priority must be one of: {', '.join(valid_priorities)}"
    
    # Confidence validation
    conf = req.get("confidence", 0.0)
    if not isinstance(conf, (int, float)):
        return False, "Confidence must be a number"
    
    if not (0.0 <= conf <= 1.0):
        return False, f"Confidence must be between 0.0 and 1.0, got {conf}"
    
    # Page number validation (optional)
    if "page_number" in req:
        page = req["page_number"]
        if not isinstance(page, int) or page < 1:
            return False, f"Page number must be a positive integer, got {page}"
    
    return True, ""


def validate_risk(risk: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate a single risk.
    
    Args:
        risk: Risk dictionary
    
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    # Clause text validation
    if not risk.get("clause_text") or risk["clause_text"].strip() == "":
        return False, "Clause text is required"
    
    if len(risk["clause_text"]) < 10:
        return False, "Clause text must be at least 10 characters"
    
    if len(risk["clause_text"]) > 2000:
        return False, "Clause text must be less than 2000 characters"
    
    # Category validation
    valid_categories = ["Legal", "Financial", "Timeline", "Technical", "Compliance"]
    if risk.get("category") not in valid_categories:
        return False, f"Category must be one of: {', '.join(valid_categories)}"
    
    # Severity validation
    valid_severities = ["Critical", "High", "Medium", "Low"]
    if risk.get("severity") not in valid_severities:
        return False, f"Severity must be one of: {', '.join(valid_severities)}"
    
    # Confidence validation
    conf = risk.get("confidence", 0.0)
    if not isinstance(conf, (int, float)):
        return False, "Confidence must be a number"
    
    if not (0.0 <= conf <= 1.0):
        return False, f"Confidence must be between 0.0 and 1.0, got {conf}"
    
    # Page number validation (optional)
    if "page_number" in risk:
        page = risk["page_number"]
        if not isinstance(page, int) or page < 1:
            return False, f"Page number must be a positive integer, got {page}"
    
    # Recommendation validation (optional)
    if "recommendation" in risk and risk["recommendation"]:
        if len(risk["recommendation"]) > 1000:
            return False, "Recommendation must be less than 1000 characters"
    
    # Alternative language validation (optional)
    if "alternative_language" in risk and risk["alternative_language"]:
        if len(risk["alternative_language"]) > 2000:
            return False, "Alternative language must be less than 2000 characters"
    
    return True, ""


# ============================================================================
# Batch Validation
# ============================================================================

def validate_requirements_batch(requirements: list) -> Tuple[int, list]:
    """
    Validate a batch of requirements.
    
    Args:
        requirements: List of requirement dictionaries
    
    Returns:
        Tuple of (valid_count: int, errors: list of tuples (index, error_msg))
    """
    valid_count = 0
    errors = []
    
    for idx, req in enumerate(requirements):
        is_valid, error_msg = validate_requirement(req)
        if is_valid:
            valid_count += 1
        else:
            errors.append((idx, error_msg))
    
    return valid_count, errors


def validate_risks_batch(risks: list) -> Tuple[int, list]:
    """
    Validate a batch of risks.
    
    Args:
        risks: List of risk dictionaries
    
    Returns:
        Tuple of (valid_count: int, errors: list of tuples (index, error_msg))
    """
    valid_count = 0
    errors = []
    
    for idx, risk in enumerate(risks):
        is_valid, error_msg = validate_risk(risk)
        if is_valid:
            valid_count += 1
        else:
            errors.append((idx, error_msg))
    
    return valid_count, errors

