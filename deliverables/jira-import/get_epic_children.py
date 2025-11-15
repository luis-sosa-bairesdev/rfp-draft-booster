#!/usr/bin/env python3
"""Get child issues from an Epic."""

import json
import urllib.request
import urllib.error
import base64

# Configuration
JIRA_URL = "https://luis-sosa-bairesdev.atlassian.net"
EMAIL = "luis.sosa@bairesdev.com"
API_TOKEN = "ATATT3xFfGF0sSVc0RTQhwj6YNxUmVNcEVQAM4OWpmI-E553Bsc46avo_OI-Hlvf_IrYjf0_FBtsCgKBbIJ1KNM2gdrHvfsijPku4fIR9BrLCnm9WcpSKVr_EDeBG1te_aNUatYT5b9w6JSdNt7sgtl6ZdH32IgnTYWLCOh3VEGhnDF6mvWj1g0=0882E324"
EPIC_KEY = "RDBP-78"


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


def main():
    """Get Epic and its children."""
    print("="*80)
    print(f"GETTING EPIC {EPIC_KEY} AND ITS CHILDREN")
    print("="*80)
    
    # Get Epic info
    print(f"\n1️⃣ Getting Epic {EPIC_KEY} info...")
    url = f"{JIRA_URL}/rest/api/3/issue/{EPIC_KEY}?fields=summary,status,issuetype"
    epic_info = make_request(url)
    
    if epic_info:
        print(f"   ✅ Epic Found: {epic_info['fields']['summary']}")
        print(f"   Status: {epic_info['fields']['status']['name']}")
    else:
        print(f"   ❌ Could not get Epic {EPIC_KEY}")
        return
    
    # Search for child issues (stories with parent = EPIC_KEY)
    print(f"\n2️⃣ Searching for child issues...")
    search_url = f"{JIRA_URL}/rest/api/3/search"
    jql = f'parent = "{EPIC_KEY}" ORDER BY created ASC'
    
    search_data = {
        "jql": jql,
        "fields": ["summary", "status", "key", "issuetype"],
        "maxResults": 100
    }
    
    result = make_request(search_url, method="POST", data=search_data)
    
    if not result or 'issues' not in result:
        print("   ❌ Could not search for child issues")
        return
    
    issues = result['issues']
    print(f"   ✅ Found {len(issues)} child issues\n")
    
    if len(issues) == 0:
        print("   ⚠️  No child issues found. Epic may not have stories yet.")
        return
    
    # Display issues
    keys = []
    print("   " + "="*70)
    for issue in issues:
        key = issue['key']
        summary = issue['fields']['summary']
        status = issue['fields']['status']['name']
        issue_type = issue['fields']['issuetype']['name']
        keys.append(key)
        
        print(f"   {key}: {summary[:55]}")
        print(f"      Type: {issue_type} | Status: {status}")
        print("   " + "-"*70)
    
    # Generate script array
    print(f"\n3️⃣ Issue Keys for close script:")
    print("\nEPIC_6_STORIES = [")
    for key in keys:
        print(f'    "{key}",')
    print("]")
    
    print("\n" + "="*80)
    print(f"✅ DONE! Found {len(keys)} stories to close")
    print("="*80)


if __name__ == "__main__":
    main()

