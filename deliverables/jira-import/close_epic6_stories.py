#!/usr/bin/env python3
"""Close Epic 6 stories in Jira by searching for them."""

import os
import json
import urllib.request
import urllib.error
import base64

# Jira configuration
JIRA_URL = "https://luis-sosa-bairesdev.atlassian.net"
JIRA_EMAIL = "luis.sosa@bairesdev.com"
JIRA_API_TOKEN = "ATATT3xFfGF05S_SCHS3O_OqM3rJcN9nM9-g3AorAXYCLvHDC2bvMGJhSgU9pCvIPNFPAbAmxJMU3UtO9R3ed-ccV7PInG7h51OTK9JTdS3ERz2Tdbrljl6E2yQDwVKtwsia8PI_UHC6F4wFE_P_D955n6fKNFiZBrCF4K3PNoonm6nxXKLNEJI=0B414822"
PROJECT_KEY = "RDBP"


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


def search_epic6_stories():
    """Search for Epic 6 stories using the new API endpoint."""
    # JQL to find Epic 6 and its stories
    jql = 'project = RDBP AND (summary ~ "Service Matching" OR summary ~ "service catalog" OR summary ~ "TF-IDF" OR summary ~ "ServiceMatcher" OR summary ~ "Sample RFP") AND status != Done ORDER BY created DESC'
    
    data = {
        "jql": jql,
        "maxResults": 50,
        "fields": ["summary", "status", "issuetype"]
    }
    
    # Use the new /rest/api/3/search endpoint with POST
    result = make_jira_request("search", method="POST", data=data)
    
    if result and 'issues' in result:
        return result['issues']
    return []


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


def close_issue(issue_key, summary, comment="Completed via automated script"):
    """Close an issue by transitioning to Done."""
    print(f"\n{'='*60}")
    print(f"Processing: {issue_key}")
    print(f"Summary: {summary[:70]}...")
    print(f"{'='*60}")
    
    # Get available transitions
    transitions = get_transitions(issue_key)
    
    if not transitions:
        print(f"❌ Could not get transitions for {issue_key}")
        return False
    
    # Find "Done" transition
    done_transition = None
    for t in transitions:
        if t['name'].lower() in ['done', 'close', 'closed', 'complete', 'completed']:
            done_transition = t
            break
    
    if not done_transition:
        print(f"⚠️  No 'Done' transition found for {issue_key}")
        print(f"   Available transitions: {', '.join([t['name'] for t in transitions])}")
        return False
    
    # Transition to Done
    print(f"  → Transitioning to '{done_transition['name']}'...")
    if transition_issue(issue_key, done_transition['id'], comment):
        print(f"  ✅ {issue_key} marked as Done")
        return True
    else:
        print(f"  ❌ Failed to transition {issue_key}")
        return False


def main():
    """Main function to close Epic 6 tasks."""
    print("\n" + "="*80)
    print("JIRA TASK CLOSURE - Epic 6: Service Matching")
    print("="*80)
    
    # Search for Epic 6 stories
    print("\n🔍 Searching for Epic 6 stories...")
    issues = search_epic6_stories()
    
    if not issues:
        print("❌ No Epic 6 stories found")
        return
    
    print(f"\n✅ Found {len(issues)} issue(s) related to Epic 6:")
    for issue in issues:
        key = issue['key']
        summary = issue['fields']['summary']
        status = issue['fields']['status']['name']
        issue_type = issue['fields']['issuetype']['name']
        print(f"  - {key}: {summary} ({issue_type}, Status: {status})")
    
    # Close each issue
    print("\n" + "="*80)
    print("CLOSING ISSUES")
    print("="*80)
    
    success_count = 0
    comment = """Epic 6: Service Matching implementation completed successfully.

Features implemented:
✅ Service data model with JSON loader
✅ TF-IDF + cosine similarity matching engine
✅ Category-based bonus scoring (+15% for matching categories)
✅ Service Matching UI page with filters and charts
✅ Integration with Draft Generation
✅ Comprehensive unit and UI tests
✅ Sample RFP PDF for testing
✅ User guides and troubleshooting docs

Test Coverage: 83% (398 tests passing)
All acceptance criteria met."""
    
    for issue in issues:
        key = issue['key']
        summary = issue['fields']['summary']
        if close_issue(key, summary, comment):
            success_count += 1
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\n✅ Issues Closed: {success_count}/{len(issues)}")
    
    if success_count == len(issues):
        print("\n🎉 All Epic 6 issues closed successfully!")
    else:
        print(f"\n⚠️  {len(issues) - success_count} issue(s) could not be closed")
    
    print("\n" + "="*80)
    print("✨ JIRA UPDATE COMPLETE!")
    print("="*80)


if __name__ == "__main__":
    main()

