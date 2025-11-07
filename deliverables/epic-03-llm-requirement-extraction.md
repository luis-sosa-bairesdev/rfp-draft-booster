# Epic: [EPIC] LLM Requirement Extraction

## Epic Information

- **Epic Key:** RFP-40
- **Epic Name:** [EPIC] LLM Requirement Extraction
- **Status:** To Do
- **Priority:** Critical
- **Owner:** Tech Lead
- **Start Date:** 2025-11-25
- **Target Date:** 2025-12-06

---

## Summary

Implement AI-powered requirement extraction that analyzes RFP text and extracts structured requirements with categorization, prioritization, and confidence scoring. This is the core intelligence of the system that eliminates manual requirement identification.

---

## Business Value

### Problem Being Solved

Sales teams spend 3-5 hours manually reading through RFPs and cataloging requirements. This is tedious, error-prone, and requirements are often missed or misclassified.

### Expected Benefits

- **Time Savings:** Reduce requirement identification from 3-5 hours to under 2 minutes
- **Completeness:** AI doesn't get tired and miss requirements
- **Consistency:** Standardized categorization across all RFPs
- **Confidence Scores:** Know which extractions need human review

### Success Metrics

| Metric | Target | How Measured |
|--------|--------|--------------|
| Extraction Speed | < 2 minutes | Time for 50-page RFP |
| Requirement Recall | > 90% | % of actual requirements found |
| Categorization Accuracy | > 85% | Correct category assignments |
| Avg Confidence Score | > 0.75 | Mean confidence of extractions |
| User Verification Time | < 15 minutes | Time to verify/adjust extractions |

---

## User Stories

### Must-Have Stories (P0)

- [ ] **RFP-41:** As a sales rep, I want AI to extract requirements from my RFP automatically, so that I don't have to read 50+ pages manually
- [ ] **RFP-42:** As a sales rep, I want requirements categorized (technical, functional, timeline, budget, compliance), so that I can quickly understand what's needed
- [ ] **RFP-43:** As a sales rep, I want requirements prioritized (critical, high, medium, low), so that I focus on what matters most
- [ ] **RFP-44:** As a sales rep, I want confidence scores for each extraction, so that I know which ones to double-check
- [ ] **RFP-45:** As a sales rep, I want to see source page numbers, so that I can reference the original RFP
- [ ] **RFP-46:** As a sales rep, I want to edit extracted requirements, so that I can correct mistakes or add clarification
- [ ] **RFP-47:** As a sales rep, I want to add requirements manually, so that I can capture items the AI missed
- [ ] **RFP-48:** As a sales rep, I want to delete incorrect extractions, so that my requirement list is accurate

### Should-Have Stories (P1)

- [ ] **RFP-49:** As a sales rep, I want to mark requirements as verified, so that I track my review progress
- [ ] **RFP-50:** As a sales rep, I want to filter requirements by category/priority, so that I can focus on specific types

**Total Story Points:** 65

---

## Technical Overview

### Architecture

```
RFP Text → Chunking → LLM Prompt → Parse Response → Requirement Objects → Display in UI
                                          ↓
                                   Categorization
                                   Prioritization
                                   Confidence Score
```

### Key Components

1. **Text Chunker:** Split large RFPs into manageable chunks (respect LLM context limits)
2. **Prompt Engine:** Crafted prompts for requirement extraction
3. **LLM Client:** Integration with Gemini/Groq/Ollama
4. **Response Parser:** Convert LLM JSON output to Requirement objects
5. **Requirement Manager:** CRUD operations for requirements
6. **Verification UI:** Table view with inline editing

### Technology Stack

- **LangChain:** Prompt management, LLM orchestration
- **Google Gemini:** Primary LLM (free tier, good performance)
- **Groq:** Fallback LLM
- **Ollama:** Local LLM option
- **Pydantic:** Data validation for requirements

---

## Prompt Strategy

### Extraction Prompt Template

