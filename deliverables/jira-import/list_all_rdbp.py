"""List all RDBP issues to find Epic 3."""

import requests

JIRA_URL = 'https://luis-sosa-bairesdev.atlassian.net'
JIRA_EMAIL = 'luis.sosa@bairesdev.com'
JIRA_TOKEN = 'ATATT3xFfGF05S_SCHS3O_OqM3rJcN9nM9-g3AorAXYCLvHDC2bvMGJhSgU9pCvIPNFPAbAmxJMU3UtO9R3ed-ccV7PInG7h51OTK9JTdS3ERz2Tdbrljl6E2yQDwVKtwsia8PI_UHC6F4wFE_P_D955n6fKNFiZBrCF4K3PNoonm6nxXKLNEJI=0B414822'

headers = {
    'Accept': 'application/json',
    'Authorization': f'Basic {requests.auth._basic_auth_str(JIRA_EMAIL, JIRA_TOKEN)}'
}

# Try getting board issues
print("Method 1: Get board issues")
board_id = '34'  # RDBP board
url = f'{JIRA_URL}/rest/agile/1.0/board/{board_id}/issue?maxResults=100'
response = requests.get(url, headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    issues = response.json().get('issues', [])
    print(f"Found {len(issues)} issues on board\n")
    
    epics = []
    stories = []
    for issue in issues:
        key = issue['key']
        summary = issue['fields']['summary']
        issue_type = issue['fields']['issuetype']['name']
        status = issue['fields']['status']['name']
        parent = issue['fields'].get('parent', {})
        
        if issue_type.lower() == 'epic':
            epics.append((key, summary, status))
        elif issue_type.lower() in ['story', 'user story']:
            stories.append((key, summary, status, parent.get('key', 'None')))
    
    print("Epics:")
    for key, summary, status in epics:
        print(f"  {key}: {summary[:60]}... ({status})")
    
    print(f"\nStories ({len(stories)}):")
    for key, summary, status, parent in stories[:30]:
        print(f"  {key}: {summary[:50]}... | Parent: {parent} | Status: {status}")
else:
    print(f"Error: {response.text[:200]}")

# Try Sprint 2
print("\n\nMethod 2: Get Sprint 2 issues")
sprint_id = '10002'
url = f'{JIRA_URL}/rest/agile/1.0/sprint/{sprint_id}/issue'
response = requests.get(url, headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    issues = response.json().get('issues', [])
    print(f"Found {len(issues)} issues in Sprint 2\n")
    for issue in issues:
        key = issue['key']
        summary = issue['fields']['summary']
        issue_type = issue['fields']['issuetype']['name']
        status = issue['fields']['status']['name']
        parent = issue['fields'].get('parent', {})
        print(f"  {key} ({issue_type}): {summary[:50]}... | Parent: {parent.get('key', 'None')} | Status: {status}")



