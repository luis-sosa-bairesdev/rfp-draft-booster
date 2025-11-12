#!/usr/bin/env python3
"""Upload Epic 4 documentation to Confluence."""

import json
import urllib.request
import urllib.error
import base64
from pathlib import Path

# Configuration
CONFLUENCE_URL = "https://luis-sosa-bairesdev.atlassian.net"
EMAIL = "luis.sosa@bairesdev.com"
API_TOKEN = "ATATT3xFfGF05S_SCHS3O_OqM3rJcN9nM9-g3AorAXYCLvHDC2bvMGJhSgU9pCvIPNFPAbAmxJMU3UtO9R3ed-ccV7PInG7h51OTK9JTdS3ERz2Tdbrljl6E2yQDwVKtwsia8PI_UHC6F4wFE_P_D955n6fKNFiZBrCF4K3PNoonm6nxXKLNEJI=0B414822"
SPACE_KEY = "~712020bfc89abf8f5841728f3bd48d6a60043a"  # Personal space
PAGE_TITLE = "Epic 4: Risk Detection & Analysis - Completion Report"

# Create auth header
auth_string = f"{EMAIL}:{API_TOKEN}"
auth_bytes = auth_string.encode('ascii')
auth_b64 = base64.b64encode(auth_bytes).decode('ascii')

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': f'Basic {auth_b64}'
}


def read_markdown_file(file_path):
    """Read markdown file content."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def make_request(url, method="GET", data=None):
    """Make a request to Confluence API."""
    if data:
        data_bytes = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
    else:
        req = urllib.request.Request(url, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status in [200, 201]:
                response_data = response.read().decode('utf-8')
                return json.loads(response_data) if response_data else {}
            else:
                print(f"Error {response.status}")
                return None
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"Error {e.code}: {error_body[:500]}")
        return None


def create_confluence_page(space_key, title, content):
    """Create a new Confluence page."""
    url = f'{CONFLUENCE_URL}/wiki/rest/api/content'
    
    data = {
        "type": "page",
        "title": title,
        "space": {"key": space_key},
        "body": {
            "storage": {
                "value": content,
                "representation": "storage"
            }
        }
    }
    
    return make_request(url, method="POST", data=data)


def update_confluence_page(page_id, title, content, version):
    """Update an existing Confluence page."""
    url = f'{CONFLUENCE_URL}/wiki/rest/api/content/{page_id}'
    
    data = {
        "version": {"number": version + 1},
        "title": title,
        "type": "page",
        "body": {
            "storage": {
                "value": content,
                "representation": "storage"
            }
        }
    }
    
    return make_request(url, method="PUT", data=data)


def search_page(space_key, title):
    """Search for a page by title."""
    import urllib.parse
    url = f'{CONFLUENCE_URL}/wiki/rest/api/content'
    params = {
        'spaceKey': space_key,
        'title': title,
        'expand': 'version'
    }
    url_with_params = f"{url}?{urllib.parse.urlencode(params)}"
    
    result = make_request(url_with_params)
    if result:
        results = result.get('results', [])
        return results[0] if results else None
    return None


def convert_markdown_to_confluence_storage(markdown_content):
    """Convert markdown to Confluence storage format."""
    import re
    
    html_content = markdown_content
    
    # Headers
    html_content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html_content, flags=re.MULTILINE)
    
    # Bold
    html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
    
    # Code blocks
    html_content = re.sub(r'```(\w+)?\n(.*?)```', r'<pre><code>\2</code></pre>', html_content, flags=re.DOTALL)
    
    # Inline code
    html_content = re.sub(r'`([^`]+)`', r'<code>\1</code>', html_content)
    
    # Links
    html_content = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', html_content)
    
    # Lists
    html_content = re.sub(r'^- (.+)$', r'<li>\1</li>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', html_content, flags=re.MULTILINE)
    
    # Paragraphs
    html_content = re.sub(r'\n\n', '</p><p>', html_content)
    html_content = '<p>' + html_content + '</p>'
    
    # Clean up
    html_content = re.sub(r'<p></p>', '', html_content)
    html_content = re.sub(r'<p><h', '<h', html_content)
    html_content = re.sub(r'</h([1-6])><p>', '</h\1>', html_content)
    
    return html_content


def main():
    """Upload Epic 4 documentation to Confluence."""
    print('=' * 80)
    print('Uploading Epic 4 Documentation to Confluence')
    print('=' * 80)
    
    # Read markdown file
    md_file = Path(__file__).parent.parent.parent / 'EPIC-4-COMPLETION-SUMMARY.md'
    if not md_file.exists():
        # Try alternative path
        md_file = Path(__file__).parent.parent / 'EPIC-4-COMPLETION-SUMMARY.md'
    if not md_file.exists():
        print(f'❌ File not found: {md_file}')
        return
    
    print(f'\n1. Reading markdown file...')
    markdown_content = read_markdown_file(md_file)
    print(f'   ✅ Read {len(markdown_content)} characters')
    
    # Check if page exists
    print(f'\n2. Checking if page exists...')
    existing_page = search_page(SPACE_KEY, PAGE_TITLE)
    
    if existing_page:
        print(f'   ✅ Page exists: {existing_page["id"]}')
        print(f'   📝 Updating page...')
        
        # Convert markdown to Confluence format
        confluence_content = convert_markdown_to_confluence_storage(markdown_content)
        
        # Update page
        version = existing_page['version']['number']
        result = update_confluence_page(
            existing_page['id'],
            PAGE_TITLE,
            confluence_content,
            version
        )
        
        if result:
            page_url = f"{CONFLUENCE_URL}/wiki{result['_links']['webui']}"
            print(f'   ✅ Page updated successfully!')
            print(f'   🔗 URL: {page_url}')
        else:
            print(f'   ❌ Failed to update page')
    else:
        print(f'   📄 Page does not exist, creating new page...')
        
        # Convert markdown to Confluence format
        confluence_content = convert_markdown_to_confluence_storage(markdown_content)
        
        # Create page
        result = create_confluence_page(SPACE_KEY, PAGE_TITLE, confluence_content)
        
        if result:
            page_url = f"{CONFLUENCE_URL}/wiki{result['_links']['webui']}"
            print(f'   ✅ Page created successfully!')
            print(f'   🔗 URL: {page_url}')
        else:
            print(f'   ❌ Failed to create page')
    
    print('\n' + '=' * 80)
    print('✅ CONFLUENCE UPDATE COMPLETE!')
    print('=' * 80)


if __name__ == '__main__':
    main()

