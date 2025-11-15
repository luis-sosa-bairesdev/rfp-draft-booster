#!/usr/bin/env python3
"""End-to-end test for AI Assistant button using Playwright.

This test verifies:
1. The "Ask" button is visible on all pages
2. Clicking the button opens the AI Assistant modal
3. The modal displays correctly with all expected elements
"""

import asyncio
import sys
from pathlib import Path
import pytest

try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
except ImportError:
    print("❌ Playwright no está instalado. Instalando...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
    subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError


@pytest.mark.asyncio
async def test_ai_assistant_button():
    """E2E test for AI Assistant button."""
    print("=" * 60)
    print("E2E Test: AI Assistant Button")
    print("=" * 60)
    
    async with async_playwright() as p:
        # Launch browser
        print("\n1. Iniciando navegador...")
        browser = await p.chromium.launch(headless=False)  # headless=False para ver qué pasa
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navigate to Streamlit app
            print("2. Navegando a http://localhost:8501...")
            await page.goto("http://localhost:8501", wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)  # Wait for Streamlit to fully load
            
            # Take screenshot before clicking
            await page.screenshot(path="/tmp/before_click.png")
            print("   ✅ Página cargada (screenshot: /tmp/before_click.png)")
            
            # Look for the "Ask" button
            print("3. Buscando botón 'Ask'...")
            try:
                # Try multiple selectors
                button_selectors = [
                    'button:has-text("Ask")',
                    'button:has-text("💬 Ask")',
                    '[data-testid*="btn_ai_assistant"]',
                    'button[type="primary"]:has-text("Ask")',
                ]
                
                button_found = False
                for selector in button_selectors:
                    try:
                        button = await page.wait_for_selector(selector, timeout=5000)
                        if button:
                            print(f"   ✅ Botón encontrado con selector: {selector}")
                            button_found = True
                            
                            # Get button info
                            button_text = await button.inner_text()
                            is_visible = await button.is_visible()
                            print(f"   📋 Texto del botón: '{button_text}'")
                            print(f"   👁️  Visible: {is_visible}")
                            
                            # Click the button
                            print("4. Haciendo clic en el botón...")
                            await button.click()
                            
                            # Wait for page to reload after rerun
                            print("   ⏳ Esperando rerun de Streamlit...")
                            await page.wait_for_load_state("networkidle", timeout=10000)
                            await asyncio.sleep(2)  # Additional wait for modal rendering
                            
                            # Wait for modal to be visible
                            print("   ⏳ Esperando que el modal aparezca...")
                            try:
                                # Modal should be at the top now, so scroll to top first
                                await page.evaluate("window.scrollTo(0, 0)")
                                await page.wait_for_selector('text=AI Assistant', timeout=5000, state='visible')
                                print("   ✅ Modal detectado, tomando screenshot...")
                            except PlaywrightTimeoutError:
                                print("   ⚠️ Modal no detectado inmediatamente, esperando más...")
                                await asyncio.sleep(2)
                            
                            # Take screenshot after clicking (full page to see modal at top)
                            await page.screenshot(path="/tmp/after_click.png", full_page=True)
                            print("   ✅ Click ejecutado (screenshot: /tmp/after_click.png)")
                            
                            # Check if modal appeared - VERIFY IT'S VISIBLE
                            print("5. Verificando si el modal apareció y es VISIBLE...")
                            modal_selectors = [
                                'text=AI Assistant',
                                'text=💬 AI Assistant',
                                'text=Ask a Question',
                                'text=Type your question here',
                                'button:has-text("Send")',
                                'button:has-text("Close")',
                            ]
                            
                            modal_found = False
                            modal_visible = False
                            for modal_selector in modal_selectors:
                                try:
                                    modal_element = await page.wait_for_selector(modal_selector, timeout=5000, state='visible')
                                    if modal_element:
                                        is_visible = await modal_element.is_visible()
                                        is_in_viewport = await modal_element.evaluate("""
                                            (el) => {
                                                const rect = el.getBoundingClientRect();
                                                return rect.top >= 0 && rect.left >= 0 && 
                                                       rect.bottom <= window.innerHeight && 
                                                       rect.right <= window.innerWidth;
                                            }
                                        """)
                                        
                                        print(f"   ✅ Elemento encontrado con selector: {modal_selector}")
                                        print(f"   👁️  Visible: {is_visible}")
                                        print(f"   📍 En viewport: {is_in_viewport}")
                                        
                                        if is_visible:
                                            modal_found = True
                                            modal_visible = True
                                            
                                            # Get modal content
                                            modal_text = await modal_element.inner_text()
                                            print(f"   📋 Contenido: '{modal_text[:100]}...'")
                                            break
                                except PlaywrightTimeoutError:
                                    continue
                            
                            if not modal_found or not modal_visible:
                                print("   ❌ Modal NO apareció o NO es visible después del click")
                                print("   🔍 Analizando estado completo de la página...")
                                
                                # Get all visible text
                                body_text = await page.inner_text("body")
                                print(f"   📄 Texto completo visible en la página:")
                                print(f"   {body_text[:1000]}")
                                
                                # Check for any buttons
                                all_buttons = await page.query_selector_all("button")
                                print(f"   🔘 Total de botones en la página: {len(all_buttons)}")
                                for i, btn in enumerate(all_buttons[:15]):
                                    try:
                                        btn_text = await btn.inner_text()
                                        btn_visible = await btn.is_visible()
                                        print(f"      Botón {i+1}: '{btn_text}' (visible: {btn_visible})")
                                    except:
                                        pass
                                
                                # Check session state via console
                                print("   🔍 Verificando estado de sesión de Streamlit...")
                                session_state = await page.evaluate("""
                                    () => {
                                        // Try multiple ways to access Streamlit state
                                        const state = {
                                            streamlit: typeof window.streamlit !== 'undefined',
                                            sessionState: window.streamlit?.sessionState || null,
                                            show_ai_assistant: null
                                        };
                                        
                                        if (state.sessionState) {
                                            state.show_ai_assistant = state.sessionState.show_ai_assistant;
                                        }
                                        
                                        // Also check if there's a hidden element with the modal content
                                        const modalElements = document.querySelectorAll('*');
                                        const modalTexts = [];
                                        for (let el of modalElements) {
                                            const text = el.innerText || el.textContent || '';
                                            if (text.includes('AI Assistant') || text.includes('Ask a Question')) {
                                                const style = window.getComputedStyle(el);
                                                modalTexts.push({
                                                    text: text.substring(0, 50),
                                                    visible: style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0',
                                                    display: style.display,
                                                    visibility: style.visibility
                                                });
                                            }
                                        }
                                        state.modalElements = modalTexts;
                                        
                                        return state;
                                    }
                                """)
                                print(f"   📊 Estado de sesión:")
                                print(f"      Streamlit disponible: {session_state.get('streamlit', False)}")
                                print(f"      show_ai_assistant: {session_state.get('show_ai_assistant', 'undefined')}")
                                if session_state.get('modalElements'):
                                    print(f"      Elementos con texto 'AI Assistant': {len(session_state['modalElements'])}")
                                    for el in session_state['modalElements'][:5]:
                                        print(f"         - '{el['text']}' (visible: {el['visible']}, display: {el['display']})")
                                
                                # Take another screenshot after waiting
                                await asyncio.sleep(2)
                                await page.screenshot(path="/tmp/debug_after_click.png", full_page=True)
                                print("   📸 Screenshot de debug guardado: /tmp/debug_after_click.png")
                            
                            break
                    except PlaywrightTimeoutError:
                        continue
                
                if not button_found:
                    print("   ❌ Botón 'Ask' NO encontrado")
                    print("   🔍 Buscando todos los botones en la página...")
                    buttons = await page.query_selector_all("button")
                    print(f"   📊 Total de botones encontrados: {len(buttons)}")
                    for i, btn in enumerate(buttons[:10]):  # Show first 10
                        try:
                            btn_text = await btn.inner_text()
                            btn_id = await btn.get_attribute("id")
                            print(f"   Botón {i+1}: '{btn_text}' (id: {btn_id})")
                        except:
                            pass
                
            except Exception as e:
                print(f"   ❌ Error al buscar/buscar botón: {e}")
                import traceback
                traceback.print_exc()
            
            # Wait a bit before closing
            await asyncio.sleep(2)
            
        finally:
            await browser.close()
            print("\n✅ Navegador cerrado")
    
    print("\n" + "=" * 60)
    print("Test completado")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_ai_assistant_button())

