# Epic 7: Google Docs Export - Technical Spike

**Date:** 2025-11-13  
**Epic Key:** RDBP-70 (Proposed)  
**Type:** Feature / Integration  
**Status:** 📋 Planning

---

## 🎯 Executive Summary

**Goal:** Enable one-click export of generated proposal drafts to Google Docs, allowing sales teams to collaborate, edit, and share proposals directly in Google Workspace.

**Approach:** Integrate Google Docs API for authenticated export with automatic formatting (headings, bold, lists, tables). Fallback to `.docx` download via `python-docx` when Google credentials unavailable.

**Value Proposition:**
- **Collaboration:** Seamless sharing with team members and clients
- **Professional Output:** Properly formatted documents matching corporate standards
- **Flexibility:** Cloud-based (Google Docs) or local (.docx) options
- **Speed:** One-click export vs. copy-paste + manual formatting (saves 10-15 min)

---

## 📊 Problem Statement

### Current Pain Point

After generating a draft in Streamlit:
1. User copies Markdown content manually
2. Pastes into Google Docs or Word
3. Manually applies formatting (headings, bold, lists)
4. Fixes broken formatting and spacing
5. Adds metadata (client name, date)
6. Shares with team for review

**Time Cost:** 10-15 minutes per draft  
**Error Rate:** Formatting inconsistencies, lost metadata

### Desired State

User clicks "Export to Google Docs" → System creates fully-formatted Google Doc with:
- Proper headings and styling
- RFP metadata (client, date, deadline)
- Service matches table (if Epic 6 complete)
- Shareable link for immediate collaboration

**Alternative:** If no Google credentials → Download formatted `.docx` file

---

## 🏗️ Architecture & Design

### 1. Authentication Flow

```
┌─────────────────────┐
│ st.secrets          │
│ GOOGLE_CREDENTIALS  │
│ (JSON string)       │
└─────────────────────┘
          │
          ▼
┌─────────────────────┐
│ json.loads()        │
│ Parse credentials   │
└─────────────────────┘
          │
          ▼
┌─────────────────────┐
│ google.auth         │
│ Authenticate        │
└─────────────────────┘
          │
          ├─ Success ──────────────┐
          │                        ▼
          │              ┌─────────────────────┐
          │              │ Google Docs API     │
          │              │ Create & Format Doc │
          │              └─────────────────────┘
          │                        │
          │                        ▼
          │              ┌─────────────────────┐
          │              │ Share Link          │
          │              │ (Viewer permission) │
          │              └─────────────────────┘
          │
          └─ Fail ────────────────┐
                                  ▼
                        ┌─────────────────────┐
                        │ python-docx         │
                        │ Generate .docx      │
                        └─────────────────────┘
                                  │
                                  ▼
                        ┌─────────────────────┐
                        │ st.download_button  │
                        │ Download file       │
                        └─────────────────────┘
```

**Google Service Account Scopes:**
- `https://www.googleapis.com/auth/documents` - Create and edit Google Docs
- `https://www.googleapis.com/auth/drive` - Create files and manage sharing

**Secrets Configuration (`streamlit/secrets.toml`):**
```toml
[GOOGLE_CREDENTIALS]
type = "service_account"
project_id = "rfp-draft-booster"
private_key_id = "abc123..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "rfp-service@rfp-draft-booster.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

### 2. Document Structure

**Mapping Rules:**

| Markdown | Google Docs Style |
|----------|-------------------|
| Draft Title | Document Title (Bold, 16pt) |
| `## Heading` | Heading 1 (14pt, Bold) |
| `### Subheading` | Heading 2 (12pt, Bold) |
| `**bold**` | Bold text |
| `*italic*` | Italic text |
| `- list item` | Bullet list |
| `1. numbered` | Numbered list |

