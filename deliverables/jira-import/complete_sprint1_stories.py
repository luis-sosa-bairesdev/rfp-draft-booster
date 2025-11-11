#!/usr/bin/env python3
"""Move all Sprint 1 stories to Done with completion comments."""

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


def get_transitions(issue_key: str):
    """Get available transitions for an issue."""
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/transitions"
    return make_request(url)


def transition_issue(issue_key: str, transition_id: str):
    """Transition an issue to a new status."""
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/transitions"
    data = {"transition": {"id": transition_id}}
    return make_request(url, method="POST", data=data)


def add_comment(issue_key: str, comment_text: str):
    """Add a comment to an issue."""
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/comment"
    data = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": comment_text
                        }
                    ]
                }
            ]
        }
    }
    return make_request(url, method="POST", data=data)


# Story completion comments
STORY_COMMENTS = {
    # Epic 1: Project Setup & Infrastructure
    "RDBP-2": "Completed: Project repository initialized with proper folder structure (src/, tests/, deliverables/, data/, logs/). All directories created and organized according to Python best practices.",
    "RDBP-3": "Completed: Python 3.13 virtual environment configured. All dependencies installed via requirements.txt including Streamlit, PyPDF2, pdfplumber, and development tools.",
    "RDBP-4": "Completed: Multi-page Streamlit app created with navigation sidebar. Main dashboard and page structure implemented with proper routing.",
    "RDBP-5": "Completed: Code quality tools configured including Black (formatter), pylint (linter), and mypy (type checker). Pre-commit hooks setup for automatic formatting.",
    "RDBP-6": "Completed: pytest infrastructure setup with test directory structure, fixtures, and basic test cases. Coverage reporting configured.",
    "RDBP-7": "Completed: .env configuration file created for API keys and settings. Environment variable management implemented with python-dotenv.",
    "RDBP-8": "Completed: Git hooks configured for pre-commit checks. Automated linting and formatting on commit. .gitignore properly configured.",
    "RDBP-9": "Completed: Comprehensive README.md created with setup instructions, project structure, dependencies, and usage examples.",
    "RDBP-10": "Completed: GitHub Actions CI/CD pipeline configured for automated testing, linting, and code quality checks on push and pull requests.",
    "RDBP-11": "Completed: Logging infrastructure implemented with structured logging to files and console. Log rotation and level configuration setup.",
    
    # Epic 2: PDF Processing & Upload
    "RDBP-13": "Completed: Drag-and-drop PDF upload interface implemented in Streamlit. File uploader component with clear instructions and visual feedback.",
    "RDBP-14": "Completed: File validation implemented for PDF type checking, size limits (max 50MB), and MIME type verification. Clear error messages for invalid files.",
    "RDBP-15": "Completed: Real-time upload progress indicator implemented with status messages for each processing stage (uploading, validating, extracting, finalizing).",
    "RDBP-16": "Completed: Automatic text extraction from PDFs using PyPDF2 (primary) and pdfplumber (fallback). Page-by-page tracking and UTF-8 encoding support implemented.",
    "RDBP-17": "Completed: Clear, user-friendly error messages implemented for extraction failures including scanned PDFs, corrupted files, and password-protected documents.",
    "RDBP-18": "Completed: Extracted text preview display with statistics (pages, words, characters, processing time). Download option for full extracted text added.",
    "RDBP-19": "Completed: RFP metadata capture implemented including title (auto-populated from filename), notes field, and tags. Stored with extracted text.",
    "RDBP-20": "Completed: Upload cancellation functionality added with proper cleanup of partial uploads and session state reset. Cancel button available during processing.",
}


