#!/usr/bin/env python3
import json
import sys
import urllib.request
import base64

api_token = sys.argv[1]
base_url = "https://luis-sosa-bairesdev.atlassian.net"
email = "luis.sosa@bairesdev.com"
project_key = "SCRUM"

credentials = f"{email}:{api_token}"
b64_credentials = base64.b64encode(credentials.encode()).decode()
auth_header = f"Basic {b64_credentials}"

def make_request(url, data=None, method="POST"):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": auth_header
    }
    request_data = json.dumps(data).encode('utf-8') if data else None
    request = urllib.request.Request(url, data=request_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error: {e}")
        return None

print("=" * 80)
print("🚀 Importing Epic 2: PDF Processing & Upload")
print("=" * 80)

# Load data
with open("epic-02-jira.json", "r") as f:
    epic_json = json.load(f)
with open("user-stories-epic-02.json", "r") as f:
    stories_json = json.load(f)

# Create Epic
print("\n📦 Creating Epic...")
epic_data = epic_json["epic"]
epic_issue = {
    "fields": {
        "project": {"key": project_key},
        "summary": epic_data["summary"],
        "description": {
            "type": "doc",
            "version": 1,
            "content": [{
                "type": "paragraph",
                "content": [{"type": "text", "text": epic_data["description"][:10000]}]
            }]
        },
        "issuetype": {"name": "Epic"},
        "labels": epic_data.get("labels", [])
    }
}

url = f"{base_url}/rest/api/3/issue"
epic_result = make_request(url, epic_issue)

if not epic_result or 'key' not in epic_result:
    print("❌ Failed to create Epic")
    sys.exit(1)

epic_key = epic_result['key']
print(f"✅ Epic created: {epic_key} - {epic_data['summary']}")

# Create User Stories
print(f"\n📝 Creating {len(stories_json['user_stories'])} User Stories...")
created_count = 0

for story in stories_json["user_stories"]:
    story_issue = {
        "fields": {
            "project": {"key": project_key},
            "summary": story["summary"],
            "description": {
                "type": "doc",
                "version": 1,
                "content": [{
                    "type": "paragraph",
                    "content": [{"type": "text", "text": story["description"][:5000]}]
                }]
            },
            "issuetype": {"name": story["issue_type"]},
            "labels": story.get("labels", []),
            "parent": {"key": epic_key}
        }
    }
    
    result = make_request(url, story_issue)
    if result and 'key' in result:
        print(f"✅ Created: {result['key']} - {story['summary']}")
        created_count += 1

print("\n" + "=" * 80)
print("✅ Import Complete!")
print("=" * 80)
print(f"\nEpic: {base_url}/browse/{epic_key}")
print(f"Stories Created: {created_count}/{len(stories_json['user_stories'])}")
