#!/usr/bin/env python3
"""Get issues from Epic 6."""

import json
import urllib.request
import urllib.error
import base64

# Configuration
JIRA_URL = "https://luis-sosa-bairesdev.atlassian.net"
EMAIL = "luis.sosa@bairesdev.com"
API_TOKEN = "ATATT3xFfGF05S_SCHS3O_OqM3rJcN9nM9-g3AorAXYCLvHDC2bvMGJhSgU9pCvIPNFPAbAmxJMU3UtO9R3ed-ccV7PInG7h51OTK9JTdS3ERz2Tdbrljl6E2yQDwVKtwsia8PI_UHC6F4wFE_P_D955n6fKNFiZBrCF4K3PNoonm6nxXKLNEJI=0B414822"
EPIC_6_KEY = "RDBP-78"


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
    
    req_data = json.dumps(data).encode('utf-8') if data else None
    request = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(request) as response:
            if response.status in [200, 201, 204]:
                response_data = response.read().decode('utf-8')
                return json.loads(response_data) if response_data else {}
            else:
                raise Exception(f"HTTP {response.status}")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"❌ HTTP {e.code}: {error_body}")
        return None


def get_epic_info():
    """Get Epic 6 information."""
    url = f"{JIRA_URL}/rest/api/3/issue/{EPIC_6_KEY}"
    return make_request(url)


def get_epic_child_issues():
    """Get child issues of Epic 6."""
    # Method 1: Try to get child issues directly
    url = f"{JIRA_URL}/rest/api/3/issue/{EPIC_6_KEY}?fields=subtasks"
    result = make_request(url)
    
    if result:
        print("\n📋 Epic Info:")
        print(json.dumps(result, indent=2))
    
    # Method 2: Search for issues with parent = RDBP-78
    print("\n\n🔍 Searching for child issues...")
    search_url = f"{JIRA_URL}/rest/api/3/search"
    jql = f"parent = {EPIC_6_KEY} ORDER BY created ASC"
    search_data = {
        "jql": jql,
        "fields": ["summary", "status", "key"],
        "maxResults": 50
    }
    
    search_result = make_request(search_url, method="POST", data=search_data)
    
    if search_result and 'issues' in search_result:
        issues = search_result['issues']
        print(f"\n✅ Found {len(issues)} child issues:\n")
        
        keys = []
        for issue in issues:
            key = issue['key']
            summary = issue['fields']['summary']
            status = issue['fields']['status']['name']
            keys.append(key)
            print(f"   {key}: {summary}")
            print(f"      Status: {status}")
        
        print(f"\n\n📝 Issue Keys for Script:")
        print("EPIC_6_STORIES = [")
        for key in keys:
            print(f'    "{key}",')
        print("]")
        
        return keys
    
    return []


def main():
    """Main function."""
    print("="*80)
    print(f"GETTING EPIC 6 ISSUES: {EPIC_6_KEY}")
    print("="*80)
    
    # Get Epic info
    epic_info = get_epic_info()
    if epic_info:
        print(f"\n✅ Epic Found: {epic_info['fields']['summary']}")
        print(f"   Status: {epic_info['fields']['status']['name']}")
    
    # Get child issues
    child_keys = get_epic_child_issues()
    
    if not child_keys:
        print("\n❌ No child issues found")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()

