#!/usr/bin/env python3
"""Update Epic 2 documentation in Confluence."""

import json
import urllib.request
import urllib.error
import base64

# Configuration
CONFLUENCE_URL = "https://luis-sosa-bairesdev.atlassian.net"
EMAIL = "luis.sosa@bairesdev.com"
API_TOKEN = "ATATT3xFfGF05S_SCHS3O_OqM3rJcN9nM9-g3AorAXYCLvHDC2bvMGJhSgU9pCvIPNFPAbAmxJMU3UtO9R3ed-ccV7PInG7h51OTK9JTdS3ERz2Tdbrljl6E2yQDwVKtwsia8PI_UHC6F4wFE_P_D955n6fKNFiZBrCF4K3PNoonm6nxXKLNEJI=0B414822"
SPACE_KEY = "~712020bfc89abf8f5841728f3bd48d6a60043a"
PAGE_TITLE = "[EPIC 2] PDF Processing & Upload - COMPLETED ✅"
EPIC_2_PAGE_ID = "1900642"


def make_confluence_request(endpoint: str, method: str = "GET", data: dict = None):
    """Make a request to Confluence API."""
    url = f"{CONFLUENCE_URL}/wiki/api/v2/{endpoint}"
    
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
            response_data = response.read().decode('utf-8')
            return json.loads(response_data) if response_data else {}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"HTTP {e.code}: {error_body}")
        raise


def get_page_by_title(title: str):
    """Search for a page by title."""
    try:
        endpoint = f"pages?spaceKey={SPACE_KEY}&title={urllib.parse.quote(title)}"
        result = make_confluence_request(endpoint)
        pages = result.get('results', [])
        return pages[0] if pages else None
    except Exception as e:
        print(f"Error searching for page: {e}")
        return None


def update_page(page_id: str, title: str, content: str, version: int):
    """Update an existing Confluence page."""
    endpoint = f"pages/{page_id}"
    
    # Convert markdown to Confluence storage format (simplified)
    body = {
        "representation": "storage",
        "value": markdown_to_html(content)
    }
    
    data = {
        "id": page_id,
        "status": "current",
        "title": title,
        "body": body,
        "version": {
            "number": version + 1,
            "message": "Updated Epic 2 status to COMPLETED"
        }
    }
    
    return make_confluence_request(endpoint, method="PUT", data=data)


def create_page(space_id: str, title: str, content: str, parent_id: str = None):
    """Create a new Confluence page."""
    endpoint = "pages"
    
    body = {
        "representation": "storage",
        "value": markdown_to_html(content)
    }
    
    data = {
        "spaceId": space_id,
        "status": "current",
        "title": title,
        "body": body
    }
    
    if parent_id:
        data["parentId"] = parent_id
    
    return make_confluence_request(endpoint, method="POST", data=data)


def markdown_to_html(markdown: str) -> str:
    """Convert simplified markdown to HTML."""
    html = markdown
    
    # Headers
    html = html.replace("### ", "<h3>").replace("\n\n", "</h3>\n\n")
    html = html.replace("## ", "<h2>").replace("\n\n", "</h2>\n\n")
    html = html.replace("# ", "<h1>").replace("\n\n", "</h1>\n\n")
    
    # Bold
    while "**" in html:
        html = html.replace("**", "<strong>", 1)
        html = html.replace("**", "</strong>", 1)
    
    # Lists
    html = html.replace("- [x]", "<li>✅")
    html = html.replace("- [ ]", "<li>☐")
    html = html.replace("- ", "<li>")
    
    # Line breaks
    html = html.replace("\n", "<br/>")
    
    return html


def main():
    """Update Epic 2 documentation in Confluence."""
    
    print("=" * 80)
    print("UPDATING CONFLUENCE - EPIC 2 COMPLETED")
    print("=" * 80)
    
    # Read the markdown file
    with open("confluence-epic-02.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    print("\n1. Reading Epic 2 documentation...")
    print(f"   ✅ Loaded {len(content)} characters")
    
    # Try to find existing page
    print(f"\n2. Searching for existing page: '{PAGE_TITLE}'...")
    page = get_page_by_title(PAGE_TITLE)
    
    if page:
        page_id = page['id']
        version = page['version']['number']
        print(f"   ✅ Found page: {page_id} (version {version})")
        
        print("\n3. Updating page...")
        result = update_page(page_id, PAGE_TITLE, content, version)
        print(f"   ✅ Page updated!")
        print(f"   URL: {CONFLUENCE_URL}/wiki/pages/viewpage.action?pageId={page_id}")
    else:
        print("   ℹ️  Page not found, will create new page")
        
        # Get space info
        space_endpoint = f"spaces?keys={SPACE_KEY}"
        space_result = make_confluence_request(space_endpoint)
        spaces = space_result.get('results', [])
        
        if not spaces:
            print("   ❌ Space not found!")
            return
        
        space_id = spaces[0]['id']
        print(f"   ✅ Found space: {space_id}")
        
        print("\n3. Creating new page...")
        result = create_page(space_id, PAGE_TITLE, content)
        page_id = result['id']
        print(f"   ✅ Page created!")
        print(f"   URL: {CONFLUENCE_URL}/wiki/pages/viewpage.action?pageId={page_id}")
    
    print("\n" + "=" * 80)
    print("✅ CONFLUENCE UPDATED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    main()

