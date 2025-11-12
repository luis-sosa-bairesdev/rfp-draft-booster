#!/usr/bin/env python3
"""Close completed Epic 5 tasks in Jira."""

import json
import urllib.request
import urllib.error
from typing import Optional

# Configuration
JIRA_URL = "https://luis-sosa-bairesdev.atlassian.net"
EMAIL = "luis.sosa@bairesdev.com"
API_TOKEN = "ATATT3xFfGF05S_SCHS3O_OqM3rJcN9nM9-g3AorAXYCLvHDC2bvMGJhSgU9pCvIPNFPAbAmxJMU3UtO9R3ed-ccV7PInG7h51OTK9JTdS3ERz2Tdbrljl6E2yQDwVKtwsia8PI_UHC6F4wFE_P_D955n6fKNFiZBrCF4K3PNoonm6nxXKLNEJI=0B414822"
PROJECT_KEY = "RDBP"


def make_request(url: str, method: str = "GET", data: dict = None):
    """Make a request to Jira API."""
    auth_string = f"{EMAIL}:{API_TOKEN}"
    auth_bytes = auth_string.encode('ascii')
    import base64
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
                raise Exception(f"HTTP {response.status}: {response.read().decode('utf-8')}")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        raise Exception(f"HTTP {e.code}: {error_body}")


def get_transitions(issue_key: str):
    """Get available transitions for an issue."""
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/transitions"
    return make_request(url)


def transition_issue(issue_key: str, transition_id: str, comment: str = ""):
    """Transition an issue to a new status."""
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/transitions"
    data = {
        "transition": {"id": transition_id}
    }
    if comment:
        data["update"] = {
            "comment": [{
                "add": {
                    "body": {
                        "type": "doc",
                        "version": 1,
                        "content": [{
                            "type": "paragraph",
                            "content": [{"type": "text", "text": comment}]
                        }]
                    }
                }
            }]
        }
    return make_request(url, method="POST", data=data)


def close_issue(issue_key: str, comment: str = ""):
    """Close an issue by transitioning to Done."""
    transitions = get_transitions(issue_key)
    
    # Find "Done" transition
    done_transition = None
    for transition in transitions.get("transitions", []):
        if transition.get("to", {}).get("name", "").lower() == "done":
            done_transition = transition["id"]
            break
    
    if not done_transition:
        print(f"⚠️  No 'Done' transition found for {issue_key}")
        return False
    
    try:
        transition_issue(issue_key, done_transition, comment)
        print(f"✅ Closed {issue_key}")
        return True
    except Exception as e:
        print(f"❌ Error closing {issue_key}: {e}")
        return False


def main():
    """Close all completed Epic 5 tasks."""
    # Epic 5 tasks that were completed
    completed_tasks = [
        "RDBP-56",  # Backend - Draft generation service
        "RDBP-57",  # Backend - Draft model and storage
        "RDBP-58",  # Backend - Section regeneration capability
        "RDBP-59",  # Backend - AI Assistant service
        "RDBP-60",  # UI - Draft generation page
        "RDBP-61",  # UI - Draft editing and preview
        "RDBP-62",  # UI - AI Assistant modal
        "RDBP-63",  # UI - Progress tracking dashboard
        "RDBP-64",  # UI - Global search
        "RDBP-65",  # Testing - Unit tests for draft generation
        "RDBP-66",  # Testing - Unit tests for AI Assistant
        "RDBP-67",  # Testing - UI tests for draft generation page
        "RDBP-68",  # Testing - UI tests for AI Assistant modal
    ]
    
    print("=" * 60)
    print("Closing Epic 5 Tasks")
    print("=" * 60)
    
    comment = "Task completed. AI Assistant with page context, modal rendering improvements, and comprehensive testing implemented."
    
    success_count = 0
    for task_key in completed_tasks:
        if close_issue(task_key, comment):
            success_count += 1
    
    print(f"\n✅ Closed {success_count}/{len(completed_tasks)} tasks")
    
    # Also close Epic 5 itself
    print("\nClosing Epic 5...")
    if close_issue("RDBP-55", "Epic 5 completed. All features implemented and tested."):
        print("✅ Epic 5 closed")


if __name__ == "__main__":
    main()

