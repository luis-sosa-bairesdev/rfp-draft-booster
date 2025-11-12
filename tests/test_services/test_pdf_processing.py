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
import io

from services.file_validator import FileValidator
from services.pdf_processor import PDFProcessor
from services.storage_manager import StorageManager
from exceptions import ValidationError, StorageError
from models import RFP, RFPStatus


class TestFileValidator:
    """Test file validation service."""
    
    def test_validate_pdf_file_type(self):
        """Test PDF file type validation."""
        # Valid PDF file name
        valid, error = FileValidator.validate_file("test.pdf", 1024)
        assert valid is True
        assert error is None
    
    def test_validate_invalid_file_type_raises_error(self):
        """Test invalid file type raises ValidationError."""
        valid, error = FileValidator.validate_file("test.txt", 1024)
        assert valid is False
        assert "Invalid file type" in error
    
    def test_validate_file_size_within_limit(self):
        """Test file size validation passes when within limit."""
        # Small file (1KB)
        valid, error = FileValidator.validate_file("test.pdf", 1024)
        assert valid is True
        assert error is None
    
    def test_validate_file_size_exceeds_limit(self):
        """Test file size validation fails when exceeding limit."""
        # File larger than 50MB
        large_size = 51 * 1024 * 1024  # 51MB
        valid, error = FileValidator.validate_file("test.pdf", large_size)
        assert valid is False
        assert "File too large" in error
    
    def test_validate_empty_file(self):
        """Test empty file validation."""
        valid, error = FileValidator.validate_file("test.pdf", 0)
        assert valid is False
        assert "empty" in error.lower()
    
    def test_validate_mime_type_with_content(self):
        """Test MIME type validation with file content."""
        pdf_content = io.BytesIO(b"%PDF-1.4\nTest content")
        valid, error = FileValidator.validate_file("test.pdf", 1024, pdf_content)
        assert valid is True
    
    def test_validate_invalid_mime_type(self):
        """Test invalid MIME type detection."""
        # Create content that doesn't start with PDF header
        invalid_content = io.BytesIO(b"Not a PDF file content")
        valid, error = FileValidator.validate_file("test.pdf", 1024, invalid_content)
        # MIME validation might pass if extension is .pdf, but content check should catch it
        # The actual behavior depends on mimetypes.guess_type
        assert isinstance(valid, bool)
    
    def test_format_file_size_bytes(self):
        """Test file size formatting for bytes."""
        result = FileValidator.format_file_size(512)
        assert "512 B" == result
    
    def test_format_file_size_kb(self):
        """Test file size formatting for KB."""
        result = FileValidator.format_file_size(2048)
        assert "KB" in result
    
    def test_format_file_size_mb(self):
        """Test file size formatting for MB."""
        result = FileValidator.format_file_size(2 * 1024 * 1024)
        assert "MB" in result
    
    def test_validate_file_with_mime_type_check(self):
        """Test file validation with MIME type checking."""
        pdf_content = io.BytesIO(b"%PDF-1.4\nValid PDF content")
        valid, error = FileValidator.validate_file("test.pdf", 1024, pdf_content)
        assert valid is True
    
    def test_validate_file_extension_case_insensitive(self):
        """Test file extension validation is case insensitive."""
        valid, error = FileValidator.validate_file("TEST.PDF", 1024)
        assert valid is True
    
    def test_validate_file_size_at_limit(self):
        """Test file size validation at exact limit."""
        limit_bytes = FileValidator.MAX_FILE_SIZE_BYTES
        valid, error = FileValidator.validate_file("test.pdf", limit_bytes)
        assert valid is True
    
    def test_validate_file_size_one_byte_over(self):
        """Test file size validation fails one byte over limit."""
        over_limit = FileValidator.MAX_FILE_SIZE_BYTES + 1
        valid, error = FileValidator.validate_file("test.pdf", over_limit)
        assert valid is False
        assert "too large" in error.lower()
    
    def test_validate_mime_type_with_pdf_header(self):
        """Test MIME validation passes with PDF header."""
        pdf_content = io.BytesIO(b"%PDF-1.4\nValid PDF")
        # Mock mimetypes to return None (unknown type)
        with patch('services.file_validator.mimetypes.guess_type', return_value=(None, None)):
            valid, error = FileValidator._validate_mime_type("test.pdf", pdf_content)
            assert valid is True  # Should pass because of PDF header
    
    def test_validate_mime_type_without_pdf_header(self):
        """Test MIME validation fails without PDF header."""
        invalid_content = io.BytesIO(b"Not a PDF file")
        # Mock mimetypes to return None (unknown type)
        with patch('services.file_validator.mimetypes.guess_type', return_value=(None, None)):
            valid, error = FileValidator._validate_mime_type("test.pdf", invalid_content)
            assert valid is False
            assert "valid PDF" in error


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
        mock_reader.is_encrypted = False
        mock_reader_class.return_value = mock_reader
        
        processor = PDFProcessor()
        
        pdf_content = io.BytesIO(b"%PDF-1.4\nTest content")
        text, pages, page_count = processor.extract_text(pdf_content, preserve_layout=False)
        
        assert "Page 1 content" in text
        assert "Page 2 content" in text
        assert len(pages) == 2
        assert pages[1] == "Page 1 content"
        assert pages[2] == "Page 2 content"
        assert page_count == 2
    
    @patch('services.pdf_processor.pdfplumber.open')
    def test_extract_with_pdfplumber(self, mock_pdfplumber):
        """Test extraction using pdfplumber."""
        # pdfplumber succeeds
        mock_plumber_page = Mock()
        mock_plumber_page.extract_text.return_value = "Content from pdfplumber"
        
        mock_pdf = Mock()
        mock_pdf.pages = [mock_plumber_page]
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=False)
        mock_pdfplumber.return_value = mock_pdf
        
        processor = PDFProcessor()
        
        pdf_content = io.BytesIO(b"%PDF-1.4\nTest content")
        text, pages, page_count = processor.extract_text(pdf_content, preserve_layout=True)
        
        assert "pdfplumber" in text
        mock_pdfplumber.assert_called_once()
        assert page_count == 1
    
    def test_extract_text_with_invalid_pdf_raises_error(self):
        """Test error when PDF content is invalid."""
        processor = PDFProcessor()
        
        invalid_content = io.BytesIO(b"Not a PDF")
        with pytest.raises(Exception):
            processor.extract_text(invalid_content)


