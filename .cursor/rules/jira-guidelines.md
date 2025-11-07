# Jira Guidelines

## Overview

This document defines how to integrate Jira with the RFP Draft Booster development workflow using the MCP Atlassian integration.

## Jira Project Setup

### Project Details

- **Project Key:** `RFP`
- **Project Name:** RFP Draft Booster
- **Project Type:** Software Development
- **Atlassian URL:** `https://bairesdev.atlassian.net`

## Issue Types

### Epic
Large features spanning multiple sprints
- **Example:** "PDF Processing Pipeline", "LLM Integration", "Google Docs Export"

### Story
User-facing feature delivering value
- **Example:** "As a sales rep, I want to upload RFP PDFs..."

### Task
Technical work not directly user-facing
- **Example:** "Setup Streamlit project structure", "Configure Gemini API"

### Bug
Defect needing correction
- **Example:** "PDF upload fails for files with special characters"

### Sub-task
Breakdown of Story/Task
- **Example:** "Add file size validation" (under "PDF Upload" story)

## Issue Fields

### Required Fields

- **Summary:** Clear, concise title (50-70 characters)
- **Issue Type:** Epic, Story, Task, Bug, Sub-task
- **Priority:** Blocker, High, Medium, Low
- **Description:** Detailed explanation with acceptance criteria
- **Assignee:** Team member responsible
- **Labels:** Tags for categorization (e.g., `backend`, `frontend`, `llm`)

### Optional Fields

- **Story Points:** Fibonacci scale (1, 2, 3, 5, 8, 13, 21)
- **Sprint:** Current sprint assignment
- **Epic Link:** Link to parent epic
- **Original Estimate:** Time estimate in hours
- **Due Date:** Hard deadline (if applicable)
- **Components:** System components (PDF, LLM, UI, Export)

## Naming Conventions

### Epics

Format: `[EPIC] Feature Area`

Examples:
```
[EPIC] PDF Processing & Upload
[EPIC] LLM Requirement Extraction
[EPIC] Risk Detection & Analysis
[EPIC] Service Matching Engine
[EPIC] Draft Generation
[EPIC] Google Docs Integration
```

### Stories

Format: User story template

Examples:
```
RFP-1: Upload RFP PDF with validation
RFP-5: Extract requirements using LLM
RFP-12: Detect risk clauses in RFP
RFP-18: Generate draft response
RFP-25: Export draft to Google Docs
```

### Tasks

Format: Action + Component

Examples:
```
RFP-2: Setup Streamlit app structure
RFP-6: Configure Gemini API integration
RFP-13: Implement regex patterns for risk detection
RFP-19: Create draft template engine
```

### Bugs

Format: `[BUG] Brief description`

Examples:
```
RFP-30: [BUG] File upload fails for PDFs over 40MB
RFP-31: [BUG] LLM extraction timeout for large documents
RFP-32: [BUG] Google Docs export loses formatting
```

## Story Description Template

```markdown
## User Story
As a [user type],
I want to [action],
So that [benefit].

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Technical Notes
- Implementation hints
- Dependencies
- Constraints

## Design/Mockups
[Link to designs if applicable]

## Definition of Done
- [ ] Code complete and reviewed
- [ ] Unit tests written (80%+ coverage)
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] No critical bugs
- [ ] Deployed to test environment
```

## Status Workflow

### Standard Workflow

```
To Do → In Progress → In Review → Done
```

### Detailed Status Definitions

**To Do**
- Story is refined and ready for development
- All acceptance criteria defined
- Dependencies identified
- Assigned to team member

**In Progress**
- Developer actively working on story
- Branch created from main
- Code being written and tested

**In Review**
- Code complete and pushed
- Pull Request created
- Awaiting code review
- Tests passing

**Done**
- Code reviewed and approved
- Merged to main
- Deployed to test/production
- Acceptance criteria verified

### Bug Workflow

```
Open → In Progress → Testing → Verified → Closed
```

## Labels

### Category Labels
- `backend` - Backend/API work
- `frontend` - UI/Streamlit work
- `llm` - LLM integration
- `infrastructure` - DevOps, deployment
- `documentation` - Docs only

### Priority Labels
- `critical` - Blocks development
- `high-priority` - Important, needed soon
- `tech-debt` - Technical debt cleanup
- `quick-win` - Easy, fast implementation

### Component Labels
- `pdf-processing` - PDF upload and parsing
- `extraction` - Requirement extraction
- `risk-detection` - Risk analysis
- `matching` - Service matching
- `draft-generation` - Draft creation
- `export` - Google Docs export

## Using MCP for Jira Integration

### Query Jira from Cursor

```python
# In Cursor chat, you can ask:
"Show me all open stories in RFP project"
"List all high priority bugs"
"Get details for RFP-15"
"Show stories assigned to me"
```

### Create Jira Issues

```python
# From Cursor, create issue:
"Create a story: As a sales rep, I want to upload RFP PDFs"
```

The AI will:
1. Format the story properly
2. Add to Jira
3. Return the issue key (e.g., RFP-45)

### Update Issues

```python
# Update issue status:
"Move RFP-15 to In Progress"
"Add comment to RFP-20: Implemented PDF validation"
"Update RFP-25 status to Done"
```

### Search and Filter

