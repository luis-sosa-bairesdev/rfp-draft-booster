#!/usr/bin/env python3
"""Import Epic 2: PDF Processing & Upload to JIRA"""

import json
import sys
import urllib.request
import base64
from typing import Dict, Optional

def make_request(base_url, email, api_token, url, data=None, method="GET"):
    """Make HTTP request to JIRA API."""
    credentials = f"{email}:{api_token}"
    b64_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Basic {b64_credentials}"
    }
    
    request_data = None
    if data:
        request_data = json.dumps(data).encode('utf-8')
    
    request = urllib.request.Request(url, data=request_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"❌ Error: {e}")
        if hasattr(e, 'read'):
            print(f"   Response: {e.read().decode()}")
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 import_epic_02.py YOUR_API_TOKEN")
        sys.exit(1)

    api_token = sys.argv[1]
    base_url = "https://luis-sosa-bairesdev.atlassian.net"
    email = "luis.sosa@bairesdev.com"
    project_key = "SCRUM"

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

    result = make_request(base_url, email, api_token, 
                         f"{base_url}/rest/api/3/issue", 
                         data=epic_issue, method="POST")
    
    if not result or 'key' not in result:
        print("❌ Failed to create Epic")
        sys.exit(1)

    epic_key = result['key']
    print(f"✅ Created Epic: {epic_key} - {epic_data['summary']}")

    # Create Stories
    print(f"\n📝 Creating {len(stories_json['user_stories'])} User Stories...")
    
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

        result = make_request(base_url, email, api_token,
                            f"{base_url}/rest/api/3/issue",
                            data=story_issue, method="POST")
        
        if result and 'key' in result:
            print(f"✅ Created: {result['key']} - {story['summary']}")

    print("\n" + "=" * 80)
    print("✅ Epic 2 Import Complete!")
    print("=" * 80)
    print(f"\n📍 Epic URL: {base_url}/browse/{epic_key}")

if __name__ == "__main__":
    main()



