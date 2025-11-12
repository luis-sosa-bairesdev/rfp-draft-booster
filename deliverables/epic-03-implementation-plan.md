# Epic 3: LLM Requirement Extraction - Implementation Plan

## 📊 Overview

**Epic:** RDBP-21 - LLM Requirement Extraction  
**Sprint:** Sprint 2  
**Stories:** 10 (RDBP-22 to RDBP-31)  
**Story Points:** 65  
**Status:** ✅ Sprint 2 Aligned - Ready to Implement

---

## 🎯 Implementation Strategy

### Phase 1: Core Infrastructure (Stories 1-2)
**RDBP-22 & RDBP-23** - AI Extraction + Categorization

1. Create `Requirement` data model
2. Implement LLM client (Gemini/Groq)
3. Create prompt templates
4. Implement extraction service
5. Add categorization logic

### Phase 2: Enhancement & Metadata (Stories 3-5)
**RDBP-24, RDBP-25, RDBP-26** - Prioritization + Confidence + Page Numbers

1. Add prioritization logic
2. Implement confidence scoring
3. Track source page numbers
4. Enhance response parsing

### Phase 3: UI & Display (Story 6-7)
**RDBP-27, RDBP-28, RDBP-29** - Edit + Add + Delete

1. Create Requirements page
2. Display requirements in table
3. Implement edit functionality
4. Add manual requirement creation
5. Add delete functionality

### Phase 4: Polish & Filtering (Stories 8-10)
**RDBP-30, RDBP-31** - Verification + Filtering

1. Add verification checkboxes
2. Implement category filters
3. Implement priority filters
4. Add search functionality

---

## 📁 File Structure

```
src/
├── models/
│   └── requirement.py          # NEW - Requirement data model
├── services/
│   ├── llm_client.py           # NEW - LLM integration (Gemini/Groq)
│   ├── requirement_extractor.py # NEW - Main extraction service
│   └── text_chunker.py         # NEW - Text chunking for large RFPs
└── utils/
    └── prompt_templates.py     # NEW - LLM prompts

pages/
└── 2_📋_Requirements.py        # UPDATE - Requirements display & management

tests/
├── test_llm_client.py          # NEW - LLM client tests
├── test_requirement_extractor.py # NEW - Extractor tests
└── test_requirement_model.py   # NEW - Model tests

requirements.txt                # UPDATE - Add langchain, google-generativeai, groq
```

---

## 🔧 Technical Implementation Details

### 1. Requirement Model

```python
@dataclass
class Requirement:
    id: str
    rfp_id: str
    description: str
    category: RequirementCategory  # technical, functional, timeline, budget, compliance
    priority: RequirementPriority  # critical, high, medium, low
    confidence: float  # 0.0-1.0
    page_number: Optional[int]
    verified: bool = False
    created_at: datetime
    updated_at: datetime
```

### 2. LLM Client

```python
class LLMClient:
    def __init__(self, provider="gemini"):
        # Support multiple providers: gemini, groq, ollama
        
    def extract_requirements(self, text: str, context: dict) -> list[Requirement]:
        # Send prompt to LLM
        # Parse JSON response
        # Return structured requirements
```

### 3. Requirement Extractor

```python
class RequirementExtractor:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.chunker = TextChunker()
        
    def extract_from_rfp(self, rfp: RFP) -> list[Requirement]:
        # Chunk text if needed
        # Call LLM for each chunk
        # Merge and deduplicate results
        # Return all requirements
```

### 4. Prompt Template

```python
EXTRACTION_PROMPT = """
You are an expert at analyzing Request for Proposals (RFPs) and extracting key requirements.

Analyze the following RFP section and extract ALL requirements.

RFP Text:
{rfp_text}

For each requirement, provide:
1. category: technical | functional | timeline | budget | compliance
2. description: Clear, complete requirement description
3. priority: critical | high | medium | low
4. confidence: Your confidence in this extraction (0.0-1.0)
5. page_number: Source page number (if available)

Return as a JSON array with this structure:
[
  {
    "category": "technical",
    "description": "Solution must support 99.9% uptime",
    "priority": "critical",
    "confidence": 0.95,
    "page_number": 3
  },
  ...
]

IMPORTANT:
- Extract EVERY requirement you find
- Be specific and complete in descriptions
- Use exact category and priority values
- Provide realistic confidence scores
"""
```

---

## 📝 Story-by-Story Implementation

### ✅ RDBP-22: AI extracts requirements from RFP automatically (13 pts)

**Files to Create:**
- `src/models/requirement.py`
- `src/services/llm_client.py`
- `src/services/requirement_extractor.py`
- `src/utils/prompt_templates.py`

