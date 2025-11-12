#!/usr/bin/env python3
"""Verify current Jira status - all issues and sprints."""

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
BOARD_ID = 1


def make_request(url: str, method: str = "GET"):
    """Make a request to Jira API."""
    auth_string = f"{EMAIL}:{API_TOKEN}"
    auth_bytes = auth_string.encode('ascii')
    auth_header = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Accept": "application/json"
    }
    
    req = urllib.request.Request(url, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode('utf-8')
            return json.loads(response_data) if response_data else {}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"HTTP {e.code}: {error_body}")
        return None


def get_all_issues():
    """Get all issues in the project."""
    url = f"{JIRA_URL}/rest/api/3/search/jql?jql={urllib.parse.quote(f'project = {PROJECT_KEY} ORDER BY key ASC')}&fields=key,summary,status,issuetype,sprint,customfield_10020&maxResults=100"
    return make_request(url)


def get_all_sprints():
    """Get all sprints for the board."""
    url = f"{JIRA_URL}/rest/agile/1.0/board/{BOARD_ID}/sprint"
    return make_request(url)


def main():
    """Verify current Jira status."""
    
    print("=" * 100)
    print("JIRA STATUS VERIFICATION")
    print("=" * 100)
    
    # Get all sprints
    print("\n📅 SPRINTS:")
    print("-" * 100)
    sprints_data = get_all_sprints()
    
    if sprints_data:
        sprints = sprints_data.get('values', [])
        print(f"\nTotal Sprints: {len(sprints)}\n")
        
        for sprint in sprints:
            state_emoji = "✅" if sprint['state'] == 'closed' else "🔄" if sprint['state'] == 'active' else "📋"
            print(f"{state_emoji} Sprint {sprint['id']}: {sprint['name']}")
            print(f"   State: {sprint['state'].upper()}")
            print(f"   Start: {sprint.get('startDate', 'N/A')[:10]}")
            print(f"   End: {sprint.get('endDate', 'N/A')[:10]}")
            print()
    else:
        print("❌ Could not retrieve sprints")
    
    # Get all issues
    print("\n📋 ALL ISSUES IN PROJECT:")
    print("-" * 100)
    
    issues_data = get_all_issues()
    
    if not issues_data:
        print("❌ Could not retrieve issues")
        return
    
    issues = issues_data.get('issues', [])
    print(f"\nTotal Issues: {len(issues)}\n")
    
    # Categorize by type
    epics = []
    stories = []
    tasks = []
    others = []
    
    for issue in issues:
        issue_type = issue['fields']['issuetype']['name']
        if issue_type == 'Epic':
            epics.append(issue)
        elif issue_type in ['Historia', 'Story', 'User Story']:
            stories.append(issue)
        elif issue_type in ['Tarea', 'Task']:
            tasks.append(issue)
        else:
            others.append(issue)
    
    # Display Epics
    print(f"🎯 EPICS ({len(epics)}):")
    print(f"{'Key':<12} {'Summary':<60} {'Status':<20} {'Sprint'}")
    print("-" * 100)
    
    if epics:
        for epic in epics:
            key = epic['key']
            summary = epic['fields']['summary'][:57] + "..." if len(epic['fields']['summary']) > 60 else epic['fields']['summary']
            status = epic['fields']['status']['name']
            sprint_info = epic['fields'].get('customfield_10020', [])
            sprint_name = sprint_info[0]['name'] if sprint_info and isinstance(sprint_info, list) and sprint_info else "No Sprint"
            
            print(f"{key:<12} {summary:<60} {status:<20} {sprint_name}")
    else:
        print("   (No epics found)")
    
    # Display User Stories
    print(f"\n📝 USER STORIES ({len(stories)}):")
    print(f"{'Key':<12} {'Summary':<60} {'Status':<20} {'Sprint'}")
    print("-" * 100)
    
    if stories:
        for story in stories[:10]:  # Show first 10
            key = story['key']
            summary = story['fields']['summary'][:57] + "..." if len(story['fields']['summary']) > 60 else story['fields']['summary']
            status = story['fields']['status']['name']
            sprint_info = story['fields'].get('customfield_10020', [])
            sprint_name = sprint_info[0]['name'] if sprint_info and isinstance(sprint_info, list) and sprint_info else "No Sprint"
            
            print(f"{key:<12} {summary:<60} {status:<20} {sprint_name}")
        
        if len(stories) > 10:
            print(f"   ... and {len(stories) - 10} more user stories")
    else:
        print("   (No user stories found)")
    
    # Display Tasks
    print(f"\n📌 TASKS ({len(tasks)}):")
    print(f"{'Key':<12} {'Summary':<60} {'Status':<20} {'Sprint'}")
    print("-" * 100)
    
    if tasks:
        for task in tasks[:10]:  # Show first 10
            key = task['key']
            summary = task['fields']['summary'][:57] + "..." if len(task['fields']['summary']) > 60 else task['fields']['summary']
            status = task['fields']['status']['name']
            sprint_info = task['fields'].get('customfield_10020', [])
            sprint_name = sprint_info[0]['name'] if sprint_info and isinstance(sprint_info, list) and sprint_info else "No Sprint"
            
            print(f"{key:<12} {summary:<60} {status:<20} {sprint_name}")
        
        if len(tasks) > 10:
            print(f"   ... and {len(tasks) - 10} more tasks")
    else:
        print("   (No tasks found)")
    
    # Summary
    print("\n" + "=" * 100)
    print("📊 SUMMARY:")
    print("=" * 100)
    print(f"Total Issues: {len(issues)}")
    print(f"  - Epics: {len(epics)}")
    print(f"  - User Stories: {len(stories)}")
    print(f"  - Tasks: {len(tasks)}")
    print(f"  - Others: {len(others)}")
    
    print(f"\n🔗 View in Jira:")
    print(f"   Board: https://luis-sosa-bairesdev.atlassian.net/jira/software/projects/SCRUM/boards/1")
    print(f"   Backlog: https://luis-sosa-bairesdev.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog")


if __name__ == "__main__":
    main()



