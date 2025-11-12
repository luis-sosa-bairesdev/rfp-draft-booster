#!/usr/bin/env python3
"""
Setup Epic 5: Draft Generation & AI Assistant + Sprint 4
Combines original draft generation with competitor-inspired AI Assistant features.
"""

import urllib.request
import urllib.error
import json
import base64
import time
from datetime import datetime, timedelta

# Jira Configuration
JIRA_URL = "https://luis-sosa-bairesdev.atlassian.net"
EMAIL = "luis.sosa@bairesdev.com"
API_TOKEN = "ATATT3xFfGF05S_SCHS3O_OqM3rJcN9nM9-g3AorAXYCLvHDC2bvMGJhSgU9pCvIPNFPAbAmxJMU3UtO9R3ed-ccV7PInG7h51OTK9JTdS3ERz2Tdbrljl6E2yQDwVKtwsia8PI_UHC6F4wFE_P_D955n6fKNFiZBrCF4K3PNoonm6nxXKLNEJI=0B414822"

PROJECT_KEY = "RDBP"
BOARD_ID = 34
ASSIGNEE = "luis.sosa@bairesdev.com"

def make_request(url: str, method: str = "GET", data: dict = None):
    """Make authenticated request to Jira API."""
    credentials = base64.b64encode(f"{EMAIL}:{API_TOKEN}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    req_data = None
    if data:
        req_data = json.dumps(data).encode('utf-8')
    
    request = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"   ❌ HTTP {e.code}: {error_body}")
        return None
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None

def create_epic(project_key: str, summary: str, description: str, priority: str = "High"):
    """Create Epic in Jira."""
    url = f"{JIRA_URL}/rest/api/3/issue"
    
    # Convert markdown description to Jira storage format
    description_content = []
    for line in description.split('\n'):
        if line.strip():
            description_content.append({
                "type": "paragraph",
                "content": [{"type": "text", "text": line}]
            })
        else:
            description_content.append({"type": "paragraph", "content": []})
    
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
        "issuetype": {"name": "Epic"},
        "priority": {"name": priority}
    }
    
    data = {"fields": fields}
    return make_request(url, method="POST", data=data)

def create_sprint(board_id: int, name: str, start_date: str, end_date: str, goal: str = ""):
    """Create Sprint in Jira."""
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
                 assignee: str = None, parent_key: str = None, story_points: int = None,
                 priority: str = None):
    """Create issue (Story/Task) in Jira."""
    url = f"{JIRA_URL}/rest/api/3/issue"
    
    # Convert markdown description to Jira storage format
    description_content = []
    for line in description.split('\n'):
        if line.strip():
            description_content.append({
                "type": "paragraph",
                "content": [{"type": "text", "text": line}]
            })
        else:
            description_content.append({"type": "paragraph", "content": []})
    
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

def move_issues_to_sprint(sprint_id: int, issue_keys: list):
    """Add issues to sprint."""
    url = f"{JIRA_URL}/rest/agile/1.0/sprint/{sprint_id}/issue"
    data = {"issues": issue_keys}
    return make_request(url, method="POST", data=data)