**Document Layout:**
```
┌────────────────────────────────────────────┐
│ RFP Draft - [Client Name] - [Date]        │ ← Title
├────────────────────────────────────────────┤
│ RFP Metadata Header                        │ ← Normal paragraph
│ Client: ACME Corp                          │
│ Deadline: 2025-12-31                       │
│ Generated: 2025-11-13                      │
├────────────────────────────────────────────┤
│                                            │
│ ## Executive Summary                       │ ← Heading 1
│ [Content with **bold** and *italic*]      │ ← Formatted text
│                                            │
│ ## Technical Approach                      │ ← Heading 1
│ ### Architecture Overview                  │ ← Heading 2
│ [Content...]                               │
│                                            │
│ ## Proposed Services                       │ ← Heading 1
│ [Content...]                               │
│                                            │
│ ### Service Matches (if Epic 6 complete)  │ ← Heading 2
│ ┌────────────┬─────────────┬───────────┐  │
│ │ Requirement│ Service     │ % Fit     │  │ ← Table
│ ├────────────┼─────────────┼───────────┤  │
│ │ 99.9% SLA  │ K8s Support │ 95%       │  │
│ │ ...        │ ...         │ ...       │  │
│ └────────────┴─────────────┴───────────┘  │
│                                            │
│ ## Timeline & Milestones                   │
│ [Content...]                               │
│                                            │
│ ## Pricing Structure                       │
│ [Content...]                               │
│                                            │
│ ## Risk Mitigation                         │
│ [Content...]                               │
└────────────────────────────────────────────┘
```

### 3. Export Service Implementation

**File:** `src/services/google_docs_exporter.py`

