"""
E2E tests for Requirements page CRUD operations.
Tests for Epic 9 regression - verify edit/delete/verify buttons work correctly.
"""

import pytest
from playwright.sync_api import Page, expect


def test_requirements_page_preserves_data_on_rerun(page: Page):
    """Test that requirements data persists when clicking edit/verify buttons."""
    page.goto("http://localhost:8501/Requirements")
    
    # Wait for page to load
    page.wait_for_selector("div[data-testid='stAppViewContainer']", timeout=10000)
    
    # Check if "No RFP loaded" message appears
    no_rfp_message = page.locator("text=/No RFP loaded/i")
    
    if no_rfp_message.is_visible():
        # This is expected - no RFP loaded, so we can't test CRUD
        # This test should be skipped or pass
        pytest.skip("No RFP loaded in current session - CRUD test not applicable")
    
    # If we have requirements, verify they persist after clicking buttons
    # Look for any edit button (using emoji)
    edit_buttons = page.locator("button:has-text('✏️')")
    
    if edit_buttons.count() > 0:
        # Count requirements before clicking
        initial_req_count = edit_buttons.count()
        
        # Click first edit button
        edit_buttons.first.click()
        
        # Wait for page to rerun
        page.wait_for_timeout(1000)
        
        # Count requirements after clicking
        after_req_count = page.locator("button:has-text('✏️')").count()
        
        # Requirements should still be there
        assert after_req_count == initial_req_count, f"Requirements disappeared after clicking edit! Before: {initial_req_count}, After: {after_req_count}"
    else:
        pytest.skip("No requirements in current session - CRUD test not applicable")


def test_requirements_page_loads_without_errors(page: Page):
    """Basic smoke test - verify Requirements page loads without errors."""
    page.goto("http://localhost:8501/Requirements")
    
    # Wait for page to load
    page.wait_for_selector("div[data-testid='stAppViewContainer']", timeout=10000)
    
    # Verify title is visible
    expect(page.locator("text=/Requirements Extraction/i")).to_be_visible()
    
    # Verify AI Assistant button is in sidebar (use first() to avoid strict mode violation)
    expect(page.locator("button:has-text('Ask AI Assistant')").first).to_be_visible()

