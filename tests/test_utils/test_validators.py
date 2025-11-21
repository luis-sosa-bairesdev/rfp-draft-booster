"""
Unit tests for validators module.

Tests JSON schema validation and input validation functions.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock

from src.utils.validators import (
    validate_json_import,
    validate_requirements_json,
    validate_risks_json,
    validate_draft_json,
    validate_rfp_json,
    validate_rfp_upload,
    validate_requirement,
    validate_risk,
    validate_requirements_batch,
    validate_risks_batch
)
from src.utils.schemas import (
    REQUIREMENT_SCHEMA,
    RISK_SCHEMA,
    DRAFT_SCHEMA,
    RFP_SCHEMA
)


class TestJSONValidation:
    """Test JSON schema validation."""
    
    def test_validate_json_import_valid_requirement(self):
        """Test valid requirement JSON."""
        data = {
            "description": "Cloud infrastructure with 99.9% uptime",
            "category": "Technical",
            "priority": "Critical",
            "confidence": 0.95
        }
        
        is_valid, error = validate_json_import(data, REQUIREMENT_SCHEMA)
        assert is_valid
        assert error == ""
    
    def test_validate_json_import_invalid_requirement(self):
        """Test invalid requirement JSON (missing required field)."""
        data = {
            "description": "Test requirement",
            "category": "Technical"
            # Missing required fields: priority, confidence
        }
        
        is_valid, error = validate_json_import(data, REQUIREMENT_SCHEMA)
        assert not is_valid
        assert "required" in error.lower() or "property" in error.lower()
    
    def test_validate_json_import_invalid_type(self):
        """Test invalid field type."""
        data = {
            "description": "Test requirement",
            "category": "Technical",
            "priority": "High",
            "confidence": "invalid"  # Should be number
        }
        
        is_valid, error = validate_json_import(data, REQUIREMENT_SCHEMA)
        assert not is_valid
        assert "confidence" in error.lower() or "type" in error.lower()
    
    def test_validate_json_import_invalid_enum(self):
        """Test invalid enum value."""
        data = {
            "description": "Test requirement",
            "category": "InvalidCategory",  # Not in enum
            "priority": "High",
            "confidence": 0.9
        }
        
        is_valid, error = validate_json_import(data, REQUIREMENT_SCHEMA)
        assert not is_valid
        assert "category" in error.lower() or "enum" in error.lower()
    
    def test_validate_requirements_json_valid_list(self):
        """Test valid requirements list."""
        data = [
            {
                "description": "Requirement 1",
                "category": "Technical",
                "priority": "High",
                "confidence": 0.9
            },
            {
                "description": "Requirement 2",
                "category": "Functional",
                "priority": "Medium",
                "confidence": 0.85
            }
        ]
        
        is_valid, error = validate_requirements_json(data)
        assert is_valid
        assert error == ""
    
    def test_validate_requirements_json_empty_list(self):
        """Test empty requirements list."""
        is_valid, error = validate_requirements_json([])
        assert is_valid  # Empty list is valid
    
    def test_validate_risks_json_valid(self):
        """Test valid risks list."""
        data = [
            {
                "clause_text": "Unlimited liability for data breaches",
                "category": "Legal",
                "severity": "High",
                "confidence": 0.92
            }
        ]
        
        is_valid, error = validate_risks_json(data)
        assert is_valid
    
    def test_validate_draft_json_valid(self):
        """Test valid draft JSON."""
        data = {
            "id": "draft-123",
            "rfp_id": "rfp-456",
            "content": "Draft content here",
            "status": "Draft"
        }
        
        is_valid, error = validate_draft_json(data)
        assert is_valid
    
    def test_validate_rfp_json_valid(self):
        """Test valid RFP JSON."""
        data = {
            "id": "rfp-123",
            "file_name": "test.pdf",
            "client_name": "Acme Corp"
        }
        
        is_valid, error = validate_rfp_json(data)
        assert is_valid
    
    def test_validate_json_import_unexpected_error(self):
        """Test unexpected error during validation."""
        # Passing None should trigger an unexpected error
        is_valid, error = validate_json_import(None, REQUIREMENT_SCHEMA)
        assert not is_valid
        assert "unexpected" in error.lower() or "error" in error.lower()


class TestRFPUploadValidation:
    """Test RFP upload validation."""
    
    def test_validate_rfp_upload_valid(self):
        """Test valid RFP upload."""
        file = Mock()
        file.name = "test.pdf"
        file.size = 1024 * 1024  # 1MB
        
        is_valid, error = validate_rfp_upload(
            file=file,
            title="Test RFP",
            client="Test Client",
            deadline=datetime.now() + timedelta(days=30)
        )
        
        assert is_valid
        assert error == ""
    
    def test_validate_rfp_upload_no_file(self):
        """Test upload with no file."""
        is_valid, error = validate_rfp_upload(
            file=None,
            title="Test RFP",
            client="Test Client"
        )
        
        assert not is_valid
        assert "no file" in error.lower()
    
    def test_validate_rfp_upload_empty_file(self):
        """Test upload with empty file."""
        file = Mock()
        file.name = "test.pdf"
        file.size = 0
        
        is_valid, error = validate_rfp_upload(
            file=file,
            title="Test RFP",
            client="Test Client"
        )
        
        assert not is_valid
        assert "empty" in error.lower()
    
    def test_validate_rfp_upload_file_too_large(self):
        """Test upload with file > 50MB."""
        file = Mock()
        file.name = "test.pdf"
        file.size = 60 * 1024 * 1024  # 60MB
        
        is_valid, error = validate_rfp_upload(
            file=file,
            title="Test RFP",
            client="Test Client"
        )
        
        assert not is_valid
        assert "large" in error.lower() or "50mb" in error.lower()
    
    def test_validate_rfp_upload_invalid_file_type(self):
        """Test upload with non-PDF file."""
        file = Mock()
        file.name = "test.docx"
        file.size = 1024
        
        is_valid, error = validate_rfp_upload(
            file=file,
            title="Test RFP",
            client="Test Client"
        )
        
        assert not is_valid
        assert "pdf" in error.lower() or "type" in error.lower()
    
    def test_validate_rfp_upload_empty_title(self):
        """Test upload with empty title."""
        file = Mock()
        file.name = "test.pdf"
        file.size = 1024
        
        is_valid, error = validate_rfp_upload(
            file=file,
            title="",
            client="Test Client"
        )
        
        assert not is_valid
        assert "title" in error.lower()
    
    def test_validate_rfp_upload_short_title(self):
        """Test upload with title < 5 chars."""
        file = Mock()
        file.name = "test.pdf"
        file.size = 1024
        
        is_valid, error = validate_rfp_upload(
            file=file,
            title="ab",
            client="Test Client"
        )
        
        assert not is_valid
        assert "5 character" in error.lower()
    
    def test_validate_rfp_upload_long_title(self):
        """Test upload with title > 255 chars."""
        file = Mock()
        file.name = "test.pdf"
        file.size = 1024
        
        is_valid, error = validate_rfp_upload(
            file=file,
            title="x" * 300,
            client="Test Client"
        )
        
        assert not is_valid
        assert "255" in error
    
    def test_validate_rfp_upload_empty_client(self):
        """Test upload with empty client name."""
        file = Mock()
        file.name = "test.pdf"
        file.size = 1024
        
        is_valid, error = validate_rfp_upload(
            file=file,
            title="Test RFP",
            client=""
        )
        
        assert not is_valid
        assert "client" in error.lower()
    
    def test_validate_rfp_upload_short_client(self):
        """Test upload with client name < 2 chars."""
        file = Mock()
        file.name = "test.pdf"
        file.size = 1024
        
        is_valid, error = validate_rfp_upload(
            file=file,
            title="Test RFP",
            client="A"
        )
        
        assert not is_valid
        assert "2 character" in error.lower()
    
    def test_validate_rfp_upload_past_deadline(self):
        """Test upload with deadline in the past."""
        file = Mock()
        file.name = "test.pdf"
        file.size = 1024
        
        is_valid, error = validate_rfp_upload(
            file=file,
            title="Test RFP",
            client="Test Client",
            deadline=datetime.now() - timedelta(days=1)
        )
        
        assert not is_valid
        assert "future" in error.lower()
    
    def test_validate_rfp_upload_invalid_deadline_type(self):
        """Test upload with invalid deadline type."""
        file = Mock()
        file.name = "test.pdf"
        file.size = 1024
        
        is_valid, error = validate_rfp_upload(
            file=file,
            title="Test RFP",
            client="Test Client",
            deadline="invalid"
        )
        
        assert not is_valid
        assert "datetime" in error.lower()
    
    def test_validate_rfp_upload_no_deadline(self):
        """Test upload without deadline (optional)."""
        file = Mock()
        file.name = "test.pdf"
        file.size = 1024
        
        is_valid, error = validate_rfp_upload(
            file=file,
            title="Test RFP",
            client="Test Client",
            deadline=None
        )
        
        assert is_valid  # Deadline is optional
    
    def test_validate_rfp_upload_invalid_file_object(self):
        """Test upload with file object missing size attribute."""
        file = Mock(spec=[])  # No attributes
        
        is_valid, error = validate_rfp_upload(
            file=file,
            title="Test RFP",
            client="Test Client"
        )
        
        assert not is_valid
        assert "invalid file" in error.lower() or "file object" in error.lower()
    
    def test_validate_rfp_upload_whitespace_title(self):
        """Test upload with whitespace-only title."""
        file = Mock()
        file.name = "test.pdf"
        file.size = 1024
        
        is_valid, error = validate_rfp_upload(
            file=file,
            title="   ",
            client="Test Client"
        )
        
        assert not is_valid
        assert "title" in error.lower()
    
    def test_validate_rfp_upload_whitespace_client(self):
        """Test upload with whitespace-only client."""
        file = Mock()
        file.name = "test.pdf"
        file.size = 1024
        
        is_valid, error = validate_rfp_upload(
            file=file,
            title="Test RFP",
            client="   "
        )
        
        assert not is_valid
        assert "client" in error.lower()


class TestRequirementValidation:
    """Test individual requirement validation."""
    
    def test_validate_requirement_valid(self):
        """Test valid requirement."""
        req = {
            "description": "Cloud infrastructure with 99.9% uptime SLA",
            "category": "Technical",
            "priority": "Critical",
            "confidence": 0.95
        }
        
        is_valid, error = validate_requirement(req)
        assert is_valid
        assert error == ""
    
    def test_validate_requirement_empty_description(self):
        """Test requirement with empty description."""
        req = {
            "description": "",
            "category": "Technical",
            "priority": "High",
            "confidence": 0.9
        }
        
        is_valid, error = validate_requirement(req)
        assert not is_valid
        assert "description" in error.lower()
    
    def test_validate_requirement_short_description(self):
        """Test requirement with description < 10 chars."""
        req = {
            "description": "Short",
            "category": "Technical",
            "priority": "High",
            "confidence": 0.9
        }
        
        is_valid, error = validate_requirement(req)
        assert not is_valid
        assert "10 character" in error.lower()
    
    def test_validate_requirement_long_description(self):
        """Test requirement with description > 1000 chars."""
        req = {
            "description": "x" * 1100,
            "category": "Technical",
            "priority": "High",
            "confidence": 0.9
        }
        
        is_valid, error = validate_requirement(req)
        assert not is_valid
        assert "1000" in error
    
    def test_validate_requirement_invalid_category(self):
        """Test requirement with invalid category."""
        req = {
            "description": "Test requirement description here",
            "category": "InvalidCategory",
            "priority": "High",
            "confidence": 0.9
        }
        
        is_valid, error = validate_requirement(req)
        assert not is_valid
        assert "category" in error.lower()
    
    def test_validate_requirement_invalid_priority(self):
        """Test requirement with invalid priority."""
        req = {
            "description": "Test requirement description here",
            "category": "Technical",
            "priority": "InvalidPriority",
            "confidence": 0.9
        }
        
        is_valid, error = validate_requirement(req)
        assert not is_valid
        assert "priority" in error.lower()
    
    def test_validate_requirement_invalid_confidence_type(self):
        """Test requirement with non-numeric confidence."""
        req = {
            "description": "Test requirement description here",
            "category": "Technical",
            "priority": "High",
            "confidence": "invalid"
        }
        
        is_valid, error = validate_requirement(req)
        assert not is_valid
        assert "confidence" in error.lower() and "number" in error.lower()
    
    def test_validate_requirement_confidence_too_low(self):
        """Test requirement with confidence < 0."""
        req = {
            "description": "Test requirement description here",
            "category": "Technical",
            "priority": "High",
            "confidence": -0.1
        }
        
        is_valid, error = validate_requirement(req)
        assert not is_valid
        assert "0.0 and 1.0" in error
    
    def test_validate_requirement_confidence_too_high(self):
        """Test requirement with confidence > 1."""
        req = {
            "description": "Test requirement description here",
            "category": "Technical",
            "priority": "High",
            "confidence": 1.5
        }
        
        is_valid, error = validate_requirement(req)
        assert not is_valid
        assert "0.0 and 1.0" in error
    
    def test_validate_requirement_invalid_page_number(self):
        """Test requirement with invalid page number."""
        req = {
            "description": "Test requirement description here",
            "category": "Technical",
            "priority": "High",
            "confidence": 0.9,
            "page_number": 0
        }
        
        is_valid, error = validate_requirement(req)
        assert not is_valid
        assert "page number" in error.lower()


class TestRiskValidation:
    """Test individual risk validation."""
    
    def test_validate_risk_valid(self):
        """Test valid risk."""
        risk = {
            "clause_text": "Unlimited liability for data breaches",
            "category": "Legal",
            "severity": "High",
            "confidence": 0.92
        }
        
        is_valid, error = validate_risk(risk)
        assert is_valid
        assert error == ""
    
    def test_validate_risk_empty_clause(self):
        """Test risk with empty clause text."""
        risk = {
            "clause_text": "",
            "category": "Legal",
            "severity": "High",
            "confidence": 0.9
        }
        
        is_valid, error = validate_risk(risk)
        assert not is_valid
        assert "clause" in error.lower()
    
    def test_validate_risk_short_clause(self):
        """Test risk with clause < 10 chars."""
        risk = {
            "clause_text": "Short",
            "category": "Legal",
            "severity": "High",
            "confidence": 0.9
        }
        
        is_valid, error = validate_risk(risk)
        assert not is_valid
        assert "10 character" in error.lower()
    
    def test_validate_risk_long_clause(self):
        """Test risk with clause > 2000 chars."""
        risk = {
            "clause_text": "x" * 2100,
            "category": "Legal",
            "severity": "High",
            "confidence": 0.9
        }
        
        is_valid, error = validate_risk(risk)
        assert not is_valid
        assert "2000" in error
    
    def test_validate_risk_invalid_category(self):
        """Test risk with invalid category."""
        risk = {
            "clause_text": "Test clause text here with enough length",
            "category": "InvalidCategory",
            "severity": "High",
            "confidence": 0.9
        }
        
        is_valid, error = validate_risk(risk)
        assert not is_valid
        assert "category" in error.lower()
    
    def test_validate_risk_invalid_severity(self):
        """Test risk with invalid severity."""
        risk = {
            "clause_text": "Test clause text here with enough length",
            "category": "Legal",
            "severity": "InvalidSeverity",
            "confidence": 0.9
        }
        
        is_valid, error = validate_risk(risk)
        assert not is_valid
        assert "severity" in error.lower()
    
    def test_validate_risk_long_recommendation(self):
        """Test risk with recommendation > 1000 chars."""
        risk = {
            "clause_text": "Test clause text here with enough length",
            "category": "Legal",
            "severity": "High",
            "confidence": 0.9,
            "recommendation": "x" * 1100
        }
        
        is_valid, error = validate_risk(risk)
        assert not is_valid
        assert "recommendation" in error.lower() and "1000" in error
    
    def test_validate_risk_long_alternative(self):
        """Test risk with alternative language > 2000 chars."""
        risk = {
            "clause_text": "Test clause text here with enough length",
            "category": "Legal",
            "severity": "High",
            "confidence": 0.9,
            "alternative_language": "x" * 2100
        }
        
        is_valid, error = validate_risk(risk)
        assert not is_valid
        assert "alternative" in error.lower() and "2000" in error
    
    def test_validate_risk_with_empty_recommendation(self):
        """Test risk with empty recommendation (should be ignored)."""
        risk = {
            "clause_text": "Test clause text here with enough length",
            "category": "Legal",
            "severity": "High",
            "confidence": 0.9,
            "recommendation": ""
        }
        
        is_valid, error = validate_risk(risk)
        assert is_valid  # Empty recommendation is OK
    
    def test_validate_risk_with_empty_alternative(self):
        """Test risk with empty alternative language (should be ignored)."""
        risk = {
            "clause_text": "Test clause text here with enough length",
            "category": "Legal",
            "severity": "High",
            "confidence": 0.9,
            "alternative_language": ""
        }
        
        is_valid, error = validate_risk(risk)
        assert is_valid  # Empty alternative is OK
    
    def test_validate_risk_invalid_confidence_type(self):
        """Test risk with non-numeric confidence."""
        risk = {
            "clause_text": "Test clause text here with enough length",
            "category": "Legal",
            "severity": "High",
            "confidence": "invalid"
        }
        
        is_valid, error = validate_risk(risk)
        assert not is_valid
        assert "confidence" in error.lower() and "number" in error.lower()
    
    def test_validate_risk_confidence_out_of_range(self):
        """Test risk with confidence out of range."""
        risk = {
            "clause_text": "Test clause text here with enough length",
            "category": "Legal",
            "severity": "High",
            "confidence": 1.5
        }
        
        is_valid, error = validate_risk(risk)
        assert not is_valid
        assert "0.0 and 1.0" in error
    
    def test_validate_risk_invalid_page_number(self):
        """Test risk with invalid page number."""
        risk = {
            "clause_text": "Test clause text here with enough length",
            "category": "Legal",
            "severity": "High",
            "confidence": 0.9,
            "page_number": -1
        }
        
        is_valid, error = validate_risk(risk)
        assert not is_valid
        assert "page number" in error.lower()


class TestBatchValidation:
    """Test batch validation functions."""
    
    def test_validate_requirements_batch_all_valid(self):
        """Test batch validation with all valid requirements."""
        requirements = [
            {
                "description": "Requirement 1 description",
                "category": "Technical",
                "priority": "High",
                "confidence": 0.9
            },
            {
                "description": "Requirement 2 description",
                "category": "Functional",
                "priority": "Medium",
                "confidence": 0.85
            }
        ]
        
        valid_count, errors = validate_requirements_batch(requirements)
        assert valid_count == 2
        assert len(errors) == 0
    
    def test_validate_requirements_batch_some_invalid(self):
        """Test batch validation with some invalid requirements."""
        requirements = [
            {
                "description": "Valid requirement description",
                "category": "Technical",
                "priority": "High",
                "confidence": 0.9
            },
            {
                "description": "Short",  # Invalid
                "category": "Functional",
                "priority": "Medium",
                "confidence": 0.85
            },
            {
                "description": "Another valid requirement",
                "category": "Budget",
                "priority": "Low",
                "confidence": 0.8
            }
        ]
        
        valid_count, errors = validate_requirements_batch(requirements)
        assert valid_count == 2
        assert len(errors) == 1
        assert errors[0][0] == 1  # Index of invalid requirement
    
    def test_validate_risks_batch_all_valid(self):
        """Test batch validation with all valid risks."""
        risks = [
            {
                "clause_text": "Risk clause 1 with enough text",
                "category": "Legal",
                "severity": "High",
                "confidence": 0.9
            },
            {
                "clause_text": "Risk clause 2 with enough text",
                "category": "Financial",
                "severity": "Medium",
                "confidence": 0.85
            }
        ]
        
        valid_count, errors = validate_risks_batch(risks)
        assert valid_count == 2
        assert len(errors) == 0
    
    def test_validate_risks_batch_some_invalid(self):
        """Test batch validation with some invalid risks."""
        risks = [
            {
                "clause_text": "Valid risk clause with enough text",
                "category": "Legal",
                "severity": "High",
                "confidence": 0.9
            },
            {
                "clause_text": "Short",  # Invalid
                "category": "Financial",
                "severity": "Medium",
                "confidence": 0.85
            }
        ]
        
        valid_count, errors = validate_risks_batch(risks)
        assert valid_count == 1
        assert len(errors) == 1
        assert errors[0][0] == 1  # Index of invalid risk

