"""
E2E tests for ROI Calculator page using Playwright.

Tests basic navigation and page structure.
Note: Streamlit multi-page apps are challenging for E2E testing due to
dynamic reloading and iframe structure. These tests verify core functionality.
"""

import pytest


@pytest.fixture(scope="module")
def browser_context_args(browser_context_args):
    """Configure browser context for ROI Calculator tests."""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 1024}
    }


def test_roi_calculator_page_exists(page):
    """Test that ROI Calculator page can be accessed directly."""
    # Navigate directly to ROI Calculator page
    page.goto("http://localhost:8501/ROI_Calculator")
    page.wait_for_load_state("networkidle")
    
    # Wait for Streamlit to fully load
    page.wait_for_timeout(3000)
    
    # Verify main heading exists
    heading = page.locator("h1")
    assert heading.count() > 0


def test_roi_calculator_has_buttons(page):
    """Test that ROI Calculator page has interactive buttons."""
    # Navigate to ROI Calculator page
    page.goto("http://localhost:8501/ROI_Calculator")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)
    
    # Verify buttons exist
    buttons = page.locator("button")
    assert buttons.count() > 0

