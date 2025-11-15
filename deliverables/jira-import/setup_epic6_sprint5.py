#!/usr/bin/env python3
"""
Create Epic 6 (Service Matching) and Sprint 5 in Jira with user stories.

Based on: deliverables/epic-06-service-matching.md
"""

import urllib.request
import urllib.error
import json
import base64
from datetime import datetime, timedelta

# Jira Configuration
JIRA_URL = "https://luis-sosa-bairesdev.atlassian.net"
EMAIL = "luis.sosa@bairesdev.com"
API_TOKEN = "ATATT3xFfGF05S_SCHS3O_OqM3rJcN9nM9-g3AorAXYCLvHDC2bvMGJhSgU9pCvIPNFPAbAmxJMU3UtO9R3ed-ccV7PInG7h51OTK9JTdS3ERz2Tdbrljl6E2yQDwVKtwsia8PI_UHC6F4wFE_P_D955n6fKNFiZBrCF4K3PNoonm6nxXKLNEJI=0B414822"
PROJECT_KEY = "RDBP"
BOARD_ID = "34"
ASSIGNEE = "luis.sosa@bairesdev.com"

# Create auth header
auth_string = f"{EMAIL}:{API_TOKEN}"
auth_bytes = auth_string.encode('ascii')
base64_auth = base64.b64encode(auth_bytes).decode('ascii')

HEADERS = {
    "Authorization": f"Basic {base64_auth}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}


def create_sprint(name: str, start_date: str, end_date: str, goal: str) -> int:
    """Create a sprint in Jira."""
    url = f"{JIRA_URL}/rest/agile/1.0/sprint"
    
    data = {
        "name": name,
        "startDate": start_date,
        "endDate": end_date,
        "originBoardId": int(BOARD_ID),
        "goal": goal
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers=HEADERS,
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            sprint_id = result['id']
            print(f"✅ Sprint created: {name} (ID: {sprint_id})")
            return sprint_id
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"❌ Error creating sprint: {e.code}")
        print(f"   Response: {error_body}")
        raise


def create_issue(summary: str, description: str, issue_type: str = "Story",
                 story_points: int = None, priority: str = "Medium",
                 parent_key: str = None) -> str:
    """Create an issue in Jira."""
    url = f"{JIRA_URL}/rest/api/3/issue"
    
    fields = {
        "project": {"key": PROJECT_KEY},
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
        "issuetype": {"name": issue_type},
        "priority": {"name": priority}
    }
    
    # Add assignee
    if issue_type != "Epic":
        fields["assignee"] = {"emailAddress": ASSIGNEE}
    
    # Add parent for stories
    if parent_key and issue_type != "Epic":
        fields["parent"] = {"key": parent_key}
    
    # Add story points for stories
    if story_points and issue_type == "Story":
        fields["customfield_10016"] = story_points  # Story Points field
    
    data = {"fields": fields}
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers=HEADERS,
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            issue_key = result['key']
            print(f"✅ Created {issue_type}: {issue_key} - {summary}")
            return issue_key
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"❌ Error creating issue: {e.code}")
        print(f"   Summary: {summary}")
        print(f"   Response: {error_body}")
        raise


def move_issues_to_sprint(sprint_id: int, issue_keys: list):
    """Move issues to a sprint."""
    url = f"{JIRA_URL}/rest/agile/1.0/sprint/{sprint_id}/issue"
    
    data = {
        "issues": issue_keys
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers=HEADERS,
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            print(f"✅ Moved {len(issue_keys)} issues to Sprint {sprint_id}")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"❌ Error moving issues to sprint: {e.code}")
        print(f"   Response: {error_body}")
        # Continue even if this fails - issues can be moved manually


