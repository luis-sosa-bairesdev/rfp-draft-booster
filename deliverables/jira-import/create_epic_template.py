#!/usr/bin/env python3
"""
Generic template to create a new Epic, Sprint, and User Stories in Jira.

USAGE:
1. Update the configuration section below with your Epic details
2. Update the USER_STORIES list with your stories
3. Run: python3 create_epic_template.py
"""

import json
import urllib.request
import urllib.error
import base64
from datetime import datetime, timedelta

# ============================================================================
# CONFIGURATION - UPDATE THIS FOR YOUR NEW EPIC
# ============================================================================

JIRA_URL = "https://luis-sosa-bairesdev.atlassian.net"
EMAIL = "luis.sosa@bairesdev.com"
API_TOKEN = "ATATT3xFfGF0sSVc0RTQhwj6YNxUmVNcEVQAM4OWpmI-E553Bsc46avo_OI-Hlvf_IrYjf0_FBtsCgKBbIJ1KNM2gdrHvfsijPku4fIR9BrLCnm9WcpSKVr_EDeBG1te_aNUatYT5b9w6JSdNt7sgtl6ZdH32IgnTYWLCOh3VEGhnDF6mvWj1g0=0882E324"
PROJECT_KEY = "RDBP"
BOARD_ID = 1
ASSIGNEE = "luis.sosa@bairesdev.com"

# Epic details
EPIC_SUMMARY = "[EPIC] Your Epic Name Here"
EPIC_DESCRIPTION = """Your epic description here.

Key Features:
- Feature 1
- Feature 2
- Feature 3

Value: Describe the value/impact
"""

# Sprint details
SPRINT_NAME = "Sprint X - Your Sprint Name"
SPRINT_DURATION_DAYS = 14  # 2 weeks
SPRINT_GOAL = "Your sprint goal here"

# User Stories
USER_STORIES = [
    {
        "summary": "Story 1 summary",
        "description": """As a [user], I want [goal], so that [benefit].

Acceptance Criteria:
- Criterion 1
- Criterion 2

Technical Notes:
- Note 1""",
        "points": 5,
        "priority": "High"
    },
    {
        "summary": "Story 2 summary",
        "description": """Story 2 description...""",
        "points": 3,
        "priority": "Medium"
    },
    # Add more stories here...
]

# ============================================================================
# SCRIPT LOGIC - DON'T MODIFY BELOW UNLESS NEEDED
# ============================================================================

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Basic {base64.b64encode(f'{EMAIL}:{API_TOKEN}'.encode()).decode()}"
}


def make_request(url: str, method: str = "GET", data: dict = None):
    """Make request to Jira API."""
    req_data = json.dumps(data).encode('utf-8') if data else None
    request = urllib.request.Request(url, data=req_data, headers=HEADERS, method=method)
    
    try:
        with urllib.request.urlopen(request) as response:
            if response.status in [200, 201, 204]:
                response_data = response.read().decode('utf-8')
                return json.loads(response_data) if response_data else {}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"❌ HTTP {e.code}: {error_body}")
        raise


def create_sprint(name: str, start_date: str, end_date: str, goal: str = ""):
    """Create a new sprint."""
    url = f"{JIRA_URL}/rest/agile/1.0/sprint"
    data = {
        "name": name,
        "startDate": start_date,
        "endDate": end_date,
        "originBoardId": BOARD_ID,
        "goal": goal
    }
    result = make_request(url, method="POST", data=data)
    return result['id']


def create_issue(summary: str, description: str, issue_type: str, 
                 priority: str = "Medium", story_points: int = None, 
                 parent_key: str = None):
    """Create a new issue."""
    url = f"{JIRA_URL}/rest/api/3/issue"
    
    fields = {
        "project": {"key": PROJECT_KEY},
        "summary": summary,
        "description": {
            "type": "doc",
            "version": 1,
            "content": [{
                "type": "paragraph",
                "content": [{"type": "text", "text": description}]
            }]
        },
        "issuetype": {"name": issue_type},
        "priority": {"name": priority}
    }
    
    if issue_type != "Epic":
        fields["assignee"] = {"emailAddress": ASSIGNEE}
    
    if parent_key and issue_type != "Epic":
        fields["parent"] = {"key": parent_key}
    
    if story_points and issue_type == "Story":
        fields["customfield_10016"] = story_points
    
    result = make_request(url, method="POST", data={"fields": fields})
    print(f"✅ Created {issue_type}: {result['key']} - {summary}")
    return result['key']


def move_issues_to_sprint(sprint_id: int, issue_keys: list):
    """Move issues to a sprint."""
    url = f"{JIRA_URL}/rest/agile/1.0/sprint/{sprint_id}/issue"
    data = {"issues": issue_keys}
    
    try:
        make_request(url, method="POST", data=data)
        print(f"✅ Moved {len(issue_keys)} issues to Sprint {sprint_id}")
    except:
        print(f"⚠️  Could not move issues to sprint (may need manual move)")


def main():
    """Create Epic, Sprint, and Stories."""
    print("\n" + "="*80)
    print("🚀 Creating New Epic, Sprint, and Stories")
    print("="*80)
    
    # Create Epic
    print("\n📋 Step 1: Creating Epic...")
    epic_key = create_issue(
        summary=EPIC_SUMMARY,
        description=EPIC_DESCRIPTION,
        issue_type="Epic",
        priority="Medium"
    )
    
    # Create Sprint
    print("\n📅 Step 2: Creating Sprint...")
    start_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT09:00:00.000Z")
    end_date = (datetime.now() + timedelta(days=SPRINT_DURATION_DAYS)).strftime("%Y-%m-%dT17:00:00.000Z")
    
    sprint_id = create_sprint(
        name=SPRINT_NAME,
        start_date=start_date,
        end_date=end_date,
        goal=SPRINT_GOAL
    )
    print(f"✅ Created Sprint: {sprint_id}")
    
    # Create User Stories
    print(f"\n📝 Step 3: Creating {len(USER_STORIES)} User Stories...")
    story_keys = []
    
    for story in USER_STORIES:
        story_key = create_issue(
            summary=story["summary"],
            description=story["description"],
            issue_type="Story",
            story_points=story.get("points"),
            priority=story.get("priority", "Medium"),
            parent_key=epic_key
        )
        story_keys.append(story_key)
    
    # Move stories to sprint
    print(f"\n📦 Step 4: Moving stories to Sprint...")
    move_issues_to_sprint(sprint_id, story_keys)
    
    # Summary
    print("\n" + "="*80)
    print("✅ DONE!")
    print("="*80)
    print(f"\n📊 Summary:")
    print(f"   Epic: {epic_key} - {EPIC_SUMMARY}")
    print(f"   Sprint: {sprint_id} - {SPRINT_NAME}")
    print(f"   Stories Created: {len(story_keys)}")
    print(f"   Total Story Points: {sum(s.get('points', 0) for s in USER_STORIES)}")
    print(f"\n🔗 Links:")
    print(f"   Epic: {JIRA_URL}/browse/{epic_key}")
    print(f"   Board: {JIRA_URL}/jira/software/projects/{PROJECT_KEY}/boards/{BOARD_ID}")


if __name__ == "__main__":
    main()

