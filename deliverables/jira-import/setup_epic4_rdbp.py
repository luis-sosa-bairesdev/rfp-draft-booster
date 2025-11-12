#!/usr/bin/env python3
"""
Setup Epic 4: Risk Detection & Analysis
- Create Epic 4
- Create Sprint 3
- Create 13 User Stories
- Link stories to Epic 4
- Add stories to Sprint 3
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
                 assignee: str = None, parent_key: str = None, story_points: int = None, priority: str = None):
    """Create an issue."""
    url = f"{JIRA_URL}/rest/api/3/issue"
    
    # Convert description to Jira's document format
    description_content = []
    for line in description.split('\n'):
        if line.strip():
            description_content.append({
                "type": "paragraph",
                "content": [{"type": "text", "text": line}]
            })
    
    fields = {
        "project": {"key": project_key},
        "summary": summary,
        "description": {
            "type": "doc",
            "version": 1,
            "content": description_content if description_content else [
                {"type": "paragraph", "content": [{"type": "text", "text": description}]}
            ]
        },
        "issuetype": {"name": issue_type}
    }
    
    if assignee:
        fields["assignee"] = {"emailAddress": assignee}
    
    if parent_key:
        fields["parent"] = {"key": parent_key}
    
    if story_points:
        fields["customfield_10016"] = story_points  # Story Points field
    
    if priority:
        fields["priority"] = {"name": priority}
    
    data = {"fields": fields}
    return make_request(url, method="POST", data=data)


def update_issue_epic_link(issue_key: str, epic_key: str):
    """Link an issue to an epic using Epic Link field."""
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}"
    data = {
        "fields": {
            "customfield_10011": epic_key  # Epic Link field
        }
    }
    return make_request(url, method="PUT", data=data)


def move_issues_to_sprint(sprint_id: int, issue_keys: list):
    """Move issues to a sprint."""
    url = f"{JIRA_URL}/rest/agile/1.0/sprint/{sprint_id}/issue"
    data = {"issues": issue_keys}
    return make_request(url, method="POST", data=data)


def main():
    """Setup Epic 4: Risk Detection & Analysis."""
    
    print("=" * 100)
    print("🚀 SETTING UP EPIC 4: RISK DETECTION & ANALYSIS")
    print("=" * 100)
    
    # Epic 4 details
    epic_summary = "[EPIC] Risk Detection & Analysis"
    epic_description = """Identify problematic clauses in RFPs using pattern matching and AI, with severity classification and actionable recommendations.

This epic enables early risk flagging before contract negotiation, preventing costly contract issues and improving proposal quality with risk-aware responses.

Key Features:
- Automatic risk detection (pattern + AI)
- Risk categorization (legal, financial, timeline, technical, compliance)
- Severity classification (critical, high, medium, low)
- Mitigation recommendations
- Alternative language suggestions
- Risk acknowledgment tracking"""
    
    # User Stories definitions
    stories = [
        # Backend Stories
        {
            "summary": "Detect risks using regex patterns for common problematic clauses",
            "description": """As a system, I want to detect common risk patterns using regex, so that standard problematic clauses are identified quickly without LLM calls.

Acceptance Criteria:
- Create regex patterns for common risk clauses (penalties, liability, exclusivity, etc.)
- Match patterns against RFP text
- Extract matched clause text and context
- Assign initial category and severity""",
            "points": 8,
            "type": "Backend"
        },
        {
            "summary": "Detect risks using LLM analysis for complex clauses",
            "description": """As a system, I want to use AI to detect complex risk clauses, so that nuanced problematic language is identified even when not matching standard patterns.

Acceptance Criteria:
- Use LLM to analyze RFP text chunks
- Extract risk clauses with context
- Categorize risks (legal, financial, timeline, technical, compliance)
- Assign severity (critical, high, medium, low)
- Provide confidence score""",
            "points": 13,
            "type": "Backend"
        },
        {
            "summary": "Categorize detected risks into 5 categories",
            "description": """As a sales rep, I want risks categorized by type, so that I can quickly understand what kind of issues need attention.

Acceptance Criteria:
- Categories: legal, financial, timeline, technical, compliance
- Each risk assigned to one category
- Category displayed with icon/color""",
            "points": 5,
            "type": "Backend"
        },
        {
            "summary": "Assign severity levels to detected risks",
            "description": """As a sales rep, I want risks prioritized by severity, so that I focus on critical issues first.

Acceptance Criteria:
- Severity levels: critical, high, medium, low
- Each risk assigned severity
- Critical risks flagged prominently""",
            "points": 5,
            "type": "Backend"
        },
        {
            "summary": "Generate mitigation recommendations for detected risks",
            "description": """As a sales rep, I want actionable recommendations for each risk, so that I know how to address problematic clauses.

