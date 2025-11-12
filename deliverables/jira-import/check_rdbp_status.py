#!/usr/bin/env python3
"""Check RDBP project status."""

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


def make_request(url: str):
    """Make a GET request to Jira API."""
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
            return json.loads(response_data) if response_data else {}
    except Exception as e:
        print(f"Error: {e}")
        return None


def main():
    """Check RDBP project status."""
    
    print("=" * 120)
    print("📊 RDBP PROJECT STATUS")
    print("=" * 120)
    
    # Get all issues
    url = f"{JIRA_URL}/rest/api/3/search/jql?jql={urllib.parse.quote(f'project = {PROJECT_KEY} ORDER BY key ASC')}&fields=key,summary,issuetype,parent,customfield_10020&maxResults=100"
    result = make_request(url)
    
    if not result:
        print("❌ Failed to retrieve issues")
        return
    
    issues = result.get('issues', [])
    print(f"\n✅ Found {len(issues)} issues total\n")
    
    # Categorize
    epics = []
    stories = []
    others = []
    
    for issue in issues:
        issue_type = issue['fields']['issuetype']['name']
        if issue_type == 'Epic':
            epics.append(issue)
        elif issue_type == 'Story':
            stories.append(issue)
        else:
            others.append(issue)
    
    # Display Epics
    print(f"{'='*120}")
    print(f"🎯 EPICS ({len(epics)})")
    print(f"{'='*120}")
    print(f"{'Key':<12} {'Summary':<70} {'Sprint'}")
    print(f"{'-'*120}")
    
    for epic in epics:
        key = epic['key']
        summary = epic['fields']['summary'][:67] + "..." if len(epic['fields']['summary']) > 70 else epic['fields']['summary']
        sprint_info = epic['fields'].get('customfield_10020', [])
        sprint_name = sprint_info[0]['name'] if sprint_info and isinstance(sprint_info, list) and sprint_info else "No Sprint"
        
        print(f"{key:<12} {summary:<70} {sprint_name}")
    
    # Display Stories
    print(f"\n{'='*120}")
    print(f"📝 USER STORIES ({len(stories)})")
    print(f"{'='*120}")
    print(f"{'Key':<12} {'Summary':<50} {'Parent':<12} {'Sprint'}")
    print(f"{'-'*120}")
    
    for story in stories:
        key = story['key']
        summary = story['fields']['summary'][:47] + "..." if len(story['fields']['summary']) > 50 else story['fields']['summary']
        parent = story['fields'].get('parent')
        parent_key = parent['key'] if parent else "No Parent"
        sprint_info = story['fields'].get('customfield_10020', [])
        sprint_name = sprint_info[0]['name'] if sprint_info and isinstance(sprint_info, list) and sprint_info else "No Sprint"
        
        print(f"{key:<12} {summary:<50} {parent_key:<12} {sprint_name}")
    
    # Display Others
    if others:
        print(f"\n{'='*120}")
        print(f"📌 OTHER ISSUES ({len(others)})")
        print(f"{'='*120}")
        for other in others[:5]:
            key = other['key']
            issue_type = other['fields']['issuetype']['name']
            summary = other['fields']['summary'][:50]
            print(f"{key:<12} ({issue_type}) {summary}")
        if len(others) > 5:
            print(f"   ... and {len(others) - 5} more")
    
    # Summary
    print(f"\n{'='*120}")
    print(f"📊 SUMMARY")
    print(f"{'='*120}")
    print(f"Total Issues: {len(issues)}")
    print(f"  - Epics: {len(epics)}")
    print(f"  - Stories: {len(stories)}")
    print(f"  - Others: {len(others)}")
    
    # Check for issues
    stories_without_parent = [s for s in stories if not s['fields'].get('parent')]
    stories_without_sprint = [s for s in stories if not s['fields'].get('customfield_10020')]
    
    if stories_without_parent:
        print(f"\n⚠️  WARNING: {len(stories_without_parent)} stories WITHOUT parent Epic")
    
    if stories_without_sprint:
        print(f"⚠️  WARNING: {len(stories_without_sprint)} stories WITHOUT Sprint")
    
    print(f"\n🔗 View Board: https://luis-sosa-bairesdev.atlassian.net/jira/software/projects/RDBP/boards/34")
    print(f"🔗 View Backlog: https://luis-sosa-bairesdev.atlassian.net/jira/software/projects/RDBP/boards/34/backlog")


if __name__ == "__main__":
    main()



