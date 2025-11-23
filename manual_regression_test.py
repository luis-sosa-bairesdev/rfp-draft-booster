#!/usr/bin/env python3
"""Manual regression test for Epic 9 - Test ALL pages systematically."""

import asyncio
from playwright.async_api import async_playwright
import sys

async def test_all_pages():
    """Test all pages load without Python errors."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Show browser
        page = await browser.new_page()
        
        pages_to_test = [
            ("📤 Upload RFP", "Upload_RFP"),
            ("📋 Requirements", "Requirements"),
            ("🔗 Service Matching", "Service_Matching"),
            ("⚠️ Risk Analysis", "Risk_Analysis"),
            ("✍️ Draft Generation", "Draft_Generation"),
            ("💰 ROI Calculator", "ROI_Calculator"),
        ]
        
        errors = []
        
        try:
            print("🔍 Starting comprehensive regression test...\n")
            
            # Navigate to main page
            await page.goto("http://localhost:8501", timeout=30000)
            await asyncio.sleep(3)
            
            for icon, page_name in pages_to_test:
                print(f"Testing: {icon} {page_name}")
                
                try:
                    # Navigate directly by URL (sidebar can be flaky)
                    await page.goto(f"http://localhost:8501/{page_name}", timeout=15000)
                    await page.wait_for_load_state("networkidle")
                    await asyncio.sleep(3)
                    
                    # Check for Python errors in page
                    page_text = await page.inner_text("body")
                    
                    if "Traceback" in page_text or "AttributeError" in page_text or "Error" in page_text:
                        # Check if it's a real error or just UI text
                        if "AttributeError:" in page_text or "IndentationError:" in page_text or "SyntaxError:" in page_text:
                            error_msg = f"❌ PYTHON ERROR on {page_name}"
                            print(f"  {error_msg}")
                            errors.append(error_msg)
                            
                            # Take screenshot
                            await page.screenshot(path=f"/tmp/error_{page_name}.png")
                            
                            # Extract error details
                            lines = page_text.split('\n')
                            for i, line in enumerate(lines):
                                if "Error:" in line:
                                    print(f"  Error details: {line}")
                                    if i + 1 < len(lines):
                                        print(f"  {lines[i+1]}")
                            continue
                    
                    # Check for critical UI elements
                    if "No RFP loaded" not in page_text and page_name != "Upload_RFP" and page_name != "ROI_Calculator":
                        # These pages should have RFP info or error
                        if "Current RFP" not in page_text and "Upload" not in page_text:
                            warning = f"⚠️ WARNING: {page_name} might not be displaying correctly"
                            print(f"  {warning}")
                    
                    print(f"  ✅ {page_name} loaded successfully")
                    
                except Exception as e:
                    error_msg = f"❌ EXCEPTION on {page_name}: {str(e)}"
                    print(f"  {error_msg}")
                    errors.append(error_msg)
                    await page.screenshot(path=f"/tmp/error_{page_name}.png")
            
            print("\n" + "="*60)
            if errors:
                print(f"❌ FOUND {len(errors)} ERRORS:")
                for error in errors:
                    print(f"  - {error}")
                print("\nScreenshots saved to /tmp/error_*.png")
                return False
            else:
                print("✅ ALL PAGES LOADED WITHOUT ERRORS!")
                return True
                
        finally:
            await browser.close()

if __name__ == "__main__":
    result = asyncio.run(test_all_pages())
    sys.exit(0 if result else 1)

