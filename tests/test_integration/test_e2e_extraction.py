"""
End-to-end integration tests for requirement extraction flow.

Tests the complete workflow:
1. Upload PDF
2. Validate file
3. Extract text from PDF
4. Extract requirements using LLM
5. Verify and filter results
6. Save to storage

This ensures all components work together correctly.
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from models import RFP, RFPStatus, Requirement, RequirementCategory, RequirementPriority
from services.file_validator import FileValidator
from services.pdf_processor import PDFProcessor
from services.storage_manager import StorageManager
from services.llm_client import LLMClient
from services.requirement_extractor import RequirementExtractor


class TestEndToEndRequirementExtraction:
    """End-to-end tests for complete requirement extraction flow."""
    
    @patch('services.llm_client.genai')
    @patch('services.pdf_processor.PyPDF2.PdfReader')
    def test_complete_extraction_workflow(self, mock_pdf_reader, mock_genai):
        """
        Test complete workflow from PDF upload to requirement extraction.
        
        Flow:
        1. Create RFP
        2. Validate PDF file
        3. Extract text from PDF
        4. Extract requirements using LLM
        5. Verify results
        """
        # Setup: Create temp directory for storage
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock PDF file
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                f.write(b"%PDF-1.4\nMock PDF content")
                pdf_path = f.name
            
            try:
                # Step 1: Create RFP
                rfp = RFP(
                    id="test-rfp-001",
                    filename="sample_rfp.pdf",
                    uploaded_at=datetime.now()
                )
                assert rfp.status == RFPStatus.UPLOADED
                
                # Step 2: Validate file
                validator = FileValidator()
                validator.validate_file_size(pdf_path, max_size_mb=50)
                validator.validate_file_type(pdf_path, allowed_types=["pdf"])
                
                # Step 3: Extract text from PDF
                mock_page1 = Mock()
                mock_page1.extract_text.return_value = """
                REQUIREMENTS FOR PROPOSAL
                
                1. Technical Requirements:
                   - System must support 99.9% uptime SLA
                   - AWS cloud infrastructure required
                   - PostgreSQL database with replication
                
                2. Timeline:
                   - Project completion within 90 days from kickoff
                   - Weekly sprint reviews
                
                3. Budget:
                   - Total cost not to exceed $750,000 USD
                   - Payment terms: Net 30 days
                
                4. Compliance:
                   - Must be HIPAA compliant
                   - SOC 2 Type II certification required
                """
                
                mock_pdf_reader.return_value.pages = [mock_page1]
                
                processor = PDFProcessor()
                extracted_text, pages = processor.extract_text(pdf_path)
                
                rfp.extracted_text = extracted_text
                rfp.extracted_text_by_page = pages
                rfp.status = RFPStatus.PROCESSED
                
                assert len(extracted_text) > 0
                assert "99.9% uptime" in extracted_text
                
                # Step 4: Extract requirements using LLM (mocked)
                mock_llm_response = Mock()
                mock_llm_response.text = """
                [
                  {
                    "description": "System must support 99.9% uptime SLA",
                    "category": "technical",
                    "priority": "critical",
                    "confidence": 0.95,
                    "page_number": 1
                  },
                  {
                    "description": "AWS cloud infrastructure required",
                    "category": "technical",
                    "priority": "high",
                    "confidence": 0.90,
                    "page_number": 1
                  },
                  {
                    "description": "PostgreSQL database with replication",
                    "category": "technical",
                    "priority": "high",
                    "confidence": 0.88,
                    "page_number": 1
                  },
                  {
                    "description": "Project completion within 90 days from kickoff",
                    "category": "timeline",
                    "priority": "high",
                    "confidence": 0.92,
                    "page_number": 1
                  },
                  {
                    "description": "Total cost not to exceed $750,000 USD",
                    "category": "budget",
                    "priority": "critical",
                    "confidence": 0.95,
                    "page_number": 1
                  },
                  {
                    "description": "Must be HIPAA compliant",
                    "category": "compliance",
                    "priority": "critical",
                    "confidence": 0.98,
                    "page_number": 1
                  },
                  {
                    "description": "SOC 2 Type II certification required",
                    "category": "compliance",
                    "priority": "critical",
                    "confidence": 0.95,
                    "page_number": 1
                  }
                ]
                """
                
                mock_model = Mock()
                mock_model.generate_content.return_value = mock_llm_response
                mock_genai.GenerativeModel.return_value = mock_model
                mock_genai.configure = Mock()
                
                with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
                    llm_client = LLMClient(provider="gemini")
                    extractor = RequirementExtractor(llm_client=llm_client, min_confidence=0.8)
                    
                    requirements = extractor.extract_from_rfp(rfp)
                
                # Step 5: Verify results
                assert len(requirements) > 0
                
                # Check we have requirements from all categories
                categories = {req.category for req in requirements}
                assert RequirementCategory.TECHNICAL in categories
                assert RequirementCategory.TIMELINE in categories
                assert RequirementCategory.BUDGET in categories
                assert RequirementCategory.COMPLIANCE in categories
                
                # Check priorities
                priorities = {req.priority for req in requirements}
                assert RequirementPriority.CRITICAL in priorities
                assert RequirementPriority.HIGH in priorities
                
                # Check confidence filtering (min 0.8)
                assert all(req.confidence >= 0.8 for req in requirements)
                
                # Check specific requirements
                uptime_req = next((r for r in requirements if "99.9% uptime" in r.description), None)
                assert uptime_req is not None
                assert uptime_req.category == RequirementCategory.TECHNICAL
                assert uptime_req.priority == RequirementPriority.CRITICAL
                
                budget_req = next((r for r in requirements if "$750,000" in r.description), None)
                assert budget_req is not None
                assert budget_req.category == RequirementCategory.BUDGET
                
                hipaa_req = next((r for r in requirements if "HIPAA" in r.description), None)
                assert hipaa_req is not None
                assert hipaa_req.category == RequirementCategory.COMPLIANCE
                
                # Step 6: Save to storage
                storage = StorageManager(base_path=temp_dir)
                saved_pdf_path = storage.save_uploaded_file(pdf_path, rfp)
                saved_text_path = storage.save_extracted_text(rfp)
                
                assert Path(saved_pdf_path).exists()
                assert Path(saved_text_path).exists()
                
                # Verify final state
                assert rfp.status == RFPStatus.PROCESSED
                assert rfp.extracted_text is not None
                assert len(rfp.extracted_text_by_page) > 0
                
            finally:
                if os.path.exists(pdf_path):
                    os.unlink(pdf_path)
    
    @patch('services.llm_client.genai')
    @patch('services.pdf_processor.PyPDF2.PdfReader')
    def test_extraction_with_multiple_pages(self, mock_pdf_reader, mock_genai):
        """Test extraction from multi-page RFP."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                pdf_path = f.name
            
            try:
                # Mock 3-page PDF
                mock_page1 = Mock()
                mock_page1.extract_text.return_value = "Page 1: Technical requirements"
                
                mock_page2 = Mock()
                mock_page2.extract_text.return_value = "Page 2: Timeline and budget"
                
                mock_page3 = Mock()
                mock_page3.extract_text.return_value = "Page 3: Compliance requirements"
                
                mock_pdf_reader.return_value.pages = [mock_page1, mock_page2, mock_page3]
                
                processor = PDFProcessor()
                rfp = RFP(id="multi-page-test", filename="multi.pdf")
                
                text, pages = processor.extract_text(pdf_path)
                rfp.extracted_text = text
                rfp.extracted_text_by_page = pages
                
                # Verify all pages extracted
                assert len(pages) == 3
                assert 1 in pages
                assert 2 in pages
                assert 3 in pages
                
                # Mock LLM responses for each page
                mock_llm_response = Mock()
                mock_llm_response.text = '[{"description": "Test req", "category": "technical", "priority": "high", "confidence": 0.9}]'
                
                mock_model = Mock()
                mock_model.generate_content.return_value = mock_llm_response
                mock_genai.GenerativeModel.return_value = mock_model
                mock_genai.configure = Mock()
                
                with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
                    llm_client = LLMClient(provider="gemini")
                    extractor = RequirementExtractor(llm_client=llm_client)
                    
                    requirements = extractor.extract_from_rfp(rfp)
                    
                    # Should have requirements from all pages
                    assert len(requirements) > 0
                
            finally:
                if os.path.exists(pdf_path):
                    os.unlink(pdf_path)
    
    def test_error_handling_in_workflow(self):
        """Test error handling at each step of the workflow."""
        # Test 1: Invalid file type
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"Not a PDF")
            txt_path = f.name
        
        try:
            validator = FileValidator()
            with pytest.raises(Exception):  # Should raise ValidationError
                validator.validate_file_type(txt_path, allowed_types=["pdf"])
        finally:
            if os.path.exists(txt_path):
                os.unlink(txt_path)
        
        # Test 2: RFP without extracted text
        mock_client = Mock()
        extractor = RequirementExtractor(llm_client=mock_client)
        
        rfp_no_text = RFP(id="test", filename="test.pdf")
        rfp_no_text.extracted_text = None
        
        with pytest.raises(ValueError, match="RFP must have extracted_text"):
            extractor.extract_from_rfp(rfp_no_text)
    
    def test_requirement_serialization_for_storage(self):
        """Test requirements can be serialized for storage."""
        requirements = [
            Requirement(
                rfp_id="test",
                description="Test requirement 1",
                category=RequirementCategory.TECHNICAL,
                priority=RequirementPriority.HIGH,
                confidence=0.9,
                page_number=1
            ),
            Requirement(
                rfp_id="test",
                description="Test requirement 2",
                category=RequirementCategory.BUDGET,
                priority=RequirementPriority.CRITICAL,
                confidence=0.95,
                page_number=2
            ),
        ]
        
        # Serialize to dict
        serialized = [req.to_dict() for req in requirements]
        
        assert len(serialized) == 2
        assert all("id" in req for req in serialized)
        assert all("description" in req for req in serialized)
        
        # Deserialize back
        deserialized = [Requirement.from_dict(data) for data in serialized]
        
        assert len(deserialized) == 2
        assert deserialized[0].description == "Test requirement 1"
        assert deserialized[1].category == RequirementCategory.BUDGET

