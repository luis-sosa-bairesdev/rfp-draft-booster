"""
Close Epic 9: Error Handling & UX Polish (RDBP-116).

This script closes all 17 user stories and the epic.

Usage:
    python deliverables/jira-import/close_epic9.py
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from integrations.jira_client import JiraAPIClient

# Initialize Jira client
jira = JiraAPIClient()

# Epic 9 details
EPIC_KEY = "RDBP-116"

# All 17 user stories
USER_STORIES = [
    "RDBP-117",  # Centralized error handling framework
    "RDBP-118",  # Structured logging system
    "RDBP-119",  # Retry mechanisms with exponential backoff
    "RDBP-120",  # Input validation framework
    "RDBP-121",  # Mock data fallback system
    "RDBP-122",  # Session state guards
    "RDBP-123",  # Comprehensive unit tests
    "RDBP-124",  # Error boundaries & recovery UI
    "RDBP-125",  # Loading states & progress indicators
    "RDBP-126",  # E2E test suite
    "RDBP-127",  # Unified AI Assistant Chat
    "RDBP-128",  # Manual Risk Addition
    "RDBP-129",  # Duplicate Requirement Detection
    "RDBP-130",  # Real-Time Progress Feedback
    "RDBP-131",  # Navigation Flow Buttons
    "RDBP-132",  # Consistent Settings Across Pages
    "RDBP-133",  # Epic Documentation & Summary
]


def close_story(story_key: str, resolution: str = "Done") -> None:
    """Close a user story."""
    try:
        print(f"Closing {story_key}...")
        
        # Transition to Done
        jira.transition_issue(story_key, "Done")
        
        print(f"✅ {story_key} closed successfully")
    except Exception as e:
        print(f"❌ Failed to close {story_key}: {str(e)}")


def close_epic() -> None:
    """Close all stories and the epic."""
    print(f"\n🚀 Closing Epic 9: {EPIC_KEY}")
    print(f"📝 Total stories: {len(USER_STORIES)}")
    print("=" * 60)
    
    # Close all user stories
    for story_key in USER_STORIES:
        close_story(story_key)
    
    print("\n" + "=" * 60)
    print(f"📦 Closing Epic: {EPIC_KEY}")
    
    try:
        # Transition epic to Done
        jira.transition_issue(EPIC_KEY, "Done")
        print(f"✅ Epic {EPIC_KEY} closed successfully")
    except Exception as e:
        print(f"❌ Failed to close epic {EPIC_KEY}: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ Epic 9 closure complete!")
    print("\n📊 Summary:")
    print(f"  - Stories closed: {len(USER_STORIES)}")
    print(f"  - Epic closed: {EPIC_KEY}")
    print(f"  - Status: DONE")


if __name__ == "__main__":
    close_epic()

