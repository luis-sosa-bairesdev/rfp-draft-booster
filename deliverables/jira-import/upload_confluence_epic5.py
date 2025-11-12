#!/usr/bin/env python3
"""Upload Epic 5 completion summary to Confluence."""

import json
import urllib.request
import urllib.error
import base64
from pathlib import Path

# Configuration
JIRA_URL = "https://luis-sosa-bairesdev.atlassian.net"
EMAIL = "luis.sosa@bairesdev.com"
API_TOKEN = "ATATT3xFfGF05S_SCHS3O_OqM3rJcN9nM9-g3AorAXYCLvHDC2bvMGJhSgU9pCvIPNFPAbAmxJMU3UtO9R3ed-ccV7PInG7h51OTK9JTdS3ERz2Tdbrljl6E2yQDwVKtwsia8PI_UHC6F4wFE_P_D955n6fKNFiZBrCF4K3PNoonm6nxXKLNEJI=0B414822"
SPACE_KEY = "~712020bfc89abf8f5841728f3bd48d6a60043a"  # Personal space
PAGE_TITLE = "Epic 5: Draft Generation & AI Assistant - Completion Summary"


def make_request(url: str, method: str = "GET", data: dict = None):
    """Make a request to Confluence API."""
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
                raise Exception(f"HTTP {response.status}: {response.read().decode('utf-8')}")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        raise Exception(f"HTTP {e.code}: {error_body}")


def markdown_to_confluence_storage(markdown_text: str) -> dict:
    """Convert markdown to Confluence storage format."""
    lines = markdown_text.split('\n')
    content = []
    current_paragraph = []
    
    for line in lines:
        line = line.strip()
        
        if not line:
            if current_paragraph:
                content.append({
                    "type": "paragraph",
                    "content": [{"type": "text", "text": " ".join(current_paragraph)}]
                })
                current_paragraph = []
            continue
        
        # Headers
        if line.startswith('# '):
            if current_paragraph:
                content.append({
                    "type": "paragraph",
                    "content": [{"type": "text", "text": " ".join(current_paragraph)}]
                })
                current_paragraph = []
            content.append({
                "type": "heading",
                "attrs": {"level": 1},
                "content": [{"type": "text", "text": line[2:]}]
            })
        elif line.startswith('## '):
            if current_paragraph:
                content.append({
                    "type": "paragraph",
                    "content": [{"type": "text", "text": " ".join(current_paragraph)}]
                })
                current_paragraph = []
            content.append({
                "type": "heading",
                "attrs": {"level": 2},
                "content": [{"type": "text", "text": line[3:]}]
            })
        elif line.startswith('### '):
            if current_paragraph:
                content.append({
                    "type": "paragraph",
                    "content": [{"type": "text", "text": " ".join(current_paragraph)}]
                })
                current_paragraph = []
            content.append({
                "type": "heading",
                "attrs": {"level": 3},
                "content": [{"type": "text", "text": line[4:]}]
            })
        # Lists
        elif line.startswith('- ') or line.startswith('* '):
            if current_paragraph:
                content.append({
                    "type": "paragraph",
                    "content": [{"type": "text", "text": " ".join(current_paragraph)}]
                })
                current_paragraph = []
            content.append({
                "type": "bulletList",
                "content": [{
                    "type": "listItem",
                    "content": [{
                        "type": "paragraph",
                        "content": [{"type": "text", "text": line[2:]}]
                    }]
                }]
            })
        else:
            current_paragraph.append(line)
    
    if current_paragraph:
        content.append({
            "type": "paragraph",
            "content": [{"type": "text", "text": " ".join(current_paragraph)}]
        })
    
    return {
        "type": "doc",
        "version": 1,
        "content": content if content else [{
            "type": "paragraph",
            "content": []
        }]
    }


def search_page(title: str):
    """Search for existing page."""
    url = f"{JIRA_URL}/wiki/rest/api/content"
    params = f"?spaceKey={SPACE_KEY}&title={urllib.parse.quote(title)}&expand=version"
    return make_request(url + params)


def create_or_update_page(title: str, content_markdown: str):
    """Create or update Confluence page."""
    # Search for existing page
    existing = search_page(title)
    
    content_storage = markdown_to_confluence_storage(content_markdown)
    
    if existing.get("results"):
        # Update existing page
        page_id = existing["results"][0]["id"]
        version = existing["results"][0]["version"]["number"]
        
        url = f"{JIRA_URL}/wiki/rest/api/content/{page_id}"
        data = {
            "version": {"number": version + 1},
            "title": title,
            "type": "page",
            "body": {
                "storage": content_storage
            }
        }
        
        result = make_request(url, method="PUT", data=data)
        print(f"✅ Updated page: {title}")
        print(f"   URL: {JIRA_URL}/wiki{result.get('_links', {}).get('webui', '')}")
        return result
    else:
        # Create new page
        url = f"{JIRA_URL}/wiki/rest/api/content"
        data = {
            "type": "page",
            "title": title,
            "space": {"key": SPACE_KEY},
            "body": {
                "storage": content_storage
            }
        }
        
        result = make_request(url, method="POST", data=data)
        print(f"✅ Created page: {title}")
        print(f"   URL: {JIRA_URL}/wiki{result.get('_links', {}).get('webui', '')}")
        return result


def main():
    """Upload Epic 5 completion summary to Confluence."""
    import urllib.parse
    
    summary_path = Path(__file__).parent.parent / "EPIC-5-COMPLETION-SUMMARY.md"
    
    if not summary_path.exists():
        print(f"❌ Summary file not found: {summary_path}")
        return
    
    with open(summary_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("=" * 60)
    print("Uploading Epic 5 Completion Summary to Confluence")
    print("=" * 60)
    
    try:
        create_or_update_page(PAGE_TITLE, content)
        print("\n✅ Successfully uploaded to Confluence!")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()

