#!/usr/bin/env python3
"""Update Epic 2 and its User Stories to Done status in Jira."""

import json
import urllib.request
import urllib.error
from typing import Optional

# Configuration
JIRA_URL = "https://luis-sosa-bairesdev.atlassian.net"
EMAIL = "luis.sosa@bairesdev.com"
API_TOKEN = "ATATT3xFfGF05S_SCHS3O_OqM3rJcN9nM9-g3AorAXYCLvHDC2bvMGJhSgU9pCvIPNFPAbAmxJMU3UtO9R3ed-ccV7PInG7h51OTK9JTdS3ERz2Tdbrljl6E2yQDwVKtwsia8PI_UHC6F4wFE_P_D955n6fKNFiZBrCF4K3PNoonm6nxXKLNEJI=0B414822"
PROJECT_KEY = "SCRUM"


def make_jira_request(endpoint: str, method: str = "GET", data: Optional[dict] = None) -> dict:
    """Make a request to Jira API."""
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
    
    # Prepare request
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


def search_issues(jql: str) -> list:
    """Search for issues using JQL."""
    endpoint = f"search/jql?jql={urllib.parse.quote(jql)}&fields=key,summary,status,issuetype"
    result = make_jira_request(endpoint)
    return result.get('issues', [])


def get_transitions(issue_key: str) -> list:
    """Get available transitions for an issue."""
    endpoint = f"issue/{issue_key}/transitions"
    result = make_jira_request(endpoint)
    return result.get('transitions', [])


def transition_issue(issue_key: str, transition_id: str) -> None:
    """Transition an issue to a new status."""
    endpoint = f"issue/{issue_key}/transitions"
    data = {
        "transition": {
            "id": transition_id
        }
    }
    make_jira_request(endpoint, method="POST", data=data)


def main():
    """Update Epic 2 and its User Stories to Done."""
    
    print("=" * 60)
    print("UPDATING EPIC 2 TO DONE")
    print("=" * 60)
    
    # Step 1: Find Epic 2
    print("\n1. Searching for Epic 2...")
    epic_jql = f'project = {PROJECT_KEY} AND summary ~ "PDF Processing" AND type = Epic'
    epics = search_issues(epic_jql)
    
    if not epics:
        print("❌ Epic 2 not found!")
        return
    
    # Use the most recent one (highest key number)
    epic = sorted(epics, key=lambda x: int(x['key'].split('-')[1]), reverse=True)[0]
    epic_key = epic['key']
    print(f"✅ Found Epic 2: {epic_key} - {epic['fields']['summary']}")
    print(f"   Current Status: {epic['fields']['status']['name']}")
    
    # Step 2: Find User Stories in Epic 2
    print(f"\n2. Searching for User Stories in {epic_key}...")
    stories_jql = f'project = {PROJECT_KEY} AND parent = {epic_key}'
    stories = search_issues(stories_jql)
    
    print(f"✅ Found {len(stories)} User Stories:")
    for story in stories:
        print(f"   - {story['key']}: {story['fields']['summary']}")
        print(f"     Status: {story['fields']['status']['name']}")
    
    # Step 3: Get "Done" transition for Epic
    print(f"\n3. Getting transitions for Epic {epic_key}...")
    epic_transitions = get_transitions(epic_key)
    done_transition = None
    
    for transition in epic_transitions:
        print(f"   - {transition['name']} (ID: {transition['id']})")
        if transition['name'].lower() in ['done', 'hecho', 'complete', 'completed', 'listo']:
            done_transition = transition['id']
    
    if not done_transition:
        print("❌ 'Done' transition not found for Epic!")
        print("   Available transitions:", [t['name'] for t in epic_transitions])
        return
    
    # Step 4: Transition User Stories to Done
    print("\n4. Transitioning User Stories to Done...")
    for story in stories:
        story_key = story['key']
        current_status = story['fields']['status']['name'].lower()
        
        if current_status in ['done', 'listo']:
            print(f"   ⏭️  {story_key} already Done")
            continue
        
        story_transitions = get_transitions(story_key)
        story_done_transition = None
        
        for transition in story_transitions:
            if transition['name'].lower() in ['done', 'hecho', 'complete', 'completed', 'listo']:
                story_done_transition = transition['id']
                break
        
        if story_done_transition:
            transition_issue(story_key, story_done_transition)
            print(f"   ✅ {story_key} → Done")
        else:
            print(f"   ⚠️  {story_key} - 'Done' transition not available")
    
    # Step 5: Transition Epic to Done
    print(f"\n5. Transitioning Epic {epic_key} to Done...")
    transition_issue(epic_key, done_transition)
    print(f"   ✅ {epic_key} → Done")
    
    print("\n" + "=" * 60)
    print("✅ EPIC 2 COMPLETED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    main()

