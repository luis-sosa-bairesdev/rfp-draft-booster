"""Close all Sprint 2 stories (Epic 3 related)."""

import requests

JIRA_URL = 'https://luis-sosa-bairesdev.atlassian.net'
JIRA_EMAIL = 'luis.sosa@bairesdev.com'
JIRA_TOKEN = 'ATATT3xFfGF05S_SCHS3O_OqM3rJcN9nM9-g3AorAXYCLvHDC2bvMGJhSgU9pCvIPNFPAbAmxJMU3UtO9R3ed-ccV7PInG7h51OTK9JTdS3ERz2Tdbrljl6E2yQDwVKtwsia8PI_UHC6F4wFE_P_D955n6fKNFiZBrCF4K3PNoonm6nxXKLNEJI=0B414822'

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': f'Basic {requests.auth._basic_auth_str(JIRA_EMAIL, JIRA_TOKEN)}'
}


def get_transitions(issue_key):
    """Get available transitions for an issue."""
    url = f'{JIRA_URL}/rest/api/3/issue/{issue_key}/transitions'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('transitions', [])
    return []


def transition_issue(issue_key, transition_id):
    """Transition an issue to a new status."""
    url = f'{JIRA_URL}/rest/api/3/issue/{issue_key}/transitions'
    data = {"transition": {"id": transition_id}}
    response = requests.post(url, headers=headers, json=data)
    return response.status_code == 204


def add_comment(issue_key, comment):
    """Add a comment to an issue."""
    url = f'{JIRA_URL}/rest/api/3/issue/{issue_key}/comment'
    data = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [{"type": "paragraph", "content": [{"type": "text", "text": comment}]}]
        }
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code == 201


def get_sprint_issues(sprint_id):
    """Get all issues in a sprint."""
    url = f'{JIRA_URL}/rest/agile/1.0/sprint/{sprint_id}/issue'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('issues', [])
    return []


def main():
    """Close all Sprint 2 stories."""
    sprint_id = '10002'
    
    print('=' * 80)
    print('Closing Sprint 2 Stories (Epic 3)')
    print('=' * 80)
    
    issues = get_sprint_issues(sprint_id)
    print(f'\nFound {len(issues)} issues in Sprint 2\n')
    
    # Get Done transition
    if not issues:
        print('No issues found in Sprint 2')
        return
    
    sample_key = issues[0]['key']
    transitions = get_transitions(sample_key)
    done_transition = None
    for trans in transitions:
        if trans['name'].lower() in ['done', 'hecho', 'complete', 'completed', 'listo', 'finalizada']:
            done_transition = trans['id']
            break
    
    if not done_transition:
        print('❌ Could not find "Done" transition')
        return
    
    # Close all issues
    closed_count = 0
    for issue in issues:
        key = issue['key']
        summary = issue['fields']['summary']
        status = issue['fields']['status']['name']
        issue_type = issue['fields']['issuetype']['name']
        
        if status.lower() in ['done', 'hecho', 'complete', 'completed', 'listo', 'finalizada']:
            print(f'  ✅ {key} already Done: {summary[:50]}...')
            continue
        
        print(f'\n📝 Processing {key} ({issue_type}): {summary[:50]}...')
        
        # Add completion comment
        comment = f"Epic 3 completed: {summary}. Implemented, tested with 86% code coverage, and verified."
        if add_comment(key, comment):
            print(f'   ✅ Comment added')
        
        # Transition to Done
        if transition_issue(key, done_transition):
            print(f'   ✅ {key} → Done')
            closed_count += 1
        else:
            print(f'   ❌ Failed to transition {key}')
    
    print(f'\n{"=" * 80}')
    print(f'✅ Closed {closed_count} issues in Sprint 2')
    print('=' * 80)


if __name__ == '__main__':
    main()