```python
"""Google Docs export service."""

import json
import re
from datetime import datetime
from typing import Optional, Dict, Any

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

try:
    from docx import Document
    from docx.shared import Pt, Inches
    from docx.enum.style import WD_STYLE_TYPE
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

from models import Draft, RFP


class GoogleDocsExporter:
    """Export drafts to Google Docs or .docx format."""
    
    SCOPES = [
        'https://www.googleapis.com/auth/documents',
        'https://www.googleapis.com/auth/drive'
    ]
    
    def __init__(self, credentials_json: Optional[str] = None):
        """
        Initialize exporter.
        
        Args:
            credentials_json: JSON string of service account credentials
        """
        self.credentials = None
        self.docs_service = None
        self.drive_service = None
        
        if credentials_json and GOOGLE_AVAILABLE:
            try:
                creds_dict = json.loads(credentials_json)
                self.credentials = service_account.Credentials.from_service_account_info(
                    creds_dict,
                    scopes=self.SCOPES
                )
                self.docs_service = build('docs', 'v1', credentials=self.credentials)
                self.drive_service = build('drive', 'v3', credentials=self.credentials)
            except (json.JSONDecodeError, Exception) as e:
                print(f"Failed to initialize Google credentials: {e}")
    
    def is_google_available(self) -> bool:
        """Check if Google Docs export is available."""
        return self.credentials is not None and self.docs_service is not None
    
    def export_to_google_docs(
        self,
        draft: Draft,
        rfp: Optional[RFP] = None,
        service_matches: Optional[list] = None,
        share_with_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Export draft to Google Docs.
        
        Args:
            draft: Draft object to export
            rfp: Optional RFP object for metadata
            service_matches: Optional list of approved service matches
            share_with_email: Optional email to share document with
        
        Returns:
            Dict with 'success', 'doc_id', 'doc_url', 'error'
        """
        if not self.is_google_available():
            return {
                'success': False,
                'error': 'Google Docs credentials not configured'
            }
        
        try:
            # 1. Create document
            doc_title = self._generate_doc_title(draft, rfp)
            doc = self.docs_service.documents().create(body={'title': doc_title}).execute()
            doc_id = doc.get('documentId')
            
            # 2. Build content requests
            requests = self._build_content_requests(draft, rfp, service_matches)
            
            # 3. Batch update document
            if requests:
                self.docs_service.documents().batchUpdate(
                    documentId=doc_id,
                    body={'requests': requests}
                ).execute()
            
            # 4. Set permissions (anyone with link can view)
            self.drive_service.permissions().create(
                fileId=doc_id,
                body={
                    'type': 'anyone',
                    'role': 'reader'
                }
            ).execute()
            
            # 5. Optional: Share with specific email
            if share_with_email:
                self.drive_service.permissions().create(
                    fileId=doc_id,
                    body={
                        'type': 'user',
                        'role': 'reader',
                        'emailAddress': share_with_email
                    },
                    sendNotificationEmail=True
                ).execute()
            
            doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
            
            return {
                'success': True,
                'doc_id': doc_id,
                'doc_url': doc_url,
                'title': doc_title
            }
        
        except HttpError as e:
            return {
                'success': False,
                'error': f"Google API error: {e}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Export failed: {str(e)}"
            }
    
    def export_to_docx(
        self,
        draft: Draft,
        rfp: Optional[RFP] = None,
        service_matches: Optional[list] = None
    ) -> Optional[bytes]:
        """
        Export draft to .docx format (fallback).
        
        Args:
            draft: Draft object to export
            rfp: Optional RFP object for metadata
            service_matches: Optional list of approved service matches
        
        Returns:
            Bytes of .docx file or None if failed
        """
        if not DOCX_AVAILABLE:
            return None
        
        try:
            doc = Document()
            
            # 1. Add title
            title = self._generate_doc_title(draft, rfp)
            doc.add_heading(title, level=0)
            
            # 2. Add RFP metadata
            if rfp:
                metadata = self._build_metadata_text(rfp)
                doc.add_paragraph(metadata)
                doc.add_paragraph()  # Blank line
            
            # 3. Parse and add draft content
            self._add_markdown_to_docx(doc, draft.content)
            
            # 4. Add service matches table if available
            if service_matches:
                doc.add_heading("Service Matches", level=2)
                self._add_matches_table_to_docx(doc, service_matches)
            
            # 5. Save to bytes
            from io import BytesIO
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            return buffer.getvalue()
        
        except Exception as e:
            print(f"Failed to create .docx: {e}")
            return None
    
    def _generate_doc_title(self, draft: Draft, rfp: Optional[RFP]) -> str:
        """Generate document title."""
        client_name = "Sample"
        if rfp and rfp.client_name:
            client_name = rfp.client_name
        elif draft.rfp_id:
            client_name = draft.rfp_id[:8]
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        title = f"RFP Draft - {client_name} - {date_str}"
        
        # Sanitize: Remove invalid characters
        title = re.sub(r'[<>:"/\\|?*]', '-', title)
        return title
    
    def _build_metadata_text(self, rfp: RFP) -> str:
        """Build RFP metadata header text."""
        lines = []
        if rfp.client_name:
            lines.append(f"Client: {rfp.client_name}")
        if rfp.deadline:
            lines.append(f"Deadline: {rfp.deadline.strftime('%Y-%m-%d')}")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        return "\n".join(lines)
    
    def _build_content_requests(
        self,
        draft: Draft,
        rfp: Optional[RFP],
        service_matches: Optional[list]
    ) -> list:
        """
        Build Google Docs API requests for content.
        
        Returns list of requests for batchUpdate.
        """
        requests = []
        index = 1  # Start after title
        
        # 1. Insert RFP metadata header
        if rfp:
            metadata_text = self._build_metadata_text(rfp)
            requests.append({
                'insertText': {
                    'location': {'index': index},
                    'text': metadata_text + '\n\n'
                }
            })
            index += len(metadata_text) + 2
        
        # 2. Parse and insert Markdown content
        content_requests, new_index = self._parse_markdown_to_requests(draft.content, index)
        requests.extend(content_requests)
        index = new_index
        
        # 3. Add service matches table if available
        if service_matches:
            table_requests, new_index = self._build_matches_table_requests(service_matches, index)
            requests.extend(table_requests)
            index = new_index
        
        return requests
    
    def _parse_markdown_to_requests(self, markdown: str, start_index: int) -> tuple:
        """
        Parse Markdown to Google Docs API requests.
        
        Returns (requests, end_index).
        """
        requests = []
        index = start_index
        
        lines = markdown.split('\n')
        
        for line in lines:
            line = line.rstrip()
            
            # Heading 1 (##)
            if line.startswith('## '):
                text = line[3:] + '\n'
                requests.append({
                    'insertText': {
                        'location': {'index': index},
                        'text': text
                    }
                })
                # Apply Heading 1 style
                requests.append({
                    'updateParagraphStyle': {
                        'range': {
                            'startIndex': index,
                            'endIndex': index + len(text)
                        },
                        'paragraphStyle': {
                            'namedStyleType': 'HEADING_1'
                        },
                        'fields': 'namedStyleType'
                    }
                })
                index += len(text)
            
            # Heading 2 (###)
            elif line.startswith('### '):
                text = line[4:] + '\n'
                requests.append({
                    'insertText': {
                        'location': {'index': index},
                        'text': text
                    }
                })
                # Apply Heading 2 style
                requests.append({
                    'updateParagraphStyle': {
                        'range': {
                            'startIndex': index,
                            'endIndex': index + len(text)
                        },
                        'paragraphStyle': {
                            'namedStyleType': 'HEADING_2'
                        },
                        'fields': 'namedStyleType'
                    }
                })
                index += len(text)
            
            # Bullet list (-)
            elif line.startswith('- '):
                text = line[2:] + '\n'
                requests.append({
                    'insertText': {
                        'location': {'index': index},
                        'text': text
                    }
                })
                # Apply bullet list
                requests.append({
                    'createParagraphBullets': {
                        'range': {
                            'startIndex': index,
                            'endIndex': index + len(text)
                        },
                        'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE'
                    }
                })
                index += len(text)
            
            # Normal paragraph
            else:
                if line:
                    text = line + '\n'
                    requests.append({
                        'insertText': {
                            'location': {'index': index},
                            'text': text
                        }
                    })
                    
                    # Apply bold/italic formatting
                    bold_requests = self._apply_inline_formatting(text, index)
                    requests.extend(bold_requests)
                    
                    index += len(text)
                else:
                    # Empty line
                    requests.append({
                        'insertText': {
                            'location': {'index': index},
                            'text': '\n'
                        }
                    })
                    index += 1
        
        return requests, index
    
    def _apply_inline_formatting(self, text: str, start_index: int) -> list:
        """Apply bold and italic formatting to text."""
        requests = []
        
        # Bold (**text**)
        bold_pattern = r'\*\*(.+?)\*\*'
        for match in re.finditer(bold_pattern, text):
            bold_text = match.group(1)
            match_start = start_index + match.start()
            match_end = match_start + len(match.group(0))
            
            requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': match_start,
                        'endIndex': match_end
                    },
                    'textStyle': {
                        'bold': True
                    },
                    'fields': 'bold'
                }
            })
        
        # Italic (*text*)
        italic_pattern = r'\*(.+?)\*'
        for match in re.finditer(italic_pattern, text):
            # Skip if it's part of **
            if text[match.start() - 1:match.start()] != '*' and text[match.end():match.end() + 1] != '*':
                match_start = start_index + match.start()
                match_end = match_start + len(match.group(0))
                
                requests.append({
                    'updateTextStyle': {
                        'range': {
                            'startIndex': match_start,
                            'endIndex': match_end
                        },
                        'textStyle': {
                            'italic': True
                        },
                        'fields': 'italic'
                    }
                })
        
        return requests
    
    def _build_matches_table_requests(self, service_matches: list, start_index: int) -> tuple:
        """Build requests for service matches table."""
        requests = []
        index = start_index
        
        # 1. Insert heading
        heading = "\nService Matches\n"
        requests.append({
            'insertText': {
                'location': {'index': index},
                'text': heading
            }
        })
        requests.append({
            'updateParagraphStyle': {
                'range': {
                    'startIndex': index,
                    'endIndex': index + len(heading)
                },
                'paragraphStyle': {
                    'namedStyleType': 'HEADING_2'
                },
                'fields': 'namedStyleType'
            }
        })
        index += len(heading)
        
        # 2. Insert table
        rows = len(service_matches) + 1  # +1 for header
        cols = 3
        
        requests.append({
            'insertTable': {
                'location': {'index': index},
                'rows': rows,
                'columns': cols
            }
        })
        
        # 3. Populate table (header + data)
        # Note: This is simplified - full implementation would use updateTableCellStyle
        # and insertText for each cell
        
        return requests, index + 10  # Approximate index after table
    
    def _add_markdown_to_docx(self, doc: Document, markdown: str):
        """Add Markdown content to .docx document."""
        lines = markdown.split('\n')
        
        for line in lines:
            line = line.rstrip()
            
            if line.startswith('## '):
                doc.add_heading(line[3:], level=1)
            elif line.startswith('### '):
                doc.add_heading(line[4:], level=2)
            elif line.startswith('- '):
                doc.add_paragraph(line[2:], style='List Bullet')
            elif line:
                # Simple paragraph (note: doesn't handle **bold** yet)
                doc.add_paragraph(line)
    
    def _add_matches_table_to_docx(self, doc: Document, service_matches: list):
        """Add service matches table to .docx."""
        table = doc.add_table(rows=1 + len(service_matches), cols=3)
        table.style = 'Light Grid Accent 1'
        
        # Header
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Requirement'
        hdr_cells[1].text = 'Matched Service'
        hdr_cells[2].text = '% Fit'
        
        # Data rows
        for i, match in enumerate(service_matches, start=1):
            row_cells = table.rows[i].cells
            row_cells[0].text = match.get('requirement_desc', '')[:50]
            row_cells[1].text = match.get('service_name', '')
            row_cells[2].text = f"{match.get('match_percentage', 0)}%"
```

