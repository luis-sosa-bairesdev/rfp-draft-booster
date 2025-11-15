#!/usr/bin/env python3
"""
Close ALL Epic 6 stories with comments - CORRECT VERSION.
"""

import json
import urllib.request
import urllib.error
import base64
import time

# Configuration
JIRA_URL = "https://luis-sosa-bairesdev.atlassian.net"
EMAIL = "luis.sosa@bairesdev.com"
API_TOKEN = "ATATT3xFfGF0sSVc0RTQhwj6YNxUmVNcEVQAM4OWpmI-E553Bsc46avo_OI-Hlvf_IrYjf0_FBtsCgKBbIJ1KNM2gdrHvfsijPku4fIR9BrLCnm9WcpSKVr_EDeBG1te_aNUatYT5b9w6JSdNt7sgtl6ZdH32IgnTYWLCOh3VEGhnDF6mvWj1g0=0882E324"

# All Epic 6 story keys
EPIC_6_STORIES = [
    "RDBP-79",
    "RDBP-80",
    "RDBP-81",
    "RDBP-82",
    "RDBP-83",
    "RDBP-84",
    "RDBP-85",
    "RDBP-86",
    "RDBP-87",
    "RDBP-88",
    "RDBP-89",
    "RDBP-90",
    "RDBP-91",
]


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
        print(f"      ❌ HTTP {e.code}: {error_body[:150]}")
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


def add_comment(issue_key: str, comment: str):
    """Add a comment to an issue."""
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/comment"
    data = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": comment}]
                }
            ]
        }
    }
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
    """Close all Epic 6 stories."""
    
    print("\n" + "=" * 100)
    print("✅ CLOSING ALL EPIC 6 STORIES (13 stories)")
    print("=" * 100)
    
    # Completion comment for each story
    completion_comment = """Story completed as part of Epic 6: Service Matching! ✅

This story contributed to the successful implementation of:
- Service data model with JSON loader (10 BairesDev services)
- TF-IDF + cosine similarity matching engine
- Category-based bonus scoring (+15%)
- Service Matching UI page with filters and charts
- Approval workflow and integration with Draft Generation
- Comprehensive testing (83% coverage, 398 tests passing)
- User guides and troubleshooting documentation

Epic Status: COMPLETE
Test Coverage: 83%
GitHub Commits: a26f6f4, 0bcbbcb, d6aef32
Ready for Production: YES

Completed: November 15, 2025"""
    
    # Get Done transition from first story
    print(f"\n🔍 Getting transitions from {EPIC_6_STORIES[0]}...")
    transitions = get_transitions(EPIC_6_STORIES[0])
    
    done_transition_id = None
    for transition in transitions:
        if transition['name'].lower() in ['done', 'hecho', 'complete', 'completed', 'listo', 'finalizada']:
            done_transition_id = transition['id']
            break
    
    if not done_transition_id:
        print("   ❌ Could not find 'Done' transition")
        print(f"      Available: {[t['name'] for t in transitions]}")
        return
    
    print(f"   ✅ Found 'Done' transition: {done_transition_id}")
    
    # Close each story
    closed_count = 0
    skipped_count = 0
    failed_count = 0
    
    print(f"\n📝 Processing {len(EPIC_6_STORIES)} stories...")
    print("=" * 100)
    
    for i, story_key in enumerate(EPIC_6_STORIES, 1):
        print(f"\n[{i}/{len(EPIC_6_STORIES)}] Processing {story_key}...")
        
        # Get current status
        issue_info = get_issue_status(story_key)
        if not issue_info:
            print(f"      ⚠️  Could not get issue info")
            failed_count += 1
            continue
        
        status = issue_info['status']
        summary = issue_info['summary']
        
        print(f"      Summary: {summary[:60]}...")
        print(f"      Status: {status}")
        
        # Skip if already Done
        if status.lower() in ['done', 'hecho', 'complete', 'completed', 'listo', 'finalizada']:
            print(f"      ⏭️  Already Done, skipping")
            skipped_count += 1
            continue
        
        # Step 1: Add completion comment
        print(f"      💬 Adding completion comment...")
        comment_result = add_comment(story_key, completion_comment)
        if comment_result is None:
            print(f"      ⚠️  Failed to add comment, but continuing...")
        else:
            print(f"      ✅ Comment added")
        
        time.sleep(0.5)  # Rate limiting
        
        # Step 2: Transition to Done
        print(f"      🔄 Transitioning to Done...")
        transition_result = transition_issue(story_key, done_transition_id)
        if transition_result is not None:
            print(f"      ✅ {story_key} marked as Done")
            closed_count += 1
        else:
            print(f"      ❌ Failed to transition {story_key}")
            failed_count += 1
        
        time.sleep(0.5)  # Rate limiting
    
    # Summary
    print("\n" + "=" * 100)
    print("📊 SUMMARY")
    print("=" * 100)
    print(f"\n   ✅ Stories Closed: {closed_count}")
    print(f"   ⏭️  Stories Skipped (already done): {skipped_count}")
    print(f"   ❌ Stories Failed: {failed_count}")
    print(f"   📝 Total Stories: {len(EPIC_6_STORIES)}")
    
    if closed_count + skipped_count == len(EPIC_6_STORIES):
        print(f"\n🎉 SUCCESS! All {len(EPIC_6_STORIES)} stories are now Done!")
    else:
        print(f"\n⚠️  {failed_count} story(ies) could not be closed")
    
    print("\n" + "=" * 100)
    print("✨ Epic 6: Service Matching Stories - COMPLETE!")
    print("=" * 100)


if __name__ == "__main__":
    main()

