#!/usr/bin/env python3
"""Check the status of Epic 1 and Epic 2."""

import json
import urllib.request
import urllib.error
import urllib.parse
import base64

# Configuration
JIRA_URL = "https://luis-sosa-bairesdev.atlassian.net"
EMAIL = "luis.sosa@bairesdev.com"
API_TOKEN = "ATATT3xFfGF05S_SCHS3O_OqM3rJcN9nM9-g3AorAXYCLvHDC2bvMGJhSgU9pCvIPNFPAbAmxJMU3UtO9R3ed-ccV7PInG7h51OTK9JTdS3ERz2Tdbrljl6E2yQDwVKtwsia8PI_UHC6F4wFE_P_D955n6fKNFiZBrCF4K3PNoonm6nxXKLNEJI=0B414822"


def make_jira_request(endpoint: str, method: str = "GET", data: dict = None):
    """Make a request to Jira API."""
    url = f"{JIRA_URL}/rest/api/3/{endpoint}"
    
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
            response_data = response.read().decode('utf-8')
            return json.loads(response_data) if response_data else {}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"HTTP {e.code}: {error_body}")
        return None


def get_issue_details(issue_key: str):
    """Get detailed information about an issue."""
    endpoint = f"issue/{issue_key}?fields=summary,status,issuetype,sprint,customfield_10020"
    return make_jira_request(endpoint)


def get_agile_issue_info(issue_key: str):
    """Get agile/sprint information for an issue."""
    # Try the agile API
    url = f"{JIRA_URL}/rest/agile/1.0/issue/{issue_key}"
    
    auth_string = f"{EMAIL}:{API_TOKEN}"
    auth_bytes = auth_string.encode('ascii')
    import base64
    auth_header = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Accept": "application/json"
    }
    
    req = urllib.request.Request(url, headers=headers, method="GET")
    
    try:
        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode('utf-8')
            return json.loads(response_data) if response_data else {}
    except Exception as e:
        print(f"   Error getting agile info: {e}")
        return None


def main():
    """Check Epic 1 and Epic 2 status."""
    
    print("=" * 80)
    print("CHECKING EPIC STATUS - SCRUM-1 vs SCRUM-2")
    print("=" * 80)
    
    for issue_key in ["SCRUM-1", "SCRUM-2"]:
        print(f"\n{'='*80}")
        print(f"Checking {issue_key}...")
        print('='*80)
        
        # Get basic info
        issue = get_issue_details(issue_key)
        
        if not issue:
            print(f"❌ Could not retrieve {issue_key}")
            continue
        
        fields = issue.get('fields', {})
        
        print(f"\n📋 Basic Information:")
        print(f"   Summary: {fields.get('summary', 'N/A')}")
        print(f"   Type: {fields.get('issuetype', {}).get('name', 'N/A')}")
        print(f"   Status: {fields.get('status', {}).get('name', 'N/A')}")
        
        # Check sprint field (customfield_10020 is typically the Sprint field)
        sprint_field = fields.get('customfield_10020')
        print(f"\n🏃 Sprint Information:")
        if sprint_field:
            if isinstance(sprint_field, list):
                if sprint_field:
                    for sprint in sprint_field:
                        print(f"   ✅ In Sprint: {sprint}")
                else:
                    print(f"   📋 Sprint field exists but empty")
            else:
                print(f"   ✅ Sprint: {sprint_field}")
        else:
            print(f"   📋 Not in any Sprint")
        
        # Try agile API
        agile_info = get_agile_issue_info(issue_key)
        if agile_info:
            print(f"\n🔧 Agile Info:")
            sprint = agile_info.get('fields', {}).get('sprint')
            if sprint:
                print(f"   Sprint ID: {sprint.get('id')}")
                print(f"   Sprint Name: {sprint.get('name')}")
                print(f"   Sprint State: {sprint.get('state')}")
            else:
                print(f"   No active sprint")
        
        # Print all custom fields for debugging
        print(f"\n🔍 All Custom Fields (for debugging):")
        for key, value in fields.items():
            if key.startswith('customfield_'):
                print(f"   {key}: {value}")
    
    print("\n" + "=" * 80)
    print("✅ CHECK COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()