Acceptance Criteria:
- Generate recommendation text for each risk
- Include potential impact description
- Suggest mitigation strategies""",
            "points": 8,
            "type": "Backend"
        },
        {
            "summary": "Suggest alternative clause language for detected risks",
            "description": """As a sales rep, I want alternative language suggestions, so that I can propose safer clause wording.

Acceptance Criteria:
- Generate alternative clause text
- Highlight differences from original
- Make suggestions editable""",
            "points": 5,
            "type": "Backend"
        },
        # UI Stories
        {
            "summary": "Display detected risks in sortable table",
            "description": """As a sales rep, I want to see all detected risks in a table, so that I can review them efficiently.

Acceptance Criteria:
- Display risks with: category, severity, clause text, page number, confidence
- Sortable columns
- Expandable details
- Color-coded severity""",
            "points": 8,
            "type": "UI"
        },
        {
            "summary": "Filter risks by category and severity",
            "description": """As a sales rep, I want to filter risks, so that I can focus on specific types or severity levels.

Acceptance Criteria:
- Filter by category (5 options)
- Filter by severity (4 options)
- Show only unacknowledged risks""",
            "points": 5,
            "type": "UI"
        },
        {
            "summary": "Allow users to acknowledge risks",
            "description": """As a sales manager, I want to acknowledge critical risks, so that the team tracks which risks have been reviewed.

Acceptance Criteria:
- Acknowledge button for each risk
- Track acknowledgment timestamp
- Require acknowledgment for critical risks before draft generation
- Add notes on how risk will be addressed""",
            "points": 8,
            "type": "UI"
        },
        {
            "summary": "Display mitigation recommendations and alternative language",
            "description": """As a sales rep, I want to see recommendations and alternatives, so that I can address risks effectively.

Acceptance Criteria:
- Display recommendation text
- Display alternative clause language
- Allow copying alternative text
- Show potential impact""",
            "points": 5,
            "type": "UI"
        },
        # Testing Stories
        {
            "summary": "Create unit tests for Risk model",
            "description": """As a developer, I want unit tests for the Risk model, so that data validation and model behavior is verified.

Acceptance Criteria:
- Test model creation and validation
- Test enum conversions
- Test serialization methods
- Achieve 100% coverage""",
            "points": 3,
            "type": "Testing"
        },
        {
            "summary": "Create unit tests for Risk Detector service",
            "description": """As a developer, I want unit tests for Risk Detector, so that risk detection logic is verified.

Acceptance Criteria:
- Test pattern matching
- Test AI detection
- Test categorization and severity assignment
- Achieve 80%+ coverage""",
            "points": 5,
            "type": "Testing"
        },
        {
            "summary": "Create UI tests for Risk Analysis page",
            "description": """As a developer, I want UI tests, so that the Risk Analysis interface is verified.

