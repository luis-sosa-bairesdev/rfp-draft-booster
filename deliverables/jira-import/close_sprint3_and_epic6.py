#!/usr/bin/env python3
"""Close Sprint 3 and Epic 6 tasks in Jira."""

import os
import json
import urllib.request
import urllib.error
import base64

# Jira configuration
JIRA_URL = "https://bairesdevops.atlassian.net"
JIRA_EMAIL = "luis.sosa@bairesdev.com"
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")
PROJECT_KEY = "RDBP"

# Sprint 3 tasks (remaining from Epic 5 and bug fixes)
SPRINT_3_TASKS = [
    "RDBP-79",  # Fix AI Assistant modal rendering
    "RDBP-80",  # Fix session state consistency
    "RDBP-81",  # Add E2E tests for critical flows
    "RDBP-82",  # Fix failing regression tests
    "RDBP-83",  # Improve test coverage to 83%
]

# Epic 6 / Sprint 5 tasks
EPIC_6_TASKS = [
    "RDBP-84",  # Create Service data model
    "RDBP-85",  # Implement ServiceMatcher backend
    "RDBP-86",  # Create Service Matching UI page
    "RDBP-87",  # Integrate with Draft Generation
    "RDBP-88",  # Add service matching tests
    "RDBP-89",  # Create sample RFP for matching
    "RDBP-90",  # Document service matching feature
]

EPIC_6_KEY = "RDBP-72"  # Epic 6: Service Matching


def make_jira_request(endpoint, method="GET", data=None):
    """Make authenticated request to Jira API."""
    url = f"{JIRA_URL}/rest/api/3/{endpoint}"
    
    # Create auth header
    auth_string = f"{JIRA_EMAIL}:{JIRA_API_TOKEN}"
    auth_bytes = auth_string.encode('ascii')
    base64_auth = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        "Authorization": f"Basic {base64_auth}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Create request
    if data:
        data = json.dumps(data).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status in [200, 201, 204]:
                try:
                    return json.loads(response.read().decode('utf-8'))
                except:
                    return {"success": True}
            else:
                print(f"Warning: Unexpected status {response.status}")
                return None
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"HTTP Error {e.code}: {error_body}")
        return None


def get_transitions(issue_key):
    """Get available transitions for an issue."""
    result = make_jira_request(f"issue/{issue_key}/transitions")
    if result and 'transitions' in result:
        return result['transitions']
    return []


def transition_issue(issue_key, transition_id, comment=None):
    """Transition issue to new status."""
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
                            "content": [{
                                "type": "text",
                                "text": comment
                            }]
                        }]
                    }
                }
            }]
        }
    
    result = make_jira_request(f"issue/{issue_key}/transitions", method="POST", data=data)
    return result is not None


def close_issue(issue_key, comment="Completed via automated script"):
    """Close an issue by transitioning to Done."""
    print(f"\n{'='*60}")
    print(f"Processing: {issue_key}")
    print(f"{'='*60}")
    
    # Get available transitions
    transitions = get_transitions(issue_key)
    
    if not transitions:
        print(f"❌ Could not get transitions for {issue_key}")
        return False
    
    # Find "Done" transition
    done_transition = None
    for t in transitions:
        print(f"  Available: {t['name']} (id: {t['id']})")
        if t['name'].lower() in ['done', 'close', 'closed', 'complete', 'completed']:
            done_transition = t
            break
    
    if not done_transition:
        print(f"⚠️  No 'Done' transition found for {issue_key}")
        return False
    
    # Transition to Done
    print(f"\n  → Transitioning to '{done_transition['name']}'...")
    if transition_issue(issue_key, done_transition['id'], comment):
        print(f"  ✅ {issue_key} marked as Done")
        return True
    else:
        print(f"  ❌ Failed to transition {issue_key}")
        return False


def main():
    """Main function to close tasks."""
    print("\n" + "="*80)
    print("JIRA TASK CLOSURE - Sprint 3 & Epic 6")
    print("="*80)
    
    if not JIRA_API_TOKEN:
        print("\n❌ Error: JIRA_API_TOKEN not set")
        print("   Set it with: export JIRA_API_TOKEN='your-token-here'")
        return
    
    # Close Sprint 3 tasks
    print("\n" + "="*80)
    print("CLOSING SPRINT 3 TASKS (Bug Fixes & Testing)")
    print("="*80)
    
    sprint3_success = 0
    for task_key in SPRINT_3_TASKS:
        if close_issue(task_key, "Sprint 3 bug fixes and testing completed. Coverage improved to 83%, all tests passing."):
            sprint3_success += 1
    
    # Close Epic 6 tasks
    print("\n" + "="*80)
    print("CLOSING EPIC 6 / SPRINT 5 TASKS (Service Matching)")
    print("="*80)
    
    epic6_success = 0
    for task_key in EPIC_6_TASKS:
        if close_issue(task_key, "Epic 6 Service Matching completed. Feature implemented with TF-IDF algorithm, category bonus, and comprehensive documentation."):
            epic6_success += 1
    
    # Close Epic 6 itself
    print("\n" + "="*80)
    print("CLOSING EPIC 6")
    print("="*80)
    
    epic_closed = close_issue(
        EPIC_6_KEY,
        "Epic 6: Service Matching completed successfully. All features implemented, tested (83% coverage), and documented."
    )
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\n✅ Sprint 3 Tasks Closed: {sprint3_success}/{len(SPRINT_3_TASKS)}")
    print(f"✅ Epic 6 Tasks Closed: {epic6_success}/{len(EPIC_6_TASKS)}")
    print(f"✅ Epic 6 Closed: {'Yes' if epic_closed else 'No'}")
    print(f"\nTotal: {sprint3_success + epic6_success + (1 if epic_closed else 0)}/{len(SPRINT_3_TASKS) + len(EPIC_6_TASKS) + 1} issues closed")
    
    print("\n" + "="*80)
    print("✨ JIRA UPDATE COMPLETE!")
    print("="*80)


if __name__ == "__main__":
    main()

