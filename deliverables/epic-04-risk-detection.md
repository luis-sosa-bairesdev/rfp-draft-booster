# Epic 4: Risk Detection & Analysis

## Epic Information

- **Epic Key:** RDBP-4
- **Epic Name:** [EPIC] Risk Detection & Analysis
- **Status:** Done
- **Priority:** High
- **Owner:** Tech Lead
- **Start Date:** 2025-11-13
- **Target Date:** 2025-11-27

---

## Summary

Identify problematic clauses in RFPs using pattern matching and AI, with severity classification and actionable recommendations. Enable early risk flagging before contract negotiation, prevent costly contract issues, and improve proposal quality with risk-aware responses.

---

## Business Value

### Problem Being Solved

Sales teams need to identify contractual risks in RFPs early in the proposal process to avoid costly issues during negotiation or contract execution. Manual risk review is time-consuming, inconsistent, and often misses critical clauses.

### Expected Benefits

- **Early Risk Detection:** Identify problematic clauses before contract negotiation
- **Cost Prevention:** Avoid costly contract issues and disputes
- **Proposal Quality:** Improve responses with risk-aware recommendations
- **Consistency:** Standardized risk assessment across all RFPs
- **Time Savings:** Automated risk detection reduces manual review time

### Success Metrics

| Metric | Target | How Measured |
|--------|--------|--------------|
| Risk Detection Accuracy | > 85% | Manual validation against detected risks |
| False Positive Rate | < 15% | Review of flagged clauses |
| Time Savings | 60% reduction | Time to complete risk review |
| Critical Risks Caught | 100% | No critical risks missed in sample RFPs |

---

## User Stories

### Backend Stories (44 points)

- [x] **RDBP-37:** Detect risks using regex patterns for common problematic clauses (8 points)
- [x] **RDBP-38:** Detect risks using LLM analysis for complex clauses (13 points)
- [x] **RDBP-39:** Categorize detected risks into 5 categories (5 points)
- [x] **RDBP-40:** Assign severity levels to detected risks (5 points)
- [x] **RDBP-41:** Generate mitigation recommendations for detected risks (8 points)
- [x] **RDBP-42:** Suggest alternative clause language for detected risks (5 points)

### UI Stories (26 points)

- [x] **RDBP-43:** Display detected risks in sortable table (8 points)
- [x] **RDBP-44:** Filter risks by category and severity (5 points)
- [x] **RDBP-45:** Allow users to acknowledge risks (8 points)
- [x] **RDBP-46:** Show mitigation recommendations and alternative language (5 points)

### Testing Stories (11 points)

- [x] **RDBP-47:** Unit tests for Risk model (3 points)
- [x] **RDBP-48:** Unit tests for Risk Detector service (5 points)
- [x] **RDBP-49:** UI tests for Risk Analysis page (3 points)

**Total Story Points:** 81

---

## Technical Overview

### Architecture

Epic 4 follows the same architecture pattern as Epic 3 (Requirements Extraction):

```
RFP Text → Risk Detection (Pattern + AI) → Risk Objects → Display in UI
                                              ↓
                                    Categorization
                                    Severity Assessment
                                    Recommendations
```

### Key Components

1. **Risk Model** (`src/models/risk.py`)
   - RiskCategory enum (legal, financial, timeline, technical, compliance)
   - RiskSeverity enum (critical, high, medium, low)
   - Risk dataclass with fields: clause_text, category, severity, confidence, page_number, recommendation, alternative_language, acknowledged

2. **Risk Detector Service** (`src/services/risk_detector.py`)
   - Pattern-based detection (regex patterns for common risk clauses)
   - AI-powered detection (using LLM similar to requirement extraction)
   - Confidence scoring and deduplication

3. **Risk Prompts** (`src/utils/prompt_templates.py`)
   - RISK_DETECTION_PROMPT_TEMPLATE
   - Context-aware risk analysis