```python
EXTRACTION_PROMPT = """
You are an expert at analyzing Request for Proposals (RFPs) and extracting key requirements.

Analyze the following RFP section and extract ALL requirements:

RFP Text:
{rfp_text}

For each requirement, provide:
1. category: technical | functional | timeline | budget | compliance
2. description: Clear, complete requirement description
3. priority: critical | high | medium | low
4. confidence: Your confidence in this extraction (0.0-1.0)
5. page_number: Source page (if available)

Return as JSON array of requirements.

Examples:
- "Solution must support 99.9% uptime" → technical, critical, 0.95
- "Project completion within 60 days" → timeline, high, 0.90
- "Budget not to exceed $500K" → budget, high, 0.92

Output:
```

### Categorization Logic

| Category | Indicators | Examples |
|----------|------------|----------|
| **Technical** | Performance, architecture, technology, integrations | "99.9% uptime", "AWS infrastructure", "API integration" |
| **Functional** | Features, capabilities, use cases | "Generate reports", "User authentication", "Dashboard" |
| **Timeline** | Deadlines, milestones, phases | "Complete in 60 days", "Phase 1 by Jan 2026" |
| **Budget** | Pricing, cost constraints, payment terms | "Not exceed $500K", "Payment within 30 days" |
| **Compliance** | Legal, regulatory, certifications | "HIPAA compliant", "SOC 2 certified", "GDPR" |

---

## Dependencies

### Internal Dependencies

- **Depends On:** RFP-20 (PDF Processing) - needs extracted text

### External Dependencies

- LLM API access (Gemini/Groq)
- LangChain library

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM misses requirements | High | Confidence scoring, human verification step |
| LLM hallucinates requirements | Medium | Provide source page numbers, verification UI |
| Categorization errors | Medium | Allow manual recategorization |
| API rate limits exceeded | Medium | Implement retry logic, fallback providers |
| Context window too small for large RFPs | Medium | Chunking strategy, summarization |
| LLM costs higher than expected | Low | Use free tiers, optimize prompts, cache responses |

---

## Acceptance Criteria

- [ ] System extracts requirements from RFP text within 2 minutes
- [ ] Requirements categorized into 5 categories
- [ ] Each requirement has priority assignment
- [ ] Confidence scores between 0.0 and 1.0
- [ ] Low-confidence extractions (<0.7) flagged for review
- [ ] Source page numbers captured when available
- [ ] Requirements displayed in sortable/filterable table
- [ ] Users can edit requirement description, category, priority
- [ ] Users can add new requirements manually
- [ ] Users can delete incorrect extractions
- [ ] Changes persist in session state
- [ ] At least 90% of actual requirements extracted (validation on test RFPs)

---

## Timeline

### Sprint Breakdown

- **Sprint 3 (Week 4-5):** All stories completed

### Milestones

- **Week 4:**
  - LLM integration (Gemini)
  - Prompt engineering
  - Basic extraction working
- **Week 5:**
  - Categorization and prioritization
  - Confidence scoring
  - Verification UI

---

## Testing Strategy

### Test RFPs

Create 5 test RFPs with known requirements:
1. Simple RFP (10 pages, 5 requirements)
2. Medium RFP (30 pages, 15 requirements)
3. Complex RFP (50 pages, 30 requirements)
4. Technical RFP (heavy technical requirements)
5. Compliance-focused RFP (legal/regulatory requirements)

### Success Criteria

- **Recall:** Extract ≥ 90% of actual requirements
- **Precision:** ≥ 85% of extractions are real requirements
- **Categorization:** ≥ 85% correctly categorized
- **Speed:** < 2 minutes for 50-page RFP

---

## Notes

- Prompt engineering is critical - budget time for iteration
- Start with Gemini (free, good performance)
- Confidence scores help users prioritize review
- Human verification is part of the workflow (not a bug!)

---

## Related Links

- [PRD Section: FR-003, FR-004](prd-rfp-draft-booster.md#fr-003-llm-requirement-extraction)
- [Domain Entity: Requirement](../domain/requirement-entity.md)
- [Jira Epic](https://bairesdev.atlassian.net/browse/RFP-40)

