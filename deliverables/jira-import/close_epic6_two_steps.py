#!/usr/bin/env python3
"""Close Epic 6 in two steps: To Do -> In Progress -> Done."""

import json
import urllib.request
import urllib.error
import base64
import time

# Configuration
JIRA_URL = "https://luis-sosa-bairesdev.atlassian.net"
EMAIL = "luis.sosa@bairesdev.com"
API_TOKEN = "ATATT3xFfGF0sSVc0RTQhwj6YNxUmVNcEVQAM4OWpmI-E553Bsc46avo_OI-Hlvf_IrYjf0_FBtsCgKBbIJ1KNM2gdrHvfsijPku4fIR9BrLCnm9WcpSKVr_EDeBG1te_aNUatYT5b9w6JSdNt7sgtl6ZdH32IgnTYWLCOh3VEGhnDF6mvWj1g0=0882E324"
EPIC_6_KEY = "RDBP-78"


def make_request(url: str, method: str = "GET", data: dict = None):
    """Make a request to Jira API."""
    auth_string = f"{EMAIL}:{API_TOKEN}"
    auth_bytes = auth_string.encode('ascii')
    auth_header = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    req_data = json.dumps(data).encode('utf-8') if data else None
    request = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(request) as response:
            if response.status in [200, 201, 204]:
                response_data = response.read().decode('utf-8')
                return json.loads(response_data) if response_data else {}
            else:
                raise Exception(f"HTTP {response.status}")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"   ❌ HTTP {e.code}: {error_body}")
        return None


def get_transitions(issue_key: str):
    """Get available transitions for an issue."""
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/transitions"
    result = make_request(url)
    return result.get('transitions', []) if result else []


def transition_issue(issue_key: str, transition_id: str):
    """Transition an issue to a new status."""
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/transitions"
    data = {"transition": {"id": transition_id}}
    return make_request(url, method="POST", data=data)


def get_issue_status(issue_key: str):
    """Get current status of an issue."""
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}?fields=status,summary"
    result = make_request(url)
    if result:
        fields = result.get('fields', {})
        return {
            'status': fields.get('status', {}).get('name', 'Unknown'),
            'summary': fields.get('summary', 'N/A')
        }
    return None


def main():
    """Close Epic 6 in two steps."""
    
    print("="*80)
    print("✅ CLOSING EPIC 6: SERVICE MATCHING (Two-Step Process)")
    print("="*80)
    
    # Get current status
    epic_info = get_issue_status(EPIC_6_KEY)
    if not epic_info:
        print("❌ Could not get Epic info")
        return
    
    print(f"\n📦 Epic: {epic_info['summary']}")
    print(f"   Current Status: {epic_info['status']}")
    
    # Get available transitions
    transitions = get_transitions(EPIC_6_KEY)
    print(f"\n   Available transitions:")
    for t in transitions:
        print(f"      - {t['name']} (id: {t['id']})")
    
    # Find transition IDs
    in_progress_id = None
    done_id = None
    for t in transitions:
        if 'progress' in t['name'].lower():
            in_progress_id = t['id']
        if t['name'].lower() in ['done', 'hecho', 'complete']:
            done_id = t['id']
    
    # Step 1: Move to In Progress
    if epic_info['status'].lower() == 'to do':
        if in_progress_id:
            print(f"\n🔄 Step 1: Moving to 'In Progress'...")
            result = transition_issue(EPIC_6_KEY, in_progress_id)
            if result is not None:
                print(f"   ✅ Moved to 'In Progress'")
                time.sleep(1)
            else:
                print(f"   ❌ Failed to move to 'In Progress'")
                return
        else:
            print(f"   ⚠️  No 'In Progress' transition found")
    
    # Step 2: Move to Done
    # Get fresh transitions (they may have changed)
    transitions = get_transitions(EPIC_6_KEY)
    done_id = None
    for t in transitions:
        if t['name'].lower() in ['done', 'hecho', 'complete']:
            done_id = t['id']
    
    if done_id:
        print(f"\n✅ Step 2: Moving to 'Done'...")
        result = transition_issue(EPIC_6_KEY, done_id)
        if result is not None:
            print(f"   ✅ Epic {EPIC_6_KEY} marked as Done!")
        else:
            print(f"   ❌ Failed to move to 'Done'")
    else:
        print(f"   ⚠️  No 'Done' transition found")
    
    # Verify final status
    print(f"\n📊 Verifying final status...")
    final_status = get_issue_status(EPIC_6_KEY)
    if final_status:
        print(f"   Final Status: {final_status['status']}")
        if final_status['status'].lower() in ['done', 'hecho']:
            print(f"\n✨ SUCCESS! Epic 6 closed! ✨")
        else:
            print(f"\n⚠️  Epic not yet in 'Done' status")
    
    print("="*80)


if __name__ == "__main__":
    main()

