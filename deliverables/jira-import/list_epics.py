#!/usr/bin/env python3
"""List all epics in the project."""

import json
import urllib.request
import urllib.error
import urllib.parse

# Configuration
JIRA_URL = "https://luis-sosa-bairesdev.atlassian.net"
EMAIL = "luis.sosa@bairesdev.com"
API_TOKEN = "ATATT3xFfGF05S_SCHS3O_OqM3rJcN9nM9-g3AorAXYCLvHDC2bvMGJhSgU9pCvIPNFPAbAmxJMU3UtO9R3ed-ccV7PInG7h51OTK9JTdS3ERz2Tdbrljl6E2yQDwVKtwsia8PI_UHC6F4wFE_P_D955n6fKNFiZBrCF4K3PNoonm6nxXKLNEJI=0B414822"
PROJECT_KEY = "SCRUM"


def make_jira_request(endpoint: str) -> dict:
    """Make a GET request to Jira API."""
    url = f"{JIRA_URL}/rest/api/3/{endpoint}"
    
    # Prepare authentication
    auth_string = f"{EMAIL}:{API_TOKEN}"
    auth_bytes = auth_string.encode('ascii')
    import base64
    auth_header = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    req = urllib.request.Request(url, headers=headers, method="GET")
    
    try:
        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode('utf-8')
            return json.loads(response_data) if response_data else {}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        raise Exception(f"HTTP {e.code}: {error_body}")


def main():
    """List all epics in the project."""
    
    print("=" * 80)
    print("LISTING ALL EPICS IN PROJECT")
    print("=" * 80)
    
    # Search for all epics
    jql = f'project = {PROJECT_KEY} AND type = Epic'
    endpoint = f"search/jql?jql={urllib.parse.quote(jql)}&fields=key,summary,status&maxResults=50"
    
    result = make_jira_request(endpoint)
    issues = result.get('issues', [])
    
    print(f"\n✅ Found {len(issues)} Epics:\n")
    
    for issue in issues:
        key = issue['key']
        summary = issue['fields']['summary']
        status = issue['fields']['status']['name']
        print(f"  {key}: {summary}")
        print(f"         Status: {status}\n")
    
    print("=" * 80)


if __name__ == "__main__":
    main()

