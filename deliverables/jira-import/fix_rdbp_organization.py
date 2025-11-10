#!/usr/bin/env python3
"""Fix RDBP project organization: link stories to epics and move to sprints."""

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
SPRINT1_ID = 36
SPRINT2_ID = 37


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
        print(f"HTTP {e.code}: {error_body}")
        return None


def update_issue_parent(issue_key: str, parent_key: str):
    """Set parent for an issue."""
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}"
    data = {
        "fields": {
            "parent": {"key": parent_key}
        }
    }
    return make_request(url, method="PUT", data=data)


def move_issues_to_sprint(sprint_id: int, issue_keys: list):
    """Move issues to a sprint."""
    url = f"{JIRA_URL}/rest/agile/1.0/sprint/{sprint_id}/issue"
    data = {"issues": issue_keys}
    return make_request(url, method="POST", data=data)


def main():
    """Fix RDBP project organization."""
    
    print("=" * 100)
    print("🔧 FIXING RDBP PROJECT ORGANIZATION")
    print("=" * 100)
    
    # Get all issues
    print("\n🔍 Getting all issues...")
    url = f"{JIRA_URL}/rest/api/3/search/jql?jql={urllib.parse.quote(f'project = {PROJECT_KEY} ORDER BY key ASC')}&fields=key,summary,issuetype&maxResults=100"
    result = make_request(url)
    
    if not result:
        print("   ❌ Failed to retrieve issues")
        return
    
    issues = result.get('issues', [])
    print(f"   ✅ Found {len(issues)} issues")
    
    # Organize issues
    epic1_key = "RDBP-1"  # Epic 1
    epic2_key = "RDBP-12"  # Epic 2
    epic3_key = "RDBP-21"  # Epic 3
    
    epic1_stories = ["RDBP-2", "RDBP-3", "RDBP-4", "RDBP-5", "RDBP-6", 
                     "RDBP-7", "RDBP-8", "RDBP-9", "RDBP-10", "RDBP-11"]
    
    epic2_stories = ["RDBP-13", "RDBP-14", "RDBP-15", "RDBP-16", "RDBP-17", 
                     "RDBP-18", "RDBP-19", "RDBP-20"]
    
    epic3_stories = ["RDBP-22", "RDBP-23", "RDBP-24", "RDBP-25", "RDBP-26", 
                     "RDBP-27", "RDBP-28", "RDBP-29", "RDBP-30", "RDBP-31"]
    
    # Step 1: Link stories to epics
    print("\n" + "=" * 100)
    print("🔗 STEP 1: LINK STORIES TO EPICS")
    print("=" * 100)
    
    print(f"\n🔗 Linking Epic 1 stories ({len(epic1_stories)} stories)...")
    for story_key in epic1_stories:
        result = update_issue_parent(story_key, epic1_key)
        if result is not None:
            print(f"   ✅ {story_key} → {epic1_key}")
        else:
            print(f"   ❌ Failed to link {story_key}")
        time.sleep(0.3)
    
    print(f"\n🔗 Linking Epic 2 stories ({len(epic2_stories)} stories)...")
    for story_key in epic2_stories:
        result = update_issue_parent(story_key, epic2_key)
        if result is not None:
            print(f"   ✅ {story_key} → {epic2_key}")
        else:
            print(f"   ❌ Failed to link {story_key}")
        time.sleep(0.3)
    
    print(f"\n🔗 Linking Epic 3 stories ({len(epic3_stories)} stories)...")
    for story_key in epic3_stories:
        result = update_issue_parent(story_key, epic3_key)
        if result is not None:
            print(f"   ✅ {story_key} → {epic3_key}")
        else:
            print(f"   ❌ Failed to link {story_key}")
        time.sleep(0.3)
    
    # Step 2: Move to sprints
    print("\n" + "=" * 100)
    print("🏃 STEP 2: MOVE TO SPRINTS")
    print("=" * 100)
    
    # Move Epic 1 + Epic 2 and their stories to Sprint 1
    sprint1_issues = [epic1_key, epic2_key] + epic1_stories + epic2_stories
    
    print(f"\n🏃 Moving Epic 1 & Epic 2 to Sprint 1 ({len(sprint1_issues)} issues)...")
    result = move_issues_to_sprint(SPRINT1_ID, sprint1_issues)
    if result is not None:
        print(f"   ✅ Moved {len(sprint1_issues)} issues to Sprint 1")
        print(f"      - {epic1_key} + {len(epic1_stories)} stories")
        print(f"      - {epic2_key} + {len(epic2_stories)} stories")
    else:
        print(f"   ❌ Failed to move issues to Sprint 1")
    
    time.sleep(2)
    
    # Move Epic 3 and its stories to Sprint 2
    sprint2_issues = [epic3_key] + epic3_stories
    
    print(f"\n🏃 Moving Epic 3 to Sprint 2 ({len(sprint2_issues)} issues)...")
    result = move_issues_to_sprint(SPRINT2_ID, sprint2_issues)
    if result is not None:
        print(f"   ✅ Moved {len(sprint2_issues)} issues to Sprint 2")
        print(f"      - {epic3_key} + {len(epic3_stories)} stories")
    else:
        print(f"   ❌ Failed to move issues to Sprint 2")
    
    # Final summary
    print("\n" + "=" * 100)
    print("✅ PROJECT ORGANIZATION FIXED!")
    print("=" * 100)
    
    print(f"\n📊 Summary:")
    print(f"   ✅ Linked {len(epic1_stories) + len(epic2_stories) + len(epic3_stories)} stories to epics")
    print(f"   ✅ Sprint 1: Epic 1 ({len(epic1_stories)} stories) + Epic 2 ({len(epic2_stories)} stories)")
    print(f"   ✅ Sprint 2: Epic 3 ({len(epic3_stories)} stories)")
    
    print(f"\n🔗 View Your Board:")
    print(f"   https://luis-sosa-bairesdev.atlassian.net/jira/software/projects/RDBP/boards/34")
    print(f"\n🔗 View Backlog:")
    print(f"   https://luis-sosa-bairesdev.atlassian.net/jira/software/projects/RDBP/boards/34/backlog")
    
    print(f"\n💡 Refresh your Jira board - everything should be organized now!")


if __name__ == "__main__":
    main()

