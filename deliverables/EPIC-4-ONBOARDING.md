# Epic 4: Risk Detection & Analysis - Onboarding Guide

> **For New AI Agent:** This document provides everything you need to start implementing Epic 4

---

## 📋 Quick Context

**Project:** RFP Draft Booster  
**Current Status:** Epic 1-3 ✅ Completed | Epic 4 ⏳ Ready to Start  
**Epic 4 Key:** RDBP-4 (to be created in Jira)  
**Story Points:** 55  
**Sprint:** Sprint 3 (to be created)  
**Dependencies:** Epic 2 ✅ (needs extracted RFP text)

---

## 🎯 Epic 4 Overview

**Goal:** Identify problematic clauses in RFPs using pattern matching and AI, with severity classification and actionable recommendations.

**Business Value:**
- Early risk flagging before contract negotiation
- Prevent costly contract issues
- Improve proposal quality with risk-aware responses

**Key Features:**
- 🔍 Automatic risk detection (pattern + AI)
- 📊 Risk categorization (legal, financial, timeline, technical, compliance)
- 🎯 Severity classification (critical, high, medium, low)
- 💡 Mitigation recommendations
- ✏️ Alternative language suggestions
- ✅ Risk acknowledgment tracking

---

## 📚 Essential Documentation

### Must-Read Documents

1. **PRD (Product Requirements Document)**
   - Location: `deliverables/prd-rfp-draft-booster.md`
   - Section: FR-005 (Risk Detection)
   - Key info: Business requirements, user stories, acceptance criteria

2. **Epic Summary**
   - Location: `deliverables/epic-summary.md`
   - Epic 4 overview: Lines 36-41
   - Dependencies: Epic 4 depends on Epic 2

3. **Completed Epics (Reference)**
   - Epic 1: `deliverables/epic-01-project-setup.md`
   - Epic 2: `deliverables/epic-02-pdf-processing.md` + `deliverables/jira-import/confluence-epic-02.md`
   - Epic 3: `deliverables/epic-03-llm-requirement-extraction.md` + `deliverables/jira-import/confluence-epic-03.md`

### Codebase Structure

```
rfp-draft-booster/
├── src/
│   ├── models/
│   │   ├── rfp.py              # RFP model (has extracted_text)
│   │   └── requirement.py      # Requirement model (Epic 3)
│   ├── services/
│   │   ├── llm_client.py       # LLM integration (reusable for Epic 4)
│   │   ├── requirement_extractor.py  # Epic 3 - similar pattern for risks
│   │   └── pdf_processor.py   # Epic 2 - text extraction
│   └── utils/
│       ├── session.py          # Streamlit session management
│       └── prompt_templates.py # LLM prompts (add risk detection prompts)
├── pages/
│   ├── 1_📤_Upload_RFP.py     # Epic 2 ✅
│   ├── 2_📋_Requirements.py   # Epic 3 ✅
│   └── 3_⚠️_Risk_Analysis.py  # Epic 4 - PLACEHOLDER (needs implementation)
├── tests/
│   ├── test_models/           # Model tests
│   ├── test_services/          # Service tests
│   └── test_ui/               # UI tests
└── deliverables/
    └── jira-import/            # Jira/Confluence scripts
```

---

## 🏗️ Technical Architecture (Epic 4)

### Similar Pattern to Epic 3

Epic 4 should follow the same architecture pattern as Epic 3:

```
RFP Text → Risk Detection (Pattern + AI) → Risk Objects → Display in UI
                                              ↓
                                    Categorization
                                    Severity Assessment
                                    Recommendations
```

### Key Components to Create

1. **Risk Model** (`src/models/risk.py`)
   - Similar to `Requirement` model
   - Fields: id, rfp_id, clause_text, category, severity, confidence, page_number, recommendation, alternative_language, acknowledged, etc.

2. **Risk Detector Service** (`src/services/risk_detector.py`)
   - Pattern-based detection (regex patterns for common risk clauses)
   - AI-powered detection (using LLM similar to requirement extraction)
   - Similar to `RequirementExtractor`

3. **Risk Prompts** (`src/utils/prompt_templates.py`)
   - Add risk detection prompt template
   - Similar to `EXTRACTION_PROMPT_TEMPLATE`

4. **Risk Analysis UI** (`pages/3_⚠️_Risk_Analysis.py`)
   - Similar structure to `pages/2_📋_Requirements.py`
   - Display risks in table
   - Filter by category/severity
   - Show recommendations
   - Allow acknowledgment

---

## 🔑 Key Technical Decisions (From Previous Epics)

### LLM Integration
- **Primary Provider:** Google Gemini 2.5 Flash
- **Fallback:** Groq, Ollama
- **Client:** `src/services/llm_client.py` (reusable)
- **Pattern:** Use `create_llm_client()` helper function

