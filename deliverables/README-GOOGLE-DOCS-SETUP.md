# Google Docs Export Setup Guide

## Overview

This guide explains how to configure Google Docs export for RFP Draft Booster (Epic 7). The integration uses a Google Cloud Service Account to authenticate and create documents in Google Drive.

---

## ⚠️ Security Notice

**CRITICAL:** Service account credentials contain private keys that give full access to your Google Cloud project. NEVER commit these credentials to Git!

Files to protect:
- `.streamlit/secrets.toml` - Contains credentials in TOML format
- `.streamlit/google_credentials.json` - Raw credential JSON
- Any file with `private_key` in it

These are already added to `.gitignore`.

---

## Prerequisites

- Google Cloud Project (free tier is sufficient)
- Service Account with proper permissions
- Google Docs API enabled
- Google Drive API enabled

---

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Select a project** → **New Project**
3. Enter project name: `rfp-draft-booster` (or your choice)
4. Click **Create**
5. Wait for project creation (~30 seconds)

---

## Step 2: Enable Required APIs

### Enable Google Docs API

1. In Cloud Console, go to **APIs & Services** → **Library**
2. Search for **Google Docs API**
3. Click **Enable**

### Enable Google Drive API

1. In the same Library, search for **Google Drive API**
2. Click **Enable**

---

## Step 3: Create Service Account

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **Service Account**
3. Fill in details:
   - **Service account name:** `rfp-export-sa`
   - **Service account ID:** `rfp-export-sa` (auto-filled)
   - **Description:** "Service account for RFP Draft Booster Google Docs export"
4. Click **Create and Continue**
5. **Grant this service account access to project:**
   - Role: **Editor** (or custom role with `docs.documents.create`, `drive.files.create`)
6. Click **Continue** → **Done**

---

## Step 4: Create Service Account Key

1. In **Credentials** page, find your service account
2. Click the service account email
3. Go to **Keys** tab
4. Click **Add Key** → **Create new key**
5. Select **JSON** format
6. Click **Create**
7. A JSON file will download automatically (e.g., `steadfast-karma-478121-a3-9f1c15822e71.json`)

**IMPORTANT:** This is the only time you can download this key. Store it securely!

---

## Step 5: Configure Streamlit Secrets

### Option A: Using TOML (Recommended)

1. Ensure `.streamlit/` directory exists:
   ```bash
   mkdir -p .streamlit
   ```

2. Copy the example template:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

3. Open `.streamlit/secrets.toml` and replace placeholders with your service account values:
   ```toml
   [GOOGLE_CREDENTIALS]
   type = "service_account"
   project_id = "steadfast-karma-478121-a3"  # Your project ID
   private_key_id = "9f1c15822..."            # From JSON
   private_key = """-----BEGIN PRIVATE KEY-----
   MIIEvwIBADANBgk...
   -----END PRIVATE KEY-----"""               # Full private key
   client_email = "rfp-export-sa@steadfast-karma-478121-a3.iam.gserviceaccount.com"
   client_id = "117073452280071897604"
   # ... other fields
   ```

4. **Verify `.gitignore`** includes:
   ```
   .streamlit/secrets.toml
   .streamlit/google_credentials.json
   ```

### Option B: Using JSON File

1. Move the downloaded JSON file to `.streamlit/`:
   ```bash
   mv ~/Downloads/steadfast-karma-*.json .streamlit/google_credentials.json
   ```

2. In your code, load credentials from file:
   ```python
   import json
   from pathlib import Path
   
   creds_path = Path(__file__).parent.parent / ".streamlit" / "google_credentials.json"
   with open(creds_path, 'r') as f:
       credentials_json = f.read()
   ```

---

## Step 6: Verify Setup

### Test Authentication

Run this test script to verify credentials work:

```python
# tests/test_google_auth.py
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build

def test_google_auth():
    """Test Google Cloud authentication."""
    try:
        # Load credentials from secrets
        creds_dict = st.secrets["GOOGLE_CREDENTIALS"]
        credentials = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=[
                'https://www.googleapis.com/auth/documents',
                'https://www.googleapis.com/auth/drive'
            ]
        )
        
        # Test Docs API
        docs_service = build('docs', 'v1', credentials=credentials)
        print("✅ Google Docs API: Connected")
        
        # Test Drive API
        drive_service = build('drive', 'v3', credentials=credentials)
        print("✅ Google Drive API: Connected")
        
        return True
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

if __name__ == "__main__":
    test_google_auth()
```

Run:
```bash
streamlit run tests/test_google_auth.py
```

Expected output:
```
✅ Google Docs API: Connected
✅ Google Drive API: Connected
```

---

## Step 7: Grant Permissions (Optional)

If you want the service account to create documents in a specific Google Drive folder:

1. Open [Google Drive](https://drive.google.com/)
2. Create a folder: `RFP Drafts`
3. Right-click folder → **Share**
4. Add the service account email: `rfp-export-sa@steadfast-karma-478121-a3.iam.gserviceaccount.com`
5. Give **Editor** permission
6. Click **Send**

Now all exported docs will be accessible from this folder.

---

## Troubleshooting

### Error: "The caller does not have permission"

**Cause:** Service account doesn't have proper roles or APIs not enabled

**Fix:**
1. Check APIs are enabled (Step 2)
2. Grant **Editor** role to service account (Step 3)
3. Wait 1-2 minutes for permissions to propagate

### Error: "Invalid credentials"

**Cause:** Credentials malformed or expired

**Fix:**
1. Verify `private_key` includes full BEGIN/END markers
2. Check for extra newlines or spaces in TOML
3. Regenerate service account key if needed (Step 4)

### Error: "API quota exceeded"

**Cause:** Too many API calls (free tier limit: 300 calls/min)

**Fix:**
1. Wait 1 minute
2. Implement rate limiting in code
3. Upgrade to paid tier if needed

### Documents not visible in Drive

**Cause:** Documents created in service account's Drive (not yours)

**Fix:**
1. Share folder with service account (Step 7)
2. Or use Drive API to list files:
   ```python
   results = drive_service.files().list(pageSize=10).execute()
   ```

---

## Current Configuration

**Project:** steadfast-karma-478121-a3  
**Service Account:** rfp-export-sa@steadfast-karma-478121-a3.iam.gserviceaccount.com  
**Status:** ✅ Configured and ready

---

## Security Best Practices

1. ✅ **Never commit credentials to Git**
   - Use `.gitignore` for `.streamlit/secrets.toml`
   
2. ✅ **Rotate keys periodically**
   - Every 90 days recommended
   - Delete old keys after rotation

3. ✅ **Use least privilege**
   - Grant only required permissions
   - Consider custom roles instead of Editor

4. ✅ **Monitor usage**
   - Check Cloud Console for API calls
   - Set up billing alerts

5. ✅ **Use different accounts for dev/prod**
   - Dev: Limited scope, test project
   - Prod: Full permissions, production project

---

## Next Steps

1. ✅ Credentials configured
2. ⏳ Implement `GoogleDocsExporter` (Epic 7)
3. ⏳ Add export button to Draft Generation page
4. ⏳ Test with sample drafts
5. ⏳ Deploy to production

---

## Resources

- [Google Cloud Console](https://console.cloud.google.com/)
- [Google Docs API Documentation](https://developers.google.com/docs/api)
- [Google Drive API Documentation](https://developers.google.com/drive/api)
- [Service Account Best Practices](https://cloud.google.com/iam/docs/best-practices-service-accounts)
- [Streamlit Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)

---

**Last Updated:** 2025-11-13  
**Maintainer:** RFP Draft Booster Team

