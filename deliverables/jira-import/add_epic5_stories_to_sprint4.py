#!/usr/bin/env python3
"""Add Epic 5 stories to Sprint 4."""

import urllib.request
import urllib.error
import json
import base64

JIRA_URL = "https://luis-sosa-bairesdev.atlassian.net"
EMAIL = "luis.sosa@bairesdev.com"
API_TOKEN = "ATATT3xFfGF05S_SCHS3O_OqM3rJcN9nM9-g3AorAXYCLvHDC2bvMGJhSgU9pCvIPNFPAbAmxJMU3UtO9R3ed-ccV7PInG7h51OTK9JTdS3ERz2Tdbrljl6E2yQDwVKtwsia8PI_UHC6F4wFE_P_D955n6fKNFiZBrCF4K3PNoonm6nxXKLNEJI=0B414822"

SPRINT_ID = 104  # Sprint 4
EPIC_KEY = "RDBP-55"  # Epic 5

def make_request(url: str, method: str = "GET", data: dict = None):
    """Make authenticated request to Jira API."""
    credentials = base64.b64encode(f"{EMAIL}:{API_TOKEN}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    req_data = None
    if data:
        req_data = json.dumps(data).encode('utf-8')
    
    request = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"   ❌ HTTP {e.code}: {error_body}")
        return None
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None

def get_epic_stories(epic_key: str):
    """Get all stories linked to Epic 5."""
    jql = f'project = RDBP AND parent = {epic_key}'
    url = f"{JIRA_URL}/rest/api/3/search"
    data = {
        "jql": jql,
        "fields": ["key", "summary"],
        "maxResults": 50
    }
    result = make_request(url, method="POST", data=data)
    if result:
        return [issue['key'] for issue in result.get('issues', [])]
    return []

def add_to_sprint(sprint_id: int, issue_keys: list):
    """Add issues to sprint."""
    url = f"{JIRA_URL}/rest/agile/1.0/sprint/{sprint_id}/issue"
    data = {"issues": issue_keys}
    return make_request(url, method="POST", data=data)

def main():
    print("=" * 100)
    print("🏃 ADDING EPIC 5 STORIES TO SPRINT 4")
    print("=" * 100)
    
    # Epic 5 stories (RDBP-56 to RDBP-68)
    story_keys = [
        "RDBP-56", "RDBP-57", "RDBP-58", "RDBP-59", "RDBP-60",
        "RDBP-61", "RDBP-62", "RDBP-63", "RDBP-64", "RDBP-65",
        "RDBP-66", "RDBP-67", "RDBP-68"
    ]
    
    print(f"\n📋 Epic 5 Stories ({len(story_keys)} stories):")
    for key in story_keys:
        print(f"      - {key}")
    
    # Add to Sprint 4
    print(f"\n🏃 Adding {len(story_keys)} stories to Sprint {SPRINT_ID}...")
    result = add_to_sprint(SPRINT_ID, story_keys)
    
    if result is not None:
        print(f"   ✅ All stories added to Sprint 4")
    else:
        print(f"   ⚠️  Some stories may not have been added (check manually)")

if __name__ == "__main__":
    main()