**Dependencies:**
- `langchain`
- `google-generativeai` (Gemini)
- `groq` (fallback)

**Testing:**
- Unit tests for LLM client
- Integration tests with sample RFP
- Mock LLM responses for testing

---

### ✅ RDBP-23: Requirements categorized (8 pts)

**Enhancements:**
- Add category validation
- Create category enum
- Add category-specific prompts

**Categories:**
- Technical
- Functional
- Timeline
- Budget
- Compliance

---

### ✅ RDBP-24: Requirements prioritized (5 pts)

**Enhancements:**
- Add priority logic to prompt
- Create priority enum
- Implement priority scoring

**Priorities:**
- Critical
- High
- Medium
- Low

---

### ✅ RDBP-25: Confidence scores for each extraction (5 pts)

**Enhancements:**
- Parse confidence from LLM
- Validate confidence range (0.0-1.0)
- Add confidence threshold filtering

---

### ✅ RDBP-26: Show source page numbers for requirements (3 pts)

**Enhancements:**
- Track page numbers during extraction
- Display page numbers in UI
- Link to source page

---

### ✅ RDBP-27: Edit extracted requirements (5 pts)

**Files to Update:**
- `pages/2_📋_Requirements.py`

**Features:**
- Inline editing in table
- Update requirement description
- Update category/priority
- Save changes to session state

---

### ✅ RDBP-28: Add requirements manually (5 pts)

**Features:**
- "Add Requirement" button
- Form with all fields
- Validate inputs
- Add to requirements list

---

### ✅ RDBP-29: Delete incorrect extractions (3 pts)

**Features:**
- Delete button per requirement
- Confirmation dialog
- Remove from list
- Update counts

---

### ✅ RDBP-30: Mark requirements as verified (3 pts)

**Features:**
- Verification checkbox per requirement
- Track verification status
- Show verification progress

---

### ✅ RDBP-31: Filter requirements by category/priority (5 pts)

**Features:**
- Category multi-select filter
- Priority multi-select filter
- Search by description
- Clear filters button

---

## 🧪 Testing Strategy

### Unit Tests
- `test_requirement_model.py` - Model validation
- `test_llm_client.py` - LLM integration
- `test_requirement_extractor.py` - Extraction logic
- `test_text_chunker.py` - Text chunking

### Integration Tests
- End-to-end RFP processing
- LLM API integration
- UI interactions

### Manual Testing
- Upload real RFP
- Verify extraction quality
- Test all CRUD operations
- Verify filtering works

---

## 📦 Dependencies to Add

```txt
# LLM & AI
langchain>=0.1.0
google-generativeai>=0.3.0
groq>=0.4.0

# Optional: Local LLM
# ollama>=0.1.0
```

---

## 🎯 Success Criteria

- [ ] All 10 stories implemented and tested
- [ ] Requirements extracted from RFP with >85% accuracy
- [ ] All categories and priorities assigned correctly
- [ ] Confidence scores provided for all requirements
- [ ] Page numbers tracked and displayed
- [ ] CRUD operations working smoothly
- [ ] Filtering by category/priority functional
- [ ] Verification workflow complete
- [ ] Unit test coverage >80%
- [ ] Integration tests passing

---

## 🚀 Getting Started

### Step 1: Environment Setup
```bash
# Add new dependencies
pip install langchain google-generativeai groq

# Set up API keys in .env
echo "GEMINI_API_KEY=your_key_here" >> .env
echo "GROQ_API_KEY=your_key_here" >> .env
```

### Step 2: Start with RDBP-22
1. Create Requirement model
2. Implement LLM client
3. Create extraction service
4. Test with sample RFP

### Step 3: Build Iteratively
- Implement 1-2 stories per day
- Test each story before moving on
- Commit after each story completion

---

## 📊 Progress Tracking

| Story | Key | Status | Assignee |
|-------|-----|--------|----------|
| 1 | RDBP-22 | To Do | - |
| 2 | RDBP-23 | To Do | - |
| 3 | RDBP-24 | To Do | - |
| 4 | RDBP-25 | To Do | - |
| 5 | RDBP-26 | To Do | - |
| 6 | RDBP-27 | To Do | - |
| 7 | RDBP-28 | To Do | - |
| 8 | RDBP-29 | To Do | - |
| 9 | RDBP-30 | To Do | - |
| 10 | RDBP-31 | To Do | - |

---

**Created:** 2025-11-10  
**Last Updated:** 2025-11-10  
**Status:** Ready to Start Implementation