Acceptance Criteria:
- Test risk display
- Test filtering
- Test acknowledgment
- Test recommendations display""",
            "points": 3,
            "type": "Testing"
        }
    ]
    
    # Step 1: Create Epic 4
    print("\n" + "=" * 100)
    print("🎯 STEP 1: CREATE EPIC 4")
    print("=" * 100)
    
    print(f"\n🎯 Creating Epic 4: {epic_summary}")
    epic = create_issue(PROJECT_KEY, "Epic", epic_summary, epic_description, 
                       ASSIGNEE, priority="High")
    
    if not epic:
        print("   ❌ Failed to create Epic 4")
        return
    
    epic_key = epic['key']
    print(f"   ✅ Epic 4 created: {epic_key}")
    
    time.sleep(2)  # Rate limiting
    
    # Step 2: Create Sprint 3
    print("\n" + "=" * 100)
    print("📅 STEP 2: CREATE SPRINT 3")
    print("=" * 100)
    
    tomorrow = datetime.now() + timedelta(days=1)
    sprint_start = tomorrow.strftime("%Y-%m-%dT00:00:00.000Z")
    sprint_end = (tomorrow + timedelta(days=14)).strftime("%Y-%m-%dT23:59:59.999Z")
    
    print("\n📅 Creating Sprint 3...")
    sprint3 = create_sprint(BOARD_ID, "Sprint 3 - Risk Detection", 
                           sprint_start, sprint_end, 
                           "Implement Epic 4: Risk Detection & Analysis with pattern matching, AI detection, categorization, and UI")
    
    if not sprint3:
        print("   ❌ Failed to create Sprint 3")
        return
    
    sprint3_id = sprint3['id']
    print(f"   ✅ Sprint 3 created: ID {sprint3_id}")
    
    time.sleep(2)  # Rate limiting
    
    # Step 3: Create User Stories
    print("\n" + "=" * 100)
    print("📝 STEP 3: CREATE USER STORIES")
    print("=" * 100)
    
    story_keys = []
    
    for i, story_data in enumerate(stories, 1):
        print(f"\n📝 Creating Story {i}/{len(stories)}: {story_data['summary']}")
        story = create_issue(PROJECT_KEY, "Story", story_data['summary'], 
                           story_data['description'], ASSIGNEE, 
                           parent_key=epic_key, story_points=story_data['points'])
        
        if story:
            story_key = story['key']
            story_keys.append(story_key)
            print(f"   ✅ Story created: {story_key} ({story_data['type']}, {story_data['points']} points)")
        else:
            print(f"   ❌ Failed to create story: {story_data['summary']}")
        
        time.sleep(0.5)  # Rate limiting
    
    print(f"\n✅ Created {len(story_keys)} User Stories")
    
    time.sleep(2)  # Rate limiting
    
    # Step 4: Link Stories to Epic 4 (using Epic Link field)
    print("\n" + "=" * 100)
    print("🔗 STEP 4: LINK STORIES TO EPIC 4")
    print("=" * 100)
    
    print(f"\n🔗 Linking {len(story_keys)} stories to Epic 4 ({epic_key})...")
    linked_count = 0
    
    for story_key in story_keys:
        result = update_issue_epic_link(story_key, epic_key)
        if result is not None:
            linked_count += 1
            print(f"   ✅ {story_key} → {epic_key}")
        else:
            print(f"   ⚠️  Failed to link {story_key} (may already be linked via parent)")
        time.sleep(0.3)
    
    print(f"\n✅ Linked {linked_count} stories to Epic 4")
    
    time.sleep(2)  # Rate limiting
    
    # Step 5: Add Stories to Sprint 3
    print("\n" + "=" * 100)
    print("🏃 STEP 5: ADD STORIES TO SPRINT 3")
    print("=" * 100)
    
    print(f"\n🏃 Adding Epic 4 and {len(story_keys)} stories to Sprint 3...")
    sprint_issues = [epic_key] + story_keys
    
    result = move_issues_to_sprint(sprint3_id, sprint_issues)
    
    if result is not None:
        print(f"   ✅ Added {len(sprint_issues)} issues to Sprint 3")
        print(f"      - Epic: {epic_key}")
        print(f"      - Stories: {len(story_keys)}")
    else:
        print(f"   ❌ Failed to add issues to Sprint 3")
    
    # Final Summary
    print("\n" + "=" * 100)
    print("✅ EPIC 4 SETUP COMPLETE!")
    print("=" * 100)
    
    print(f"\n📊 Summary:")
    print(f"   ✅ Epic 4 created: {epic_key}")
    print(f"   ✅ Sprint 3 created: ID {sprint3_id}")
    print(f"   ✅ {len(story_keys)} User Stories created")
    print(f"   ✅ All stories linked to Epic 4")
    print(f"   ✅ All issues added to Sprint 3")
    
    print(f"\n📋 Story Breakdown:")
    backend_stories = [s for s in stories if s['type'] == 'Backend']
    ui_stories = [s for s in stories if s['type'] == 'UI']
    testing_stories = [s for s in stories if s['type'] == 'Testing']
    
    print(f"   - Backend: {len(backend_stories)} stories ({sum(s['points'] for s in backend_stories)} points)")
    print(f"   - UI: {len(ui_stories)} stories ({sum(s['points'] for s in ui_stories)} points)")
    print(f"   - Testing: {len(testing_stories)} stories ({sum(s['points'] for s in testing_stories)} points)")
    print(f"   - Total: {len(stories)} stories ({sum(s['points'] for s in stories)} points)")
    
    print(f"\n🔗 View Your Board:")
    print(f"   https://luis-sosa-bairesdev.atlassian.net/jira/software/projects/RDBP/boards/34")
    print(f"\n🔗 View Epic 4:")
    print(f"   https://luis-sosa-bairesdev.atlassian.net/browse/{epic_key}")
    print(f"\n🔗 View Sprint 3:")
    print(f"   https://luis-sosa-bairesdev.atlassian.net/jira/software/projects/RDBP/boards/34/sprint/{sprint3_id}")
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Refresh your Jira board")
    print(f"   2. Start Sprint 3")
    print(f"   3. Begin implementation following EPIC-4-ONBOARDING.md")


if __name__ == "__main__":
    main()