### 4. UI Integration

**Location:** Update `pages/5_✍️_Draft_Generation.py` (renumbered from Epic 6)

```python
# ... existing imports ...
from services.google_docs_exporter import GoogleDocsExporter
import streamlit as st

def render_export_section(draft: Draft, rfp: Optional[RFP], service_matches: Optional[list]):
    """Render export options."""
    st.subheader("📤 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    # Existing exports
    with col1:
        if st.button("📝 Export Markdown", key="export_md"):
            st.download_button(
                "⬇️ Download .md",
                data=draft.content,
                file_name=f"draft_{draft.rfp_id}_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )
    
    with col2:
        if st.button("📋 Export JSON", key="export_json"):
            draft_json = json.dumps(draft.to_dict(), indent=2)
            st.download_button(
                "⬇️ Download .json",
                data=draft_json,
                file_name=f"draft_{draft.rfp_id}_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    
    # NEW: Google Docs Export
    with col3:
        if st.button("📄 Export to Google Docs", key="export_gdocs"):
            export_to_google_docs(draft, rfp, service_matches)

def export_to_google_docs(draft: Draft, rfp: Optional[RFP], service_matches: Optional[list]):
    """Handle Google Docs export with fallback."""
    
    # Confirmation dialog
    with st.expander("⚠️ Confirm Export", expanded=True):
        st.warning("This will create a new Google Doc. Continue?")
        
        # Optional: Email sharing
        share_email = st.text_input(
            "Share with email (optional)",
            placeholder="colleague@example.com",
            key="share_email"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, Export", key="confirm_export"):
                _do_google_export(draft, rfp, service_matches, share_email)
        with col2:
            if st.button("❌ Cancel", key="cancel_export"):
                st.rerun()

def _do_google_export(
    draft: Draft,
    rfp: Optional[RFP],
    service_matches: Optional[list],
    share_email: Optional[str]
):
    """Perform the actual Google Docs export."""
    
    # Initialize exporter
    credentials_json = None
    if 'GOOGLE_CREDENTIALS' in st.secrets:
        # Check if it's a dict or string
        creds = st.secrets['GOOGLE_CREDENTIALS']
        if isinstance(creds, dict):
            credentials_json = json.dumps(creds)
        else:
            credentials_json = creds
    
    exporter = GoogleDocsExporter(credentials_json)
    
    # Try Google Docs first
    if exporter.is_google_available():
        with st.spinner("📄 Creating Google Doc..."):
            result = exporter.export_to_google_docs(
                draft=draft,
                rfp=rfp,
                service_matches=service_matches,
                share_with_email=share_email if share_email else None
            )
        
        if result['success']:
            st.success(f"✅ Google Doc created: **{result['title']}**")
            st.markdown(f"🔗 [Open in Google Docs]({result['doc_url']})")
            if share_email:
                st.info(f"📧 Shared with: {share_email}")
        else:
            st.error(f"❌ Google Docs export failed: {result['error']}")
            st.info("💡 Trying fallback to .docx download...")
            _do_docx_export(exporter, draft, rfp, service_matches)
    else:
        st.warning("⚠️ Google credentials not configured. Using .docx fallback.")
        _do_docx_export(exporter, draft, rfp, service_matches)

def _do_docx_export(
    exporter: GoogleDocsExporter,
    draft: Draft,
    rfp: Optional[RFP],
    service_matches: Optional[list]
):
    """Fallback to .docx export."""
    with st.spinner("📄 Generating .docx file..."):
        docx_bytes = exporter.export_to_docx(draft, rfp, service_matches)
    
    if docx_bytes:
        filename = f"draft_{rfp.client_name if rfp else 'sample'}_{datetime.now().strftime('%Y%m%d')}.docx"
        st.download_button(
            label="⬇️ Download .docx",
            data=docx_bytes,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        st.success("✅ .docx file ready for download!")
    else:
        st.error("❌ Failed to generate .docx file. Please try exporting as Markdown.")
```

