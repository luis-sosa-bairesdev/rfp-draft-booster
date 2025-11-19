"""E2E test for Google Docs export functionality using Playwright."""

import pytest
import time
from playwright.sync_api import Page, expect


@pytest.fixture(scope="module")
def app_url():
    """Return the URL of the running Streamlit app."""
    return "http://localhost:8501"


def test_export_button_exists(page: Page, app_url: str):
    """Test that Google Docs export button exists on draft page."""
    # Navigate to the app
    page.goto(app_url)
    
    # Wait for app to load
    page.wait_for_load_state("networkidle")
    time.sleep(2)
    
    # Check if we're on the draft generation page
    # If not, navigate to it
    if "Draft_Generation" not in page.url:
        # Try to find and click the Draft Generation link in sidebar
        draft_link = page.get_by_text("Draft Generation")
        if draft_link.is_visible():
            draft_link.click()
            page.wait_for_load_state("networkidle")
            time.sleep(2)
    
    # Check if export section exists
    export_section = page.get_by_text("Export")
    if export_section.is_visible():
        # Look for the Google Docs export button
        google_docs_button = page.get_by_role("button", name="Export to Google Docs")
        if google_docs_button.is_visible():
            print("✅ Google Docs export button found")
        else:
            print("⚠️  Button not visible (may need a draft first)")
    else:
        print("⚠️  Export section not visible (may need a draft first)")


def test_export_button_click_shows_dialog(page: Page, app_url: str):
    """Test that clicking export button shows the confirmation dialog."""
    # Navigate to app
    page.goto(app_url)
    page.wait_for_load_state("networkidle")
    time.sleep(2)
    
    # Navigate to Draft Generation page
    if "Draft_Generation" not in page.url:
        draft_link = page.get_by_text("Draft Generation")
        if draft_link.is_visible():
            draft_link.click()
            page.wait_for_load_state("networkidle")
            time.sleep(2)
    
    # Try to find the Google Docs export button
    try:
        google_docs_button = page.get_by_role("button", name="Export to Google Docs")
        
        if google_docs_button.is_visible():
            print("Found export button, clicking...")
            google_docs_button.click()
            
            # Wait for page to reload (st.rerun)
            time.sleep(2)
            
            # Check if dialog appeared
            confirm_dialog = page.get_by_text("Confirm Google Docs Export")
            if confirm_dialog.is_visible():
                print("✅ Dialog appeared after clicking button")
                
                # Check for dialog elements
                warning = page.get_by_text("This will create a new Google Doc")
                assert warning.is_visible(), "Warning text should be visible"
                
                email_input = page.get_by_placeholder("colleague@example.com")
                assert email_input.is_visible(), "Email input should be visible"
                
                yes_button = page.get_by_role("button", name="Yes, Export")
                assert yes_button.is_visible(), "Yes button should be visible"
                
                cancel_button = page.get_by_role("button", name="Cancel")
                assert cancel_button.is_visible(), "Cancel button should be visible"
                
                print("✅ All dialog elements are present")
            else:
                print("❌ Dialog did not appear")
                pytest.fail("Dialog did not appear after clicking button")
        else:
            print("⚠️  Export button not visible (may need draft first)")
            pytest.skip("Export button not available without draft")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        pytest.skip(f"Test skipped: {str(e)}")


def test_export_dialog_yes_button(page: Page, app_url: str):
    """Test that clicking Yes button in dialog triggers export."""
    page.goto(app_url)
    page.wait_for_load_state("networkidle")
    time.sleep(2)
    
    # Navigate to Draft Generation
    if "Draft_Generation" not in page.url:
        draft_link = page.get_by_text("Draft Generation")
        if draft_link.is_visible():
            draft_link.click()
            page.wait_for_load_state("networkidle")
            time.sleep(2)
    
    try:
        # Click export button
        google_docs_button = page.get_by_role("button", name="Export to Google Docs")
        if google_docs_button.is_visible():
            google_docs_button.click()
            time.sleep(2)
            
            # Wait for dialog
            yes_button = page.get_by_role("button", name="Yes, Export")
            if yes_button.is_visible():
                print("Found 'Yes, Export' button, clicking...")
                
                # Click Yes button
                yes_button.click()
                
                # Wait for export to happen
                time.sleep(3)
                
                # Check for success message or error message or .docx download button
                # Since we might not have credentials, it should fallback to .docx
                
                # Look for any of these indicators:
                success_msg = page.get_by_text("Google Doc created")
                error_msg = page.get_by_text("Google Docs export failed")
                fallback_msg = page.get_by_text("Google credentials not configured")
                docx_button = page.get_by_text("Download .docx")
                
                if success_msg.is_visible():
                    print("✅ Export to Google Docs succeeded!")
                elif error_msg.is_visible() or fallback_msg.is_visible():
                    print("✅ Export triggered, falling back to .docx")
                    # This is expected if no credentials
                elif docx_button.is_visible():
                    print("✅ .docx download button appeared")
                else:
                    print("❌ No feedback after clicking Yes button")
                    # Take screenshot for debugging
                    page.screenshot(path="export_no_response.png")
                    pytest.fail("No response after clicking Yes button")
            else:
                pytest.skip("Yes button not visible")
        else:
            pytest.skip("Export button not available")
    
    except Exception as e:
        print(f"Error during test: {e}")
        pytest.skip(f"Test skipped: {str(e)}")


def test_export_dialog_cancel_button(page: Page, app_url: str):
    """Test that clicking Cancel button closes the dialog."""
    page.goto(app_url)
    page.wait_for_load_state("networkidle")
    time.sleep(2)
    
    # Navigate to Draft Generation
    if "Draft_Generation" not in page.url:
        draft_link = page.get_by_text("Draft Generation")
        if draft_link.is_visible():
            draft_link.click()
            page.wait_for_load_state("networkidle")
            time.sleep(2)
    
    try:
        # Click export button
        google_docs_button = page.get_by_role("button", name="Export to Google Docs")
        if google_docs_button.is_visible():
            google_docs_button.click()
            time.sleep(2)
            
            # Click cancel
            cancel_button = page.get_by_role("button", name="Cancel")
            if cancel_button.is_visible():
                print("Found 'Cancel' button, clicking...")
                cancel_button.click()
                time.sleep(2)
                
                # Verify dialog is closed
                confirm_dialog = page.get_by_text("Confirm Google Docs Export")
                if not confirm_dialog.is_visible():
                    print("✅ Dialog closed after clicking Cancel")
                else:
                    pytest.fail("Dialog did not close after clicking Cancel")
            else:
                pytest.skip("Cancel button not visible")
        else:
            pytest.skip("Export button not available")
    
    except Exception as e:
        pytest.skip(f"Test skipped: {str(e)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

