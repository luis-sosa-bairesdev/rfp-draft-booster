#!/usr/bin/env python3
"""Identify and delete old/duplicate epics."""

import json
import urllib.request
import urllib.error
import urllib.parse
import base64

# Configuration
JIRA_URL = "https://luis-sosa-bairesdev.atlassian.net"
EMAIL = "luis.sosa@bairesdev.com"
API_TOKEN = "ATATT3xFfGF05S_SCHS3O_OqM3rJcN9nM9-g3AorAXYCLvHDC2bvMGJhSgU9pCvIPNFPAbAmxJMU3UtO9R3ed-ccV7PInG7h51OTK9JTdS3ERz2Tdbrljl6E2yQDwVKtwsia8PI_UHC6F4wFE_P_D955n6fKNFiZBrCF4K3PNoonm6nxXKLNEJI=0B414822"
PROJECT_KEY = "SCRUM"

# Correct epics (the ones we want to KEEP)
KEEP_EPICS = ["SCRUM-21", "SCRUM-32"]


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
            if response.status in [200, 201, 204]:
                response_data = response.read().decode('utf-8')
                return json.loads(response_data) if response_data else {}
            else:
                raise Exception(f"HTTP {response.status}")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"   ❌ HTTP {e.code}: {error_body}")
        return None


def search_issues(jql: str):
    """Search for issues using JQL."""
    endpoint = f"search/jql?jql={urllib.parse.quote(jql)}&fields=key,summary,status,issuetype,created&maxResults=100"
    result = make_jira_request(endpoint)
    return result.get('issues', []) if result else []


def delete_issue(issue_key: str):
    """Delete an issue."""
    endpoint = f"issue/{issue_key}"
    return make_jira_request(endpoint, method="DELETE")


def main():
    """Identify and delete old/duplicate epics."""
    
    print("=" * 80)
    print("CLEANING UP OLD/DUPLICATE EPICS")
    print("=" * 80)
    
    # Find all epics
    print(f"\n1. Searching for all Epics in project {PROJECT_KEY}...")
    jql = f'project = {PROJECT_KEY} AND type = Epic'
    epics = search_issues(jql)
    
    print(f"   ✅ Found {len(epics)} Epics total")
    
    # Categorize epics
    print(f"\n2. Analyzing Epics...")
    print(f"\n   {'Key':<12} {'Summary':<50} {'Created':<20} {'Action'}")
    print(f"   {'-'*12} {'-'*50} {'-'*20} {'-'*15}")
    
    epics_to_delete = []
    epics_to_keep = []
    
    for epic in epics:
        key = epic['key']
        summary = epic['fields']['summary'][:47] + "..." if len(epic['fields']['summary']) > 50 else epic['fields']['summary']
        created = epic['fields']['created'][:10]
        
        if key in KEEP_EPICS:
            action = "✅ KEEP"
            epics_to_keep.append(key)
        else:
            action = "🗑️  DELETE"
            epics_to_delete.append(key)
        
        print(f"   {key:<12} {summary:<50} {created:<20} {action}")
    
    # Summary
    print(f"\n3. Summary:")
    print(f"   ✅ Epics to KEEP: {len(epics_to_keep)} ({', '.join(epics_to_keep)})")
    print(f"   🗑️  Epics to DELETE: {len(epics_to_delete)} ({', '.join(epics_to_delete)})")
    
    if not epics_to_delete:
        print(f"\n   ✅ No epics to delete. All clean!")
        return
    
    # Confirm deletion
    print(f"\n4. Deleting old/duplicate Epics...")
    
    for epic_key in epics_to_delete:
        print(f"   Deleting {epic_key}...", end=" ")
        result = delete_issue(epic_key)
        if result is not None:
            print(f"✅ Deleted")
        else:
            print(f"❌ Failed")
    
    print("\n" + "=" * 80)
    print("✅ CLEANUP COMPLETE")
    print("=" * 80)
    print(f"\n💡 Kept Epics: {', '.join(epics_to_keep)}")
    print(f"🗑️  Deleted Epics: {', '.join(epics_to_delete)}")


if __name__ == "__main__":
    main()



