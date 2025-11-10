#!/usr/bin/env python3
"""Fix Epic 1 (SCRUM-21) status - move to Done."""

import json
import urllib.request
import urllib.error
import base64

# Configuration
JIRA_URL = "https://luis-sosa-bairesdev.atlassian.net"
EMAIL = "luis.sosa@bairesdev.com"
API_TOKEN = "ATATT3xFfGF05S_SCHS3O_OqM3rJcN9nM9-g3AorAXYCLvHDC2bvMGJhSgU9pCvIPNFPAbAmxJMU3UtO9R3ed-ccV7PInG7h51OTK9JTdS3ERz2Tdbrljl6E2yQDwVKtwsia8PI_UHC6F4wFE_P_D955n6fKNFiZBrCF4K3PNoonm6nxXKLNEJI=0B414822"
EPIC_KEY = "SCRUM-21"


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
        print(f"HTTP {e.code}: {error_body}")
        return None


def get_transitions(issue_key: str):
    """Get available transitions for an issue."""
    endpoint = f"issue/{issue_key}/transitions"
    return make_jira_request(endpoint)


def transition_issue(issue_key: str, transition_id: str):
    """Transition an issue to a new status."""
    endpoint = f"issue/{issue_key}/transitions"
    data = {
        "transition": {
            "id": transition_id
        }
    }
    return make_jira_request(endpoint, method="POST", data=data)


def get_issue_details(issue_key: str):
    """Get issue details."""
    endpoint = f"issue/{issue_key}?fields=summary,status"
    return make_jira_request(endpoint)


def main():
    """Fix Epic 1 status."""
    
    print("=" * 80)
    print(f"FIXING {EPIC_KEY} (Epic 1) STATUS")
    print("=" * 80)
    
    # Get current status
    print(f"\n1. Getting current status of {EPIC_KEY}...")
    issue = get_issue_details(EPIC_KEY)
    
    if not issue:
        print(f"   ❌ Could not retrieve {EPIC_KEY}")
        return
    
    current_status = issue['fields']['status']['name']
    summary = issue['fields']['summary']
    
    print(f"   ✅ {EPIC_KEY}: {summary}")
    print(f"   Current Status: {current_status}")
    
    if current_status.lower() in ['listo', 'done', 'finalizada']:
        print(f"\n   ℹ️  Epic is already in Done status!")
        return
    
    # Get available transitions
    print(f"\n2. Getting available transitions...")
    transitions_data = get_transitions(EPIC_KEY)
    
    if not transitions_data:
        print(f"   ❌ Could not retrieve transitions")
        return
    
    transitions = transitions_data.get('transitions', [])
    
    print(f"   Available transitions:")
    for t in transitions:
        print(f"      - {t['name']} (ID: {t['id']})")
    
    # Find "Listo" or "Done" transition
    done_transition_id = None
    for t in transitions:
        if t['name'].lower() in ['listo', 'done', 'finalizada']:
            done_transition_id = t['id']
            print(f"\n   ✅ Found transition: {t['name']} (ID: {done_transition_id})")
            break
    
    if not done_transition_id:
        print(f"\n   ❌ Could not find 'Listo' or 'Done' transition")
        print(f"   Available: {[t['name'] for t in transitions]}")
        return
    
    # Transition to Done
    print(f"\n3. Transitioning {EPIC_KEY} to Done...")
    result = transition_issue(EPIC_KEY, done_transition_id)
    
    if result is not None:
        print(f"   ✅ {EPIC_KEY} successfully moved to Done!")
    else:
        print(f"   ❌ Failed to transition {EPIC_KEY}")
        return
    
    # Verify
    print(f"\n4. Verifying status...")
    issue = get_issue_details(EPIC_KEY)
    new_status = issue['fields']['status']['name']
    print(f"   ✅ New Status: {new_status}")
    
    print("\n" + "=" * 80)
    print("✅ EPIC 1 STATUS FIXED")
    print("=" * 80)


if __name__ == "__main__":
    main()

