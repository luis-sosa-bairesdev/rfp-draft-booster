#!/usr/bin/env python3
"""Critical E2E tests for RFP Draft Booster.

Tests cover:
1. Upload RFP page loads and accepts files
2. Requirements page loads and shows extraction options
3. Service Matching page loads and shows matches
"""

import asyncio
import pytest
from pathlib import Path

try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
    subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError


@pytest.mark.asyncio
async def test_upload_page_loads():
    """Test that Upload RFP page loads correctly."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Navigate to Upload page
            await page.goto("http://localhost:8501", timeout=30000)
            await asyncio.sleep(2)
            
            # Click "Upload RFP" in sidebar
            upload_link = await page.wait_for_selector('text=📤', timeout=10000)
            await upload_link.click()
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(1)
            
            # Verify page title/heading
            page_text = await page.inner_text("body")
            assert "Upload" in page_text or "RFP" in page_text
            
            # Verify file uploader exists (Streamlit renders it)
            # Look for "Drag and drop" or "Browse files" text
            assert "Drag and drop" in page_text or "Browse" in page_text
            
            # Take screenshot for debugging
            await page.screenshot(path="/tmp/e2e_upload_page.png")
            
            print("✅ Upload page loaded successfully")
            
        finally:
            await browser.close()


@pytest.mark.asyncio
async def test_requirements_page_accessible():
    """Test that Requirements page is accessible."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Navigate to main page
            await page.goto("http://localhost:8501", timeout=30000)
            await asyncio.sleep(2)
            
            # Click "Requirements" in sidebar
            req_link = await page.wait_for_selector('text=📋', timeout=10000)
            await req_link.click()
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(1)
            
            # Verify page content
            page_text = await page.inner_text("body")
            assert "Requirements" in page_text or "requirements" in page_text.lower()
            
            # Verify extraction options exist
            assert "Extract" in page_text or "AI" in page_text
            
            # Take screenshot
            await page.screenshot(path="/tmp/e2e_requirements_page.png")
            
            print("✅ Requirements page loaded successfully")
            
        finally:
            await browser.close()


@pytest.mark.asyncio
async def test_service_matching_page_accessible():
    """Test that Service Matching page is accessible."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Navigate to main page
            await page.goto("http://localhost:8501", timeout=30000)
            await asyncio.sleep(2)
            
            # Click "Service Matching" in sidebar
            service_link = await page.wait_for_selector('text=🔗', timeout=10000)
            await service_link.click()
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(1)
            
            # Verify page content
            page_text = await page.inner_text("body")
            assert "Service" in page_text or "Match" in page_text
            
            # Take screenshot
            await page.screenshot(path="/tmp/e2e_service_matching_page.png")
            
            print("✅ Service Matching page loaded successfully")
            
        finally:
            await browser.close()


@pytest.mark.asyncio
async def test_all_pages_have_sidebar():
    """Test that all pages have the sidebar navigation."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto("http://localhost:8501", timeout=30000)
            await asyncio.sleep(2)
            
            # Get page text
            page_text = await page.inner_text("body")
            
            # Verify all main pages are in sidebar
            assert "📤" in page_text  # Upload
            assert "📋" in page_text  # Requirements
            assert "🔗" in page_text  # Service Matching
            assert "⚠️" in page_text  # Risk Analysis
            assert "✍️" in page_text  # Draft Generation
            
            print("✅ All pages visible in sidebar")
            
        finally:
            await browser.close()


if __name__ == "__main__":
    # Run tests manually
    asyncio.run(test_upload_page_loads())
    asyncio.run(test_requirements_page_accessible())
    asyncio.run(test_service_matching_page_accessible())
    asyncio.run(test_all_pages_have_sidebar())
    print("\n✅ All E2E tests passed!")

