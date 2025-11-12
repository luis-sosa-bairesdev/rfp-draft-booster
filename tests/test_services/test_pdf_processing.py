"""
Integration tests for PDF Processing (Epic 2 Regression).

Tests cover:
- PDF validation (file type, size, MIME)
- PDF text extraction (PyPDF2, pdfplumber)
- Storage management
- Page-by-page extraction
- Error handling for scanned PDFs
- File operations
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from services.file_validator import FileValidator, ValidationError
from services.pdf_processor import PDFProcessor
from services.storage_manager import StorageManager, StorageError
from models import RFP, RFPStatus


class TestFileValidator:
    """Test file validation service."""
    
    def test_validate_pdf_file_type(self):
        """Test PDF file type validation."""
        validator = FileValidator()
        
        # Valid PDF file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"%PDF-1.4\n")  # PDF header
            f.flush()
            temp_path = f.name
        
        try:
            # Should not raise
            validator.validate_file_type(temp_path, allowed_types=["pdf"])
        finally:
            os.unlink(temp_path)
    
    def test_validate_invalid_file_type_raises_error(self):
        """Test invalid file type raises ValidationError."""
        validator = FileValidator()
        
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"Not a PDF")
            temp_path = f.name
        
        try:
            with pytest.raises(ValidationError, match="Invalid file type"):
                validator.validate_file_type(temp_path, allowed_types=["pdf"])
        finally:
            os.unlink(temp_path)
    
    def test_validate_file_size_within_limit(self):
        """Test file size validation passes when within limit."""
        validator = FileValidator()
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"Small file content")
            temp_path = f.name
        
        try:
            # 50MB limit, file is small
            validator.validate_file_size(temp_path, max_size_mb=50)
        finally:
            os.unlink(temp_path)
    
    def test_validate_file_size_exceeds_limit(self):
        """Test file size validation fails when exceeding limit."""
        validator = FileValidator()
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            # Write 2MB of data
            f.write(b"x" * (2 * 1024 * 1024))
            temp_path = f.name
        
        try:
            with pytest.raises(ValidationError, match="File size exceeds"):
                validator.validate_file_size(temp_path, max_size_mb=1)
        finally:
            os.unlink(temp_path)


class TestPDFProcessor:
    """Test PDF processing service."""
    
    def test_initialization(self):
        """Test PDF processor initialization."""
        processor = PDFProcessor()
        assert processor is not None
    
    @patch('services.pdf_processor.PyPDF2.PdfReader')
    def test_extract_text_with_pypdf2(self, mock_reader_class):
        """Test text extraction using PyPDF2."""
        # Mock PDF reader
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 content"
        
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Page 2 content"
        
        mock_reader = Mock()
        mock_reader.pages = [mock_page1, mock_page2]
        mock_reader_class.return_value = mock_reader
        
        processor = PDFProcessor()
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name
        
        try:
            text, pages = processor.extract_text(temp_path)
            
            assert "Page 1 content" in text
            assert "Page 2 content" in text
            assert len(pages) == 2
            assert pages[1] == "Page 1 content"
            assert pages[2] == "Page 2 content"
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    @patch('services.pdf_processor.pdfplumber.open')
    @patch('services.pdf_processor.PyPDF2.PdfReader')
    def test_fallback_to_pdfplumber(self, mock_pypdf2, mock_pdfplumber):
        """Test fallback to pdfplumber when PyPDF2 fails."""
        # PyPDF2 returns empty text
        mock_page = Mock()
        mock_page.extract_text.return_value = ""
        mock_pypdf2.return_value.pages = [mock_page]
        
        # pdfplumber succeeds
        mock_plumber_page = Mock()
        mock_plumber_page.extract_text.return_value = "Content from pdfplumber"
        
        mock_pdf = Mock()
        mock_pdf.pages = [mock_plumber_page]
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=False)
        mock_pdfplumber.return_value = mock_pdf
        
        processor = PDFProcessor()
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name
        
        try:
            text, pages = processor.extract_text(temp_path)
            
            assert "pdfplumber" in text
            mock_pdfplumber.assert_called_once()
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_extract_text_from_nonexistent_file_raises_error(self):
        """Test error when PDF file doesn't exist."""
        processor = PDFProcessor()
        
        with pytest.raises(Exception):
            processor.extract_text("/nonexistent/file.pdf")


