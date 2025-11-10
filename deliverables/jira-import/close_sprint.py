#!/usr/bin/env python3
"""Close Sprint 1."""

import json
import urllib.request
import urllib.error
import base64

# Configuration
JIRA_URL = "https://luis-sosa-bairesdev.atlassian.net"
EMAIL = "luis.sosa@bairesdev.com"
API_TOKEN = "ATATT3xFfGF05S_SCHS3O_OqM3rJcN9nM9-g3AorAXYCLvHDC2bvMGJhSgU9pCvIPNFPAbAmxJMU3UtO9R3ed-ccV7PInG7h51OTK9JTdS3ERz2Tdbrljl6E2yQDwVKtwsia8PI_UHC6F4wFE_P_D955n6fKNFiZBrCF4K3PNoonm6nxXKLNEJI=0B414822"
SPRINT_ID = 1


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
        print(f"HTTP {e.code}: {error_body}")
        return None


def get_sprint_info(sprint_id: int):
    """Get sprint information."""
    url = f"{JIRA_URL}/rest/agile/1.0/sprint/{sprint_id}"
    
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


def get_sprint_issues(sprint_id: int):
    """Get all issues in a sprint."""
    url = f"{JIRA_URL}/rest/agile/1.0/sprint/{sprint_id}/issue?fields=key,summary,status"
    
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
            result = json.loads(response_data)
            return result.get('issues', [])
    except Exception as e:
        print(f"Error: {e}")
        return []


def close_sprint(sprint_id: int):
    """Close a sprint."""
    endpoint = f"sprint/{sprint_id}"
    data = {
        "state": "closed"
    }
    return make_agile_request(endpoint, method="POST", data=data)


def main():
    """Close Sprint 1."""
    
    print("=" * 80)
    print("CLOSING SPRINT 1")
    print("=" * 80)
    
    # Get sprint info
    print(f"\n1. Getting Sprint {SPRINT_ID} information...")
    sprint = get_sprint_info(SPRINT_ID)
    
    if not sprint:
        print(f"   ❌ Could not retrieve sprint info")
        return
    
    print(f"   ✅ Sprint: {sprint.get('name')}")
    print(f"   Current State: {sprint.get('state')}")
    print(f"   Start: {sprint.get('startDate', 'N/A')[:10]}")
    print(f"   End: {sprint.get('endDate', 'N/A')[:10]}")
    
    if sprint.get('state') == 'closed':
        print(f"\n   ℹ️  Sprint is already closed!")
        return
    
    # Get sprint issues
    print(f"\n2. Getting issues in Sprint {SPRINT_ID}...")
    issues = get_sprint_issues(SPRINT_ID)
    
    print(f"   ✅ Found {len(issues)} issues")
    
    # Count by status
    status_counts = {}
    for issue in issues:
        status = issue['fields']['status']['name']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print(f"\n   Issue Status Breakdown:")
    for status, count in sorted(status_counts.items()):
        print(f"      - {status}: {count}")
    
    # Close sprint
    print(f"\n3. Closing Sprint {SPRINT_ID}...")
    result = close_sprint(SPRINT_ID)
    
    if result is not None:
        print(f"   ✅ Sprint {SPRINT_ID} closed successfully!")
    else:
        print(f"   ❌ Failed to close sprint")
        return
    
    print("\n" + "=" * 80)
    print("✅ SPRINT 1 CLOSED")
    print("=" * 80)
    print(f"\n📊 Sprint Summary:")
    print(f"   Total Issues: {len(issues)}")
    for status, count in sorted(status_counts.items()):
        print(f"   {status}: {count}")
    
    print(f"\n🔗 View Sprint Report:")
    print(f"   https://luis-sosa-bairesdev.atlassian.net/jira/software/projects/SCRUM/boards/1")


if __name__ == "__main__":
    main()

