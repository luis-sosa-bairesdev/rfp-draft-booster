#!/usr/bin/env python3
"""
Generic template to upload documentation to Confluence.

USAGE:
1. Update PAGE_TITLE and MARKDOWN_FILE below
2. Run: python3 upload_confluence_template.py
"""

import json
import urllib.request
import urllib.error
import base64
from pathlib import Path

# ============================================================================
# CONFIGURATION - UPDATE THIS
# ============================================================================

CONFLUENCE_URL = "https://luis-sosa-bairesdev.atlassian.net"
EMAIL = "luis.sosa@bairesdev.com"
API_TOKEN = "ATATT3xFfGF0sSVc0RTQhwj6YNxUmVNcEVQAM4OWpmI-E553Bsc46avo_OI-Hlvf_IrYjf0_FBtsCgKBbIJ1KNM2gdrHvfsijPku4fIR9BrLCnm9WcpSKVr_EDeBG1te_aNUatYT5b9w6JSdNt7sgtl6ZdH32IgnTYWLCOh3VEGhnDF6mvWj1g0=0882E324"
SPACE_KEY = "~712020bfc89abf8f5841728f3bd48d6a60043a"  # Personal space

# Page details
PAGE_TITLE = "Your Page Title Here"
MARKDOWN_FILE = "deliverables/YOUR-FILE.md"  # Path to your markdown file

# ============================================================================
# SCRIPT LOGIC - DON'T MODIFY BELOW UNLESS NEEDED
# ============================================================================

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Basic {base64.b64encode(f'{EMAIL}:{API_TOKEN}'.encode()).decode()}"
}


def markdown_to_confluence(md_text):
    """Convert markdown to Confluence storage format (basic)."""
    lines = md_text.split('\n')
    result = []
    in_code = False
    code_lang = ""
    
    for line in lines:
        if line.startswith('```'):
            if in_code:
                result.append('</ac:plain-text-body></ac:structured-macro>')
                in_code = False
            else:
                code_lang = line[3:].strip() or 'none'
                result.append(f'<ac:structured-macro ac:name="code"><ac:parameter ac:name="language">{code_lang}</ac:parameter><ac:plain-text-body><![CDATA[')
                in_code = True
            continue
        
        if in_code:
            result.append(line)
            continue
        
        if line.startswith('# '):
            result.append(f'<h1>{line[2:]}</h1>')
        elif line.startswith('## '):
            result.append(f'<h2>{line[3:]}</h2>')
        elif line.startswith('### '):
            result.append(f'<h3>{line[4:]}</h3>')
        elif line.startswith('#### '):
            result.append(f'<h4>{line[5:]}</h4>')
        elif line.startswith('- '):
            result.append(f'<li>{line[2:]}</li>')
        elif '**' in line:
            line = line.replace('**', '<strong>', 1).replace('**', '</strong>', 1)
            result.append(f'<p>{line}</p>')
        elif not line.strip():
            result.append('<p></p>')
        else:
            result.append(f'<p>{line}</p>')
    
    return '\n'.join(result)


def make_request(url: str, method: str = "GET", data: dict = None):
    """Make request to Confluence API."""
    req_data = json.dumps(data).encode('utf-8') if data else None
    request = urllib.request.Request(url, data=req_data, headers=HEADERS, method=method)
    
    try:
        with urllib.request.urlopen(request) as response:
            if response.status in [200, 201, 204]:
                response_data = response.read().decode('utf-8')
                return json.loads(response_data) if response_data else {}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"❌ HTTP {e.code}: {error_body[:200]}")
        return None


def search_page(title):
    """Search for existing page by title."""
    import urllib.parse
    endpoint = f"content?title={urllib.parse.quote(title)}&spaceKey={SPACE_KEY}&expand=version"
    url = f"{CONFLUENCE_URL}/wiki/rest/api/{endpoint}"
    result = make_request(url)
    
    if result and 'results' in result and len(result['results']) > 0:
        return result['results'][0]
    return None


def create_page(title, content):
    """Create a new page."""
    url = f"{CONFLUENCE_URL}/wiki/rest/api/content"
    data = {
        "type": "page",
        "title": title,
        "space": {"key": SPACE_KEY},
        "body": {
            "storage": {
                "value": content,
                "representation": "storage"
            }
        }
    }
    
    result = make_request(url, method="POST", data=data)
    if result:
        print(f"✅ Created page: {title}")
        print(f"   URL: {CONFLUENCE_URL}/wiki/spaces/{SPACE_KEY}/pages/{result['id']}")
        return result
    else:
        print(f"❌ Failed to create page")
        return None


def update_page(page_id, title, content, version):
    """Update existing page."""
    url = f"{CONFLUENCE_URL}/wiki/rest/api/content/{page_id}"
    data = {
        "type": "page",
        "title": title,
        "body": {
            "storage": {
                "value": content,
                "representation": "storage"
            }
        },
        "version": {"number": version + 1}
    }
    
    result = make_request(url, method="PUT", data=data)
    if result:
        print(f"✅ Updated page: {title}")
        print(f"   URL: {CONFLUENCE_URL}/wiki/spaces/{SPACE_KEY}/pages/{page_id}")
        return result
    else:
        print(f"❌ Failed to update page")
        return None


def main():
    """Upload markdown to Confluence."""
    print("\n" + "="*80)
    print(f"📤 UPLOADING TO CONFLUENCE")
    print("="*80)
    
    # Read markdown file
    print(f"\n📄 Reading file: {MARKDOWN_FILE}")
    path = Path(MARKDOWN_FILE)
    if not path.exists():
        print(f"❌ File not found: {MARKDOWN_FILE}")
        return
    
    with open(path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    print(f"   ✅ Read {len(md_content)} characters")
    
    # Convert to Confluence format
    print(f"\n🔄 Converting markdown to Confluence format...")
    html_content = markdown_to_confluence(md_content)
    
    # Search for existing page
    print(f"\n🔍 Searching for page '{PAGE_TITLE}'...")
    existing_page = search_page(PAGE_TITLE)
    
    if existing_page:
        page_id = existing_page['id']
        version = existing_page['version']['number']
        print(f"   ✅ Found existing page (version {version})")
        print(f"\n📝 Updating page...")
        result = update_page(page_id, PAGE_TITLE, html_content, version)
    else:
        print(f"   ℹ️  Page not found")
        print(f"\n📝 Creating new page...")
        result = create_page(PAGE_TITLE, html_content)
    
    # Summary
    print("\n" + "="*80)
    if result:
        print("✅ SUCCESS! Page uploaded to Confluence")
    else:
        print("❌ FAILED! Could not upload page")
    print("="*80)


if __name__ == "__main__":
    main()

