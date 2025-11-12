"""List all Epic 3 related issues in RDBP project."""

import requests

JIRA_URL = 'https://luis-sosa-bairesdev.atlassian.net'
JIRA_EMAIL = 'luis.sosa@bairesdev.com'
JIRA_TOKEN = 'ATATT3xFfGF05S_SCHS3O_OqM3rJcN9nM9-g3AorAXYCLvHDC2bvMGJhSgU9pCvIPNFPAbAmxJMU3UtO9R3ed-ccV7PInG7h51OTK9JTdS3ERz2Tdbrljl6E2yQDwVKtwsia8PI_UHC6F4wFE_P_D955n6fKNFiZBrCF4K3PNoonm6nxXKLNEJI=0B414822'

headers = {
    'Accept': 'application/json',
    'Authorization': f'Basic {requests.auth._basic_auth_str(JIRA_EMAIL, JIRA_TOKEN)}'
}

# Search for all RDBP issues
jql = 'project = RDBP ORDER BY key ASC'
url = f'{JIRA_URL}/rest/api/3/search/jql?jql={requests.utils.quote(jql)}&fields=key,summary,status,issuetype,parent'

response = requests.get(url, headers=headers)
if response.status_code == 200:
    issues = response.json().get('issues', [])
    print(f'Found {len(issues)} issues in RDBP project:\n')
    
    epic3_issues = []
    for issue in issues:
        key = issue['key']
        summary = issue['fields']['summary']
        issue_type = issue['fields']['issuetype']['name']
        status = issue['fields']['status']['name']
        parent = issue['fields'].get('parent', {})
        parent_key = parent.get('key', 'None')
        
        # Check if it's Epic 3 or related
        if 'RDBP-3' in key or 'epic 3' in summary.lower() or 'llm' in summary.lower() or 'requirement' in summary.lower():
            epic3_issues.append(issue)
            print(f"  {key} ({issue_type}): {summary[:60]}...")
            print(f"      Status: {status} | Parent: {parent_key}")
    
    print(f'\n\nTotal Epic 3 related issues: {len(epic3_issues)}')
else:
    print(f'Error: {response.status_code}')
    print(response.text)



