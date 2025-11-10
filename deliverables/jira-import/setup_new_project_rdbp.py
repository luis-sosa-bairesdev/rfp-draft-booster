#!/usr/bin/env python3
"""
Setup complete RDBP project with:
- 2 Sprints
- 3 Epics
- All User Stories (as type Story, not Task)
- Properly organized in Sprints
"""

import json
import urllib.request
import urllib.error
import urllib.parse
import base64
import time
from datetime import datetime, timedelta

# Configuration
JIRA_URL = "https://luis-sosa-bairesdev.atlassian.net"
EMAIL = "luis.sosa@bairesdev.com"
API_TOKEN = "ATATT3xFfGF05S_SCHS3O_OqM3rJcN9nM9-g3AorAXYCLvHDC2bvMGJhSgU9pCvIPNFPAbAmxJMU3UtO9R3ed-ccV7PInG7h51OTK9JTdS3ERz2Tdbrljl6E2yQDwVKtwsia8PI_UHC6F4wFE_P_D955n6fKNFiZBrCF4K3PNoonm6nxXKLNEJI=0B414822"
PROJECT_KEY = "RDBP"
BOARD_ID = 34
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
        print(f"   ❌ HTTP {e.code}: {error_body}")
        return None


def create_sprint(board_id: int, name: str, start_date: str, end_date: str, goal: str = ""):
    """Create a sprint."""
    url = f"{JIRA_URL}/rest/agile/1.0/sprint"
    data = {
        "name": name,
        "startDate": start_date,
        "endDate": end_date,
        "originBoardId": board_id,
        "goal": goal
    }
    return make_request(url, method="POST", data=data)


def create_issue(project_key: str, issue_type: str, summary: str, description: str, 
                 assignee: str = None, epic_link: str = None, story_points: int = None):
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
    
    if epic_link:
        fields["parent"] = {"key": epic_link}
    
    if story_points:
        fields["customfield_10016"] = story_points  # Story Points field
    
    data = {"fields": fields}
    return make_request(url, method="POST", data=data)


def move_issues_to_sprint(sprint_id: int, issue_keys: list):
    """Move issues to a sprint."""
    url = f"{JIRA_URL}/rest/agile/1.0/sprint/{sprint_id}/issue"
    data = {"issues": issue_keys}
    return make_request(url, method="POST", data=data)


