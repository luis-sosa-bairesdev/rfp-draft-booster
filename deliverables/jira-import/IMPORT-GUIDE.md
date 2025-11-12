# Guide: Import Epic 1 to JIRA

This guide explains how to manually create Epic 1 and its user stories in JIRA.

## Overview

- **Epic:** RFP-1 - Project Setup & Infrastructure
- **User Stories:** 10 stories (RFP-2 to RFP-11)
- **Total Story Points:** 40
- **Project:** SCRUM
- **Assignee:** luis.sosa@bairesdev.com

---

## Option 1: Manual Creation (Recommended)

### Step 1: Create the Epic

1. Go to your JIRA project: https://luis-sosa-bairesdev.atlassian.net/jira/software/projects/SCRUM
2. Click **Create** button (top navigation)
3. Fill in the following:
   - **Project:** SCRUM
   - **Issue Type:** Epic
   - **Epic Name:** Project Setup & Infrastructure
   - **Summary:** [EPIC] Project Setup & Infrastructure
   - **Description:** Copy from `epic-01-jira.json` → `description` field
   - **Priority:** High
   - **Assignee:** luis.sosa@bairesdev.com
   - **Labels:** foundation, infrastructure, setup
   - **Start Date:** 2025-11-11
   - **Target Date:** 2025-11-15
4. Click **Create**
5. **Note the Epic Key** (should be SCRUM-X or RFP-1)

### Step 2: Create User Stories

For each story in `user-stories-epic-01.json`, repeat these steps:

1. Click **Create** button
2. Fill in:
   - **Project:** SCRUM
   - **Issue Type:** Task (or Story, depending on your project config)
   - **Summary:** [Copy from JSON]
   - **Description:** [Copy from JSON]
   - **Priority:** [Copy from JSON]
   - **Assignee:** luis.sosa@bairesdev.com
   - **Story Points:** [Copy from JSON]
   - **Labels:** [Copy from JSON]
   - **Epic Link:** Select the Epic you created in Step 1
3. Click **Create**

#### Quick Reference: User Stories

| Key | Summary | Points | Priority |
|-----|---------|--------|----------|
| RFP-2 | Setup project repository and folder structure | 5 | Highest |
| RFP-3 | Configure Python virtual environment and dependencies | 5 | Highest |
| RFP-4 | Create basic Streamlit app with navigation | 8 | Highest |
| RFP-5 | Implement code quality tools (Black, pylint, mypy) | 3 | High |
| RFP-6 | Setup pytest and test infrastructure | 5 | High |
| RFP-7 | Create .env configuration for API keys | 3 | High |
| RFP-8 | Setup Git hooks and pre-commit checks | 3 | Medium |
| RFP-9 | Create README with setup instructions | 3 | Medium |
| RFP-10 | Setup CI/CD pipeline (GitHub Actions) | 5 | Medium |
| RFP-11 | Configure logging infrastructure | 3 | Medium |

---

## Option 2: CSV Import

JIRA supports CSV import for bulk creation.

### Step 1: Prepare CSV

Create a CSV file with this structure:

```csv
Summary,Issue Type,Priority,Story Points,Description,Labels,Epic Link,Assignee
"[EPIC] Project Setup & Infrastructure",Epic,High,,[Full description],"foundation,infrastructure,setup",,luis.sosa@bairesdev.com
"Setup project repository and folder structure",Task,Highest,5,[Full description],"setup,infrastructure",RFP-1,luis.sosa@bairesdev.com
...
```

### Step 2: Import to JIRA

1. Go to **Project Settings** → **Import**
2. Select **CSV**
3. Upload your CSV file
4. Map fields correctly
5. Click **Import**

---

## Option 3: JIRA REST API

Use the JIRA REST API to create issues programmatically.

### Requirements
- JIRA API Token (you already have this)
- Python with `requests` library

### Script Usage

```bash
cd /Users/luisfelipesosa/git/rfp-draft-booster/deliverables/jira-import
python import_to_jira.py
```

*(Script to be created if you need this option)*

---

## Verification Checklist

After import, verify:

- [ ] Epic RFP-1 created successfully
- [ ] All 10 user stories created
- [ ] All stories linked to Epic RFP-1
- [ ] Story points assigned correctly (total = 40)
- [ ] All stories assigned to luis.sosa@bairesdev.com
- [ ] Labels applied correctly
- [ ] Priorities set correctly
- [ ] Descriptions formatted properly

---

## Confluence Documentation

After creating the JIRA issues, create the Confluence documentation:

1. Go to your Confluence space: https://luis-sosa-bairesdev.atlassian.net/wiki/spaces/~712020bfc89abf8f5841728f3bd48d6a60043a
2. Create new page: **Epic 1: Project Setup & Infrastructure**
3. Copy content from `confluence-epic-01.md`
4. Format using Confluence editor
5. Link to JIRA epic

---

## Support

If you encounter issues:
- Check that you have the correct permissions in JIRA
- Verify the project key is correct (SCRUM)
- Ensure Epic issue type is enabled in your project
- Contact JIRA admin if needed

---

## Next Steps

Once Epic 1 is in JIRA:
1. ✅ Review and adjust as needed
2. ✅ Start working on stories
3. ✅ Update status as you progress
4. ✅ Link to Confluence documentation

---

**Generated:** 2025-11-07
**Project:** RFP Draft Booster
**Epic:** Project Setup & Infrastructure



