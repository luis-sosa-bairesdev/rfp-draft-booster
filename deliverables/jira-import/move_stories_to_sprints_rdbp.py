#!/usr/bin/env python3
"""Move all User Stories to their respective Sprints."""

import json
import urllib.request
import urllib.error
import urllib.parse
import base64

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


def move_issues_to_sprint(sprint_id: int, issue_keys: list):
    """Move issues to a sprint."""
    url = f"{JIRA_URL}/rest/agile/1.0/sprint/{sprint_id}/issue"
    data = {"issues": issue_keys}
    return make_request(url, method="POST", data=data)


def main():
    """Move all User Stories to their respective Sprints."""
    
    print("=" * 100)
    print("🏃 MOVING USER STORIES TO SPRINTS")
    print("=" * 100)
    
    # Get all issues
    print("\n🔍 Getting all issues from project RDBP...")
    url = f"{JIRA_URL}/rest/api/3/search/jql?jql={urllib.parse.quote(f'project = {PROJECT_KEY} ORDER BY key ASC')}&fields=key,summary,issuetype,parent&maxResults=100"
    search_result = make_request(url)
    
    if not search_result:
        print("   ❌ Failed to retrieve issues")
        return
    
    issues = search_result.get('issues', [])
    print(f"   ✅ Found {len(issues)} issues total")
    
    # Organize issues
    epic1_key = "RDBP-1"  # Epic 1: Project Setup
    epic2_key = "RDBP-12"  # Epic 2: PDF Processing
    epic3_key = "RDBP-21"  # Epic 3: LLM Requirements
    
    epic1_stories = []
    epic2_stories = []
    epic3_stories = []
    
    for issue in issues:
        issue_type = issue['fields']['issuetype']['name']
        issue_key = issue['key']
        
        if issue_type == 'Story':
            parent = issue['fields'].get('parent')
            if parent:
                parent_key = parent['key']
                if parent_key == epic1_key:
                    epic1_stories.append(issue_key)
                elif parent_key == epic2_key:
                    epic2_stories.append(issue_key)
                elif parent_key == epic3_key:
                    epic3_stories.append(issue_key)
    
    print(f"\n📊 Found User Stories:")
    print(f"   Epic 1 ({epic1_key}): {len(epic1_stories)} stories")
    print(f"   Epic 2 ({epic2_key}): {len(epic2_stories)} stories")
    print(f"   Epic 3 ({epic3_key}): {len(epic3_stories)} stories")
    
    # Move Epic 1 stories to Sprint 1
    print(f"\n🏃 Moving Epic 1 stories to Sprint 1...")
    if epic1_stories:
        result = move_issues_to_sprint(SPRINT1_ID, epic1_stories)
        if result is not None:
            print(f"   ✅ Moved {len(epic1_stories)} stories to Sprint 1")
            for key in epic1_stories:
                print(f"      - {key}")
        else:
            print(f"   ❌ Failed to move Epic 1 stories")
    else:
        print(f"   ⚠️  No stories found for Epic 1")
    
    # Move Epic 2 stories to Sprint 1
    print(f"\n🏃 Moving Epic 2 stories to Sprint 1...")
    if epic2_stories:
        result = move_issues_to_sprint(SPRINT1_ID, epic2_stories)
        if result is not None:
            print(f"   ✅ Moved {len(epic2_stories)} stories to Sprint 1")
            for key in epic2_stories:
                print(f"      - {key}")
        else:
            print(f"   ❌ Failed to move Epic 2 stories")
    else:
        print(f"   ⚠️  No stories found for Epic 2")
    
    # Move Epic 3 stories to Sprint 2
    print(f"\n🏃 Moving Epic 3 stories to Sprint 2...")
    if epic3_stories:
        result = move_issues_to_sprint(SPRINT2_ID, epic3_stories)
        if result is not None:
            print(f"   ✅ Moved {len(epic3_stories)} stories to Sprint 2")
            for key in epic3_stories:
                print(f"      - {key}")
        else:
            print(f"   ❌ Failed to move Epic 3 stories")
    else:
        print(f"   ⚠️  No stories found for Epic 3")
    
    # Summary
    print("\n" + "=" * 100)
    print("✅ USER STORIES MOVED TO SPRINTS")
    print("=" * 100)
    
    print(f"\n📊 Summary:")
    print(f"   Sprint 1: Epic 1 ({len(epic1_stories)} stories) + Epic 2 ({len(epic2_stories)} stories)")
    print(f"   Sprint 2: Epic 3 ({len(epic3_stories)} stories)")
    print(f"   Total Stories Moved: {len(epic1_stories) + len(epic2_stories) + len(epic3_stories)}")
    
    print(f"\n🔗 View Your Board:")
    print(f"   https://luis-sosa-bairesdev.atlassian.net/jira/software/projects/RDBP/boards/34")
    print(f"\n🔗 View Backlog:")
    print(f"   https://luis-sosa-bairesdev.atlassian.net/jira/software/projects/RDBP/boards/34/backlog")
    
    print(f"\n💡 Refresh your Jira board to see all User Stories in their Sprints!")


if __name__ == "__main__":
    main()



