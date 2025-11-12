"""Upload Epic 3 documentation to Confluence."""

import requests
import base64
from pathlib import Path

CONFLUENCE_URL = 'https://luis-sosa-bairesdev.atlassian.net'
CONFLUENCE_EMAIL = 'luis.sosa@bairesdev.com'
CONFLUENCE_TOKEN = 'ATATT3xFfGF05S_SCHS3O_OqM3rJcN9nM9-g3AorAXYCLvHDC2bvMGJhSgU9pCvIPNFPAbAmxJMU3UtO9R3ed-ccV7PInG7h51OTK9JTdS3ERz2Tdbrljl6E2yQDwVKtwsia8PI_UHC6F4wFE_P_D955n6fKNFiZBrCF4K3PNoonm6nxXKLNEJI=0B414822'

# Create auth header
auth_string = f"{CONFLUENCE_EMAIL}:{CONFLUENCE_TOKEN}"
auth_bytes = auth_string.encode('ascii')
auth_b64 = base64.b64encode(auth_bytes).decode('ascii')

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': f'Basic {auth_b64}'
}

SPACE_KEY = '~712020bfc89abf8f5841728f3bd48d6a60043a'


def read_markdown_file(file_path):
    """Read markdown file content."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


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
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text[:500]}")
        return None


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
    
    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text[:500]}")
        return None


def search_page(space_key, title):
    """Search for a page by title."""
    url = f'{CONFLUENCE_URL}/wiki/rest/api/content'
    params = {
        'spaceKey': space_key,
        'title': title,
        'expand': 'version'
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        results = response.json().get('results', [])
        if results:
            return results[0]
    return None


def convert_markdown_to_confluence_storage(markdown_content):
    """Convert markdown to Confluence storage format (simplified)."""
    # For now, we'll use markdown format and let Confluence convert it
    # Confluence supports markdown in storage format with some conversion
    html_content = markdown_content
    
    # Basic markdown to HTML conversion (simplified)
    # In production, you'd use a proper markdown parser
    html_content = html_content.replace('\n\n', '<br/><br/>')
    html_content = html_content.replace('\n', '<br/>')
    
    # Convert headers
    import re
    html_content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
    
    return html_content


def main():
    """Upload Epic 3 documentation to Confluence."""
    print('=' * 80)
    print('Uploading Epic 3 Documentation to Confluence')
    print('=' * 80)
    
    # Read markdown file
    md_file = Path(__file__).parent / 'confluence-epic-03.md'
    if not md_file.exists():
        print(f'❌ File not found: {md_file}')
        return
    
    print(f'\n1. Reading markdown file...')
    markdown_content = read_markdown_file(md_file)
    print(f'   ✅ Read {len(markdown_content)} characters')
    
    # Check if page exists
    page_title = 'Epic 3: LLM Requirement Extraction'
    print(f'\n2. Checking if page exists...')
    existing_page = search_page(SPACE_KEY, page_title)
    
    if existing_page:
        print(f'   ✅ Page exists: {existing_page["id"]}')
        print(f'   📝 Updating page...')
        
        # Convert markdown to Confluence format
        confluence_content = convert_markdown_to_confluence_storage(markdown_content)
        
        # Update page
        version = existing_page['version']['number']
        result = update_confluence_page(
            existing_page['id'],
            page_title,
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
        result = create_confluence_page(SPACE_KEY, page_title, confluence_content)
        
        if result:
            page_url = f"{CONFLUENCE_URL}/wiki{result['_links']['webui']}"
            print(f'   ✅ Page created successfully!')
            print(f'   🔗 URL: {page_url}')
        else:
            print(f'   ❌ Failed to create page')
    
    print('\n' + '=' * 80)
    print('✅ Documentation upload complete!')
    print('=' * 80)


if __name__ == '__main__':
    main()

