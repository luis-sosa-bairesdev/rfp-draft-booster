# JIRA Import Files for Epic 1

This directory contains all the files needed to import **Epic 1: Project Setup & Infrastructure** into JIRA and create the corresponding Confluence documentation.

## 📁 Files

### 1. `epic-01-jira.json`
JSON structure for the Epic with complete description, acceptance criteria, and metadata.

### 2. `user-stories-epic-01.json`
JSON structures for all 10 user stories with:
- Complete descriptions
- Acceptance criteria
- Story points
- Priorities
- Labels
- Dependencies

### 3. `confluence-epic-01.md`
Complete Confluence documentation in Markdown format, including:
- Executive summary
- Business value
- All user stories with details
- Technical architecture
- Timeline and milestones
- Progress tracking
- Risk analysis

### 4. `IMPORT-GUIDE.md`
Step-by-step guide for manually importing to JIRA with three options:
- Manual creation (recommended)
- CSV import
- REST API

### 5. `import_to_jira.py`
Python script for automated import using JIRA REST API.

---

## 🚀 Quick Start

### Option 1: Manual Import (Easiest)

1. Read `IMPORT-GUIDE.md`
2. Follow Step 1 to create the Epic
3. Follow Step 2 to create all 10 user stories
4. Copy `confluence-epic-01.md` to Confluence

**Time Required:** ~20-30 minutes

---

### Option 2: Automated Import (Fastest)

#### Prerequisites
```bash
pip install requests
```

#### Setup
1. Get your JIRA API token from: https://id.atlassian.com/manage-profile/security/api-tokens

2. Set environment variable:
```bash
export JIRA_API_TOKEN='your-api-token-here'
```

Or create a `.env` file:
```bash
JIRA_API_TOKEN=your-api-token-here
JIRA_URL=https://luis-sosa-bairesdev.atlassian.net
JIRA_EMAIL=luis.sosa@bairesdev.com
JIRA_PROJECT_KEY=SCRUM
```

#### Run Import
```bash
cd /Users/luisfelipesosa/git/rfp-draft-booster/deliverables/jira-import
python import_to_jira.py
```

**Time Required:** ~2-3 minutes

---

## 📊 What Will Be Created

### Epic
- **Key:** RFP-1 (or SCRUM-X depending on your project)
- **Title:** [EPIC] Project Setup & Infrastructure
- **Priority:** High
- **Points:** 40
- **Stories:** 10

### User Stories

| Key | Title | Points | Priority |
|-----|-------|--------|----------|
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

**Total:** 40 story points

---

## 📝 Confluence Documentation

After creating the JIRA issues, create the Confluence page:

1. Go to: https://luis-sosa-bairesdev.atlassian.net/wiki/spaces/~712020bfc89abf8f5841728f3bd48d6a60043a
2. Click **Create** → **Blank page**
3. Title: **Epic 1: Project Setup & Infrastructure**
4. Copy content from `confluence-epic-01.md`
5. Format using Confluence editor (or use Markdown import)
6. Add link to JIRA epic
7. Publish

---

## ✅ Verification Checklist

After import, verify:

- [ ] Epic RFP-1 created successfully
- [ ] All 10 user stories created
- [ ] All stories linked to Epic RFP-1
- [ ] Story points assigned correctly (total = 40)
- [ ] All stories assigned to luis.sosa@bairesdev.com
- [ ] Labels applied correctly
- [ ] Priorities set correctly
- [ ] Descriptions formatted properly
- [ ] Confluence page created and linked

---

## 🔧 Troubleshooting

### Import Script Fails

**Problem:** Authentication error
**Solution:** Verify your API token is correct and has not expired

**Problem:** "Could not find user"
**Solution:** User email may not match JIRA account. Check JIRA user profile.

**Problem:** "Field 'customfield_10016' does not exist"
**Solution:** Story points custom field ID varies by JIRA instance. Update the script with your custom field ID.

### Manual Import Issues

**Problem:** Epic issue type not available
**Solution:** Check project settings → Issue types → Enable Epic

**Problem:** Can't link stories to Epic
**Solution:** Ensure you have the correct Epic key (RFP-1 or SCRUM-X)

---

## 📞 Support

If you encounter issues:
- Check JIRA permissions
- Verify project key is correct (SCRUM)
- Ensure you have create issue permissions
- Contact JIRA admin if needed

---

## 🔗 Related Links

- **JIRA Project:** https://luis-sosa-bairesdev.atlassian.net/jira/software/projects/SCRUM
- **Confluence Space:** https://luis-sosa-bairesdev.atlassian.net/wiki/spaces/~712020bfc89abf8f5841728f3bd48d6a60043a
- **Epic Document:** [../epic-01-project-setup.md](../epic-01-project-setup.md)
- **PRD:** [../prd-rfp-draft-booster.md](../prd-rfp-draft-booster.md)

---

**Generated:** 2025-11-07
**Version:** 1.0
**Project:** RFP Draft Booster