### Session State
- **Manager:** `src/utils/session.py`
- **Pattern:** Store risks in `st.session_state.risks = []`
- **Helper:** `get_current_rfp()` to access current RFP

### Testing
- **Framework:** pytest
- **Coverage Target:** 80%+
- **Structure:** Mirror Epic 3 test structure
- **Location:** `tests/test_services/test_risk_detector.py`, `tests/test_models/test_risk.py`, `tests/test_ui/test_risk_analysis_page.py`

### Code Style
- **Language:** All code in English
- **Logging:** DEBUG level by default
- **JSON:** snake_case convention
- **Imports:** Relative imports (e.g., `from models import Risk`)

---

## 📝 User Stories (To Be Created in Jira)

Based on PRD and Epic 3 pattern, Epic 4 should have:

### Backend Stories (~30 points)
- Risk detection using pattern matching
- AI-powered risk detection
- Risk categorization (5 categories)
- Severity classification (4 levels)
- Confidence scoring
- Page number tracking

### UI Stories (~20 points)
- Display risks in table
- Filter by category/severity
- Show recommendations
- Show alternative language
- Risk acknowledgment
- Export risks

### Testing Stories (~5 points)
- Unit tests for Risk model
- Unit tests for Risk Detector
- Integration tests
- UI tests

**Total:** ~55 story points

---

## 🚀 Getting Started Checklist

### Before Starting Implementation

- [ ] Read PRD section FR-005 (Risk Detection)
- [ ] Review Epic 3 implementation (`confluence-epic-03.md`)
- [ ] Understand `Requirement` model structure (similar for Risk)
- [ ] Review `RequirementExtractor` service (similar pattern)
- [ ] Check existing `pages/3_⚠️_Risk_Analysis.py` placeholder
- [ ] Verify Epic 2 completion (RFP text extraction works)

### Implementation Steps

1. **Create Risk Model** (`src/models/risk.py`)
   - Define `RiskCategory` enum (legal, financial, timeline, technical, compliance)
   - Define `RiskSeverity` enum (critical, high, medium, low)
   - Create `Risk` Pydantic model

2. **Create Risk Detector Service** (`src/services/risk_detector.py`)
   - Pattern-based detection (regex patterns)
   - AI-powered detection (LLM integration)
   - Similar to `RequirementExtractor`

3. **Add Risk Prompts** (`src/utils/prompt_templates.py`)
   - `RISK_DETECTION_PROMPT_TEMPLATE`
   - Include examples of risk clauses

4. **Implement Risk Analysis UI** (`pages/3_⚠️_Risk_Analysis.py`)
   - Similar to Requirements page
   - Display risks table
   - Filtering and sorting
   - Recommendations display
   - Acknowledgment tracking

5. **Create Tests**
   - Model tests
   - Service tests
   - UI tests
   - Target: 80%+ coverage

6. **Jira & Confluence**
   - Create Epic 4 in Jira (RDBP project)
   - Create user stories
   - Create Confluence documentation

---

## 🔗 Important Links

- **Jira Project:** https://luis-sosa-bairesdev.atlassian.net/jira/software/projects/RDBP/boards/34
- **Confluence Space:** https://luis-sosa-bairesdev.atlassian.net/wiki/spaces/~712020bfc89abf8f5841728f3bd48d6a60043a
- **GitHub Repo:** https://github.com/luis-sosa-bairesdev/rfp-draft-booster
- **Epic 3 Confluence:** See `deliverables/jira-import/confluence-epic-03.md` for documentation format

---

## 💡 Key Learnings from Epic 3

1. **LLM Integration:** Use `create_llm_client()` helper with fallback
2. **Error Handling:** Robust error messages for users
3. **Session State:** Store extracted data in `st.session_state`
4. **Testing:** Write tests alongside implementation
5. **Documentation:** Keep Confluence updated as you progress

---

## ⚠️ Common Pitfalls to Avoid

1. **Don't reinvent the wheel:** Reuse Epic 3 patterns
2. **Don't skip tests:** Maintain 80%+ coverage
3. **Don't forget Jira:** Create stories and track progress
4. **Don't ignore errors:** Handle LLM failures gracefully
5. **Don't forget Confluence:** Document as you go

---

## 📞 Questions?

If you need clarification:
1. Check Epic 3 implementation (similar pattern)
2. Review PRD for business requirements
3. Check existing codebase for patterns
4. Ask the user for clarification on requirements

---

## ✅ Success Criteria

Epic 4 is complete when:
- [ ] All user stories implemented
- [ ] Risk detection working (pattern + AI)
- [ ] UI fully functional
- [ ] 80%+ test coverage
- [ ] All stories closed in Jira
- [ ] Confluence documentation complete

---

**Last Updated:** 2025-11-12  
**Status:** Ready for Implementation  
**Next Steps:** Create Epic 4 in Jira and start implementation