---

## 📋 Implementation Plan

### Phase 1: Dependencies & Setup (1 hour)

**Tasks:**
1. Add dependencies to `requirements.txt`:
   ```
   gspread>=5.12.0
   google-auth>=2.23.0
   google-api-python-client>=2.100.0
   python-docx>=1.1.0
   ```
2. Create `README-GOOGLE-DOCS-SETUP.md` with:
   - How to create Google Cloud service account
   - Enable Google Docs API and Drive API
   - Download service account JSON
   - Configure `st.secrets['GOOGLE_CREDENTIALS']`
3. Create sample `secrets.toml` template

**Deliverables:**
- Updated `requirements.txt`
- `README-GOOGLE-DOCS-SETUP.md`
- `.streamlit/secrets.toml.example`

### Phase 2: Export Service (5 hours)

**Tasks:**
1. Create `src/services/google_docs_exporter.py`
2. Implement `GoogleDocsExporter` class:
   - Authentication with service account
   - `export_to_google_docs()` method
   - `export_to_docx()` fallback method
   - Markdown parsing to Google Docs API requests
   - Document title generation with sanitization
   - Metadata header insertion
   - Service matches table creation
3. Handle errors gracefully (try/except)
4. Add inline formatting (bold, italic)

**Deliverables:**
- `src/services/google_docs_exporter.py` (complete implementation)

