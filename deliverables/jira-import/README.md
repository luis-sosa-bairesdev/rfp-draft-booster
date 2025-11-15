# Jira & Confluence Import Scripts

This directory contains **reusable templates** for managing Epics and documentation in Jira and Confluence.

---

## 📁 Files

### Core Templates
1. **`create_epic_template.py`** - Create new Epic + Sprint + Stories
2. **`close_epic_template.py`** - Close Epic and all Stories with comments
3. **`upload_confluence_template.py`** - Upload markdown to Confluence

---

## 🚀 Quick Start Guide

### 1. Create a New Epic

**Step 1:** Copy the template
```bash
cp create_epic_template.py create_epic7.py
```

**Step 2:** Edit the configuration section
```python
# Update these variables:
EPIC_SUMMARY = "[EPIC] Your Epic Name"
EPIC_DESCRIPTION = "Your description..."
SPRINT_NAME = "Sprint 7 - Your Sprint"
SPRINT_DURATION_DAYS = 14

USER_STORIES = [
    {
        "summary": "Story 1",
        "description": "As a user...",
        "points": 5,
        "priority": "High"
    },
    # Add more stories...
]
```

**Step 3:** Run the script
```bash
python3 create_epic7.py
```

**Output:**
```
✅ Created Epic: RDBP-XX
✅ Created Sprint: 7
✅ Created 10 stories
✅ Moved stories to sprint
```

---

### 2. Close an Epic

**Step 1:** Copy the template
```bash
cp close_epic_template.py close_epic7.py
```

**Step 2:** Get the Epic and Story keys from Jira
- Go to your Epic page (e.g., `https://luis-sosa-bairesdev.atlassian.net/browse/RDBP-XX`)
- Note the Epic key and all Story keys

**Step 3:** Edit the configuration
```python
EPIC_KEY = "RDBP-XX"
STORY_KEYS = [
    "RDBP-79",
    "RDBP-80",
    # ... all story keys
]

# Customize comments if needed
COMPLETION_COMMENT = "Story completed! Features: ..."
EPIC_COMPLETION_COMMENT = "Epic completed! Summary: ..."
```

**Step 4:** Run the script
```bash
python3 close_epic7.py
```

**Output:**
```
✅ Closed 10 stories
✅ Closed Epic RDBP-XX
🎉 SUCCESS!
```

---

### 3. Upload to Confluence

**Step 1:** Copy the template
```bash
cp upload_confluence_template.py upload_epic7_confluence.py
```

**Step 2:** Edit the configuration
```python
PAGE_TITLE = "Epic 7: Your Epic - Completion Report"
MARKDOWN_FILE = "deliverables/EPIC-7-COMPLETION-SUMMARY.md"
```

**Step 3:** Run the script
```bash
python3 upload_epic7_confluence.py
```

**Output:**
```
✅ Page uploaded to Confluence
   URL: https://luis-sosa-bairesdev.atlassian.net/wiki/...
```

---

## 🔧 Configuration

### API Token

All scripts use the same API token. To update it:

1. Generate a new token: https://id.atlassian.com/manage-profile/security/api-tokens
2. Update the `API_TOKEN` variable in each script

```python
API_TOKEN = "YOUR_NEW_TOKEN_HERE"
```

### Jira Configuration

```python
JIRA_URL = "https://luis-sosa-bairesdev.atlassian.net"
EMAIL = "luis.sosa@bairesdev.com"
PROJECT_KEY = "RDBP"
BOARD_ID = 1
ASSIGNEE = "luis.sosa@bairesdev.com"
```

### Confluence Configuration

```python
CONFLUENCE_URL = "https://luis-sosa-bairesdev.atlassian.net"
SPACE_KEY = "~712020bfc89abf8f5841728f3bd48d6a60043a"  # Personal space
```

---

## 📋 Complete Workflow Example

### Epic 7: Example Feature

```bash
# 1. Create Epic 7
cp create_epic_template.py create_epic7.py
# Edit create_epic7.py with your details
python3 create_epic7.py

# ... implement the feature ...

# 2. Close Epic 7
cp close_epic_template.py close_epic7.py
# Edit close_epic7.py with Epic and Story keys
python3 close_epic7.py

# 3. Upload to Confluence
cp upload_confluence_template.py upload_epic7_confluence.py
# Edit upload_epic7_confluence.py with page title and file
python3 upload_epic7_confluence.py

# 4. Cleanup (optional)
rm create_epic7.py close_epic7.py upload_epic7_confluence.py
```

---

## 🛠️ Troubleshooting

### "HTTP 401: Unauthorized"
- Your API token expired
- Generate a new one and update all scripts

### "HTTP 404: Issue does not exist"
- Check the Epic/Story key is correct
- Ensure you have permission to access the issue

### "HTTP 410: API endpoint removed"
- The search endpoint has changed
- Use the hardcoded keys approach instead

### "Could not find 'Done' transition"
- Check available transitions in Jira
- Update the transition name list in the script

---

## 📝 Notes

### Story Keys
- Always get story keys from the Epic page in Jira
- Don't assume sequential numbering (gaps are normal)

### Comments
- Customize completion comments for each Epic
- Include relevant links (GitHub commits, docs, etc.)

### Confluence
- Markdown conversion is basic (headings, lists, code blocks)
- For complex formatting, edit directly in Confluence

---

## 🗑️ Cleanup Policy

**Keep:**
- The 3 template files (create/close/upload)
- This README

**Delete after use:**
- Epic-specific copies (e.g., `create_epic7.py`)
- Old scripts from completed epics

---

## 📚 Additional Resources

- [Jira REST API Docs](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Confluence REST API Docs](https://developer.atlassian.com/cloud/confluence/rest/v2/)
- [Jira Agile API Docs](https://developer.atlassian.com/cloud/jira/software/rest/)

---

**Last Updated:** November 15, 2025  
**Maintained By:** AI Assistant + Luis Sosa
