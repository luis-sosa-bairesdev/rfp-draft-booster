"""Draft Generation Page - Epic 5: Draft Generation & AI Assistant."""

import logging
import streamlit as st
from datetime import datetime
from typing import List, Optional
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.rfp import RFP
from models.draft import Draft, DraftStatus, GenerationMethod
from models.requirement import Requirement
from models.risk import Risk
from services.draft_generator import DraftGenerator
from services.llm_client import create_llm_client, LLMProvider, get_available_provider_names
from exceptions import LLMGenerationError, LLMConnectionError
from utils.session import init_session_state, get_current_rfp
from components.ai_assistant import render_ai_assistant_button, render_ai_assistant_modal

logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Draft Generation",
    page_icon="✍️",
    layout="wide"
)

# Initialize
init_session_state()

# Initialize draft in session state if not present
if "draft" not in st.session_state:
    st.session_state.draft: Optional[Draft] = None
# show_ai_assistant is initialized in init_session_state()


def check_prerequisites() -> tuple[bool, Optional[str]]:
    """Check if prerequisites are met for draft generation."""
    rfp = get_current_rfp()
    requirements = st.session_state.get("requirements", [])
    risks = st.session_state.get("risks", [])
    
    if not rfp:
        return False, "Please upload an RFP first."
    
    if not requirements:
        return False, "Please extract requirements first."
    
    # Check for unacknowledged critical risks
    critical_risks = [r for r in risks if r.severity.value == "critical" and not r.acknowledged]
    if critical_risks:
        return False, f"Please acknowledge {len(critical_risks)} critical risk(s) before generating draft."
    
    return True, None


def display_draft_sections(draft: Draft):
    """Display draft sections with regeneration capability."""
    st.markdown("### 📄 Draft Sections")
    
    for section in sorted(draft.sections, key=lambda s: s.order):
        with st.expander(f"📝 {section.title} ({section.word_count} words)", expanded=section.order == 1):
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(section.content)
            
            with col2:
                if st.button("🔄 Regenerate", key=f"regenerate_{section.id}", use_container_width=True):
                    st.session_state[f"regenerating_{section.section_type}"] = True
                    st.rerun()
                
                if section.user_edited:
                    st.caption("✏️ Edited")


