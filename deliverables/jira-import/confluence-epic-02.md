# Epic 2: PDF Processing & Upload

> **Status:** To Do | **Priority:** High | **Points:** 42
> 
> **JIRA Epic:** [SCRUM-32](https://luis-sosa-bairesdev.atlassian.net/browse/SCRUM-32)
> 
> **Timeline:** Nov 18 - Nov 29, 2025 | **Owner:** Luis Sosa

---

## 📋 Executive Summary

Build the PDF upload and text extraction functionality that allows sales reps to upload RFP documents and extract text content for downstream processing. This includes file validation, upload progress tracking, text extraction, and error handling.

### Quick Stats
- **Total Story Points:** 42
- **Number of Stories:** 8
- **Must-Have Stories:** 6 (34 points)
- **Should-Have Stories:** 2 (8 points)
- **Sprint:** Sprint 2-3 (Weeks 2-3)
- **Depends On:** Epic 1 ✅

---

## 🎯 Business Value

### Problem Being Solved

Sales reps spend 5-8 hours manually reading through 50-100 page RFP PDFs. Automated text extraction is the first critical step in the automation pipeline that will save significant time and reduce errors.

### Expected Benefits

| Benefit | Description | Impact |
|---------|-------------|--------|
| **Automated Extraction** | No manual transcription needed | High |
| **Fast Processing** | Extract text from 100-page PDFs in under 30 seconds | High |
| **Quality Validation** | Ensure PDFs contain extractable text before processing | Medium |
| **User-Friendly** | Simple drag-and-drop upload interface | High |

### Success Metrics

| Metric | Target | How Measured |
|--------|--------|--------------|
| **Upload Success Rate** | > 95% | Successful uploads / total attempts |
| **Extraction Speed** | < 30 seconds | Time for 100-page PDF |
| **Extraction Accuracy** | > 98% | Manual spot-check of text quality |
| **User Satisfaction** | > 4.0/5.0 | User feedback surveys |

---

## 📦 User Stories

### Must-Have Stories (P0) - 34 Points

#### 1. [SCRUM-33] Upload RFP PDFs via drag-and-drop (5 pts)
**Priority:** Highest

Create intuitive file upload interface with drag-and-drop functionality.

**Key Features:**
- Drag-and-drop file upload
- Browse button alternative
- Single file upload at a time
- Clear instructions and help text

**Tech:** Streamlit file_uploader, session state management

---

#### 2. [SCRUM-34] File validation (type and size) (3 pts)
**Priority:** Highest

Validate uploaded files before processing.

**Validation Rules:**
- File type must be PDF (.pdf)
- File size max 50MB
- MIME type: application/pdf
- Clear, actionable error messages

**Tech:** python-magic for type detection, custom validation exceptions

---

#### 3. [SCRUM-35] Upload progress indicator (5 pts)
**Priority:** High

Show real-time progress during upload and processing.

**Progress Stages:**
1. Uploading (0-30%)
2. Validating (30-40%)
3. Extracting (40-90%)
4. Finalizing (90-100%)

**Tech:** st.progress(), st.spinner(), session state tracking

---

#### 4. [SCRUM-36] Automatic text extraction from PDFs (13 pts)
**Priority:** Highest

Extract text content from PDF documents automatically.

**Requirements:**
- Extract text from selectable-text PDFs
- Preserve basic structure (paragraphs, line breaks)
- Track page numbers for each section
- Handle multi-column layouts
- Process up to 100 pages
- Complete within 30 seconds
- UTF-8 encoding support

**Tech:** PyPDF2 (primary), pdfplumber (fallback), PDFProcessor service class

---

#### 5. [SCRUM-37] Clear error messages for extraction failures (5 pts)
**Priority:** High

Provide user-friendly error messages when extraction fails.

**Error Cases:**
- Scanned PDFs (no selectable text)
- Corrupted PDF files
- Password-protected PDFs
- Unexpected extraction errors

**Error Message Examples:**
```
"This PDF appears to be scanned (images only). 
Please use a PDF with selectable text, or contact 
support for OCR options."
```

---

#### 6. [SCRUM-38] Extracted text preview display (5 pts)
**Priority:** High

Display preview of extracted text for quality verification.

**Features:**
- Show first 500-1000 characters
- Display statistics (pages, words, characters)
- Expandable view for full text
- Download full text option
- Read-only formatted display

---

### Should-Have Stories (P1) - 8 Points

#### 7. [SCRUM-39] Add RFP metadata (client name, deadline) (5 pts)
**Priority:** Medium

Capture and store RFP metadata for organization.

**Metadata Fields:**
- RFP title (required)
- Client name (optional)
- Deadline (optional)
- Notes (optional)
- Auto-populate title from filename

**Tech:** Streamlit forms, date picker, RFP dataclass

---

#### 8. [SCRUM-40] Cancel uploads in progress (3 pts)
**Priority:** Medium

Allow users to cancel uploads and clean up properly.

**Features:**
- Cancel button visible during upload
- Immediate stop of processing
- Cleanup of partial uploads
- Session state reset
- Confirmation message

---

## 🏗️ Technical Architecture

### PDF Upload Flow

```
User Upload
    ↓
File Validation
    ↓
Storage (data/uploads/)
    ↓
Text Extraction
    ↓
Display Results
```

### Key Components

1. **File Upload Handler**
   - Streamlit file_uploader widget
   - Drag-and-drop interface
   - File validation logic

2. **PDF Parser**
   - PyPDF2 for standard extraction
   - pdfplumber for complex layouts
   - Page tracking and metadata

3. **Storage Manager**
   - Save PDFs to data/uploads/
   - Organize by upload date
   - Cleanup old files

4. **RFP Model**
   - Dataclass for RFP data
   - Metadata storage
   - Text content with page info

5. **Session State Manager**
   - Track current RFP
   - Progress tracking
   - Error state management

### Technology Stack

- **Streamlit:** file_uploader, progress, spinner
- **PyPDF2:** PDF text extraction
- **pdfplumber:** Advanced layout preservation
- **python-magic:** File type detection
- **dataclasses:** RFP model
- **JSON:** Metadata storage

### File Structure

```python
@dataclass
class RFP:
    id: str
    title: str
    client_name: Optional[str]
    deadline: Optional[date]
    uploaded_at: datetime
    file_path: str
    file_size: int
    page_count: int
    extracted_text: Dict[int, str]  # {page_num: text}
    metadata: Dict[str, Any]
```

---

## 📅 Timeline

**Sprint 2-3 (Weeks 2-3): Nov 18-29, 2025**

### Week 2: Core Upload & Extraction
- **Day 1-2:** File upload and validation (SCRUM-33, SCRUM-34)
- **Day 3:** Progress indicators (SCRUM-35)
- **Day 4-5:** Text extraction (SCRUM-36)

### Week 3: Polish & Metadata
- **Day 1:** Error handling (SCRUM-37)
- **Day 2:** Text preview (SCRUM-38)
- **Day 3:** Metadata capture (SCRUM-39)
- **Day 4:** Cancel functionality (SCRUM-40)
- **Day 5:** Testing and bug fixes

---

## 🔗 Dependencies

### Prerequisites
- ✅ **SCRUM-1:** Project Setup & Infrastructure (Completed)

### Blocks
- **Epic 3:** LLM Requirement Extraction (needs extracted text)
- **Epic 4:** Risk Detection (needs PDF text)

---

## ⚠️ Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Scanned PDFs fail extraction** | High | High | Clear error message, suggest OCR in Phase 2 |
| **Large files timeout** | Medium | Medium | Set 50MB limit, streaming upload |
| **Complex layouts lose structure** | Medium | Medium | Use pdfplumber for better layout preservation |
| **Special characters corrupted** | Low | Low | UTF-8 encoding, test with diverse PDFs |

---

## ✅ Acceptance Criteria (Epic Level)

- [ ] Users can drag-and-drop or browse to select PDF files
- [ ] System validates file type and size before upload
- [ ] Upload progress bar shows real-time progress
- [ ] PDFs with extractable text successfully extracted
- [ ] Extracted text preserves basic structure
- [ ] Page numbers tracked for reference
- [ ] Error messages clear and actionable
- [ ] RFP metadata captured and stored
- [ ] Uploaded files saved to data/uploads/
- [ ] Session state tracks current RFP

---

## 📊 Progress Dashboard

**Status:** To Do (0% Complete)

| Status | Count | Points | Percentage |
|--------|-------|--------|------------|
| ✅ Done | 0 | 0 | 0% |
| 🔄 In Progress | 0 | 0 | 0% |
| 📋 To Do | 8 | 42 | 100% |
| **Total** | **8** | **42** | **100%** |

---

## 🔗 Related Links

- **JIRA Epic:** [SCRUM-32](https://luis-sosa-bairesdev.atlassian.net/browse/SCRUM-32)
- **Previous Epic:** [Epic 1: Project Setup](../epic-01-project-setup.md)
- **Next Epic:** [Epic 3: LLM Requirement Extraction](../epic-03-llm-requirement-extraction.md)
- **PRD Section:** [FR-001, FR-002](../prd-rfp-draft-booster.md#fr-001-pdf-upload)
- **Domain Entity:** [RFP Entity](../../domain/rfp-entity.md)

---

## 📝 Notes

- Focus on PDFs with extractable text (no OCR in Phase 1)
- Scanned PDF support deferred to Phase 2
- File size limit set at 50MB for MVP
- PyPDF2 as primary, pdfplumber as fallback
- All text stored with page metadata for reference

---

## 📞 Contact & Support

- **Epic Owner:** Luis Sosa (luis.sosa@bairesdev.com)
- **Tech Lead:** TBD
- **Product Owner:** TBD
- **Slack Channel:** #rfp-draft-booster

---

**Last Updated:** 2025-11-07  
**Version:** 1.0  
**Status:** To Do
