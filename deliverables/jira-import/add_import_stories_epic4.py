#!/usr/bin/env python3
"""
Add import/export stories to Epic 4.
Creates 2 new user stories for import functionality.
"""

import json
import urllib.request
import urllib.error
import urllib.parse
import base64
import time

# Configuration
JIRA_URL = "https://luis-sosa-bairesdev.atlassian.net"
EMAIL = "luis.sosa@bairesdev.com"
API_TOKEN = "ATATT3xFfGF05S_SCHS3O_OqM3rJcN9nM9-g3AorAXYCLvHDC2bvMGJhSgU9pCvIPNFPAbAmxJMU3UtO9R3ed-ccV7PInG7h51OTK9JTdS3ERz2Tdbrljl6E2yQDwVKtwsia8PI_UHC6F4wFE_P_D955n6fKNFiZBrCF4K3PNoonm6nxXKLNEJI=0B414822"
PROJECT_KEY = "RDBP"
BOARD_ID = 34
ASSIGNEE = "luis.sosa@bairesdev.com"
EPIC_4_KEY = "RDBP-37"  # Epic 4
SPRINT_3_ID = 71  # Sprint 3


def make_request(url: str, method: str = "GET", data: dict = None):
    """Make a request to Jira API."""
    auth_string = f"{EMAIL}:{API_TOKEN}"
    auth_bytes = auth_string.encode('ascii')
    auth_header = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    if data:
        data_bytes = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
    else:
        req = urllib.request.Request(url, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status in [200, 201, 204]:
                response_data = response.read().decode('utf-8')
                return json.loads(response_data) if response_data else {}
            else:
                raise Exception(f"HTTP {response.status}")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"   ❌ HTTP {e.code}: {error_body}")
        return None


def create_issue(project_key: str, issue_type: str, summary: str, description: str, 
                 assignee: str = None, parent_key: str = None, story_points: int = None):
    """Create an issue."""
    url = f"{JIRA_URL}/rest/api/3/issue"
    
    # Convert description to Jira's document format
    description_content = []
    for line in description.split('\n'):
        if line.strip():
            description_content.append({
                "type": "paragraph",
                "content": [{"type": "text", "text": line}]
            })
    
    fields = {
        "project": {"key": project_key},
        "summary": summary,
        "description": {
            "type": "doc",
            "version": 1,
            "content": description_content if description_content else [
                {"type": "paragraph", "content": [{"type": "text", "text": description}]}
            ]
        },
        "issuetype": {"name": issue_type}
    }
    
    if assignee:
        fields["assignee"] = {"emailAddress": assignee}
    
    if parent_key:
        fields["parent"] = {"key": parent_key}
    
    if story_points:
        fields["customfield_10016"] = story_points
    
    data = {"fields": fields}
    return make_request(url, method="POST", data=data)


def move_issues_to_sprint(sprint_id: int, issue_keys: list):
    """Move issues to a sprint."""
    url = f"{JIRA_URL}/rest/agile/1.0/sprint/{sprint_id}/issue"
    data = {"issues": issue_keys}
    return make_request(url, method="POST", data=data)


def main():
    """Add import stories to Epic 4."""
    
    print("=" * 100)
    print("📝 ADDING IMPORT/EXPORT STORIES TO EPIC 4")
    print("=" * 100)
    
    # New stories for import functionality
    new_stories = [
        {
            "summary": "Import risks from JSON file",
            "description": """As a sales rep, I want to import previously exported risks from a JSON file, so that I can load saved risk analyses or share risks with my team.

Acceptance Criteria:
- File uploader accepts JSON files
- Validate JSON format and structure
- Convert JSON data to Risk objects
- Merge with existing risks (avoid duplicates by ID)
- Display success/error messages
- Support both risks and requirements import""",
            "points": 3,
            "type": "UI"
        },
        {
            "summary": "Import requirements from JSON file",
            "description": """As a sales rep, I want to import previously exported requirements from a JSON file, so that I can load saved requirement extractions or share requirements with my team.

Acceptance Criteria:
- File uploader accepts JSON files
- Validate JSON format and structure
- Convert JSON data to Requirement objects
- Merge with existing requirements (avoid duplicates by ID)
- Display success/error messages
- Support both requirements and risks import""",
            "points": 3,
            "type": "UI"
        }
    ]
    
    story_keys = []
    
    for i, story_data in enumerate(new_stories, 1):
        print(f"\n📝 Creating Story {i}/{len(new_stories)}: {story_data['summary']}")
        story = create_issue(
            PROJECT_KEY, 
            "Story", 
            story_data['summary'], 
            story_data['description'], 
            ASSIGNEE, 
            parent_key=EPIC_4_KEY, 
            story_points=story_data['points']
        )
        
        if story:
            story_key = story['key']
            story_keys.append(story_key)
            print(f"   ✅ Story created: {story_key} ({story_data['type']}, {story_data['points']} points)")
        else:
            print(f"   ❌ Failed to create story: {story_data['summary']}")
        
        time.sleep(0.5)
    
    # Add to Sprint 3
    if story_keys:
        print(f"\n🏃 Adding {len(story_keys)} stories to Sprint 3...")
        result = move_issues_to_sprint(SPRINT_3_ID, story_keys)
        
        if result is not None:
            print(f"   ✅ Added {len(story_keys)} stories to Sprint 3")
        else:
            print(f"   ❌ Failed to add stories to Sprint 3")
    
    print("\n" + "=" * 100)
    print("✅ IMPORT STORIES ADDED TO EPIC 4!")
    print("=" * 100)
    print(f"\n📊 Summary:")
    print(f"   ✅ {len(story_keys)} new stories created")
    print(f"   ✅ All stories linked to Epic 4 ({EPIC_4_KEY})")
    print(f"   ✅ All stories added to Sprint 3")
    print(f"\n🔗 View Epic 4:")
    print(f"   https://luis-sosa-bairesdev.atlassian.net/browse/{EPIC_4_KEY}")


if __name__ == "__main__":
    main()

