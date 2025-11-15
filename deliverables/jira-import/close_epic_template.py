#!/usr/bin/env python3
"""
Generic template to close an Epic and all its User Stories in Jira.

USAGE:
1. Update EPIC_KEY and STORY_KEYS below
2. Update COMPLETION_COMMENT if needed
3. Run: python3 close_epic_template.py
"""

import json
import urllib.request
import urllib.error
import base64
import time

# ============================================================================
# CONFIGURATION - UPDATE THIS FOR YOUR EPIC
# ============================================================================

JIRA_URL = "https://luis-sosa-bairesdev.atlassian.net"
EMAIL = "luis.sosa@bairesdev.com"
API_TOKEN = "ATATT3xFfGF0sSVc0RTQhwj6YNxUmVNcEVQAM4OWpmI-E553Bsc46avo_OI-Hlvf_IrYjf0_FBtsCgKBbIJ1KNM2gdrHvfsijPku4fIR9BrLCnm9WcpSKVr_EDeBG1te_aNUatYT5b9w6JSdNt7sgtl6ZdH32IgnTYWLCOh3VEGhnDF6mvWj1g0=0882E324"

# Epic to close
EPIC_KEY = "RDBP-XX"  # UPDATE THIS

# All story keys to close (get from Epic page)
STORY_KEYS = [
    "RDBP-XX",
    "RDBP-XX",
    # Add all story keys here...
]

# Completion comment (customize as needed)
COMPLETION_COMMENT = """Story completed successfully! ✅

This story was part of [EPIC_NAME].

Features implemented:
- Feature 1
- Feature 2
- Feature 3

Test Coverage: XX%
GitHub Commit: XXXXXXX
Status: COMPLETE

Completed: {date}"""

EPIC_COMPLETION_COMMENT = """Epic completed successfully! ✅

All features implemented and tested.

Summary:
- X stories completed
- XX% test coverage
- All acceptance criteria met
- Documentation complete

Status: Ready for Production
Completed: {date}"""

# ============================================================================
# SCRIPT LOGIC - DON'T MODIFY BELOW UNLESS NEEDED
# ============================================================================

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Basic {base64.b64encode(f'{EMAIL}:{API_TOKEN}'.encode()).decode()}"
}


def make_request(url: str, method: str = "GET", data: dict = None):
    """Make request to Jira API."""
    req_data = json.dumps(data).encode('utf-8') if data else None
    request = urllib.request.Request(url, data=req_data, headers=HEADERS, method=method)
    
    try:
        with urllib.request.urlopen(request) as response:
            if response.status in [200, 201, 204]:
                response_data = response.read().decode('utf-8')
                return json.loads(response_data) if response_data else {}
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
            "content": [{
                "type": "paragraph",
                "content": [{"type": "text", "text": comment}]
            }]
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


def close_issue(issue_key: str, comment: str, done_transition_id: str):
    """Close a single issue with comment."""
    issue_info = get_issue_status(issue_key)
    if not issue_info:
        print(f"      ⚠️  Could not get issue info")
        return False
    
    status = issue_info['status']
    summary = issue_info['summary']
    
    print(f"      Summary: {summary[:60]}...")
    print(f"      Status: {status}")
    
    # Skip if already Done
    if status.lower() in ['done', 'hecho', 'complete', 'completed']:
        print(f"      ⏭️  Already Done")
        return True
    
    # Add comment
    print(f"      💬 Adding comment...")
    add_comment(issue_key, comment)
    time.sleep(0.3)
    
    # Transition to Done
    print(f"      🔄 Transitioning to Done...")
    result = transition_issue(issue_key, done_transition_id)
    if result is not None:
        print(f"      ✅ Closed")
        return True
    else:
        print(f"      ❌ Failed")
        return False


def main():
    """Close all stories and epic."""
    from datetime import datetime
    today = datetime.now().strftime("%B %d, %Y")
    
    print("\n" + "="*100)
    print(f"🔒 CLOSING EPIC: {EPIC_KEY}")
    print("="*100)
    
    # Get Done transition
    print(f"\n🔍 Getting transitions...")
    transitions = get_transitions(STORY_KEYS[0] if STORY_KEYS else EPIC_KEY)
    
    done_transition_id = None
    for t in transitions:
        if t['name'].lower() in ['done', 'hecho', 'complete', 'completed']:
            done_transition_id = t['id']
            break
    
    if not done_transition_id:
        print(f"❌ Could not find 'Done' transition")
        return
    
    print(f"   ✅ Done transition ID: {done_transition_id}")
    
    # Close stories
    closed_count = 0
    skipped_count = 0
    
    if STORY_KEYS:
        print(f"\n📝 Closing {len(STORY_KEYS)} stories...")
        print("="*100)
        
        story_comment = COMPLETION_COMMENT.format(date=today)
        
        for i, story_key in enumerate(STORY_KEYS, 1):
            print(f"\n[{i}/{len(STORY_KEYS)}] {story_key}...")
            
            if close_issue(story_key, story_comment, done_transition_id):
                if get_issue_status(story_key)['status'].lower() in ['done', 'hecho']:
                    closed_count += 1
                else:
                    skipped_count += 1
            
            time.sleep(0.5)
    
    # Close Epic
    print(f"\n📦 Closing Epic: {EPIC_KEY}...")
    print("="*100)
    
    epic_comment = EPIC_COMPLETION_COMMENT.format(date=today)
    epic_closed = close_issue(EPIC_KEY, epic_comment, done_transition_id)
    
    # Summary
    print("\n" + "="*100)
    print("📊 SUMMARY")
    print("="*100)
    
    if STORY_KEYS:
        print(f"\n   Stories Closed: {closed_count}")
        print(f"   Stories Skipped (already done): {skipped_count}")
        print(f"   Total Stories: {len(STORY_KEYS)}")
    
    print(f"   Epic Closed: {'✅ Yes' if epic_closed else '❌ No'}")
    
    if epic_closed and (not STORY_KEYS or closed_count + skipped_count == len(STORY_KEYS)):
        print(f"\n🎉 SUCCESS! Epic and all stories closed!")
    else:
        print(f"\n⚠️  Some issues could not be closed")
    
    print("\n" + "="*100)


if __name__ == "__main__":
    main()