### Phase 3: UI Integration (3 hours)

**Tasks:**
1. Update `pages/5_✍️_Draft_Generation.py`:
   - Add "Export to Google Docs" button
   - Add confirmation dialog
   - Add optional email sharing input
   - Add progress spinner
   - Display success message with doc link
   - Handle fallback to .docx
2. Update page numbering (Service Matching = 3, Risk = 4, Draft = 5)
3. Test UI flow with mock credentials

**Deliverables:**
- Updated `pages/5_✍️_Draft_Generation.py`
- Updated sidebar page numbers

### Phase 4: Testing (4 hours)

**Tasks:**
1. Create unit tests for `GoogleDocsExporter`:
   - `test_doc_title_generation()` (with sanitization)
   - `test_metadata_text_building()`
   - `test_markdown_parsing()` (headings, lists, bold/italic)
   - `test_google_export()` (with mock Google API)
   - `test_docx_export()` (actual .docx generation)
   - `test_authentication_failure()` (fallback logic)
2. Create integration tests:
   - End-to-end with test service account
   - Verify document structure
   - Verify sharing permissions
3. Manual testing:
   - Short draft (<1000 words)
   - Long draft (>5000 words)
   - Draft with service matches table
   - Fallback to .docx

**Deliverables:**
- `tests/test_services/test_google_docs_exporter.py`
- `tests/test_integration/test_google_docs_export.py`
- Test coverage >80%

