"""Find Epic 3 stories in Jira."""

import requests

JIRA_URL = 'https://luis-sosa-bairesdev.atlassian.net'
JIRA_EMAIL = 'luis.sosa@bairesdev.com'
JIRA_TOKEN = 'ATATT3xFfGF05S_SCHS3O_OqM3rJcN9nM9-g3AorAXYCLvHDC2bvMGJhSgU9pCvIPNFPAbAmxJMU3UtO9R3ed-ccV7PInG7h51OTK9JTdS3ERz2Tdbrljl6E2yQDwVKtwsia8PI_UHC6F4wFE_P_D955n6fKNFiZBrCF4K3PNoonm6nxXKLNEJI=0B414822'

headers = {
    'Accept': 'application/json',
    'Authorization': f'Basic {requests.auth._basic_auth_str(JIRA_EMAIL, JIRA_TOKEN)}'
}

# Search for Epic 3
jql = 'project = RDBP AND "Epic Link" = RDBP-3'
url = f'{JIRA_URL}/rest/api/3/search/jql?jql={requests.utils.quote(jql)}&fields=key,summary,status,issuetype,parent'

response = requests.get(url, headers=headers)
if response.status_code == 200:
    issues = response.json().get('issues', [])
    print(f'Found {len(issues)} issues linked to Epic 3:')
    for issue in issues:
        print(f"  {issue['key']}: {issue['fields']['summary']} ({issue['fields']['status']['name']})")
else:
    print(f'Error: {response.status_code}')
    print(response.text)

# Also search in Sprint 2
sprint_id = '10002'
url = f'{JIRA_URL}/rest/agile/1.0/sprint/{sprint_id}/issue'
response = requests.get(url, headers=headers)
if response.status_code == 200:
    issues = response.json().get('issues', [])
    print(f'\nFound {len(issues)} issues in Sprint 2:')
    for issue in issues:
        key = issue['key']
        summary = issue['fields']['summary']
        issue_type = issue['fields']['issuetype']['name']
        status = issue['fields']['status']['name']
        parent = issue['fields'].get('parent', {})
        print(f"  {key} ({issue_type}): {summary[:60]}... | Status: {status} | Parent: {parent.get('key', 'None')}")