4. **Risk Analysis UI** (`pages/3_⚠️_Risk_Analysis.py`)
   - Display risks in table
   - Filter by category/severity
   - Show recommendations and alternative language
   - Risk acknowledgment tracking

### Technology Stack

- Python 3.10+
- Google Gemini 2.5 Flash (primary LLM)
- Streamlit for UI
- Pydantic for data models
- pytest for testing

---

## Dependencies

### Internal Dependencies

- **Epic 2:** PDF Processing & Upload ✅ (requires extracted RFP text)
- **Epic 3:** LLM Requirement Extraction ✅ (reuses LLM client pattern)

### External Dependencies

- LLM API access (Google Gemini)
- RFP text extraction working

---

## Implementation Details

### Risk Categories

1. **Legal:** Liability clauses, indemnification, IP rights
2. **Financial:** Payment terms, penalties, pricing constraints
3. **Timeline:** Unrealistic deadlines, fixed delivery dates
4. **Technical:** Technology constraints, platform requirements
5. **Compliance:** Regulatory requirements, certifications

### Severity Levels

1. **Critical:** Show-stopper issues, deal-breaking clauses
2. **High:** Major risks requiring senior management review
3. **Medium:** Significant risks requiring mitigation
4. **Low:** Minor risks or standard clauses

### Pattern-Based Detection

Common risk patterns detected via regex:
- Unlimited liability clauses
- Payment terms > 60 days
- Exclusivity requirements
- Non-compete clauses
- Auto-renewal terms
- Penalty clauses

### AI-Powered Detection

LLM analysis for:
- Complex or nuanced risk clauses
- Context-dependent risks
- Industry-specific terminology
- Implicit obligations

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM API failures | Medium | Pattern-based detection as fallback |
| False positives | Medium | Confidence scoring, user acknowledgment |
| Performance with large RFPs | Low | Chunking strategy, caching |
| Incomplete risk coverage | Medium | Continuous pattern refinement |

---

## Acceptance Criteria

- [x] Risk Model implemented with all fields
- [x] Pattern-based risk detection working
- [x] AI-powered risk detection working
- [x] Risk categorization accurate (5 categories)
- [x] Severity classification appropriate (4 levels)
- [x] Mitigation recommendations generated
- [x] Alternative language suggested
- [x] UI displays risks with filtering
- [x] Risk acknowledgment tracking functional
- [x] 80%+ test coverage achieved
- [x] All stories completed in Jira
- [x] Confluence documentation complete

---

## Timeline

### Sprint Breakdown

- **Sprint 3 (2 weeks):** All stories completed

### Milestones

- **Week 1:** Backend implementation (models, services, detection)
- **Week 2:** UI implementation, testing, documentation

---

## Testing Strategy

### Unit Tests
- Risk model validation and serialization
- Pattern matching accuracy
- AI detection with mocked LLM
- Confidence scoring logic
- Deduplication logic

### Integration Tests
- End-to-end risk detection flow
- Session state integration
- UI component interactions

### Coverage
- Target: >80%
- Achieved: 86%

---

## Notes

- Similar implementation pattern to Epic 3 (Requirements Extraction)
- Reuses LLMClient infrastructure
- Pattern-based detection is fast and free (no LLM costs)
- AI detection is more comprehensive but slower
- Critical risks block draft generation until acknowledged

---

## Related Links

- **PRD:** `deliverables/prd-rfp-draft-booster.md` (FR-007, FR-008)
- **Epic Summary:** `deliverables/epic-summary.md`
- **Jira Epic:** https://luis-sosa-bairesdev.atlassian.net/browse/RDBP-4
- **Confluence:** See `deliverables/EPIC-4-COMPLETION-SUMMARY.md` for completion details

---

## Key Learnings

1. **Pattern Detection First:** Fast and reliable for common clauses
2. **AI as Enhancement:** Use AI for complex, nuanced risks
3. **Confidence Scoring:** Critical for reducing false positives
4. **User Acknowledgment:** Required for critical risks before draft generation
5. **Deduplication:** Essential when combining pattern and AI detection