### Phase 5: Documentation (2 hours)

**Tasks:**
1. Update PRD with FR-011 details
2. Add troubleshooting section to README
3. Document common errors and solutions
4. Add video/screenshots of export flow

**Deliverables:**
- Updated `deliverables/prd-rfp-draft-booster.md`
- Updated main `README.md`
- Troubleshooting guide

**Total Estimated Effort:** 15 hours (~2 days)

---

## ⚠️ Risks & Mitigations

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Google API quota limits** | High - Export fails | Low | Implement exponential backoff, show quota error, offer .docx |
| **Large document timeout** | Medium - Export slow/fails | Medium | Add timeout (30s), show progress, chunk insertions |
| **Formatting inconsistencies** | Low - Ugly docs | Medium | Test with sample drafts, refine Markdown parsing |
| **Authentication failure** | High - No Google export | Medium | Graceful fallback to .docx, clear error messages |

### Integration Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Service matches table rendering** | Medium - Missing data | Low | Test Epic 6 integration, handle empty matches |
| **RFP metadata missing** | Low - Incomplete header | Low | Use defaults, handle None values |
| **Session state conflicts** | Low - Lost data | Low | Validate state before export |

### UX Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Confusing export options** | Low - User error | Low | Clear button labels, tooltips, confirmation dialog |
| **Slow export (>10s)** | Medium - Frustration | Medium | Progress spinner, time estimate |
| **No feedback on success** | Medium - Unclear status | Low | Success message with direct link |

---

## 🎯 Success Criteria

### Functional Requirements

