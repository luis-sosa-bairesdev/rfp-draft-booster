#!/usr/bin/env python3
"""Create testing user stories in Sprint 2."""

import json
import urllib.request
import urllib.error
import base64
import time

# Configuration
JIRA_URL = "https://luis-sosa-bairesdev.atlassian.net"
EMAIL = "luis.sosa@bairesdev.com"
API_TOKEN = "ATATT3xFfGF05S_SCHS3O_OqM3rJcN9nM9-g3AorAXYCLvHDC2bvMGJhSgU9pCvIPNFPAbAmxJMU3UtO9R3ed-ccV7PInG7h51OTK9JTdS3ERz2Tdbrljl6E2yQDwVKtwsia8PI_UHC6F4wFE_P_D955n6fKNFiZBrCF4K3PNoonm6nxXKLNEJI=0B414822"
PROJECT_KEY = "RDBP"
EPIC3_KEY = "RDBP-21"  # Epic 3: LLM Requirements
SPRINT2_ID = 37
ASSIGNEE = "luis.sosa@bairesdev.com"


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


def create_issue(project_key: str, issue_type: str, summary: str, description: str, 
                 assignee: str = None, parent_key: str = None, story_points: int = None):
    """Create an issue."""
    url = f"{JIRA_URL}/rest/api/3/issue"
    
    fields = {
        "project": {"key": project_key},
        "summary": summary,
        "description": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": description
                        }
                    ]
                }
            ]
        },
        "issuetype": {"name": issue_type}
    }
    
    if assignee:
        fields["assignee"] = {"emailAddress": assignee}
    
    if parent_key:
        fields["parent"] = {"key": parent_key}
    
    if story_points:
        fields["customfield_10016"] = story_points
    
    data = {"fields": fields}
    return make_request(url, method="POST", data=data)


def move_to_sprint(sprint_id: int, issue_keys: list):
    """Move issues to a sprint."""
    url = f"{JIRA_URL}/rest/agile/1.0/sprint/{sprint_id}/issue"
    data = {"issues": issue_keys}
    return make_request(url, method="POST", data=data)


def main():
    """Create testing stories."""
    
    print("=" * 100)
    print("📝 CREATING TESTING USER STORIES")
    print("=" * 100)
    
    testing_stories = [
        {
            "summary": "Create unit tests for Requirement model",
            "description": "Write comprehensive unit tests for the Requirement model including validation, serialization, and helper methods. Cover all edge cases and error conditions.",
            "points": 3
        },
        {
            "summary": "Create unit tests for LLM client",
            "description": "Write unit tests for LLM client with mocked responses. Test all providers (Gemini, Groq), error handling, JSON extraction, and fallback logic.",
            "points": 5
        },
        {
            "summary": "Create unit tests for Requirement Extractor",
            "description": "Write unit tests for requirement extraction service including chunking, deduplication, confidence filtering, and page tracking.",
            "points": 5
        },
        {
            "summary": "Create integration tests for PDF processing (Epic 2 regression)",
            "description": "Write integration tests for PDF upload, validation, and text extraction. Test with various PDF types, sizes, and edge cases. Regression testing for Epic 2.",
            "points": 5
        },
        {
            "summary": "Create end-to-end test for requirement extraction flow",
            "description": "Write end-to-end test: Upload PDF → Extract text → Extract requirements → Verify results. Test complete workflow with real/mock LLM.",
            "points": 8
        },
    ]
    
    print(f"\n📋 Creating {len(testing_stories)} testing stories...")
    
    created_keys = []
    
    for i, story_data in enumerate(testing_stories, 1):
        print(f"\n{i}. Creating: {story_data['summary']}")
        
        story = create_issue(
            PROJECT_KEY,
            "Story",
            story_data["summary"],
            story_data["description"],
            ASSIGNEE,
            EPIC3_KEY,
            story_data["points"]
        )
        
        if story:
            story_key = story['key']
            created_keys.append(story_key)
            print(f"   ✅ Created: {story_key}")
        else:
            print(f"   ❌ Failed to create story")
        
        time.sleep(0.5)
    
    # Move to Sprint 2
    if created_keys:
        print(f"\n🏃 Moving {len(created_keys)} stories to Sprint 2...")
        result = move_to_sprint(SPRINT2_ID, created_keys)
        
        if result is not None:
            print(f"   ✅ All testing stories moved to Sprint 2")
        else:
            print(f"   ❌ Failed to move stories to Sprint 2")
    
    # Summary
    print("\n" + "=" * 100)
    print("✅ TESTING STORIES CREATED")
    print("=" * 100)
    
    print(f"\n📊 Summary:")
    print(f"   ✅ {len(created_keys)} testing stories created")
    print(f"   ✅ Added to Epic 3 ({EPIC3_KEY})")
    print(f"   ✅ Assigned to Sprint 2")
    print(f"   ✅ Total story points: {sum(s['points'] for s in testing_stories)}")
    
    print(f"\n📋 Created Stories:")
    for key, story in zip(created_keys, testing_stories):
        print(f"   - {key}: {story['summary']} ({story['points']} pts)")
    
    print(f"\n🔗 View Sprint 2:")
    print(f"   https://luis-sosa-bairesdev.atlassian.net/jira/software/projects/RDBP/boards/34")


if __name__ == "__main__":
    main()