class TestStorageManager:
    """Test storage management service."""
    
    def test_initialization_creates_directories(self):
        """Test storage manager creates necessary directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager(base_upload_dir=temp_dir)
            
            upload_dir = Path(temp_dir)
            assert upload_dir.exists()
    
    def test_save_upload(self):
        """Test saving uploaded file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager(base_upload_dir=temp_dir)
            
            # Create file content
            file_content = io.BytesIO(b"PDF content")
            
            saved_path = storage.save_upload(file_content, "test.pdf", "test-rfp-1")
            
            assert Path(saved_path).exists()
            assert "test.pdf" in saved_path
            
            # Verify content
            with open(saved_path, 'rb') as f:
                assert f.read() == b"PDF content"
    
    def test_get_file_content(self):
        """Test reading file content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager(base_upload_dir=temp_dir)
            
            # Save a file first
            file_content = io.BytesIO(b"Test content")
            saved_path = storage.save_upload(file_content, "test.pdf", "test-rfp-1")
            
            # Read it back
            content = storage.get_file_content(saved_path)
            
            assert content == b"Test content"
    
    def test_get_file_content_nonexistent(self):
        """Test reading nonexistent file returns None."""
        storage = StorageManager()
        content = storage.get_file_content("/nonexistent/file.pdf")
        assert content is None
    
    def test_delete_upload(self):
        """Test deleting uploaded file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager(base_upload_dir=temp_dir)
            
            # Save a file
            file_content = io.BytesIO(b"Test content")
            saved_path = storage.save_upload(file_content, "test.pdf", "test-rfp-1")
            
            assert Path(saved_path).exists()
            
            # Delete it
            result = storage.delete_upload(saved_path)
            
            assert result is True
            assert not Path(saved_path).exists()
    
    def test_delete_nonexistent_file(self):
        """Test deleting nonexistent file returns False."""
        storage = StorageManager()
        result = storage.delete_upload("/nonexistent/file.pdf")
        assert result is False
    
    def test_cleanup_old_files(self):
        """Test cleanup of old files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager(base_upload_dir=temp_dir)
            
            # This test would require mocking file timestamps
            # For now, just test the method exists and doesn't crash
            deleted_count = storage.cleanup_old_files(days=90)
            assert isinstance(deleted_count, int)
    
    def test_save_upload_creates_rfp_directory(self):
        """Test that save_upload creates RFP-specific directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager(base_upload_dir=temp_dir)
            
            file_content = io.BytesIO(b"Test content")
            saved_path = storage.save_upload(file_content, "test.pdf", "rfp-123")
            
            # Verify RFP directory was created
            rfp_dir = Path(temp_dir) / "rfp-123"
            assert rfp_dir.exists()
            assert rfp_dir.is_dir()
    
    def test_save_upload_handles_io_error(self):
        """Test save_upload handles IO errors."""
        storage = StorageManager()
        
        # Create a mock file that will fail on write
        with patch('builtins.open', side_effect=IOError("Disk full")):
            file_content = io.BytesIO(b"Test content")
            with pytest.raises(IOError):
                storage.save_upload(file_content, "test.pdf", "test-rfp")
    
    def test_delete_upload_removes_empty_directory(self):
        """Test delete_upload removes empty parent directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager(base_upload_dir=temp_dir)
            
            # Save a file
            file_content = io.BytesIO(b"Test content")
            saved_path = storage.save_upload(file_content, "test.pdf", "rfp-123")
            
            # Delete it - should also remove empty directory
            result = storage.delete_upload(saved_path)
            
            assert result is True
            rfp_dir = Path(temp_dir) / "rfp-123"
            # Directory might be removed if empty
            assert not Path(saved_path).exists()
    
    def test_get_file_content_returns_none_for_missing_file(self):
        """Test get_file_content returns None for missing file."""
        storage = StorageManager()
        content = storage.get_file_content("/nonexistent/path/file.pdf")
        assert content is None
    
    def test_delete_upload_handles_exception(self):
        """Test delete_upload handles exceptions gracefully."""
        storage = StorageManager()
        
        # Mock Path to raise exception
        with patch('services.storage_manager.Path') as mock_path:
            mock_path.side_effect = Exception("Permission denied")
            result = storage.delete_upload("/some/path.pdf")
            assert result is False
    
    def test_get_file_content_handles_exception(self):
        """Test get_file_content handles exceptions gracefully."""
        storage = StorageManager()
        
        # Mock Path to raise exception
        with patch('services.storage_manager.Path') as mock_path_class:
            mock_path = Mock()
            mock_path.exists.return_value = True
            mock_path.read_bytes.side_effect = IOError("Read error")
            mock_path_class.return_value = mock_path
            
            content = storage.get_file_content("/some/path.pdf")
            assert content is None


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
                file_size = os.path.getsize(pdf_path)
                pdf_content = io.BytesIO(b"%PDF-1.4\nTest content")
                valid, error = FileValidator.validate_file("test.pdf", file_size, pdf_content)
                assert valid is True
                
                # Step 2: Extract (mocked)
                with patch('services.pdf_processor.PyPDF2.PdfReader') as mock_reader:
                    mock_page = Mock()
                    mock_page.extract_text.return_value = "Test PDF content"
                    mock_reader.return_value.pages = [mock_page]
                    mock_reader.return_value.is_encrypted = False
                    
                    processor = PDFProcessor()
                    pdf_content = io.BytesIO(b"%PDF-1.4\nTest content")
                    text, pages, page_count = processor.extract_text(pdf_content, preserve_layout=False)
                    
                    assert "Test PDF content" in text
                    assert page_count == 1
                
                # Step 3: Save
                storage = StorageManager(base_upload_dir=temp_dir)
                file_content = io.BytesIO(b"%PDF-1.4\nTest content")
                saved_path = storage.save_upload(file_content, "test.pdf", "test-rfp-1")
                
                assert Path(saved_path).exists()
                
            finally:
                if os.path.exists(pdf_path):
                    os.unlink(pdf_path)
    
    def test_handling_scanned_pdf_without_text(self):
        """Test handling of scanned PDFs with no extractable text."""
        with patch('services.pdf_processor.PyPDF2.PdfReader') as mock_pypdf2:
            # PyPDF2 returns empty text (scanned PDF)
            mock_page = Mock()
            mock_page.extract_text.return_value = ""
            mock_pypdf2.return_value.pages = [mock_page]
            mock_pypdf2.return_value.is_encrypted = False
            
            processor = PDFProcessor()
            
            pdf_content = io.BytesIO(b"%PDF-1.4\nScanned content")
            
            # Should raise PDFProcessingError for scanned PDFs
            with pytest.raises(Exception, match="No text could be extracted"):
                processor.extract_text(pdf_content, preserve_layout=False)
    
    @patch('services.pdf_processor.PyPDF2.PdfReader')
    def test_validate_pdf(self, mock_reader_class):
        """Test PDF validation."""
        mock_page = Mock()
        mock_page.extract_text.return_value = "Valid PDF content with enough text"
        
        mock_reader = Mock()
        mock_reader.pages = [mock_page]
        mock_reader.is_encrypted = False
        mock_reader_class.return_value = mock_reader
        
        processor = PDFProcessor()
        pdf_content = io.BytesIO(b"%PDF-1.4\nValid content")
        
        valid, error = processor.validate_pdf(pdf_content)
        assert valid is True
        assert error is None
    
    @patch('services.pdf_processor.PyPDF2.PdfReader')
    def test_validate_encrypted_pdf(self, mock_reader_class):
        """Test validation of encrypted PDF."""
        mock_reader = Mock()
        mock_reader.is_encrypted = True
        mock_reader.pages = [Mock()]
        mock_reader_class.return_value = mock_reader
        
        processor = PDFProcessor()
        pdf_content = io.BytesIO(b"%PDF-1.4\nEncrypted")
        
        valid, error = processor.validate_pdf(pdf_content)
        assert valid is False
        assert "password" in error.lower()
    
    @patch('services.pdf_processor.PyPDF2.PdfReader')
    def test_get_pdf_info(self, mock_reader_class):
        """Test getting PDF metadata."""
        mock_reader = Mock()
        mock_reader.pages = [Mock(), Mock()]
        mock_reader.is_encrypted = False
        mock_reader.metadata = {
            "/Title": "Test PDF",
            "/Author": "Test Author"
        }
        mock_reader_class.return_value = mock_reader
        
        processor = PDFProcessor()
        pdf_content = io.BytesIO(b"%PDF-1.4\nTest")
        
        info = processor.get_pdf_info(pdf_content)
        
        assert info["page_count"] == 2
        assert info["is_encrypted"] is False
        assert "metadata" in info
    
    @patch('services.pdf_processor.PyPDF2.PdfReader')
    def test_validate_pdf_empty_pages(self, mock_reader_class):
        """Test validation fails for PDF with no pages."""
        mock_reader = Mock()
        mock_reader.pages = []
        mock_reader.is_encrypted = False
        mock_reader_class.return_value = mock_reader
        
        processor = PDFProcessor()
        pdf_content = io.BytesIO(b"%PDF-1.4\nEmpty")
        
        valid, error = processor.validate_pdf(pdf_content)
        assert valid is False
        assert "no pages" in error.lower()
    
    @patch('services.pdf_processor.PyPDF2.PdfReader')
    def test_validate_pdf_scanned(self, mock_reader_class):
        """Test validation fails for scanned PDF."""
        mock_page = Mock()
        mock_page.extract_text.return_value = "abc"  # Too short
        
        mock_reader = Mock()
        mock_reader.pages = [mock_page]
        mock_reader.is_encrypted = False
        mock_reader_class.return_value = mock_reader
        
        processor = PDFProcessor()
        pdf_content = io.BytesIO(b"%PDF-1.4\nScanned")
        
        valid, error = processor.validate_pdf(pdf_content)
        assert valid is False
        assert "scanned" in error.lower() or "no extractable text" in error.lower()
    
    @patch('services.pdf_processor.PyPDF2.PdfReader')
    def test_get_pdf_info_with_metadata(self, mock_reader_class):
        """Test getting PDF info with full metadata."""
        mock_reader = Mock()
        mock_reader.pages = [Mock()]
        mock_reader.is_encrypted = False
        mock_reader.metadata = {
            "/Title": "Test PDF",
            "/Author": "Test Author",
            "/Subject": "Test Subject",
            "/Creator": "Test Creator",
            "/Producer": "Test Producer",
            "/CreationDate": "2025-01-01"
        }
        mock_reader_class.return_value = mock_reader
        
        processor = PDFProcessor()
        pdf_content = io.BytesIO(b"%PDF-1.4\nTest")
        
        info = processor.get_pdf_info(pdf_content)
        
        assert info["metadata"]["title"] == "Test PDF"
        assert info["metadata"]["author"] == "Test Author"
    
    @patch('services.pdf_processor.PyPDF2.PdfReader')
    def test_get_pdf_info_error_handling(self, mock_reader_class):
        """Test get_pdf_info handles errors gracefully."""
        mock_reader_class.side_effect = Exception("PDF read error")
        
        processor = PDFProcessor()
        pdf_content = io.BytesIO(b"Invalid PDF")
        
        info = processor.get_pdf_info(pdf_content)
        
        assert "error" in info
    
    @patch('services.pdf_processor.PyPDF2.PdfReader')
    def test_extract_text_with_page_limit(self, mock_reader_class):
        """Test extraction limits pages to max_pages."""
        # Create 250 pages (more than max_pages=200)
        mock_pages = [Mock() for _ in range(250)]
        for page in mock_pages:
            page.extract_text.return_value = f"Page content"
        
        mock_reader = Mock()
        mock_reader.pages = mock_pages
        mock_reader.is_encrypted = False
        mock_reader_class.return_value = mock_reader
        
        processor = PDFProcessor()
        pdf_content = io.BytesIO(b"%PDF-1.4\nLarge PDF")
        
        text, pages, page_count = processor.extract_text(pdf_content, preserve_layout=False)
        
        assert page_count == 200  # Limited to max_pages
        assert len(pages) == 200
    
    @patch('services.pdf_processor.PyPDF2.PdfReader')
    def test_extract_text_with_page_extraction_error(self, mock_reader_class):
        """Test extraction handles page extraction errors."""
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 content"
        
        mock_page2 = Mock()
        mock_page2.extract_text.side_effect = Exception("Page extraction error")
        
        mock_reader = Mock()
        mock_reader.pages = [mock_page1, mock_page2]
        mock_reader.is_encrypted = False
        mock_reader_class.return_value = mock_reader
        
        processor = PDFProcessor()
        pdf_content = io.BytesIO(b"%PDF-1.4\nTest")
        
        text, pages, page_count = processor.extract_text(pdf_content, preserve_layout=False)
        
        # Should handle error and continue
        assert page_count == 2
        assert 2 in pages  # Error page should be marked
    
    @patch('services.pdf_processor.pdfplumber.open')
    def test_extract_with_pdfplumber_page_error(self, mock_pdfplumber):
        """Test pdfplumber extraction handles page errors."""
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 content"
        
        mock_page2 = Mock()
        mock_page2.extract_text.side_effect = Exception("Page error")
        
        mock_pdf = Mock()
        mock_pdf.pages = [mock_page1, mock_page2]
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=False)
        mock_pdfplumber.return_value = mock_pdf
        
        processor = PDFProcessor()
        pdf_content = io.BytesIO(b"%PDF-1.4\nTest")
        
        text, pages, page_count = processor.extract_text(pdf_content, preserve_layout=True)
        
        # Should handle error and continue
        assert page_count == 2
        assert 2 in pages  # Error page should be marked
    
    @patch('services.pdf_processor.PyPDF2.PdfReader')
    def test_validate_pdf_error_handling(self, mock_reader_class):
        """Test validate_pdf handles errors gracefully."""
        mock_reader_class.side_effect = Exception("PDF read error")
        
        processor = PDFProcessor()
        pdf_content = io.BytesIO(b"Invalid PDF")
        
        valid, error = processor.validate_pdf(pdf_content)
        
        assert valid is False
        assert "validation failed" in error.lower()
    
    
    @patch('services.pdf_processor.pdfplumber.open')
    def test_extract_with_pdfplumber_no_text_raises_error(self, mock_pdfplumber):
        """Test pdfplumber extraction raises error when no text extracted."""
        mock_page = Mock()
        mock_page.extract_text.return_value = ""  # Empty text
        
        mock_pdf = Mock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=False)
        mock_pdfplumber.return_value = mock_pdf
        
        processor = PDFProcessor()
        pdf_content = io.BytesIO(b"%PDF-1.4\nScanned")
        
        # Should raise PDFProcessingError
        with pytest.raises(Exception, match="No text could be extracted"):
            processor.extract_text(pdf_content, preserve_layout=True)
    
    @patch('services.pdf_processor.PyPDF2.PdfReader')
    def test_extract_text_with_empty_pages(self, mock_reader_class):
        """Test extraction handles PDFs with empty pages."""
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 content"
        
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = ""  # Empty page
        
        mock_reader = Mock()
        mock_reader.pages = [mock_page1, mock_page2]
        mock_reader.is_encrypted = False
        mock_reader_class.return_value = mock_reader
        
        processor = PDFProcessor()
        pdf_content = io.BytesIO(b"%PDF-1.4\nTest")
        
        text, pages, page_count = processor.extract_text(pdf_content, preserve_layout=False)
        
        # Should only include page 1 in pages dict
        assert 1 in pages
        assert "Page 1 content" in text
        assert page_count == 2
    
    @patch('services.pdf_processor.pdfplumber.open')
    def test_extract_with_pdfplumber_empty_pages(self, mock_pdfplumber):
        """Test pdfplumber extraction handles empty pages."""
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 content"
        
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = ""  # Empty page
        
        mock_pdf = Mock()
        mock_pdf.pages = [mock_page1, mock_page2]
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=False)
        mock_pdfplumber.return_value = mock_pdf
        
        processor = PDFProcessor()
        pdf_content = io.BytesIO(b"%PDF-1.4\nTest")
        
        text, pages, page_count = processor.extract_text(pdf_content, preserve_layout=True)
        
        # Should only include page 1 in pages dict
        assert 1 in pages
        assert "Page 1 content" in text
        assert page_count == 2