```python
# JQL queries via AI:
"Show all stories in Epic RFP-5"
"List all bugs created this week"
"Find all unassigned high-priority tasks"
```

## Sprint Planning

### Sprint Structure

- **Duration:** 2 weeks
- **Planning:** Monday start of sprint
- **Daily Standup:** Every morning
- **Review:** Friday end of sprint
- **Retrospective:** After review

### Story Points

Use Fibonacci sequence for estimation:

- **1 point:** 1-2 hours (very simple)
- **2 points:** 2-4 hours (simple)
- **3 points:** 4-8 hours (moderate)
- **5 points:** 1-2 days (complex)
- **8 points:** 2-3 days (very complex)
- **13 points:** 3-5 days (needs breakdown)
- **21+ points:** Epic, must be split

### Sprint Capacity

- **Full-time developer:** ~30-40 points per 2-week sprint
- Account for:
  - Meetings and ceremonies
  - Code reviews
  - Bug fixes
  - Context switching

## Linking Issues

### Link Types

**Blocks / Is Blocked By**
```
RFP-5 blocks RFP-12
(Requirement extraction must complete before risk detection)
```

**Relates To**
```
RFP-18 relates to RFP-25
(Draft generation relates to export)
```

**Duplicate**
```
RFP-30 duplicates RFP-28
```

**Epic Link**
```
RFP-5, RFP-6, RFP-7 → RFP-1 [EPIC]
```

## Comments

### Adding Comments

**Progress Updates:**
```
Completed PDF parsing implementation. 
Starting LLM integration next.
ETA: End of day tomorrow.
```

**Blockers:**
```
Blocked: Waiting for Gemini API key approval.
Need credentials by EOD to stay on schedule.
```

**Questions:**
```
@john.doe - Should we support scanned PDFs with OCR, 
or only PDFs with extractable text?
```

**Code References:**
```
Implemented in PR #45
Branch: feature/pdf-upload-RFP-123
Commit: a1b2c3d
```

## Integration with Git

### Commit Messages Reference Jira

```bash
git commit -m "feat(upload): add PDF file validation

Implements file size and type validation for uploads.

RFP-123"
```

### Branch Names Include Ticket

```bash
git checkout -b feature/pdf-upload-RFP-123
git checkout -b fix/export-error-RFP-156
```

### PR Description References Jira

```markdown
## Related Tickets
- RFP-123 (primary)
- RFP-124 (related)

## Description
Implements PDF upload with validation as specified in RFP-123.
```

## Automation Rules

### Auto-transition on PR

**When:** PR is created for branch with RFP-XXX
**Then:** Move RFP-XXX to "In Review"

### Auto-transition on Merge

**When:** PR merged to main
**Then:** Move linked issue to "Done"

### Auto-comment on Commit

**When:** Commit message contains RFP-XXX
**Then:** Add commit message as comment to RFP-XXX

## Reporting

### Useful JQL Queries

**My Current Work:**
```jql
project = RFP 
AND assignee = currentUser() 
AND status != Done
ORDER BY priority DESC
```

**Sprint Progress:**
```jql
project = RFP 
AND sprint in openSprints()
ORDER BY status ASC
```

**High Priority Bugs:**
```jql
project = RFP 
AND type = Bug 
AND priority in (Blocker, High)
AND status != Done
ORDER BY created DESC
```

**Overdue Tasks:**
```jql
project = RFP 
AND dueDate < now() 
AND status != Done
ORDER BY dueDate ASC
```

## Best Practices

### Story Creation

- [ ] Write clear user story (As a... I want... So that...)
- [ ] Define specific, testable acceptance criteria
- [ ] Estimate story points with team
- [ ] Add relevant labels
- [ ] Link to epic if applicable
- [ ] Attach mockups/designs if needed

### During Development

- [ ] Move story to "In Progress" when starting
- [ ] Update story with progress comments
- [ ] Log blockers immediately
- [ ] Link commits and PRs
- [ ] Keep story up to date

### Before Closing

- [ ] All acceptance criteria met
- [ ] Code reviewed and merged
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Demo to product owner (if needed)
- [ ] Move to "Done"

### General Guidelines

- Update stories daily
- Use comments for communication
- Don't create duplicate issues
- Close stale issues
- Keep descriptions current
- Use proper issue types
- Set realistic estimates

## MCP Commands Reference

### List Issues

```
# Show open stories
mcp_atlassian_jira_search("project = RFP AND type = Story AND status != Done")

# Show my issues
mcp_atlassian_jira_search("project = RFP AND assignee = currentUser()")
```

### Get Issue Details

```
# Get specific issue
mcp_atlassian_jira_get_issue("RFP-123")
```

### Create Issue

```
# Create story
mcp_atlassian_jira_create_issue({
  "project": "RFP",
  "issuetype": "Story",
  "summary": "Upload RFP PDF with validation",
  "description": "As a sales rep...",
  "priority": "High"
})
```

### Update Issue

```
# Update status
mcp_atlassian_jira_transition_issue("RFP-123", "In Progress")

# Add comment
mcp_atlassian_jira_add_comment("RFP-123", "Implementation complete, ready for review")
```

## Related Guidelines

- [Git Guidelines](git-guidelines.md)
- [User Story Guidelines](user-story-guidelines.mdc)
- [Basic Guidelines](basic-guidelines.mdc)

