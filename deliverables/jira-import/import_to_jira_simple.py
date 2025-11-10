#!/usr/bin/env python3
"""
JIRA Import Script for Epic 1: Project Setup & Infrastructure
Uses only Python standard library (no external dependencies)

Usage:
    python3 import_to_jira_simple.py YOUR_JIRA_API_TOKEN
"""

import json
import sys
import urllib.request
import urllib.error
import base64
from typing import Dict, Optional


class JiraImporter:
    """JIRA API client using urllib."""

    def __init__(self, base_url: str, email: str, api_token: str):
        self.base_url = base_url.rstrip("/")
        self.email = email
        self.api_token = api_token
        
        # Create basic auth header
        credentials = f"{email}:{api_token}"
        b64_credentials = base64.b64encode(credentials.encode()).decode()
        self.auth_header = f"Basic {b64_credentials}"

    def _make_request(self, url: str, data: Optional[Dict] = None, method: str = "GET") -> Optional[Dict]:
        """Make HTTP request to JIRA API."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": self.auth_header
        }
        
        request_data = None
        if data:
            request_data = json.dumps(data).encode('utf-8')
        
        request = urllib.request.Request(url, data=request_data, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(request) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            print(f"❌ HTTP Error {e.code}: {e.reason}")
            print(f"   Response: {error_body}")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None

    def create_issue(self, issue_data: Dict) -> Optional[Dict]:
        """Create a JIRA issue."""
        url = f"{self.base_url}/rest/api/3/issue"
        result = self._make_request(url, data=issue_data, method="POST")
        
        if result and 'key' in result:
            print(f"✅ Created: {result['key']} - {issue_data['fields']['summary']}")
        
        return result


def main():
    """Main execution."""
    print("=" * 80)
    print("🚀 JIRA Import Script - Epic 1: Project Setup & Infrastructure")
    print("=" * 80)

    # Get API token from command line
    if len(sys.argv) < 2:
        print("\n❌ Error: JIRA API token required")
        print("\nUsage:")
        print("  python3 import_to_jira_simple.py YOUR_JIRA_API_TOKEN")
        print("\nGet your token from:")
        print("  https://id.atlassian.com/manage-profile/security/api-tokens")
        sys.exit(1)

    api_token = sys.argv[1]

    # Configuration
    JIRA_URL = "https://luis-sosa-bairesdev.atlassian.net"
    JIRA_EMAIL = "luis.sosa@bairesdev.com"
    PROJECT_KEY = "SCRUM"

    print(f"\n📋 Configuration:")
    print(f"   JIRA URL: {JIRA_URL}")
    print(f"   Email: {JIRA_EMAIL}")
    print(f"   Project: {PROJECT_KEY}")

    # Initialize importer
    importer = JiraImporter(JIRA_URL, JIRA_EMAIL, api_token)

    # Load data
    print("\n📂 Loading data files...")
    try:
        with open("epic-01-jira.json", "r") as f:
            epic_json = json.load(f)
        with open("user-stories-epic-01.json", "r") as f:
            stories_json = json.load(f)
    except Exception as e:
        print(f"❌ Error loading files: {e}")
        sys.exit(1)

    # Create Epic
    print("\n📦 Creating Epic...")
    epic_data = epic_json["epic"]
    
    epic_issue_data = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": epic_data["summary"],
            "description": {
                "type": "doc",
                "version": 1,
                "content": [{
                    "type": "paragraph",
                    "content": [{
                        "type": "text",
                        "text": epic_data["description"][:10000]  # Limit description length
                    }]
                }]
            },
            "issuetype": {"name": "Epic"},
            "labels": epic_data.get("labels", [])
        }
    }

    epic_result = importer.create_issue(epic_issue_data)
    
    if not epic_result or 'key' not in epic_result:
        print("\n❌ Failed to create Epic. Aborting.")
        sys.exit(1)

    epic_key = epic_result['key']
    print(f"\n✅ Epic created: {epic_key}")

    # Create User Stories
    print(f"\n📝 Creating {len(stories_json['user_stories'])} User Stories...")
    
    created_count = 0
    for story in stories_json["user_stories"]:
        story_issue_data = {
            "fields": {
                "project": {"key": PROJECT_KEY},
                "summary": story["summary"],
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{
                        "type": "paragraph",
                        "content": [{
                            "type": "text",
                            "text": story["description"][:5000]  # Limit description length
                        }]
                    }]
                },
                "issuetype": {"name": story["issue_type"]},
                "labels": story.get("labels", []),
                "parent": {"key": epic_key}
            }
        }

        result = importer.create_issue(story_issue_data)
        if result:
            created_count += 1

    # Summary
    print("\n" + "=" * 80)
    print("✅ Import Complete!")
    print("=" * 80)
    print(f"\nEpic: {JIRA_URL}/browse/{epic_key}")
    print(f"Stories Created: {created_count}/{len(stories_json['user_stories'])}")
    print("\n🎉 Next steps:")
    print("   1. Review the Epic and stories in JIRA")
    print("   2. Adjust priorities and assignments as needed")
    print("   3. Create Confluence documentation")
    print("   4. Start working on the stories!")


if __name__ == "__main__":
    main()

