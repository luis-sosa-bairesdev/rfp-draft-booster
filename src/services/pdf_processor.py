"""PDF Processing Service for extracting text from RFP documents."""

from pathlib import Path
from typing import Dict, Optional, Tuple
import io

try:
    import PyPDF2
    import pdfplumber
except ImportError as e:
    raise ImportError(
        "PDF processing libraries not installed. "
        "Run: pip install PyPDF2 pdfplumber"
    ) from e

from src.utils.error_handler import PDFError, handle_errors
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class PDFProcessor:
    """Service for processing PDF files and extracting text."""

    def __init__(self):
        """Initialize PDF processor."""
        self.max_pages = 200  # Maximum pages to process
        self.chunk_size = 10  # Process in chunks for large PDFs

    def extract_text(
        self, 
        pdf_file: io.BytesIO,
        preserve_layout: bool = True
    ) -> Tuple[str, Dict[int, str], int]:
        """
        Extract text from PDF file.

        Args:
            pdf_file: PDF file as BytesIO object
            preserve_layout: Whether to preserve layout (uses pdfplumber)

        Returns:
            Tuple of (full_text, text_by_page, page_count)

        Raises:
            PDFError: If extraction fails
        """
        if not pdf_file:
            raise PDFError(
                "PDF file is required",
                pdf_path="<BytesIO>",
                user_message="No PDF file provided for extraction"
            )
        
        if not hasattr(pdf_file, 'read'):
            raise PDFError(
                "Invalid PDF file object",
                pdf_path="<invalid>",
                user_message="PDF file must be a readable file-like object"
            )
        
        logger.debug(f"Starting PDF extraction (preserve_layout={preserve_layout})")
        
        try:
            if preserve_layout:
                return self._extract_with_pdfplumber(pdf_file)
            else:
                return self._extract_with_pypdf2(pdf_file)
        except PDFError:
            # Re-raise PDFErrors as-is
            raise
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}", exc_info=True)
            raise PDFError(
                f"Failed to extract text from PDF: {str(e)}",
                pdf_path="<BytesIO>",
                user_message="Failed to extract text from PDF. The file might be corrupted or use unsupported features."
            ) from e

    def _extract_with_pypdf2(
        self, 
        pdf_file: io.BytesIO
    ) -> Tuple[str, Dict[int, str], int]:
        """
        Extract text using PyPDF2 (faster, basic extraction).

        Args:
            pdf_file: PDF file as BytesIO object

        Returns:
            Tuple of (full_text, text_by_page, page_count)
        """
        logger.debug("Extracting text with PyPDF2")
        
        pdf_file.seek(0)  # Reset file pointer
        reader = PyPDF2.PdfReader(pdf_file)
        
        page_count = len(reader.pages)
        if page_count > self.max_pages:
            logger.warning(f"PDF has {page_count} pages, limiting to {self.max_pages}")
            page_count = self.max_pages
        
        text_by_page: Dict[int, str] = {}
        full_text_parts = []
        
        for page_num in range(page_count):
            try:
                page = reader.pages[page_num]
                text = page.extract_text() or ""
                
                if text.strip():
                    text_by_page[page_num + 1] = text
                    full_text_parts.append(f"--- Page {page_num + 1} ---\n{text}\n")
                else:
                    logger.warning(f"Page {page_num + 1} has no extractable text")
                    
            except Exception as e:
                logger.error(f"Error extracting page {page_num + 1}: {e}")
                text_by_page[page_num + 1] = f"[Error extracting page {page_num + 1}]"
        
        full_text = "\n".join(full_text_parts)
        
        if not full_text.strip():
            raise PDFError(
                "No text could be extracted from PDF",
                pdf_path="<BytesIO>",
                user_message=(
                    "No text could be extracted from PDF. "
                    "This might be a scanned document (images only). "
                    "Please use a PDF with selectable text or consider OCR."
                )
            )
        
        logger.info(f"Successfully extracted {len(full_text)} characters from {page_count} pages using PyPDF2")
        return full_text, text_by_page, page_count

    def _extract_with_pdfplumber(
        self, 
        pdf_file: io.BytesIO
    ) -> Tuple[str, Dict[int, str], int]:
        """
        Extract text using pdfplumber (better layout preservation).

        Args:
            pdf_file: PDF file as BytesIO object

        Returns:
            Tuple of (full_text, text_by_page, page_count)
        """
        logger.debug("Extracting text with pdfplumber")
        
        pdf_file.seek(0)  # Reset file pointer
        
        text_by_page: Dict[int, str] = {}
        full_text_parts = []
        
        with pdfplumber.open(pdf_file) as pdf:
            page_count = min(len(pdf.pages), self.max_pages)
            
            for page_num, page in enumerate(pdf.pages[:page_count], start=1):
                try:
                    text = page.extract_text() or ""
                    
                    if text.strip():
                        text_by_page[page_num] = text
                        full_text_parts.append(f"--- Page {page_num} ---\n{text}\n")
                    else:
                        logger.warning(f"Page {page_num} has no extractable text")
                        
                except Exception as e:
                    logger.error(f"Error extracting page {page_num}: {e}")
                    text_by_page[page_num] = f"[Error extracting page {page_num}]"
        
        full_text = "\n".join(full_text_parts)
        
        if not full_text.strip():
            raise PDFError(
                "No text could be extracted from PDF",
                pdf_path="<BytesIO>",
                user_message=(
                    "No text could be extracted from PDF. "
                    "This might be a scanned document (images only). "
                    "Please use a PDF with selectable text or consider OCR."
                )
            )
        
        logger.info(f"Successfully extracted {len(full_text)} characters from {page_count} pages using pdfplumber")
        return full_text, text_by_page, page_count

    def validate_pdf(self, pdf_file: io.BytesIO) -> Tuple[bool, Optional[str]]:
        """
        Validate PDF file.

        Args:
            pdf_file: PDF file as BytesIO object

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not pdf_file:
            return False, "No PDF file provided"
        
        if not hasattr(pdf_file, 'read'):
            return False, "Invalid PDF file object"
        
        try:
            pdf_file.seek(0)
            reader = PyPDF2.PdfReader(pdf_file)
            
            # Check if encrypted/password protected
            if reader.is_encrypted:
                logger.warning("PDF is password-protected")
                return False, "PDF is password-protected. Please provide an unlocked version."
            
            # Check if has pages
            page_count = len(reader.pages)
            if page_count == 0:
                logger.warning("PDF has no pages")
                return False, "PDF has no pages."
            
            logger.debug(f"PDF has {page_count} pages")
            
            # Try to extract text from first page
            first_page = reader.pages[0]
            text = first_page.extract_text()
            
            if not text or len(text.strip()) < 10:
                logger.warning("PDF appears to have no extractable text")
                return False, (
                    "PDF appears to be scanned (images only) or has no extractable text. "
                    "Please use a PDF with selectable text or consider OCR."
                )
            
            logger.info("PDF validation successful")
            return True, None
            
        except Exception as e:
            logger.error(f"PDF validation failed: {e}", exc_info=True)
            return False, f"PDF validation failed: {str(e)}"

    def get_pdf_info(self, pdf_file: io.BytesIO) -> Dict[str, any]:
        """
        Get PDF metadata information.

        Args:
            pdf_file: PDF file as BytesIO object

        Returns:
            Dictionary with PDF information
        """
        try:
            pdf_file.seek(0)
            reader = PyPDF2.PdfReader(pdf_file)
            
            info = {
                "page_count": len(reader.pages),
                "is_encrypted": reader.is_encrypted,
                "metadata": {},
            }
            
            logger.debug(f"PDF info: {info['page_count']} pages, encrypted={info['is_encrypted']}")
            
            # Extract metadata if available
            if reader.metadata:
                info["metadata"] = {
                    "title": reader.metadata.get("/Title", ""),
                    "author": reader.metadata.get("/Author", ""),
                    "subject": reader.metadata.get("/Subject", ""),
                    "creator": reader.metadata.get("/Creator", ""),
                    "producer": reader.metadata.get("/Producer", ""),
                    "creation_date": reader.metadata.get("/CreationDate", ""),
                }
                logger.debug(f"PDF metadata: {info['metadata']}")
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get PDF info: {e}", exc_info=True)
            return {"error": str(e)}