def main():
    """Main page function."""
    # Render AI Assistant modal FIRST if open (so it's visible at top)
    if st.session_state.get("show_ai_assistant", False):
        render_ai_assistant_modal(key_suffix="draft", page_context="draft")
        st.markdown("---")
    
    st.title("✍️ Draft Generation")
    
    # AI Assistant button in header
    col1, col2 = st.columns([5, 1])
    with col2:
        render_ai_assistant_button(key_suffix="draft")
    
    # Check prerequisites
    can_generate, error_msg = check_prerequisites()
    
    if not can_generate:
        st.warning(f"⚠️ {error_msg}")
        st.info("💡 **Next Steps:**\n1. Upload an RFP\n2. Extract requirements\n3. Review and acknowledge critical risks")
        return
    
    # Get current data
    rfp = get_current_rfp()
    requirements = st.session_state.get("requirements", [])
    risks = st.session_state.get("risks", [])
    service_matches = st.session_state.get("service_matches", {})
    
    # Draft generation controls
    st.markdown("---")
    st.markdown("### ⚙️ Generation Settings")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tone = st.selectbox(
            "Tone",
            options=["professional", "friendly", "formal", "conversational"],
            index=0,
            key="draft_tone"
        )
    
    with col2:
        audience = st.selectbox(
            "Audience",
            options=["enterprise", "SMB", "government", "non-profit"],
            index=0,
            key="draft_audience"
        )
    
    with col3:
        word_count = st.slider(
            "Target Word Count",
            min_value=500,
            max_value=10000,
            value=2000,
            step=100,
            key="draft_word_count"
        )
    
    # Custom instructions
    instructions = st.text_area(
        "Custom Instructions (Optional)",
        placeholder="e.g., Focus on security features, emphasize our 99.9% uptime guarantee, mention our SOC 2 certification...",
        key="draft_instructions",
        height=100
    )
    
    # LLM Provider selection
    available_providers = get_available_provider_names()
    
    if not available_providers:
        st.error("❌ **No LLM Providers Configured**")
        st.info("""
        Draft generation requires a configured LLM provider.
        
        Please configure at least one in your `.env` file:
        
        - **Gemini**: Set `GEMINI_API_KEY=your_api_key`
          Get key at: https://makersuite.google.com/app/apikey
        
        - **Groq**: Set `GROQ_API_KEY=your_api_key`
          Get key at: https://console.groq.com/keys
        
        - **Ollama**: Install with `pip install ollama` and ensure Ollama is running locally
        """)
        generate_btn = False
        regenerate_btn = False
        llm_provider = None
    else:
        llm_provider = st.selectbox(
            "LLM Provider",
            options=available_providers,
            index=0,
            key="draft_llm_provider",
            help=f"Select LLM provider for draft generation ({len(available_providers)} available)"
        )
    
    # Generate button
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        generate_btn = st.button(
            "🚀 Generate Draft",
            key="btn_generate_draft",
            use_container_width=True,
            type="primary"
        )
    
    with col2:
        if st.session_state.get("draft"):
            regenerate_btn = st.button(
                "🔄 Regenerate",
                key="btn_regenerate_draft",
                use_container_width=True
            )
        else:
            regenerate_btn = False
    
    # Handle generation
    if generate_btn or regenerate_btn:
        if not llm_provider or not available_providers:
            st.error("Please configure an LLM provider to generate drafts")
            return
        
        with st.spinner("🤖 Generating draft... This may take 1-2 minutes."):
            try:
                # Create LLM client
                llm_client = create_llm_client(provider=LLMProvider(llm_provider), fallback=True)
                
                # Create generator
                generator = DraftGenerator(llm_client=llm_client, temperature=0.7)
                
                # Generate draft
                draft = generator.generate_draft(
                    rfp=rfp,
                    requirements=requirements,
                    risks=risks,
                    service_matches=list(service_matches.values()) if service_matches else [],
                    instructions=instructions,
                    tone=tone,
                    audience=audience,
                    word_count=word_count
                )
                
                # Store in session state
                st.session_state.draft = draft
                
                st.success(f"✅ Draft generated successfully! ({draft.word_count} words, {draft.section_count} sections)")
                st.rerun()
                
            except ValueError as e:
                st.error(f"❌ {str(e)}")
            except Exception as e:
                logger.error(f"Error generating draft: {e}")
                st.error(f"❌ Error generating draft: {str(e)}")
    
    # Handle section regeneration
    for section_type in ["executive_summary", "approach", "services", "timeline", "pricing", "risk_mitigation"]:
        if st.session_state.get(f"regenerating_{section_type}", False):
            draft = st.session_state.get("draft")
            if draft:
                if not llm_provider or not available_providers:
                    st.error("Please configure an LLM provider to regenerate sections")
                    st.session_state[f"regenerating_{section_type}"] = False
                    return
                
                with st.spinner(f"🔄 Regenerating {section_type.replace('_', ' ').title()}..."):
                    try:
                        llm_client = create_llm_client(provider=LLMProvider(llm_provider), fallback=True)
                        generator = DraftGenerator(llm_client=llm_client)
                        
                        generator.regenerate_section(
                            draft=draft,
                            section_type=section_type,
                            rfp=rfp,
                            requirements=requirements,
                            risks=risks,
                            service_matches=list(service_matches.values()) if service_matches else [],
                            instructions=instructions,
                            tone=tone,
                            audience=audience
                        )
                        
                        st.session_state[f"regenerating_{section_type}"] = False
                        st.success(f"✅ Section regenerated!")
                        st.rerun()
                    except Exception as e:
                        logger.error(f"Error regenerating section: {e}")
                        st.error(f"❌ Error: {str(e)}")
                        st.session_state[f"regenerating_{section_type}"] = False
    
    # Display draft if exists
    draft = st.session_state.get("draft")
    if draft:
        st.markdown("---")
        
        # Draft info
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Word Count", draft.word_count)
        with col2:
            st.metric("Sections", draft.section_count)
        with col3:
            st.metric("Completeness", f"{draft.completeness_score * 100:.0f}%" if draft.completeness_score else "N/A")
        with col4:
            st.metric("Status", draft.status.value.title())
        
        # Draft editing
        st.markdown("### ✏️ Edit Draft")
        
        edited_content = st.text_area(
            "Draft Content (Markdown)",
            value=draft.content,
            height=400,
            key="draft_editor"
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("💾 Save Changes", key="btn_save_draft"):
                draft.update_content(edited_content)
                st.session_state.draft = draft
                st.success("✅ Draft saved!")
                st.rerun()
        
        with col2:
            if st.button("👁️ Preview", key="btn_preview_draft"):
                st.session_state.show_preview = not st.session_state.get("show_preview", False)
                st.rerun()
        
        # Preview
        if st.session_state.get("show_preview", False):
            st.markdown("---")
            st.markdown("### 👁️ Preview")
            st.markdown(edited_content)
        
        # Sections view
        st.markdown("---")
        display_draft_sections(draft)
        
        # Export options
        st.markdown("---")
        st.markdown("### 📤 Export")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 Export to Markdown", key="btn_export_md"):
                st.download_button(
                    label="⬇️ Download",
                    data=draft.content,
                    file_name=f"draft_{rfp.id if rfp else 'unknown'}.md",
                    mime="text/markdown",
                    key="download_md"
                )
        
        with col2:
            draft_json = json.dumps(draft.to_dict(), indent=2, default=str)
            if st.button("📦 Export to JSON", key="btn_export_json"):
                st.download_button(
                    label="⬇️ Download",
                    data=draft_json,
                    file_name=f"draft_{rfp.id if rfp else 'unknown'}.json",
                    mime="application/json",
                    key="download_json"
                )
    


if __name__ == "__main__":
    main()