class TestStorageManager:
    """Test storage management service."""
    
    def test_initialization_creates_directories(self):
        """Test storage manager creates necessary directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager(base_path=temp_dir)
            
            upload_dir = Path(temp_dir) / "uploads"
            assert upload_dir.exists()
    
    def test_save_uploaded_file(self):
        """Test saving uploaded file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager(base_path=temp_dir)
            
            # Create a mock uploaded file
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                f.write(b"PDF content")
                source_path = f.name
            
            try:
                rfp = RFP(id="test-rfp", filename="test.pdf")
                saved_path = storage.save_uploaded_file(source_path, rfp)
                
                assert Path(saved_path).exists()
                assert Path(saved_path).name == "test.pdf"
                
                # Verify content
                with open(saved_path, 'rb') as f:
                    assert f.read() == b"PDF content"
            finally:
                if os.path.exists(source_path):
                    os.unlink(source_path)
    
    def test_save_extracted_text(self):
        """Test saving extracted text."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager(base_path=temp_dir)
            
            rfp = RFP(id="test-rfp", filename="test.pdf")
            rfp.extracted_text = "Extracted text content"
            
            text_path = storage.save_extracted_text(rfp)
            
            assert Path(text_path).exists()
            
            # Verify content
            with open(text_path, 'r') as f:
                assert f.read() == "Extracted text content"
    
    def test_get_file_path(self):
        """Test getting file path for RFP."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager(base_path=temp_dir)
            
            rfp = RFP(id="test-rfp", filename="document.pdf")
            path = storage.get_file_path(rfp)
            
            assert "uploads" in str(path)
            assert "test-rfp" in str(path)
            assert "document.pdf" in str(path)
    
    def test_file_exists(self):
        """Test checking if file exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager(base_path=temp_dir)
            
            rfp = RFP(id="test-rfp", filename="test.pdf")
            
            # File doesn't exist yet
            assert storage.file_exists(rfp) is False
            
            # Create file
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                f.write(b"Content")
                source_path = f.name
            
            try:
                storage.save_uploaded_file(source_path, rfp)
                
                # Now file exists
                assert storage.file_exists(rfp) is True
            finally:
                if os.path.exists(source_path):
                    os.unlink(source_path)


class TestPDFProcessingIntegration:
    """Integration tests for complete PDF processing workflow."""
    
    def test_complete_pdf_processing_workflow(self):
        """Test complete workflow: validate → extract → save."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a simple test PDF (mock)
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                f.write(b"%PDF-1.4\nTest content")
                pdf_path = f.name
            
            try:
                # Step 1: Validate
                validator = FileValidator()
                validator.validate_file_size(pdf_path, max_size_mb=50)
                
                # Step 2: Extract (mocked)
                with patch('services.pdf_processor.PyPDF2.PdfReader') as mock_reader:
                    mock_page = Mock()
                    mock_page.extract_text.return_value = "Test PDF content"
                    mock_reader.return_value.pages = [mock_page]
                    
                    processor = PDFProcessor()
                    text, pages = processor.extract_text(pdf_path)
                    
                    assert "Test PDF content" in text
                
                # Step 3: Save
                storage = StorageManager(base_path=temp_dir)
                rfp = RFP(id="test-rfp", filename="test.pdf")
                rfp.extracted_text = text
                
                saved_path = storage.save_uploaded_file(pdf_path, rfp)
                text_path = storage.save_extracted_text(rfp)
                
                assert Path(saved_path).exists()
                assert Path(text_path).exists()
                
            finally:
                if os.path.exists(pdf_path):
                    os.unlink(pdf_path)
    
    def test_handling_scanned_pdf_without_text(self):
        """Test handling of scanned PDFs with no extractable text."""
        with patch('services.pdf_processor.PyPDF2.PdfReader') as mock_pypdf2:
            with patch('services.pdf_processor.pdfplumber.open') as mock_pdfplumber:
                # Both extractors return empty text (scanned PDF)
                mock_page = Mock()
                mock_page.extract_text.return_value = ""
                mock_pypdf2.return_value.pages = [mock_page]
                
                mock_plumber_page = Mock()
                mock_plumber_page.extract_text.return_value = ""
                mock_pdf = Mock()
                mock_pdf.pages = [mock_plumber_page]
                mock_pdf.__enter__ = Mock(return_value=mock_pdf)
                mock_pdf.__exit__ = Mock(return_value=False)
                mock_pdfplumber.return_value = mock_pdf
                
                processor = PDFProcessor()
                
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                    temp_path = f.name
                
                try:
                    text, pages = processor.extract_text(temp_path)
                    
                    # Should return empty or minimal text
                    assert len(text.strip()) == 0 or "no text" in text.lower()
                finally:
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)

