"""Check UI stories for Epic 3 in Sprint 2."""

import os
import requests
import json

JIRA_URL = 'https://luis-sosa-bairesdev.atlassian.net'
JIRA_EMAIL = 'luis.sosa@bairesdev.com'
JIRA_TOKEN = 'ATATT3xFfGF05S_SCHS3O_OqM3rJcN9nM9-g3AorAXYCLvHDC2bvMGJhSgU9pCvIPNFPAbAmxJMU3UtO9R3ed-ccV7PInG7h51OTK9JTdS3ERz2Tdbrljl6E2yQDwVKtwsia8PI_UHC6F4wFE_P_D955n6fKNFiZBrCF4K3PNoonm6nxXKLNEJI=0B414822'

headers = {
    'Accept': 'application/json',
    'Authorization': f'Basic {requests.auth._basic_auth_str(JIRA_EMAIL, JIRA_TOKEN)}'
}

# Get Sprint 2 issues
sprint_id = '10002'
url = f'{JIRA_URL}/rest/agile/1.0/sprint/{sprint_id}/issue'
response = requests.get(url, headers=headers)

if response.status_code != 200:
    print(f"Error: {response.status_code}")
    print(response.text)
    exit(1)

issues = response.json().get('issues', [])

print('=' * 80)
print('Sprint 2 Issues (Epic 3) - UI Stories')
print('=' * 80)

ui_keywords = ['display', 'table', 'edit', 'add', 'delete', 'filter', 'ui', 'interface', 'page', 'view']
ui_stories = []

for issue in issues:
    key = issue['key']
    summary = issue['fields']['summary'].lower()
    issue_type = issue['fields']['issuetype']['name']
    status = issue['fields']['status']['name']
    parent = issue['fields'].get('parent', {}).get('key', 'N/A')
    
    # Check if it's a UI-related story
    is_ui = any(keyword in summary for keyword in ui_keywords) or issue_type.lower() in ['story', 'user story']
    
    if is_ui:
        ui_stories.append({
            'key': key,
            'summary': issue['fields']['summary'],
            'type': issue_type,
            'status': status,
            'parent': parent
        })
        print(f"\n{key}: {issue['fields']['summary']}")
        print(f"  Type: {issue_type} | Status: {status} | Parent: {parent}")

print(f'\n\nTotal UI-related stories found: {len(ui_stories)}')
print('=' * 80)

# Expected UI stories based on Epic 3
expected_ui_stories = [
    'Display extracted requirements in a table',
    'Filter requirements by category and priority',
    'Edit requirement details',
    'Add manual requirements',
    'Delete requirements'
]

print('\nExpected UI Stories:')
for i, expected in enumerate(expected_ui_stories, 1):
    found = any(expected.lower() in story['summary'].lower() for story in ui_stories)
    status_icon = '✅' if found else '❌'
    print(f"{status_icon} {i}. {expected}")



