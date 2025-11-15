#!/usr/bin/env python3
"""Upload Epic 6 documentation to Confluence."""

import os
import json
import urllib.request
import urllib.error
import base64
from pathlib import Path

# Confluence configuration
CONFLUENCE_URL = "https://luis-sosa-bairesdev.atlassian.net"
CONFLUENCE_EMAIL = "luis.sosa@bairesdev.com"
CONFLUENCE_API_TOKEN = "ATATT3xFfGF05S_SCHS3O_OqM3rJcN9nM9-g3AorAXYCLvHDC2bvMGJhSgU9pCvIPNFPAbAmxJMU3UtO9R3ed-ccV7PInG7h51OTK9JTdS3ERz2Tdbrljl6E2yQDwVKtwsia8PI_UHC6F4wFE_P_D955n6fKNFiZBrCF4K3PNoonm6nxXKLNEJI=0B414822"
SPACE_KEY = "~712020bfc89abf8f5841728f3bd48d6a60043a"  # Luis's personal space


def markdown_to_confluence_storage(md_text):
    """Convert markdown to Confluence storage format (simplified)."""
    lines = md_text.split('\n')
    result = []
    
    in_code_block = False
    code_lang = ""
    
    for line in lines:
        # Code blocks
        if line.startswith('```'):
            if in_code_block:
                result.append('</ac:plain-text-body></ac:structured-macro>')
                in_code_block = False
            else:
                code_lang = line[3:].strip() or 'none'
                result.append(f'<ac:structured-macro ac:name="code"><ac:parameter ac:name="language">{code_lang}</ac:parameter><ac:plain-text-body><![CDATA[')
                in_code_block = True
            continue
        
        if in_code_block:
            result.append(line)
            continue
        
        # Headings
        if line.startswith('# '):
            result.append(f'<h1>{line[2:]}</h1>')
        elif line.startswith('## '):
            result.append(f'<h2>{line[3:]}</h2>')
        elif line.startswith('### '):
            result.append(f'<h3>{line[4:]}</h3>')
        elif line.startswith('#### '):
            result.append(f'<h4>{line[5:]}</h4>')
        # Lists
        elif line.startswith('- '):
            result.append(f'<li>{line[2:]}</li>')
        elif line.startswith('* '):
            result.append(f'<li>{line[2:]}</li>')
        # Bold
        elif '**' in line:
            line = line.replace('**', '<strong>',  1).replace('**', '</strong>', 1)
            result.append(f'<p>{line}</p>')
        # Italic
        elif '*' in line:
            line = line.replace('*', '<em>', 1).replace('*', '</em>', 1)
            result.append(f'<p>{line}</p>')
        # Empty line
        elif not line.strip():
            result.append('<p></p>')
        # Normal paragraph
        else:
            result.append(f'<p>{line}</p>')
    
    return '\n'.join(result)


def make_confluence_request(endpoint, method="GET", data=None):
    """Make authenticated request to Confluence API."""
    url = f"{CONFLUENCE_URL}/wiki/rest/api/{endpoint}"
    
    # Create auth header
    auth_string = f"{CONFLUENCE_EMAIL}:{CONFLUENCE_API_TOKEN}"
    auth_bytes = auth_string.encode('ascii')
    base64_auth = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        "Authorization": f"Basic {base64_auth}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Create request
    if data:
        data = json.dumps(data).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status in [200, 201, 204]:
                try:
                    return json.loads(response.read().decode('utf-8'))
                except:
                    return {"success": True}
            else:
                print(f"Warning: Unexpected status {response.status}")
                return None
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"HTTP Error {e.code}: {error_body}")
        return None


def search_page(title):
    """Search for existing Confluence page by title."""
    endpoint = f"content?title={urllib.parse.quote(title)}&spaceKey={SPACE_KEY}&expand=version"
    result = make_confluence_request(endpoint)
    
    if result and 'results' in result and len(result['results']) > 0:
        return result['results'][0]
    return None


def create_page(title, content, parent_id=None):
    """Create a new Confluence page."""
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
    
    if parent_id:
        data["ancestors"] = [{"id": parent_id}]
    
    result = make_confluence_request("content", method="POST", data=data)
    
    if result:
        print(f"✅ Created page: {title}")
        print(f"   URL: {CONFLUENCE_URL}/spaces/{SPACE_KEY}/pages/{result['id']}")
        return result
    else:
        print(f"❌ Failed to create page: {title}")
        return None


def update_page(page_id, title, content, version):
    """Update existing Confluence page."""
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
    
    result = make_confluence_request(f"content/{page_id}", method="PUT", data=data)
    
    if result:
        print(f"✅ Updated page: {title}")
        print(f"   URL: {CONFLUENCE_URL}/spaces/{SPACE_KEY}/pages/{page_id}")
        return result
    else:
        print(f"❌ Failed to update page: {title}")
        return None


def upload_document(file_path, title):
    """Upload a markdown document to Confluence."""
    print(f"\n{'='*60}")
    print(f"Processing: {title}")
    print(f"Source: {file_path}")
    print(f"{'='*60}")
    
    # Read markdown file
    path = Path(file_path)
    if not path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    with open(path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert to Confluence storage format
    print("  → Converting markdown to Confluence format...")
    html_content = markdown_to_confluence_storage(md_content)
    
    # Search for existing page
    print(f"  → Searching for existing page '{title}'...")
    existing_page = search_page(title)
    
    if existing_page:
        # Update existing page
        page_id = existing_page['id']
        version = existing_page['version']['number']
        print(f"  → Found existing page (version {version}), updating...")
        result = update_page(page_id, title, html_content, version)
    else:
        # Create new page
        print("  → Page not found, creating new page...")
        result = create_page(title, html_content)
    
    return result is not None


def main():
    """Main function to upload Epic 6 documentation."""
    print("\n" + "="*80)
    print("CONFLUENCE UPLOAD - Epic 6 Documentation")
    print("="*80)
    
    # Documents to upload
    documents = [
        {
            "file": "deliverables/epic-06-service-matching.md",
            "title": "Epic 6: Service Matching - Technical Documentation"
        },
        {
            "file": "deliverables/SERVICE-MATCHING-USER-GUIDE.md",
            "title": "Service Matching - User Guide"
        },
        {
            "file": "deliverables/README-GOOGLE-DOCS-SETUP.md",
            "title": "Google Docs Export - Setup Guide"
        }
    ]
    
    # Upload each document
    success_count = 0
    for doc in documents:
        if upload_document(doc["file"], doc["title"]):
            success_count += 1
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\n✅ Documents Uploaded: {success_count}/{len(documents)}")
    
    if success_count == len(documents):
        print("\n🎉 All documentation uploaded successfully!")
    else:
        print(f"\n⚠️  {len(documents) - success_count} document(s) could not be uploaded")
    
    print("\n" + "="*80)
    print("✨ CONFLUENCE UPLOAD COMPLETE!")
    print("="*80)
    print(f"\nView your pages at: {CONFLUENCE_URL}/wiki/spaces/{SPACE_KEY}")


if __name__ == "__main__":
    main()