def main():
    """Setup Epic 5: Draft Generation & AI Assistant + Sprint 4."""
    
    print("=" * 100)
    print("🚀 SETTING UP EPIC 5: DRAFT GENERATION & AI ASSISTANT + SPRINT 4")
    print("=" * 100)
    
    # Epic 5 Description
    epic_description = """Generate AI-powered proposal drafts with conversational AI assistant support.

This epic combines:
1. **Draft Generation** (Original MVP): Generate complete proposal drafts with standard sections
2. **AI Assistant** (Competitor-Inspired): Conversational "Ask" feature for contextual help
3. **Enhanced UX**: Progress dashboard and global search for better usability

Key Features:
- AI-powered draft generation with customizable instructions
- Conversational AI assistant ("Ask" button) for contextual help
- Draft editing and section regeneration
- Progress tracking dashboard
- Global search across all content
- Export to Google Docs (Epic 7 - future)

Business Value:
- Complete the MVP workflow: Upload → Requirements → Risks → Draft
- Differentiate with AI Assistant feature
- Improve usability with search and progress tracking
- Reduce draft generation time from 10-20 hours to under 2 minutes"""
    
    # Step 1: Create Epic 5
    print("\n" + "=" * 100)
    print("📋 STEP 1: CREATE EPIC 5")
    print("=" * 100)
    
    print("\n📝 Creating Epic 5: Draft Generation & AI Assistant...")
    epic = create_epic(
        PROJECT_KEY,
        "[EPIC] Draft Generation & AI Assistant",
        epic_description,
        priority="High"
    )
    
    if not epic:
        print("   ❌ Failed to create Epic 5")
        return
    
    epic_key = epic['key']
    print(f"   ✅ Epic 5 created: {epic_key}")
    
    time.sleep(2)
    
    # Step 2: Create Sprint 4
    print("\n" + "=" * 100)
    print("🏃 STEP 2: CREATE SPRINT 4")
    print("=" * 100)
    
    # Calculate dates (2 weeks sprint)
    start_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")
    
    print(f"\n📅 Creating Sprint 4 ({start_date} to {end_date})...")
    sprint4 = create_sprint(
        BOARD_ID,
        "Sprint 4 - Draft & AI",
        start_date,
        end_date,
        "Implement Epic 5: Draft generation with AI assistant, progress dashboard, and global search"
    )
    
    if not sprint4:
        print("   ❌ Failed to create Sprint 4")
        return
    
    sprint4_id = sprint4['id']
    print(f"   ✅ Sprint 4 created: ID {sprint4_id}")
    
    time.sleep(2)
    
    # Step 3: Create User Stories
    print("\n" + "=" * 100)
    print("📝 STEP 3: CREATE USER STORIES")
    print("=" * 100)
    
    stories = [
        # ===== DRAFT GENERATION (Backend) =====
        {
            "summary": "Backend: Draft generation service with customizable instructions",
            "description": """As a developer, I want a draft generation service that creates proposal drafts with customizable AI instructions, so that users can control the tone, style, and content of generated drafts.

Acceptance Criteria:
- Create DraftGenerator service class
- Support customizable AI instructions (tone, word count, audience)
- Generate drafts with sections: executive summary, approach, services, timeline, pricing, risk mitigation
- Use approved service matches in services section
- Address detected risks in risk mitigation section
- Generate in Markdown format
- Complete generation within 2 minutes
- Ensure word count between 500-10,000 words
- Block generation if critical risks not acknowledged""",
            "type": "Story",
            "points": 8,
            "priority": "High"
        },
        {
            "summary": "Backend: Draft model and storage",
            "description": """As a developer, I want a Draft data model to store draft content and metadata, so that drafts can be saved, edited, and versioned.

Acceptance Criteria:
- Create Draft model with fields: id, rfp_id, content (markdown), sections, word_count, generated_at, updated_at
- Support draft versioning
- Store draft in session state
- Support draft serialization/deserialization""",
            "type": "Story",
            "points": 3,
            "priority": "High"
        },
        {
            "summary": "Backend: Section regeneration capability",
            "description": """As a developer, I want the ability to regenerate individual draft sections, so that users can refine specific parts without regenerating the entire draft.

Acceptance Criteria:
- Support regenerating individual sections (exec summary, approach, services, etc.)
- Maintain context from other sections
- Preserve user edits in non-regenerated sections
- Update draft metadata on regeneration""",
            "type": "Story",
            "points": 5,
            "priority": "Medium"
        },
        
        # ===== AI ASSISTANT (Backend) =====
        {
            "summary": "Backend: AI Assistant service for contextual help",
            "description": """As a developer, I want an AI Assistant service that provides contextual help about RFP content, requirements, and risks, so that users can get instant answers to their questions.

Acceptance Criteria:
- Create AIAssistant service class
- Support conversational queries about:
  - Current RFP content and context
  - Extracted requirements (explain, summarize, count)
  - Detected risks (analysis, recommendations, severity)
  - Best practices for RFP responses
  - How to use application features
- Include RFP, requirements, and risks in context
- Store conversation history in session state
- Support follow-up questions
- Return formatted, helpful responses""",
            "type": "Story",
            "points": 8,
            "priority": "Highest"
        },
        
        # ===== DRAFT GENERATION (UI) =====
        {
            "summary": "UI: Draft generation page with instructions",
            "description": """As a sales rep, I want a page to generate proposal drafts with customizable instructions, so that I can control the tone and style of my proposal.

Acceptance Criteria:
- Create "Generate Draft" page
- Display AI instructions input (tone, word count, audience)
- Show generation progress
- Display generated draft in editable Markdown editor
- Show word count
- Display sections with ability to regenerate individual sections
- Block generation if critical risks not acknowledged (with warning)
- Show estimated generation time""",
            "type": "Story",
            "points": 8,
            "priority": "High"
        },
        {
            "summary": "UI: Draft editing and preview",
            "description": """As a sales rep, I want to edit the generated draft directly in the app with real-time preview, so that I can customize it before export.

Acceptance Criteria:
- Editable Markdown text area
- Real-time formatted preview
- Auto-save edits (every 30 seconds)
- Track editing time
- Show word count
- Highlight changes from original
- Support Markdown formatting (headings, lists, bold, italic)
- Undo/redo functionality""",
            "type": "Story",
            "points": 5,
            "priority": "High"
        },
        
        # ===== AI ASSISTANT (UI) =====
        {
            "summary": "UI: AI Assistant modal with chat interface",
            "description": """As a sales rep, I want an "Ask" button that opens a conversational AI assistant, so that I can get instant help about my RFP, requirements, and risks.

Acceptance Criteria:
- Purple "Ask" button always visible in header/navigation
- Modal pop-up with chat interface on click
- Display conversation history
- Input field for questions
- Loading states during AI processing
- "Copy answer" button for each response
- Support follow-up questions
- Close modal with X button or outside click
- Keyboard shortcut (Cmd/Ctrl + K) to open""",
            "type": "Story",
            "points": 8,
            "priority": "Highest"
        },
        
        # ===== PROGRESS DASHBOARD (UI) =====
        {
            "summary": "UI: Progress tracking dashboard",
            "description": """As a sales rep, I want a progress dashboard showing overall RFP analysis status, so that I can understand what's been completed and what needs attention.

Acceptance Criteria:
- Display on main page or dedicated dashboard
- Show metrics:
  - Total requirements extracted: X
  - Requirements by category breakdown
  - Total risks detected: X
  - Risks by severity: Critical (X), High (Y), Medium (Z), Low (W)
  - Risks acknowledged: X/Y
  - Critical risks acknowledged: X/Y (if any)
- Visual progress bars
- Color-coded indicators (green = good, yellow = attention, red = critical)
- Clickable metrics (navigate to relevant page)""",
            "type": "Story",
            "points": 3,
            "priority": "Medium"
        },
        
        # ===== GLOBAL SEARCH (UI) =====
        {
            "summary": "UI: Global search across all content",
            "description": """As a sales rep, I want to search across all RFP content (requirements, risks, extracted text), so that I can quickly find specific information.

Acceptance Criteria:
- Search bar in main navigation (always visible)
- Search across:
  - Requirement text, descriptions, categories
  - Risk clause text, recommendations, categories
  - Extracted RFP text (full text search)
- Highlight matching terms in results
- Filter results by type (All, Requirements, Risks, Text)
- Show result count
- Keyboard shortcut (Cmd/Ctrl + K) to focus search
- Clear search button
- Recent searches (optional)""",
            "type": "Story",
            "points": 5,
            "priority": "High"
        },
        
        # ===== TESTING =====
        {
            "summary": "Testing: Unit tests for draft generation service",
            "description": """As a developer, I want unit tests for the draft generation service, so that draft generation is reliable and maintainable.

Acceptance Criteria:
- Test draft generation with various instructions
- Test section generation
- Test word count validation
- Test critical risk blocking
- Test error handling
- Achieve 80%+ code coverage""",
            "type": "Story",
            "points": 5,
            "priority": "High"
        },
        {
            "summary": "Testing: Unit tests for AI Assistant service",
            "description": """As a developer, I want unit tests for the AI Assistant service, so that contextual help is reliable.

Acceptance Criteria:
- Test question answering with RFP context
- Test requirement queries
- Test risk queries
- Test conversation history
- Test error handling
- Achieve 80%+ code coverage""",
            "type": "Story",
            "points": 5,
            "priority": "High"
        },
        {
            "summary": "Testing: UI tests for draft generation page",
            "description": """As a developer, I want UI tests for the draft generation page, so that the interface is verified.

Acceptance Criteria:
- Test draft generation flow
- Test instruction input
- Test draft editing
- Test section regeneration
- Test progress indicators
- Test error states""",
            "type": "Story",
            "points": 3,
            "priority": "Medium"
        },
        {
            "summary": "Testing: UI tests for AI Assistant modal",
            "description": """As a developer, I want UI tests for the AI Assistant modal, so that the chat interface is verified.

Acceptance Criteria:
- Test modal open/close
- Test question submission
- Test response display
- Test copy answer functionality
- Test conversation history
- Test loading states""",
            "type": "Story",
            "points": 3,
            "priority": "Medium"
        }
    ]
    
    story_keys = []
    
    for i, story_data in enumerate(stories, 1):
        print(f"\n📝 Creating Story {i}/{len(stories)}: {story_data['summary']}")
        story = create_issue(
            PROJECT_KEY,
            story_data['type'],
            story_data['summary'],
            story_data['description'],
            ASSIGNEE,
            parent_key=epic_key,
            story_points=story_data['points'],
            priority=story_data['priority']
        )
        
        if story:
            story_key = story['key']
            story_keys.append(story_key)
            print(f"   ✅ Story created: {story_key} ({story_data['type']}, {story_data['points']} points, {story_data['priority']} priority)")
        else:
            print(f"   ❌ Failed to create story: {story_data['summary']}")
        
        time.sleep(0.5)  # Rate limiting
    
    print(f"\n✅ Created {len(story_keys)} User Stories")
    
    time.sleep(2)
    
    # Step 4: Add Stories to Sprint 4
    print("\n" + "=" * 100)
    print("🏃 STEP 4: ADD STORIES TO SPRINT 4")
    print("=" * 100)
    
    print(f"\n🏃 Adding {len(story_keys)} stories to Sprint 4...")
    result = move_issues_to_sprint(sprint4_id, story_keys)
    
    if result:
        print(f"   ✅ All stories added to Sprint 4")
    else:
        print(f"   ⚠️  Some stories may not have been added (check manually)")
    
    # Summary
    total_points = sum(s['points'] for s in stories)
    print("\n" + "=" * 100)
    print("✅ SETUP COMPLETE")
    print("=" * 100)
    print(f"\n📊 Summary:")
    print(f"   Epic: {epic_key} - Draft Generation & AI Assistant")
    print(f"   Sprint: Sprint 4 (ID: {sprint4_id})")
    print(f"   Stories: {len(story_keys)}")
    print(f"   Total Story Points: {total_points}")
    print(f"\n📋 Stories Breakdown:")
    print(f"   Backend: 4 stories (24 points)")
    print(f"   UI: 5 stories (29 points)")
    print(f"   Testing: 4 stories (16 points)")
    print(f"\n🎯 Priority Breakdown:")
    print(f"   Highest: 2 stories (16 points) - AI Assistant")
    print(f"   High: 6 stories (37 points) - Draft Generation")
    print(f"   Medium: 5 stories (16 points) - UX Enhancements & Testing")
    print(f"\n🔗 Jira Links:")
    print(f"   Epic: {JIRA_URL}/browse/{epic_key}")
    print(f"   Sprint: {JIRA_URL}/jira/software/projects/{PROJECT_KEY}/boards/{BOARD_ID}")

if __name__ == "__main__":
    main()