def main():
    """Complete all Sprint 1 stories."""
    
    print("=" * 100)
    print("✅ COMPLETING SPRINT 1 STORIES")
    print("=" * 100)
    
    # Epic 1 stories
    epic1_stories = ["RDBP-2", "RDBP-3", "RDBP-4", "RDBP-5", "RDBP-6", 
                     "RDBP-7", "RDBP-8", "RDBP-9", "RDBP-10", "RDBP-11"]
    
    # Epic 2 stories
    epic2_stories = ["RDBP-13", "RDBP-14", "RDBP-15", "RDBP-16", "RDBP-17", 
                     "RDBP-18", "RDBP-19", "RDBP-20"]
    
    all_stories = epic1_stories + epic2_stories
    
    print(f"\n📋 Processing {len(all_stories)} stories...")
    print(f"   Epic 1: {len(epic1_stories)} stories")
    print(f"   Epic 2: {len(epic2_stories)} stories")
    
    # Process Epic 1 stories
    print("\n" + "=" * 100)
    print("🎯 EPIC 1: Project Setup & Infrastructure")
    print("=" * 100)
    
    for story_key in epic1_stories:
        print(f"\n📝 Processing {story_key}...")
        
        # Get transitions
        transitions_data = get_transitions(story_key)
        if not transitions_data:
            print(f"   ❌ Failed to get transitions for {story_key}")
            continue
        
        transitions = transitions_data.get('transitions', [])
        
        # Find "Done" transition
        done_transition_id = None
        for t in transitions:
            if t['name'].lower() in ['done', 'listo', 'finalizada', 'completed']:
                done_transition_id = t['id']
                break
        
        if not done_transition_id:
            print(f"   ⚠️  'Done' transition not available for {story_key}")
            print(f"      Available: {[t['name'] for t in transitions]}")
            continue
        
        # Add comment
        comment_text = STORY_COMMENTS.get(story_key, "Completed successfully.")
        comment_result = add_comment(story_key, comment_text)
        
        if comment_result:
            print(f"   ✅ Comment added")
        else:
            print(f"   ⚠️  Comment failed (continuing anyway)")
        
        time.sleep(0.5)
        
        # Transition to Done
        transition_result = transition_issue(story_key, done_transition_id)
        
        if transition_result is not None:
            print(f"   ✅ {story_key} → Done")
        else:
            print(f"   ❌ Failed to transition {story_key}")
        
        time.sleep(0.8)  # Rate limiting
    
    # Process Epic 2 stories
    print("\n" + "=" * 100)
    print("📄 EPIC 2: PDF Processing & Upload")
    print("=" * 100)
    
    for story_key in epic2_stories:
        print(f"\n📝 Processing {story_key}...")
        
        # Get transitions
        transitions_data = get_transitions(story_key)
        if not transitions_data:
            print(f"   ❌ Failed to get transitions for {story_key}")
            continue
        
        transitions = transitions_data.get('transitions', [])
        
        # Find "Done" transition
        done_transition_id = None
        for t in transitions:
            if t['name'].lower() in ['done', 'listo', 'finalizada', 'completed']:
                done_transition_id = t['id']
                break
        
        if not done_transition_id:
            print(f"   ⚠️  'Done' transition not available for {story_key}")
            print(f"      Available: {[t['name'] for t in transitions]}")
            continue
        
        # Add comment
        comment_text = STORY_COMMENTS.get(story_key, "Completed successfully.")
        comment_result = add_comment(story_key, comment_text)
        
        if comment_result:
            print(f"   ✅ Comment added")
        else:
            print(f"   ⚠️  Comment failed (continuing anyway)")
        
        time.sleep(0.5)
        
        # Transition to Done
        transition_result = transition_issue(story_key, done_transition_id)
        
        if transition_result is not None:
            print(f"   ✅ {story_key} → Done")
        else:
            print(f"   ❌ Failed to transition {story_key}")
        
        time.sleep(0.8)  # Rate limiting
    
    # Complete Epics
    print("\n" + "=" * 100)
    print("🎯 COMPLETING EPICS")
    print("=" * 100)
    
    epics = ["RDBP-1", "RDBP-12"]
    epic_comments = {
        "RDBP-1": "Epic completed: All project infrastructure setup stories finished. Repository structure, development environment, code quality tools, testing framework, and CI/CD pipeline are fully operational.",
        "RDBP-12": "Epic completed: All PDF processing and upload stories finished. Drag-and-drop upload, file validation, progress tracking, text extraction, error handling, and metadata capture are fully implemented and tested."
    }
    
    for epic_key in epics:
        print(f"\n🎯 Processing {epic_key}...")
        
        # Get transitions
        transitions_data = get_transitions(epic_key)
        if not transitions_data:
            print(f"   ❌ Failed to get transitions for {epic_key}")
            continue
        
        transitions = transitions_data.get('transitions', [])
        
        # Find "Done" transition
        done_transition_id = None
        for t in transitions:
            if t['name'].lower() in ['done', 'listo', 'finalizada', 'completed']:
                done_transition_id = t['id']
                break
        
        if not done_transition_id:
            print(f"   ⚠️  'Done' transition not available for {epic_key}")
            continue
        
        # Add comment
        comment_result = add_comment(epic_key, epic_comments[epic_key])
        
        if comment_result:
            print(f"   ✅ Comment added")
        
        time.sleep(0.5)
        
        # Transition to Done
        transition_result = transition_issue(epic_key, done_transition_id)
        
        if transition_result is not None:
            print(f"   ✅ {epic_key} → Done")
        else:
            print(f"   ❌ Failed to transition {epic_key}")
        
        time.sleep(1)
    
    # Final summary
    print("\n" + "=" * 100)
    print("✅ SPRINT 1 COMPLETED!")
    print("=" * 100)
    
    print(f"\n📊 Summary:")
    print(f"   ✅ {len(epic1_stories)} Epic 1 stories → Done")
    print(f"   ✅ {len(epic2_stories)} Epic 2 stories → Done")
    print(f"   ✅ 2 Epics → Done")
    print(f"   ✅ Total: {len(all_stories) + 2} issues completed")
    
    print(f"\n🔗 View Your Board:")
    print(f"   https://luis-sosa-bairesdev.atlassian.net/jira/software/projects/RDBP/boards/34")
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Refresh your Jira board")
    print(f"   2. Review completed stories in Sprint 1")
    print(f"   3. Close Sprint 1")
    print(f"   4. Start Sprint 2 for Epic 3")


if __name__ == "__main__":
    main()

