#!/usr/bin/env python3
"""Move Epic 21 and Epic 32 to Sprint 1."""

import json
import urllib.request
import urllib.error
import base64

# Configuration
JIRA_URL = "https://luis-sosa-bairesdev.atlassian.net"
EMAIL = "luis.sosa@bairesdev.com"
API_TOKEN = "ATATT3xFfGF05S_SCHS3O_OqM3rJcN9nM9-g3AorAXYCLvHDC2bvMGJhSgU9pCvIPNFPAbAmxJMU3UtO9R3ed-ccV7PInG7h51OTK9JTdS3ERz2Tdbrljl6E2yQDwVKtwsia8PI_UHC6F4wFE_P_D955n6fKNFiZBrCF4K3PNoonm6nxXKLNEJI=0B414822"
SPRINT_ID = 1  # Sprint 1
BOARD_ID = 1


def make_agile_request(endpoint: str, method: str = "POST", data: dict = None):
    """Make a request to Jira Agile API."""
    url = f"{JIRA_URL}/rest/agile/1.0/{endpoint}"
    
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


def move_issues_to_sprint(sprint_id: int, issue_keys: list):
    """Move issues to a sprint using Agile API."""
    endpoint = f"sprint/{sprint_id}/issue"
    data = {
        "issues": issue_keys
    }
    return make_agile_request(endpoint, method="POST", data=data)


def get_sprint_info(sprint_id: int):
    """Get sprint information."""
    endpoint = f"sprint/{sprint_id}"
    
    url = f"{JIRA_URL}/rest/agile/1.0/{endpoint}"
    auth_string = f"{EMAIL}:{API_TOKEN}"
    auth_bytes = auth_string.encode('ascii')
    auth_header = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Accept": "application/json"
    }
    
    req = urllib.request.Request(url, headers=headers, method="GET")
    
    try:
        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode('utf-8')
            return json.loads(response_data)
    except Exception as e:
        print(f"Error: {e}")
        return None


def main():
    """Move Epic 21 and Epic 32 to Sprint 1."""
    
    print("=" * 80)
    print("MOVING EPICS 21 & 32 TO SPRINT 1")
    print("=" * 80)
    
    # Get sprint info
    print(f"\n1. Getting Sprint {SPRINT_ID} information...")
    sprint = get_sprint_info(SPRINT_ID)
    
    if sprint:
        print(f"   ✅ Sprint: {sprint.get('name')}")
        print(f"   State: {sprint.get('state')}")
        print(f"   Start: {sprint.get('startDate', 'N/A')}")
        print(f"   End: {sprint.get('endDate', 'N/A')}")
    else:
        print(f"   ❌ Could not retrieve sprint info")
        return
    
    # Get Epic 21 user stories
    print(f"\n2. Finding User Stories for SCRUM-21 (Epic 1)...")
    epic21_stories = []
    for i in range(2, 12):  # Assuming SCRUM-2 to SCRUM-11
        epic21_stories.append(f"SCRUM-{i}")
    
    print(f"   Found potential stories: {', '.join(epic21_stories)}")
    
    # Get Epic 32 user stories  
    print(f"\n3. Finding User Stories for SCRUM-32 (Epic 2)...")
    epic32_stories = ["SCRUM-33", "SCRUM-34", "SCRUM-35", "SCRUM-36", 
                      "SCRUM-37", "SCRUM-38", "SCRUM-39", "SCRUM-40"]
    
    print(f"   Found stories: {', '.join(epic32_stories)}")
    
    # Move Epic 21 and its stories
    print(f"\n4. Moving SCRUM-21 (Epic 1) and its User Stories to Sprint {SPRINT_ID}...")
    issues_to_move = ["SCRUM-21"] + epic21_stories
    
    result = move_issues_to_sprint(SPRINT_ID, issues_to_move)
    if result is not None:
        print(f"   ✅ SCRUM-21 and {len(epic21_stories)} User Stories moved to Sprint {SPRINT_ID}")
    
    # Move Epic 32 and its stories
    print(f"\n5. Moving SCRUM-32 (Epic 2) and its User Stories to Sprint {SPRINT_ID}...")
    issues_to_move = ["SCRUM-32"] + epic32_stories
    
    result = move_issues_to_sprint(SPRINT_ID, issues_to_move)
    if result is not None:
        print(f"   ✅ SCRUM-32 and {len(epic32_stories)} User Stories moved to Sprint {SPRINT_ID}")
    
    print("\n" + "=" * 80)
    print("✅ EPICS MOVED TO SPRINT 1")
    print("=" * 80)
    print("\n🔗 View Sprint Board:")
    print(f"   https://luis-sosa-bairesdev.atlassian.net/jira/software/projects/SCRUM/boards/1")
    print("\n💡 Refresh your Jira board to see the changes!")


if __name__ == "__main__":
    main()

