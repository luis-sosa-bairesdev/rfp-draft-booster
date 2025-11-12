# Epic 4: Risk Detection & Analysis - Start Prompt

> **Copy this entire prompt to start a new AI agent session for Epic 4**

---

## 🎯 Mission

You are tasked with implementing **Epic 4: Risk Detection & Analysis** for the RFP Draft Booster project. This epic will identify problematic clauses in RFPs using pattern matching and AI, with severity classification and actionable recommendations.

**Your first task is to:**
1. Create Epic 4 in Jira (RDBP project)
2. Create Sprint 3
3. Create all user stories for Epic 4
4. Link stories to Epic 4
5. Add stories to Sprint 3
6. Then begin implementation

---

## 📋 Project Context

**Project:** RFP Draft Booster  
**Repository:** https://github.com/luis-sosa-bairesdev/rfp-draft-booster  
**Jira Project:** RDBP (https://luis-sosa-bairesdev.atlassian.net/jira/software/projects/RDBP/boards/34)  
**Confluence Space:** https://luis-sosa-bairesdev.atlassian.net/wiki/spaces/~712020bfc89abf8f5841728f3bd48d6a60043a

**Current Status:**
- ✅ Epic 1: Project Setup & Infrastructure (Done)
- ✅ Epic 2: PDF Processing & Upload (Done)
- ✅ Epic 3: LLM Requirement Extraction (Done)
- ⏳ Epic 4: Risk Detection & Analysis (Your task)

**Dependencies:** Epic 4 depends on Epic 2 (needs extracted RFP text) ✅

---

## 📚 Essential Reading (Do This First!)

Before starting, read these documents in order:

1. **Onboarding Guide:** `deliverables/EPIC-4-ONBOARDING.md`
   - Complete context and architecture
   - Technical decisions and patterns
   - Implementation checklist

2. **PRD Section FR-007 & FR-008:** `deliverables/prd-rfp-draft-booster.md`
   - Lines 340-367: Risk Detection requirements
   - User stories and acceptance criteria
   - Business requirements

3. **Epic Summary:** `deliverables/epic-summary.md`
   - Lines 36-41: Epic 4 overview
   - Dependencies and timeline

4. **Epic 3 Reference:** `deliverables/jira-import/confluence-epic-03.md`
   - Similar implementation pattern
   - Documentation format to follow

5. **Jira Setup Script:** `deliverables/jira-import/setup_new_project_rdbp.py`
   - Reference for creating issues in Jira
   - API patterns and structure

---

## 🔧 Jira Configuration

**Jira Credentials:**
- URL: `https://luis-sosa-bairesdev.atlassian.net`
- Email: `luis.sosa@bairesdev.com`
- API Token: `ATATT3xFfGF05S_SCHS3O_OqM3rJcN9nM9-g3AorAXYCLvHDC2bvMGJhSgU9pCvIPNFPAbAmxJMU3UtO9R3ed-ccV7PInG7h51OTK9JTdS3ERz2Tdbrljl6E2yQDwVKtwsia8PI_UHC6F4wFE_P_D955n6fKNFiZBrCF4K3PNoonm6nxXKLNEJI=0B414822`

**Project Details:**
- Project Key: `RDBP`
- Board ID: `34`
- Assignee: `luis.sosa@bairesdev.com`

---

## 📝 Step 1: Create Epic 4 in Jira

**Epic Details:**
- **Summary:** `[EPIC] Risk Detection & Analysis`
- **Description:** 
  ```
  Identify problematic clauses in RFPs using pattern matching and AI, with severity classification and actionable recommendations.
  
  This epic enables early risk flagging before contract negotiation, preventing costly contract issues and improving proposal quality with risk-aware responses.
  
  Key Features:
  - Automatic risk detection (pattern + AI)
  - Risk categorization (legal, financial, timeline, technical, compliance)
  - Severity classification (critical, high, medium, low)
  - Mitigation recommendations
  - Alternative language suggestions
  - Risk acknowledgment tracking
  ```
- **Issue Type:** `Epic`
- **Priority:** `High`
- **Story Points:** `55`

**API Endpoint:** `POST /rest/api/3/issue`

**Reference:** See `deliverables/jira-import/setup_new_project_rdbp.py` for the `create_issue()` function pattern.

---

## 📝 Step 2: Create Sprint 3

**Sprint Details:**
- **Name:** `Sprint 3 - Risk Detection`
- **Start Date:** `2025-11-13` (or current date + 1 day)
- **End Date:** `2025-11-27` (2 weeks from start)
- **Goal:** `Implement Epic 4: Risk Detection & Analysis with pattern matching, AI detection, categorization, and UI`
- **Board ID:** `34`

**API Endpoint:** `POST /rest/agile/1.0/sprint`

**Reference:** See `deliverables/jira-import/setup_new_project_rdbp.py` for the `create_sprint()` function pattern.

---

## 📝 Step 3: Create User Stories

Based on PRD sections FR-007 and FR-008, create the following user stories:

### Backend Stories (Pattern + AI Detection)

#### Story 1: Pattern-based risk detection
- **Summary:** `Detect risks using regex patterns for common problematic clauses`
- **Description:** `As a system, I want to detect common risk patterns using regex, so that standard problematic clauses are identified quickly without LLM calls.`
- **Acceptance Criteria:**
  - Create regex patterns for common risk clauses (penalties, liability, exclusivity, etc.)
  - Match patterns against RFP text
  - Extract matched clause text and context
  - Assign initial category and severity
- **Story Points:** `8`
- **Issue Type:** `Story`

#### Story 2: AI-powered risk detection
- **Summary:** `Detect risks using LLM analysis for complex clauses`
- **Description:** `As a system, I want to use AI to detect complex risk clauses, so that nuanced problematic language is identified even when not matching standard patterns.`
- **Acceptance Criteria:**
  - Use LLM to analyze RFP text chunks
  - Extract risk clauses with context
  - Categorize risks (legal, financial, timeline, technical, compliance)
  - Assign severity (critical, high, medium, low)
  - Provide confidence score
- **Story Points:** `13`
- **Issue Type:** `Story`

#### Story 3: Risk categorization
- **Summary:** `Categorize detected risks into 5 categories`
- **Description:** `As a sales rep, I want risks categorized by type, so that I can quickly understand what kind of issues need attention.`
- **Acceptance Criteria:**
  - Categories: legal, financial, timeline, technical, compliance
  - Each risk assigned to one category
  - Category displayed with icon/color
- **Story Points:** `5`
- **Issue Type:** `Story`

#### Story 4: Severity classification
- **Summary:** `Assign severity levels to detected risks`
- **Description:** `As a sales rep, I want risks prioritized by severity, so that I focus on critical issues first.`
- **Acceptance Criteria:**
  - Severity levels: critical, high, medium, low
  - Each risk assigned severity
  - Critical risks flagged prominently
- **Story Points:** `5`
- **Issue Type:** `Story`

#### Story 5: Mitigation recommendations
- **Summary:** `Generate mitigation recommendations for detected risks`
- **Description:** `As a sales rep, I want actionable recommendations for each risk, so that I know how to address problematic clauses.`
- **Acceptance Criteria:**
  - Generate recommendation text for each risk
  - Include potential impact description
  - Suggest mitigation strategies
- **Story Points:** `8`
- **Issue Type:** `Story`

#### Story 6: Alternative language suggestions
- **Summary:** `Suggest alternative clause language for detected risks`
- **Description:** `As a sales rep, I want alternative language suggestions, so that I can propose safer clause wording.`
- **Acceptance Criteria:**
  - Generate alternative clause text
  - Highlight differences from original
  - Make suggestions editable
- **Story Points:** `5`
- **Issue Type:** `Story`

### UI Stories

#### Story 7: Display risks in table
- **Summary:** `Display detected risks in sortable table`
- **Description:** `As a sales rep, I want to see all detected risks in a table, so that I can review them efficiently.`
- **Acceptance Criteria:**
  - Display risks with: category, severity, clause text, page number, confidence
  - Sortable columns
  - Expandable details
  - Color-coded severity
- **Story Points:** `8`
- **Issue Type:** `Story`

#### Story 8: Filter risks by category and severity
- **Summary:** `Filter risks by category and severity`
- **Description:** `As a sales rep, I want to filter risks, so that I can focus on specific types or severity levels.`
- **Acceptance Criteria:**
  - Filter by category (5 options)
  - Filter by severity (4 options)
  - Show only unacknowledged risks
- **Story Points:** `5`
- **Issue Type:** `Story`

#### Story 9: Risk acknowledgment
- **Summary:** `Allow users to acknowledge risks`
- **Description:** `As a sales manager, I want to acknowledge critical risks, so that the team tracks which risks have been reviewed.`
- **Acceptance Criteria:**
  - Acknowledge button for each risk
  - Track acknowledgment timestamp
  - Require acknowledgment for critical risks before draft generation
  - Add notes on how risk will be addressed
- **Story Points:** `8`
- **Issue Type:** `Story`

#### Story 10: Show recommendations and alternatives
- **Summary:** `Display mitigation recommendations and alternative language`
- **Description:** `As a sales rep, I want to see recommendations and alternatives, so that I can address risks effectively.`
- **Acceptance Criteria:**
  - Display recommendation text
  - Display alternative clause language
  - Allow copying alternative text
  - Show potential impact
- **Story Points:** `5`
- **Issue Type:** `Story`

### Testing Stories

#### Story 11: Unit tests for Risk model
- **Summary:** `Create unit tests for Risk model`
- **Description:** `As a developer, I want unit tests for the Risk model, so that data validation and model behavior is verified.`
- **Acceptance Criteria:**
  - Test model creation and validation
  - Test enum conversions
  - Test serialization methods
  - Achieve 100% coverage
- **Story Points:** `3`
- **Issue Type:** `Story`

#### Story 12: Unit tests for Risk Detector service
- **Summary:** `Create unit tests for Risk Detector service`
- **Description:** `As a developer, I want unit tests for Risk Detector, so that risk detection logic is verified.`
- **Acceptance Criteria:**
  - Test pattern matching
  - Test AI detection
  - Test categorization and severity assignment
  - Achieve 80%+ coverage
- **Story Points:** `5`
- **Issue Type:** `Story`

#### Story 13: UI tests for Risk Analysis page
- **Summary:** `Create UI tests for Risk Analysis page`
- **Description:** `As a developer, I want UI tests, so that the Risk Analysis interface is verified.`
- **Acceptance Criteria:**
  - Test risk display
  - Test filtering
  - Test acknowledgment
  - Test recommendations display
- **Story Points:** `3`
- **Issue Type:** `Story`

**Total Story Points:** 55

---

## 📝 Step 4: Link Stories to Epic 4

After creating all stories, link them to Epic 4 using the "Epic Link" field.

**API Endpoint:** `PUT /rest/api/3/issue/{issueKey}`

**Field:** `customfield_10011` (Epic Link) - Use the Epic key (e.g., `RDBP-4`)

**Reference:** See `deliverables/jira-import/fix_rdbp_organization.py` for linking pattern.

---

## 📝 Step 5: Add Stories to Sprint 3

After creating Sprint 3, add all stories to the sprint.

**API Endpoint:** `POST /rest/agile/1.0/sprint/{sprintId}/issue`

**Reference:** See `deliverables/jira-import/move_stories_to_sprints_rdbp.py` for adding issues to sprint.

---

## 🚀 Step 6: Begin Implementation

After completing Jira setup, follow the implementation plan in `deliverables/EPIC-4-ONBOARDING.md`:

1. Create Risk Model (`src/models/risk.py`)
2. Create Risk Detector Service (`src/services/risk_detector.py`)
3. Add Risk Prompts (`src/utils/prompt_templates.py`)
4. Implement Risk Analysis UI (`pages/3_⚠️_Risk_Analysis.py`)
5. Create Tests (target: 80%+ coverage)
6. Create Confluence Documentation

---

## ✅ Success Criteria

Epic 4 is complete when:
- [ ] Epic 4 created in Jira
- [ ] Sprint 3 created
- [ ] All 13 user stories created and linked to Epic 4
- [ ] All stories added to Sprint 3
- [ ] All user stories implemented
- [ ] Risk detection working (pattern + AI)
- [ ] UI fully functional
- [ ] 80%+ test coverage
- [ ] All stories closed in Jira
- [ ] Confluence documentation complete

---

## 🔗 Quick Reference Links

- **Onboarding Guide:** `deliverables/EPIC-4-ONBOARDING.md`
- **PRD:** `deliverables/prd-rfp-draft-booster.md` (FR-007, FR-008)
- **Epic Summary:** `deliverables/epic-summary.md`
- **Epic 3 Reference:** `deliverables/jira-import/confluence-epic-03.md`
- **Jira Scripts:** `deliverables/jira-import/` directory
- **Codebase:** See `EPIC-4-ONBOARDING.md` for structure

---

## 💡 Important Notes

1. **Follow Epic 3 Pattern:** Epic 4 should follow the same architecture pattern as Epic 3 (see `confluence-epic-03.md`)
2. **Use Existing Infrastructure:** Reuse `LLMClient`, `session.py`, and other utilities from Epic 3
3. **Test Coverage:** Maintain 80%+ code coverage (Epic 3 achieved 86%)
4. **Documentation:** Create Confluence documentation similar to Epic 3 format
5. **Language:** All code, comments, and documentation must be in English
6. **Jira:** Use issue type "Story" (not "Task") for user stories

---

## 🎯 Your First Actions

1. ✅ Read `deliverables/EPIC-4-ONBOARDING.md` completely
2. ✅ Read PRD sections FR-007 and FR-008
3. ✅ Review Epic 3 implementation for patterns
4. ✅ Create Epic 4 in Jira
5. ✅ Create Sprint 3
6. ✅ Create all 13 user stories
7. ✅ Link stories to Epic 4
8. ✅ Add stories to Sprint 3
9. ✅ Begin implementation following the onboarding guide

---

**Good luck! You have everything you need to succeed. 🚀**