- ✅ **FR-7.1:** "Export to Google Docs" button appears after draft generation
- ✅ **FR-7.2:** Clicking button shows confirmation dialog with optional email field
- ✅ **FR-7.3:** System authenticates with service account JSON from `st.secrets`
- ✅ **FR-7.4:** Document created with proper title format: "RFP Draft - {client} - {date}"
- ✅ **FR-7.5:** RFP metadata (client, deadline, generated date) appears as header
- ✅ **FR-7.6:** Markdown headings (## = H1, ### = H2) correctly applied
- ✅ **FR-7.7:** Inline formatting (bold, italic, lists) rendered correctly
- ✅ **FR-7.8:** Service matches table included if Epic 6 matches approved
- ✅ **FR-7.9:** Document shared with "anyone with link" (viewer permission)
- ✅ **FR-7.10:** Optional email sharing with viewer permission
- ✅ **FR-7.11:** Success message displays with direct link to Google Doc
- ✅ **FR-7.12:** Fallback to .docx download if Google auth fails

### Performance Requirements

- ⚡ **Export Speed:** <10 seconds for 5000-word draft
- 📄 **Document Size:** Support up to 50 pages (~12,500 words)
- 💾 **Memory:** <200MB during export

### Quality Requirements

- 🧪 **Test Coverage:** >80% for exporter service
- 📝 **Documentation:** Complete setup guide with screenshots
- 🔍 **Accuracy:** 95%+ formatting correctness (manual QA)

---

## 🚀 Future Enhancements (Post-MVP)

### Stretch Goals

1. **Update Existing Doc**
   - Save `doc_id` in session state
   - Offer "Update" vs. "Create New" option
   - Preserve comments and suggestions

2. **Template Selection**
   - Pre-defined BairesDev templates
   - Logo, header/footer, color scheme
   - Custom styles per client

3. **Collaborative Editing**
   - Share with team members automatically
   - Add comment with draft generation metadata
   - Track revisions

4. **PDF Export**
   - Use Google Docs API to export as PDF
   - Download or email directly

5. **Batch Export**
   - Export multiple drafts at once
   - Create folder structure in Drive
   - Summary dashboard

6. **Version Comparison**
   - Show diff between draft versions
   - Highlight changes in Google Doc
   - Rollback to previous version

---

## 📚 References

### Technical Documentation

- [Google Docs API - Create Document](https://developers.google.com/docs/api/how-tos/documents#create_a_document)
- [Google Docs API - Update Content](https://developers.google.com/docs/api/how-tos/documents#update_content)
- [Google Drive API - Permissions](https://developers.google.com/drive/api/v3/reference/permissions)
- [python-docx Documentation](https://python-docx.readthedocs.io/)
- [Service Account Authentication](https://cloud.google.com/iam/docs/service-accounts)

### Domain Documentation

- `src/models/draft.py` - Draft data model
- `src/models/rfp.py` - RFP data model
- `deliverables/EPIC-6-SERVICE-MATCHING-SPIKE.md` - Service matches integration

### Related Epics

- **Epic 5:** Draft Generation (provides draft content)
- **Epic 6:** Service Matching (provides matches table)
- **Epic 8 (Future):** Email Integration (send docs via email)

---

## ✅ Acceptance Checklist

Before marking Epic 7 complete:

- [ ] Dependencies added to `requirements.txt`
- [ ] `README-GOOGLE-DOCS-SETUP.md` created with setup instructions
- [ ] Sample `secrets.toml.example` provided
- [ ] `GoogleDocsExporter` class implemented
- [ ] Google Docs export working with test service account
- [ ] .docx fallback working without Google credentials
- [ ] Document title properly formatted and sanitized
- [ ] RFP metadata header included
- [ ] Markdown parsing correct (headings, bold, italic, lists)
- [ ] Service matches table rendered (if Epic 6 complete)
- [ ] Sharing permissions set correctly (anyone with link)
- [ ] Optional email sharing working
- [ ] Success message with doc link displayed
- [ ] Confirmation dialog working
- [ ] Export button placed correctly in UI
- [ ] Progress spinner shown during export
- [ ] Error handling for auth failures
- [ ] Unit tests pass with >80% coverage
- [ ] Integration tests verify end-to-end flow
- [ ] Manual testing with short and long drafts
- [ ] Documentation updated (PRD, README)
- [ ] Code reviewed and merged

---

## 📞 Questions & Clarifications

**Resolved:**
1. ✅ Scopes → `documents` + `drive`
2. ✅ Service account → Assume exists, document setup
3. ✅ Secrets format → JSON string, parse with `json.loads`
4. ✅ Document structure → Title, metadata header, H1/H2, bold/italic/lists
5. ✅ Fallback → `python-docx` for .docx download
6. ✅ Naming → "RFP Draft - {client} - {date}", sanitize invalid chars
7. ✅ UX → Button after exports, direct link, confirmation dialog, always new doc
8. ✅ Errors → Show error + fallback, no retry, no test button
9. ✅ Testing → Mock creds, test short/long drafts
10. ✅ Permissions → Viewer link, optional email sharing (viewer)
11. ✅ Dependencies → All in requirements.txt, try/except for optional
12. ✅ Epic 6 integration → Include matches table if approved (>80%)

**Open:**
- None

---

**Status:** ✅ Ready for Sprint Planning  
**Next Steps:** 
1. Review spike with team
2. Create Jira Epic 7 + user stories
3. Set up test Google Cloud project + service account
4. Assign to Sprint 5 or 6
5. Begin implementation

---

**Author:** AI Assistant  
**Reviewed By:** TBD  
**Approved By:** TBD

