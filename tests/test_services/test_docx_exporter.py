"""Unit tests for DocxExporter service."""

import pytest
from datetime import datetime
from io import BytesIO
from unittest.mock import Mock, patch, MagicMock

from src.services.docx_exporter import DocxExporter
from src.models.draft import Draft, DraftStatus, GenerationMethod
from src.models.rfp import RFP


class TestDocxExporter:
    """Test cases for DocxExporter."""
    
    def test_init(self):
        """Test DocxExporter initialization."""
        exporter = DocxExporter()
        assert exporter is not None
    
    def test_is_available_with_docx(self):
        """Test is_available returns True when python-docx is installed."""
        exporter = DocxExporter()
        # Should be True in test environment (python-docx is in requirements)
        assert exporter.is_available() is True
    
    @patch('src.services.docx_exporter.DOCX_AVAILABLE', False)
    def test_is_available_without_docx(self):
        """Test is_available returns False when python-docx is not installed."""
        exporter = DocxExporter()
        assert exporter.is_available() is False
    
    def test_export_to_docx_basic(self):
        """Test basic DOCX export with minimal data."""
        exporter = DocxExporter()
        
        # Create minimal draft
        draft = Draft(
            id="test-123",
            rfp_id="rfp-456",
            content="# Test Draft\n\nThis is a test.",
            status=DraftStatus.APPROVED,
            generated_by=GenerationMethod.MANUAL
        )
        
        result = exporter.export_to_docx(draft)
        
        assert result is not None
        assert isinstance(result, bytes)
        assert len(result) > 0
    
    def test_export_to_docx_with_rfp(self):
        """Test DOCX export with RFP metadata."""
        exporter = DocxExporter()
        
        draft = Draft(
            id="test-123",
            rfp_id="rfp-456",
            content="# Proposal\n\nContent here.",
            status=DraftStatus.APPROVED,
            generated_by=GenerationMethod.AI
        )
        
        rfp = RFP(
            id="rfp-456",
            file_name="test.pdf",
            client_name="Test Org"
        )
        
        result = exporter.export_to_docx(draft, rfp=rfp)
        
        assert result is not None
        assert isinstance(result, bytes)
        assert len(result) > 0
    
    def test_export_to_docx_with_service_matches(self):
        """Test DOCX export with service matches table."""
        exporter = DocxExporter()
        
        draft = Draft(
            id="test-123",
            rfp_id="rfp-456",
            content="# Proposal\n\nContent.",
            status=DraftStatus.APPROVED,
            generated_by=GenerationMethod.AI
        )
        
        service_matches = [
            {
                'requirement_desc': 'Need cloud hosting',
                'service_name': 'AWS EC2',
                'match_percentage': 95.5
            },
            {
                'requirement_desc': 'Need database',
                'service_name': 'PostgreSQL',
                'match_percentage': 88.0
            }
        ]
        
        result = exporter.export_to_docx(draft, service_matches=service_matches)
        
        assert result is not None
        assert isinstance(result, bytes)
        assert len(result) > 0
    
    def test_export_to_docx_complex_markdown(self):
        """Test DOCX export with complex markdown formatting."""
        exporter = DocxExporter()
        
        content = """# Main Title

## Section 1

This is **bold text** and this is *italic text*.

### Subsection

- Item 1
- Item 2
- Item 3

1. First
2. Second
3. Third

Some `inline code` here.

## Section 2

More content with **bold** and *italic* formatting.
"""
        
        draft = Draft(
            id="test-123",
            rfp_id="rfp-456",
            content=content,
            status=DraftStatus.APPROVED,
            generated_by=GenerationMethod.AI
        )
        
        result = exporter.export_to_docx(draft)
        
        assert result is not None
        assert isinstance(result, bytes)
        assert len(result) > 1000  # Should be substantial with formatting
    
    @patch('src.services.docx_exporter.DOCX_AVAILABLE', False)
    def test_export_to_docx_without_library(self):
        """Test export fails gracefully when python-docx not available."""
        exporter = DocxExporter()
        
        draft = Draft(
            id="test-123",
            rfp_id="rfp-456",
            content="# Test",
            status=DraftStatus.APPROVED,
            generated_by=GenerationMethod.MANUAL
        )
        
        result = exporter.export_to_docx(draft)
        
        assert result is None
    
    def test_generate_doc_title_with_rfp(self):
        """Test document title generation with RFP."""
        exporter = DocxExporter()
        
        draft = Draft(
            id="test-123",
            rfp_id="rfp-456789",
            content="# Test",
            status=DraftStatus.APPROVED,
            generated_by=GenerationMethod.AI
        )
        
        rfp = RFP(
            id="rfp-456789",
            file_name="test.pdf"
        )
        
        title = exporter._generate_doc_title(draft, rfp)
        
        assert "RFP Draft" in title
        assert "rfp-4567" in title  # First 8 chars
        assert datetime.now().strftime('%Y-%m-%d') in title
    
    def test_generate_doc_title_without_rfp(self):
        """Test document title generation without RFP."""
        exporter = DocxExporter()
        
        draft = Draft(
            id="test-123",
            rfp_id="rfp-456",
            content="# Test",
            status=DraftStatus.APPROVED,
            generated_by=GenerationMethod.MANUAL
        )
        
        title = exporter._generate_doc_title(draft, None)
        
        assert "Draft" in title
        assert datetime.now().strftime('%Y-%m-%d') in title
    
    def test_add_metadata(self):
        """Test metadata table creation."""
        exporter = DocxExporter()
        
        # Mock Document
        doc = Mock()
        doc.add_heading = Mock(return_value=Mock())
        doc.add_table = Mock(return_value=Mock())
        doc.add_paragraph = Mock(return_value=Mock())
        
        # Mock table with rows
        table = Mock()
        table.style = None
        table.add_row = Mock(return_value=Mock(cells=[Mock(), Mock()]))
        doc.add_table.return_value = table
        
        rfp = RFP(
            id="rfp-123",
            file_name="test.pdf",
            client_name="Test Org"
        )
        
        exporter._add_metadata(doc, rfp)
        
        doc.add_heading.assert_called_once_with("RFP Information", level=2)
        doc.add_table.assert_called_once()
    
    def test_add_service_matches_table_empty(self):
        """Test service matches table with no matches."""
        exporter = DocxExporter()
        
        doc = Mock()
        doc.add_heading = Mock(return_value=Mock())
        doc.add_paragraph = Mock(return_value=Mock())
        
        exporter._add_service_matches_table(doc, [])
        
        doc.add_heading.assert_called_once()
        doc.add_paragraph.assert_called_once()
    
    def test_add_service_matches_table_with_data(self):
        """Test service matches table with data."""
        exporter = DocxExporter()
        
        doc = Mock()
        doc.add_heading = Mock(return_value=Mock())
        doc.add_paragraph = Mock(return_value=Mock())
        
        # Mock table
        table = Mock()
        table.style = None
        table.rows = [Mock(cells=[Mock(), Mock(), Mock()])]
        table.add_row = Mock(return_value=Mock(cells=[Mock(), Mock(), Mock()]))
        doc.add_table = Mock(return_value=table)
        
        matches = [
            {'requirement_desc': 'Req 1', 'service_name': 'Service 1', 'match_percentage': 95.0},
            {'requirement_desc': 'Req 2', 'service_name': 'Service 2', 'match_percentage': 88.5}
        ]
        
        exporter._add_service_matches_table(doc, matches)
        
        doc.add_heading.assert_called_once()
        doc.add_table.assert_called_once()
        assert table.add_row.call_count == 2
    
    def test_add_markdown_content_headings(self):
        """Test markdown content conversion - headings."""
        exporter = DocxExporter()
        
        doc = Mock()
        doc.add_heading = Mock(return_value=Mock())
        doc.add_paragraph = Mock(return_value=Mock())
        
        content = "# H1\n## H2\n### H3\n#### H4"
        
        exporter._add_markdown_content(doc, content)
        
        # Should add 4 headings
        assert doc.add_heading.call_count == 4
    
    def test_add_markdown_content_lists(self):
        """Test markdown content conversion - lists."""
        exporter = DocxExporter()
        
        doc = Mock()
        doc.add_paragraph = Mock(return_value=Mock())
        
        content = "- Item 1\n- Item 2\n1. First\n2. Second"
        
        exporter._add_markdown_content(doc, content)
        
        # Should add 4 list items
        assert doc.add_paragraph.call_count == 4
    
    def test_add_inline_formatting(self):
        """Test inline formatting (bold, italic, code)."""
        exporter = DocxExporter()
        
        paragraph = Mock()
        paragraph.add_run = Mock(return_value=Mock())
        
        text = "This is **bold** and this is *italic* and `code`"
        
        exporter._add_inline_formatting(paragraph, text)
        
        # Should add multiple runs for different formats
        assert paragraph.add_run.call_count > 0