def main():
    """Create Epic 6 and Sprint 5 with user stories."""
    
    print("\n" + "="*60)
    print("🚀 Setting up Epic 6: Service Matching & Sprint 5")
    print("="*60 + "\n")
    
    # Step 1: Create Epic 6
    print("\n📋 Step 1: Creating Epic 6...")
    epic_description = """Implement intelligent service-to-requirement matching to help sales teams quickly identify which BairesDev offerings best fulfill each RFP requirement.

Key Features:
- Automated matching using TF-IDF + cosine similarity
- Visual match scoring with color coding (>80% green, 50-80% yellow, <50% red)
- Filterable match table by category and threshold
- Coverage chart by requirement category
- Approval workflow for matches
- Integration with Draft Generation

Value: Reduce proposal assembly time by 50% (from 2-4 hours to 15-30 minutes)
"""
    
    epic_key = create_issue(
        summary="[EPIC] Service Matching Screen",
        description=epic_description,
        issue_type="Epic",
        priority="Medium"
    )
    
    # Step 2: Create Sprint 5
    print("\n📅 Step 2: Creating Sprint 5...")
    start_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")
    
    sprint_id = create_sprint(
        name="Sprint 5 - Service Matching",
        start_date=start_date,
        end_date=end_date,
        goal="Implement Epic 6: Service Matching with TF-IDF matching engine, filterable UI, and Draft Generation integration"
    )
    
    # Step 3: Create User Stories
    print("\n📝 Step 3: Creating User Stories...")
    
    stories = []
    
    # Backend Stories (26 points)
    backend_stories = [
        {
            "summary": "Create service catalog data model and JSON loader",
            "description": """As a developer, I want a data model for the service catalog, so that services can be loaded and managed consistently.

Acceptance Criteria:
- Create Service dataclass with fields: id, name, category, description, capabilities, success_rate, tags
- Create ServiceCategory enum (technical, functional, timeline, budget, compliance)
- Implement load_services_from_json() function
- Create data/services.json with 10 BairesDev sample services
- Validate JSON schema on load
- Handle missing/malformed JSON gracefully

Technical Notes:
- Similar pattern to RFP and Requirement models
- Use Pydantic for validation
- Store in src/models/service.py""",
            "points": 5,
            "priority": "High"
        },
        {
            "summary": "Implement TF-IDF matching engine with cosine similarity",
            "description": """As a developer, I want a matching engine that computes similarity scores between requirements and services, so that relevant matches are identified automatically.

Acceptance Criteria:
- Create ServiceMatcher class in src/services/service_matcher.py
- Implement match_requirement() for single requirement matching
- Implement match_all_requirements() for batch processing
- Use scikit-learn TfidfVectorizer for text vectorization
- Use cosine_similarity for scoring (0.0-1.0)
- Return top N matches per requirement (default: top 3)
- Include reasoning field explaining why service matches
- Performance: <2 seconds for 50 requirements × 10 services

Technical Notes:
- Combine requirement description + service description + capabilities for matching
- Use English stopwords removal
- Cache vectorizer for performance""",
            "points": 13,
            "priority": "High"
        },
        {
            "summary": "Add coverage calculation and statistics utilities",
            "description": """As a sales rep, I want to see coverage statistics by requirement category, so that I can identify gaps before drafting.

Acceptance Criteria:
- Implement calculate_coverage_by_category() in ServiceMatcher
- Return dict with category → avg match % mapping
- Implement get_overall_coverage() for average across all matches
- Add color_for_score() utility (green/yellow/red based on thresholds)
- Count approved matches vs. total matches
- Handle edge cases (no requirements, no matches)

Technical Notes:
- Used for bar chart data in UI
- Store thresholds as constants: GREEN = 0.80, YELLOW = 0.50""",
            "points": 5,
            "priority": "Medium"
        },
        {
            "summary": "Add session state management for service matches",
            "description": """As a developer, I want service matches persisted in session state, so that approved matches are available across pages.

Acceptance Criteria:
- Add service_matches: List[ServiceMatch] to session.py
- Add approved_matches: List[ServiceMatch] to session.py
- ServiceMatch dataclass: requirement_id, service_id, score, reasoning, approved
- Initialize empty lists on session start
- Clear matches when new RFP uploaded
- Export/import from JSON

Technical Notes:
- Similar to requirements and risks storage
- Used by Draft Generation to include approved services""",
            "points": 3,
            "priority": "High"
        }
    ]
    
    # UI Stories (29 points)
    ui_stories = [
        {
            "summary": "Create Service Matching page with filters and table",
            "description": """As a sales rep, I want to see all service matches in a filterable table, so that I can review and approve relevant matches.

Acceptance Criteria:
- Create pages/3_🔗_Service_Matching.py (shift Risk Analysis to page 4)
- Display header with stats: X requirements, Y services, Z% avg match
- Add filters:
  - Category dropdown (All, Technical, Functional, Timeline, Budget, Compliance)
  - Match % slider (minimum threshold: 0-100%)
  - Sort order dropdown (Highest Match First, Lowest Match First, Requirement Order)
- Display matches table with columns:
  - Requirement ID, Description (truncated), Matched Service, % Fit, Reasoning (expandable), Approve checkbox
- Color-code rows: Green (>80%), Yellow (50-80%), Red (<50%)
- Show empty state if no matches above threshold
- Update table when filters change

Technical Notes:
- Use st.dataframe or custom table with st.columns
- Store filter state in session_state
- Responsive layout (mobile-friendly)""",
            "points": 13,
            "priority": "High"
        },
        {
            "summary": "Add coverage bar chart by requirement category",
            "description": """As a sales manager, I want to see match coverage by requirement category, so that I can identify weak areas before proposal submission.

Acceptance Criteria:
- Display bar chart below matches table
- X-axis: Requirement categories (Technical, Functional, etc.)
- Y-axis: Average match % (0-100%)
- Color bars by threshold (green/yellow/red)
- Show subtitle with overall average match %
- Add tooltip with detailed stats on hover (if possible)
- Handle empty categories gracefully

Technical Notes:
- Use st.bar_chart or plotly for interactivity
- Data from ServiceMatcher.calculate_coverage_by_category()
- Update chart when matches or approvals change""",
            "points": 5,
            "priority": "Medium"
        },
        {
            "summary": "Implement approval workflow with checkboxes",
            "description": """As a sales rep, I want to approve/reject matches via checkboxes, so that only relevant services are used in draft generation.

Acceptance Criteria:
- Add 'Approve?' checkbox column in matches table
- Auto-check matches >80% by default
- Persist approval state in session_state.approved_matches
- Show count of approved matches in header (e.g., '15/23 approved')
- Add 'Approve All High' button (bulk approve >80%)
- Add 'Clear All' button (bulk deselect)
- Approval state persists when navigating away and back

Technical Notes:
- Use unique keys for checkboxes: f'approve_{req.id}_{service.id}'
- Update session_state on checkbox change
- Filter approved matches for draft generation""",
            "points": 8,
            "priority": "High"
        },
        {
            "summary": "Add export matches functionality",
            "description": """As a sales rep, I want to export service matches to JSON, so that I can review offline or share with team.

Acceptance Criteria:
- Add 'Export Matches' button below chart
- Generate JSON with structure:
  {
    \"rfp_id\": \"...\",
    \"exported_at\": \"2025-XX-XX\",
    \"matches\": [{\"requirement_id\", \"service_id\", \"score\", \"reasoning\", \"approved\"}],
    \"coverage\": {\"category\": \"avg_%\"},
    \"overall_coverage\": \"X%\"
  }
- Use st.download_button for JSON download
- Filename: service_matches_rfp-{rfp_id}_YYYYMMDD.json
- Include only approved matches if 'Approved Only' checkbox is checked
- Show success message after export

Technical Notes:
- JSON should be importable for future restore functionality
- Pretty-print JSON (indent=2)""",
            "points": 3,
            "priority": "Low"
        }
    ]
    
    # Integration Stories (8 points)
    integration_stories = [
        {
            "summary": "Integrate approved matches with Draft Generation",
            "description": """As a sales rep, I want approved service matches automatically included in draft generation, so that the proposal highlights our relevant offerings.

Acceptance Criteria:
- Update get_draft_generation_prompt() in prompt_templates.py
- Add section to prompt: 'Approved Service Matches' with list of services
- Include service name, match %, and reasoning for each
- Only include matches with approved=True and score>80%
- Format as bullet list for LLM consumption
- Update Draft Generation page to show 'Using X approved matches' indicator
- Add 'View Matches' link from Draft page to Service Matching page

Technical Notes:
- Access session_state.approved_matches in prompt builder
- Test with and without approved matches
- Draft should naturally mention matched services in relevant sections""",
            "points": 5,
            "priority": "High"
        },
        {
            "summary": "Add AI Assistant help for Service Matching page",
            "description": """As a sales rep, I want AI Assistant to answer questions about service matches, so that I understand why specific services were suggested.

Acceptance Criteria:
- Add page_context='service_matching' to AI Assistant call
- Update get_page_help() with Service Matching help text:
  - Explains matching algorithm (TF-IDF + cosine similarity)
  - How to interpret match scores
  - When to approve/reject matches
  - How matches feed into drafts
- AI Assistant can answer:
  - 'Why was service X matched to requirement Y?'
  - 'What does a 75% match mean?'
  - 'Should I approve this match?'
- Include approved_matches in AI context

Technical Notes:
- Similar to other page-specific help (requirements, risks, draft)
- Pass approved_matches to _build_context()""",
            "points": 3,
            "priority": "Low"
        }
    ]
    
    # Testing Stories (11 points)
    testing_stories = [
        {
            "summary": "Create unit tests for ServiceMatcher engine",
            "description": """As a developer, I want comprehensive unit tests for ServiceMatcher, so that matching logic is verified and regressions are prevented.

Acceptance Criteria:
- Create tests/test_services/test_service_matcher.py
- Test cases:
  - test_load_services_from_json() - valid and invalid JSON
  - test_match_requirement() - single requirement, top 3 matches
  - test_match_all_requirements() - batch processing
  - test_calculate_coverage_by_category() - various scenarios
  - test_color_for_score() - thresholds (green/yellow/red)
  - test_empty_catalog() - handle no services gracefully
  - test_empty_requirements() - handle no requirements
  - test_performance() - ensure <2s for 50 reqs × 10 services
- Achieve >80% code coverage for service_matcher.py
- All tests pass

Technical Notes:
- Mock services and requirements with pytest fixtures
- Use time.time() to measure performance""",
            "points": 5,
            "priority": "High"
        },
        {
            "summary": "Create UI tests for Service Matching page",
            "description": """As a developer, I want UI tests for the Service Matching page, so that filters and approval workflow are validated.

Acceptance Criteria:
- Create tests/test_ui/test_service_matching_page.py
- Test cases:
  - test_filters_category() - filter by category updates table
  - test_filters_match_threshold() - slider updates matches
  - test_sort_order() - sorting works correctly
  - test_approval_checkboxes() - state persists in session
  - test_approve_all_high() - bulk approve >80%
  - test_export_matches() - JSON export functionality
  - test_coverage_chart() - chart data correct
  - test_empty_state() - no matches display
- Mock session_state and ServiceMatcher
- Achieve >80% coverage for service_matching_page.py

Technical Notes:
- Similar to test_requirements_page.py and test_risk_analysis_page.py
- Mock Streamlit components (st.dataframe, st.bar_chart)""",
            "points": 3,
            "priority": "Medium"
        },
        {
            "summary": "Integration test: Service Matching end-to-end flow",
            "description": """As a QA engineer, I want an integration test for the complete service matching flow, so that the feature works end-to-end.

Acceptance Criteria:
- Create tests/test_integration/test_service_matching_flow.py
- Test full workflow:
  1. Upload RFP (Epic 2)
  2. Extract requirements (Epic 3)
  3. Navigate to Service Matching page
  4. Verify matches computed
  5. Filter matches by category
  6. Approve high-confidence matches
  7. Navigate to Draft Generation
  8. Verify approved matches in draft context
- Test with sample RFP (10-15 requirements)
- Verify session state persistence
- All assertions pass

Technical Notes:
- Use pytest fixtures for sample data
- Mock LLM calls for requirements extraction
- Mock file upload for RFP""",
            "points": 3,
            "priority": "Low"
        }
    ]
    
    # Combine all stories
    all_stories_data = (
        backend_stories + 
        ui_stories + 
        integration_stories + 
        testing_stories
    )
    
    # Create stories in Jira
    for story_data in all_stories_data:
        story_key = create_issue(
            summary=story_data["summary"],
            description=story_data["description"],
            issue_type="Story",
            story_points=story_data["points"],
            priority=story_data["priority"],
            parent_key=epic_key
        )
        stories.append(story_key)
    
    # Step 4: Add stories to Sprint 5
    print(f"\n📦 Step 4: Adding {len(stories)} stories to Sprint 5...")
    move_issues_to_sprint(sprint_id, stories)
    
    # Summary
    print("\n" + "="*60)
    print("✅ Epic 6 & Sprint 5 Setup Complete!")
    print("="*60)
    print(f"\n📊 Summary:")
    print(f"   Epic: {epic_key} - Service Matching Screen")
    print(f"   Sprint: {sprint_id} - Sprint 5 - Service Matching")
    print(f"   Stories Created: {len(stories)}")
    print(f"   Total Story Points: {sum(s['points'] for s in all_stories_data)}")
    print(f"\n   Backend Stories: 4 (26 points)")
    print(f"   UI Stories: 4 (29 points)")
    print(f"   Integration Stories: 2 (8 points)")
    print(f"   Testing Stories: 3 (11 points)")
    print(f"\n🔗 Links:")
    print(f"   Epic: {JIRA_URL}/browse/{epic_key}")
    print(f"   Board: {JIRA_URL}/jira/software/projects/{PROJECT_KEY}/boards/{BOARD_ID}")
    print("\n💡 Next Steps:")
    print("   1. Review stories in Jira")
    print("   2. Start Sprint 5")
    print("   3. Begin implementation with backend stories (highest priority)")
    print("   4. Create data/services.json with sample BairesDev services")
    print("   5. Follow deliverables/epic-06-service-matching.md for implementation")


if __name__ == "__main__":
    main()