def main():
    """Setup complete RDBP project."""
    
    print("=" * 100)
    print("🚀 SETTING UP NEW RDBP PROJECT")
    print("=" * 100)
    
    # Epic and Story definitions
    epics = [
        {
            "summary": "[EPIC] Project Setup & Infrastructure",
            "description": "Establish the foundational project structure, development environment, and core infrastructure needed for the RFP Draft Booster application.",
            "stories": [
                {"summary": "Setup project repository and folder structure", "points": 5},
                {"summary": "Configure Python virtual environment and dependencies", "points": 3},
                {"summary": "Create basic Streamlit app with navigation", "points": 5},
                {"summary": "Implement code quality tools (Black, pylint, mypy)", "points": 5},
                {"summary": "Setup pytest and test infrastructure", "points": 5},
                {"summary": "Create .env configuration for API keys", "points": 3},
                {"summary": "Setup Git hooks and pre-commit checks", "points": 3},
                {"summary": "Create README with setup instructions", "points": 3},
                {"summary": "Setup CI/CD pipeline (GitHub Actions)", "points": 5},
                {"summary": "Configure logging infrastructure", "points": 3},
            ]
        },
        {
            "summary": "[EPIC] PDF Processing & Upload",
            "description": "Build the PDF upload and text extraction functionality that allows sales reps to upload RFP documents and extract text content for downstream processing.",
            "stories": [
                {"summary": "Upload RFP PDFs via drag-and-drop", "points": 5},
                {"summary": "File validation (type and size)", "points": 3},
                {"summary": "Upload progress indicator", "points": 5},
                {"summary": "Automatic text extraction from PDFs", "points": 13},
                {"summary": "Clear error messages for extraction failures", "points": 3},
                {"summary": "Extracted text preview display", "points": 5},
                {"summary": "Add RFP metadata (client name, deadline)", "points": 5},
                {"summary": "Cancel uploads in progress", "points": 3},
            ]
        },
        {
            "summary": "[EPIC] LLM Requirement Extraction",
            "description": "Implement AI-powered requirement extraction that analyzes RFP text and extracts structured requirements with categorization, prioritization, and confidence scoring.",
            "stories": [
                {"summary": "AI extracts requirements from RFP automatically", "points": 13},
                {"summary": "Requirements categorized (technical, functional, timeline, budget, compliance)", "points": 8},
                {"summary": "Requirements prioritized (critical, high, medium, low)", "points": 5},
                {"summary": "Confidence scores for each extraction", "points": 5},
                {"summary": "Show source page numbers for requirements", "points": 3},
                {"summary": "Edit extracted requirements", "points": 5},
                {"summary": "Add requirements manually", "points": 5},
                {"summary": "Delete incorrect extractions", "points": 3},
                {"summary": "Mark requirements as verified", "points": 3},
                {"summary": "Filter requirements by category/priority", "points": 5},
            ]
        }
    ]
    
    # Step 1: Create Sprints
    print("\n" + "=" * 100)
    print("📅 STEP 1: CREATE SPRINTS")
    print("=" * 100)
    
    today = datetime.now()
    sprint1_start = today.strftime("%Y-%m-%dT00:00:00.000Z")
    sprint1_end = (today + timedelta(days=14)).strftime("%Y-%m-%dT23:59:59.999Z")
    sprint2_start = (today + timedelta(days=14)).strftime("%Y-%m-%dT00:00:00.000Z")
    sprint2_end = (today + timedelta(days=28)).strftime("%Y-%m-%dT23:59:59.999Z")
    
    print("\n📅 Creating Sprint 1...")
    sprint1 = create_sprint(BOARD_ID, "Sprint 1 - Setup & Upload", 
                           sprint1_start, sprint1_end, 
                           "Setup project infrastructure and PDF upload functionality")
    
    if sprint1:
        sprint1_id = sprint1['id']
        print(f"   ✅ Sprint 1 created: ID {sprint1_id}")
    else:
        print("   ❌ Failed to create Sprint 1")
        return
    
    print("\n📅 Creating Sprint 2...")
    sprint2 = create_sprint(BOARD_ID, "Sprint 2 - LLM Extract", 
                           sprint2_start, sprint2_end, 
                           "Implement AI-powered requirement extraction")
    
    if sprint2:
        sprint2_id = sprint2['id']
        print(f"   ✅ Sprint 2 created: ID {sprint2_id}")
    else:
        print("   ❌ Failed to create Sprint 2")
        return
    
    time.sleep(2)  # Rate limiting
    
    # Step 2: Create Epics and Stories
    print("\n" + "=" * 100)
    print("🎯 STEP 2: CREATE EPICS AND USER STORIES")
    print("=" * 100)
    
    epic_keys = []
    all_issues = []
    
    for i, epic_data in enumerate(epics, 1):
        print(f"\n🎯 Creating Epic {i}: {epic_data['summary']}")
        
        # Create Epic
        epic = create_issue(PROJECT_KEY, "Epic", epic_data['summary'], 
                           epic_data['description'], ASSIGNEE)
        
        if not epic:
            print(f"   ❌ Failed to create Epic {i}")
            continue
        
        epic_key = epic['key']
        epic_keys.append(epic_key)
        all_issues.append(epic_key)
        print(f"   ✅ Epic created: {epic_key}")
        
        time.sleep(1)  # Rate limiting
        
        # Create User Stories for this Epic
        print(f"   📝 Creating {len(epic_data['stories'])} User Stories...")
        
        story_keys = []
        for j, story_data in enumerate(epic_data['stories'], 1):
            story = create_issue(PROJECT_KEY, "Story", story_data['summary'], 
                               f"Story for {epic_data['summary']}", 
                               ASSIGNEE, epic_key, story_data['points'])
            
            if story:
                story_key = story['key']
                story_keys.append(story_key)
                all_issues.append(story_key)
                print(f"      ✅ Story {j}/{len(epic_data['stories'])}: {story_key} - {story_data['summary']}")
            else:
                print(f"      ❌ Failed to create story: {story_data['summary']}")
            
            time.sleep(0.5)  # Rate limiting
        
        print(f"   ✅ Created {len(story_keys)} User Stories for Epic {i}")
        
        time.sleep(2)  # Rate limiting between epics
    
    # Step 3: Move Epics to Sprints
    print("\n" + "=" * 100)
    print("🏃 STEP 3: MOVE EPICS TO SPRINTS")
    print("=" * 100)
    
    # Get all issues to organize them
    print("\n🔍 Getting all created issues...")
    url = f"{JIRA_URL}/rest/api/3/search/jql?jql={urllib.parse.quote(f'project = {PROJECT_KEY} ORDER BY key ASC')}&fields=key,summary,issuetype,parent&maxResults=100"
    search_result = make_request(url)
    
    if not search_result:
        print("   ❌ Failed to retrieve issues")
        return
    
    issues = search_result.get('issues', [])
    
    # Organize issues by epic
    epic1_issues = [epic_keys[0]]
    epic2_issues = [epic_keys[1]]
    epic3_issues = [epic_keys[2]]
    
    for issue in issues:
        if issue['fields']['issuetype']['name'] == 'Story':
            parent = issue['fields'].get('parent')
            if parent:
                parent_key = parent['key']
                if parent_key == epic_keys[0]:
                    epic1_issues.append(issue['key'])
                elif parent_key == epic_keys[1]:
                    epic2_issues.append(issue['key'])
                elif parent_key == epic_keys[2]:
                    epic3_issues.append(issue['key'])
    
    # Move Epic 1 and Epic 2 to Sprint 1
    print(f"\n🏃 Moving Epic 1 and Epic 2 to Sprint 1...")
    print(f"   Epic 1: {len(epic1_issues)} issues")
    print(f"   Epic 2: {len(epic2_issues)} issues")
    
    sprint1_issues = epic1_issues + epic2_issues
    result = move_issues_to_sprint(sprint1_id, sprint1_issues)
    
    if result is not None:
        print(f"   ✅ Moved {len(sprint1_issues)} issues to Sprint 1")
    else:
        print(f"   ❌ Failed to move issues to Sprint 1")
    
    time.sleep(2)
    
    # Move Epic 3 to Sprint 2
    print(f"\n🏃 Moving Epic 3 to Sprint 2...")
    print(f"   Epic 3: {len(epic3_issues)} issues")
    
    result = move_issues_to_sprint(sprint2_id, epic3_issues)
    
    if result is not None:
        print(f"   ✅ Moved {len(epic3_issues)} issues to Sprint 2")
    else:
        print(f"   ❌ Failed to move issues to Sprint 2")
    
    # Final Summary
    print("\n" + "=" * 100)
    print("✅ PROJECT SETUP COMPLETE!")
    print("=" * 100)
    
    print(f"\n📊 Summary:")
    print(f"   ✅ 2 Sprints created")
    print(f"   ✅ 3 Epics created: {', '.join(epic_keys)}")
    print(f"   ✅ {len(all_issues) - 3} User Stories created")
    print(f"   ✅ Sprint 1: Epic 1 + Epic 2 ({len(sprint1_issues)} issues)")
    print(f"   ✅ Sprint 2: Epic 3 ({len(epic3_issues)} issues)")
    
    print(f"\n🔗 View Your Board:")
    print(f"   https://luis-sosa-bairesdev.atlassian.net/jira/software/projects/RDBP/boards/34")
    print(f"\n🔗 View Backlog:")
    print(f"   https://luis-sosa-bairesdev.atlassian.net/jira/software/projects/RDBP/boards/34/backlog")
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Refresh your Jira board")
    print(f"   2. Start Sprint 1")
    print(f"   3. Begin working on Epic 1 stories")


if __name__ == "__main__":
    main()

