"""Find all RDBP issues to identify Epic 3 stories."""

import requests
import json

JIRA_URL = 'https://luis-sosa-bairesdev.atlassian.net'
JIRA_EMAIL = 'luis.sosa@bairesdev.com'
JIRA_TOKEN = 'ATATT3xFfGF05S_SCHS3O_OqM3rJcN9nM9-g3AorAXYCLvHDC2bvMGJhSgU9pCvIPNFPAbAmxJMU3UtO9R3ed-ccV7PInG7h51OTK9JTdS3ERz2Tdbrljl6E2yQDwVKtwsia8PI_UHC6F4wFE_P_D955n6fKNFiZBrCF4K3PNoonm6nxXKLNEJI=0B414822'

headers = {
    'Accept': 'application/json',
    'Authorization': f'Basic {requests.auth._basic_auth_str(JIRA_EMAIL, JIRA_TOKEN)}'
}

# Try different search methods
print("Method 1: Search by project")
jql = 'project = RDBP'
url = f'{JIRA_URL}/rest/api/3/search?jql={requests.utils.quote(jql)}&maxResults=100&fields=key,summary,status,issuetype,parent'
response = requests.get(url, headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    issues = data.get('issues', [])
    print(f"Found {len(issues)} issues\n")
    for issue in issues[:20]:  # Show first 20
        key = issue['key']
        summary = issue['fields']['summary']
        issue_type = issue['fields']['issuetype']['name']
        status = issue['fields']['status']['name']
        print(f"  {key} ({issue_type}): {summary[:60]}... | {status}")
else:
    print(f"Error: {response.text[:200]}")

print("\n\nMethod 2: Get project issues directly")
url = f'{JIRA_URL}/rest/api/3/project/RDBP'
response = requests.get(url, headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print(json.dumps(response.json(), indent=2)[:500])

print("\n\nMethod 3: Search for Epic 3")
jql = 'project = RDBP AND type = Epic AND summary ~ "Epic 3"'
url = f'{JIRA_URL}/rest/api/3/search?jql={requests.utils.quote(jql)}&fields=key,summary'
response = requests.get(url, headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    issues = response.json().get('issues', [])
    print(f"Found {len(issues)} epics")
    for issue in issues:
        print(f"  {issue['key']}: {issue['fields']['summary']}")



