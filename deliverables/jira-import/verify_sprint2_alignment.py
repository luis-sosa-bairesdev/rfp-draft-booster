#!/usr/bin/env python3
"""Verify Sprint 2 stories are aligned with Epic 3."""

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
EPIC3_KEY = "RDBP-21"


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
    """Verify Sprint 2 alignment with Epic 3."""
    
    print("=" * 120)
    print("🔍 VERIFYING SPRINT 2 ALIGNMENT WITH EPIC 3")
    print("=" * 120)
    
    # Get all issues from project
    print("\n📋 Getting all project issues...")
    url = f"{JIRA_URL}/rest/api/3/search/jql?jql={urllib.parse.quote(f'project = {PROJECT_KEY} ORDER BY key ASC')}&fields=key,summary,issuetype,parent,customfield_10020,status&maxResults=100"
    result = make_request(url)
    
    if not result:
        print("   ❌ Failed to retrieve issues")
        return
    
    issues = result.get('issues', [])
    print(f"   ✅ Found {len(issues)} issues total")
    
    # Find Sprint 2 issues
    sprint2_issues = []
    epic3_stories = []
    
    for issue in issues:
        sprint_info = issue['fields'].get('customfield_10020', [])
        sprint_name = sprint_info[0]['name'] if sprint_info and isinstance(sprint_info, list) and sprint_info else ""
        
        if 'Sprint 2' in sprint_name or 'LLM' in sprint_name:
            sprint2_issues.append(issue)
        
        # Track Epic 3 stories
        if issue['fields']['issuetype']['name'] in ['Story', 'Historia']:
            parent = issue['fields'].get('parent')
            if parent and parent['key'] == EPIC3_KEY:
                epic3_stories.append(issue)
    
    # Display Sprint 2 issues
    print("\n" + "=" * 120)
    print(f"🏃 SPRINT 2 ISSUES ({len(sprint2_issues)} total)")
    print("=" * 120)
    print(f"{'Key':<12} {'Type':<12} {'Summary':<60} {'Parent':<12} {'Status'}")
    print("-" * 120)
    
    sprint2_epics = []
    sprint2_stories = []
    
    for issue in sprint2_issues:
        key = issue['key']
        issue_type = issue['fields']['issuetype']['name']
        summary = issue['fields']['summary'][:57] + "..." if len(issue['fields']['summary']) > 60 else issue['fields']['summary']
        parent = issue['fields'].get('parent')
        parent_key = parent['key'] if parent else "No Parent"
        status = issue['fields']['status']['name']
        
        if issue_type == 'Epic':
            sprint2_epics.append(issue)
        else:
            sprint2_stories.append(issue)
        
        print(f"{key:<12} {issue_type:<12} {summary:<60} {parent_key:<12} {status}")
    
    # Display Epic 3 stories
    print("\n" + "=" * 120)
    print(f"🎯 EPIC 3 STORIES ({len(epic3_stories)} total)")
    print("=" * 120)
    print(f"{'Key':<12} {'Summary':<70} {'Sprint':<25} {'Status'}")
    print("-" * 120)
    
    for story in epic3_stories:
        key = story['key']
        summary = story['fields']['summary'][:67] + "..." if len(story['fields']['summary']) > 70 else story['fields']['summary']
        sprint_info = story['fields'].get('customfield_10020', [])
        sprint_name = sprint_info[0]['name'] if sprint_info and isinstance(sprint_info, list) and sprint_info else "No Sprint"
        status = story['fields']['status']['name']
        
        print(f"{key:<12} {summary:<70} {sprint_name:<25} {status}")
    
    # Analysis
    print("\n" + "=" * 120)
    print("📊 ALIGNMENT ANALYSIS")
    print("=" * 120)
    
    # Check if Epic 3 is in Sprint 2
    epic3_in_sprint2 = any(issue['key'] == EPIC3_KEY for issue in sprint2_issues)
    
    # Check if all Epic 3 stories are in Sprint 2
    epic3_stories_in_sprint2 = [s for s in epic3_stories if any(si['key'] == s['key'] for si in sprint2_issues)]
    epic3_stories_not_in_sprint2 = [s for s in epic3_stories if not any(si['key'] == s['key'] for si in sprint2_issues)]
    
    # Check for non-Epic 3 stories in Sprint 2
    non_epic3_stories_in_sprint2 = [s for s in sprint2_stories if s['fields'].get('parent', {}).get('key') != EPIC3_KEY]
    
    print(f"\n✅ Epic 3 (RDBP-21) in Sprint 2: {'YES' if epic3_in_sprint2 else 'NO'}")
    print(f"✅ Epic 3 stories in Sprint 2: {len(epic3_stories_in_sprint2)}/{len(epic3_stories)}")
    
    if epic3_stories_not_in_sprint2:
        print(f"\n⚠️  WARNING: {len(epic3_stories_not_in_sprint2)} Epic 3 stories NOT in Sprint 2:")
        for story in epic3_stories_not_in_sprint2:
            print(f"   - {story['key']}: {story['fields']['summary']}")
    
    if non_epic3_stories_in_sprint2:
        print(f"\n⚠️  WARNING: {len(non_epic3_stories_in_sprint2)} stories in Sprint 2 that DON'T belong to Epic 3:")
        for story in non_epic3_stories_in_sprint2:
            parent_key = story['fields'].get('parent', {}).get('key', 'No Parent')
            print(f"   - {story['key']}: {story['fields']['summary']} (Parent: {parent_key})")
    
    # Final verdict
    print("\n" + "=" * 120)
    if epic3_in_sprint2 and len(epic3_stories_in_sprint2) == len(epic3_stories) and len(non_epic3_stories_in_sprint2) == 0:
        print("✅ PERFECT ALIGNMENT!")
        print("   All Epic 3 stories are in Sprint 2, and Sprint 2 only contains Epic 3 stories.")
    elif len(epic3_stories_in_sprint2) == len(epic3_stories):
        print("✅ GOOD ALIGNMENT!")
        print("   All Epic 3 stories are in Sprint 2.")
        if non_epic3_stories_in_sprint2:
            print(f"   ⚠️  But Sprint 2 also contains {len(non_epic3_stories_in_sprint2)} stories from other epics.")
    else:
        print("⚠️  ALIGNMENT ISSUES DETECTED!")
        print(f"   Only {len(epic3_stories_in_sprint2)}/{len(epic3_stories)} Epic 3 stories are in Sprint 2.")
    
    print("=" * 120)
    
    # Epic 3 Story Details
    print("\n" + "=" * 120)
    print("📋 EPIC 3: LLM REQUIREMENT EXTRACTION - STORY DETAILS")
    print("=" * 120)
    
    epic3_expected_stories = [
        "RDBP-22: AI extracts requirements from RFP automatically",
        "RDBP-23: Requirements categorized (technical, functional, timeline, budget, compliance)",
        "RDBP-24: Requirements prioritized (critical, high, medium, low)",
        "RDBP-25: Confidence scores for each extraction",
        "RDBP-26: Show source page numbers for requirements",
        "RDBP-27: Edit extracted requirements",
        "RDBP-28: Add requirements manually",
        "RDBP-29: Delete incorrect extractions",
        "RDBP-30: Mark requirements as verified",
        "RDBP-31: Filter requirements by category/priority",
    ]
    
    print("\n✅ Expected Epic 3 Stories (10 total):")
    for expected in epic3_expected_stories:
        key = expected.split(':')[0]
        found = any(s['key'] == key for s in epic3_stories)
        in_sprint2 = any(s['key'] == key for s in epic3_stories_in_sprint2)
        status_emoji = "✅" if found and in_sprint2 else "⚠️" if found else "❌"
        sprint_status = "in Sprint 2" if in_sprint2 else "NOT in Sprint 2" if found else "NOT FOUND"
        print(f"   {status_emoji} {expected} - {sprint_status}")
    
    print(f"\n🔗 View Sprint 2:")
    print(f"   https://luis-sosa-bairesdev.atlassian.net/jira/software/projects/RDBP/boards/34")


if __name__ == "__main__":
    main()

