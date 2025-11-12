#!/usr/bin/env python3
"""
JIRA Import Script for Epic 1: Project Setup & Infrastructure

This script automates the creation of Epic 1 and its user stories in JIRA
using the JIRA REST API.

Requirements:
    - Python 3.10+
    - requests library: pip install requests
    - JIRA API token configured

Usage:
    python import_to_jira.py
"""

import json
import os
import sys
from typing import Dict, List, Optional

try:
    import requests
except ImportError:
    print("❌ Error: 'requests' library not found.")
    print("Install it with: pip install requests")
    sys.exit(1)


class JiraImporter:
    """JIRA API client for importing Epic 1."""

    def __init__(self, base_url: str, email: str, api_token: str):
        """
        Initialize JIRA importer.

        Args:
            base_url: JIRA instance URL (e.g., https://company.atlassian.net)
            email: User email for authentication
            api_token: JIRA API token
        """
        self.base_url = base_url.rstrip("/")
        self.auth = (email, api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update(self.headers)

    def create_issue(self, issue_data: Dict) -> Optional[Dict]:
        """
        Create a JIRA issue.

        Args:
            issue_data: Issue data in JIRA format

        Returns:
            Created issue data or None if failed
        """
        url = f"{self.base_url}/rest/api/3/issue"

        try:
            response = self.session.post(url, json=issue_data)
            response.raise_for_status()
            created_issue = response.json()
            print(f"✅ Created: {created_issue['key']} - {issue_data['fields']['summary']}")
            return created_issue
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to create issue: {e}")
            if hasattr(e.response, "text"):
                print(f"   Response: {e.response.text}")
            return None

    def get_issue(self, issue_key: str) -> Optional[Dict]:
        """
        Get a JIRA issue by key.

        Args:
            issue_key: Issue key (e.g., RFP-1)

        Returns:
            Issue data or None if not found
        """
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None

    def search_issues(self, jql: str) -> List[Dict]:
        """
        Search JIRA issues using JQL.

        Args:
            jql: JQL query string

        Returns:
            List of matching issues
        """
        url = f"{self.base_url}/rest/api/3/search"
        params = {"jql": jql, "maxResults": 100}

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json().get("issues", [])
        except requests.exceptions.RequestException as e:
            print(f"❌ Search failed: {e}")
            return []


def load_json_file(filepath: str) -> Dict:
    """Load JSON file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {filepath}: {e}")
        sys.exit(1)


def create_epic(importer: JiraImporter, epic_data: Dict, project_key: str) -> Optional[str]:
    """
    Create Epic in JIRA.

    Args:
        importer: JiraImporter instance
        epic_data: Epic data from JSON
        project_key: JIRA project key

    Returns:
        Created Epic key or None if failed
    """
    print("\n📦 Creating Epic...")

    issue_data = {
        "fields": {
            "project": {"key": project_key},
            "summary": epic_data["summary"],
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": epic_data["description"]
                            }
                        ]
                    }
                ]
            },
            "issuetype": {"name": "Epic"},
            "priority": {"name": epic_data["priority"]},
            "labels": epic_data.get("labels", []),
        }
    }

    # Add assignee if provided
    if epic_data.get("assignee"):
        issue_data["fields"]["assignee"] = {"emailAddress": epic_data["assignee"]}

    created = importer.create_issue(issue_data)
    return created["key"] if created else None


def create_user_stories(
    importer: JiraImporter, stories: List[Dict], project_key: str, epic_key: str
) -> None:
    """
    Create user stories in JIRA.

    Args:
        importer: JiraImporter instance
        stories: List of story data from JSON
        project_key: JIRA project key
        epic_key: Parent Epic key
    """
    print(f"\n📝 Creating {len(stories)} User Stories...")

    for story in stories:
        issue_data = {
            "fields": {
                "project": {"key": project_key},
                "summary": story["summary"],
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": story["description"]
                                }
                            ]
                        }
                    ]
                },
                "issuetype": {"name": story["issue_type"]},
                "priority": {"name": story["priority"]},
                "labels": story.get("labels", []),
                "parent": {"key": epic_key},  # Link to Epic
            }
        }

        # Add assignee if provided
        if story.get("assignee"):
            issue_data["fields"]["assignee"] = {"emailAddress": story["assignee"]}

        # Add story points if provided (custom field varies by JIRA instance)
        # You may need to adjust the custom field ID
        if story.get("story_points"):
            # Common custom field IDs for Story Points:
            # customfield_10016 (Jira Cloud)
            # customfield_10004 (Some instances)
            issue_data["fields"]["customfield_10016"] = story["story_points"]

        importer.create_issue(issue_data)


def main():
    """Main execution function."""
    print("=" * 80)
    print("🚀 JIRA Import Script - Epic 1: Project Setup & Infrastructure")
    print("=" * 80)

    # Configuration
    JIRA_URL = os.getenv("JIRA_URL", "https://luis-sosa-bairesdev.atlassian.net")
    JIRA_EMAIL = os.getenv("JIRA_EMAIL", "luis.sosa@bairesdev.com")
    JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
    PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "SCRUM")

    # Validate configuration
    if not JIRA_API_TOKEN:
        print("❌ Error: JIRA_API_TOKEN environment variable not set")
        print("\nSet it with:")
        print("  export JIRA_API_TOKEN='your-api-token-here'")
        print("\nOr create a .env file with:")
        print("  JIRA_API_TOKEN=your-api-token-here")
        sys.exit(1)

    print(f"\n📋 Configuration:")
    print(f"   JIRA URL: {JIRA_URL}")
    print(f"   Email: {JIRA_EMAIL}")
    print(f"   Project: {PROJECT_KEY}")

    # Get user confirmation
    print("\n⚠️  This will create the Epic and 10 user stories in JIRA.")
    response = input("Continue? (yes/no): ")
    if response.lower() not in ["yes", "y"]:
        print("❌ Import cancelled.")
        sys.exit(0)

    # Initialize importer
    importer = JiraImporter(JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN)

    # Load JSON files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    epic_file = os.path.join(script_dir, "epic-01-jira.json")
    stories_file = os.path.join(script_dir, "user-stories-epic-01.json")

    epic_json = load_json_file(epic_file)
    stories_json = load_json_file(stories_file)

    # Create Epic
    epic_key = create_epic(importer, epic_json["epic"], PROJECT_KEY)
    if not epic_key:
        print("\n❌ Failed to create Epic. Aborting.")
        sys.exit(1)

    print(f"\n✅ Epic created: {epic_key}")

    # Create User Stories
    create_user_stories(
        importer, stories_json["user_stories"], PROJECT_KEY, epic_key
    )

    # Summary
    print("\n" + "=" * 80)
    print("✅ Import Complete!")
    print("=" * 80)
    print(f"\nEpic: {JIRA_URL}/browse/{epic_key}")
    print(f"Total Stories Created: {len(stories_json['user_stories'])}")
    print("\n🎉 Next steps:")
    print("   1. Review the Epic and stories in JIRA")
    print("   2. Adjust priorities and assignments as needed")
    print("   3. Create Confluence documentation")
    print("   4. Start working on the stories!")


if __name__ == "__main__":
    main()