class TestDocxExporterIntegration:
    """Integration tests for DocxExporter."""
    
    def test_full_export_workflow(self):
        """Test complete export workflow from draft to bytes."""
        exporter = DocxExporter()
        
        # Create complete draft
        draft = Draft(
            id="test-123",
            rfp_id="rfp-456",
            content="""# Proposal for Test Project

## Executive Summary

This is a **bold statement** with *italic emphasis*.

## Technical Approach

- Requirement 1
- Requirement 2
- Requirement 3

### Implementation Plan

1. Phase 1
2. Phase 2
3. Phase 3

## Conclusion

Some `inline code` and more content.
""",
            status=DraftStatus.APPROVED,
            generated_by=GenerationMethod.AI,
            word_count=150,
            section_count=5
        )
        
        rfp = RFP(
            id="rfp-456",
            file_name="test.pdf",
            client_name="Acme Corp"
        )
        
        service_matches = [
            {
                'requirement_desc': 'Cloud infrastructure needed',
                'service_name': 'AWS Infrastructure',
                'match_percentage': 92.5
            }
        ]
        
        result = exporter.export_to_docx(draft, rfp, service_matches)
        
        assert result is not None
        assert isinstance(result, bytes)
        assert len(result) > 5000  # Should be substantial
        
        # Verify it's a valid DOCX (ZIP format)
        assert result[:4] == b'PK\x03\x04'  # ZIP file signature

