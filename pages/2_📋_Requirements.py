"""Requirements Page - Epic 3: LLM Requirement Extraction."""

import streamlit as st
from datetime import datetime
from typing import List, Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.rfp import RFP
from models.requirement import Requirement, RequirementCategory, RequirementPriority
from services.requirement_extractor import RequirementExtractor, extract_requirements_from_rfp
from services.llm_client import LLMClient, create_llm_client, LLMProvider, get_available_provider_names
from src.utils.error_handler import LLMError, ValidationError, handle_errors, handle_error
from src.utils.logger import setup_logger
from src.utils.duplicate_detector import get_duplicate_requirement_groups
from utils.session import init_session_state, get_current_rfp
from components.navigation_flow import render_navigation_buttons


def get_category_icon(category: RequirementCategory) -> str:
    """Get emoji icon for a category."""
    icons = {
        RequirementCategory.TECHNICAL: "⚙️",
        RequirementCategory.FUNCTIONAL: "🎯",
        RequirementCategory.TIMELINE: "📅",
        RequirementCategory.BUDGET: "💰",
        RequirementCategory.COMPLIANCE: "✅",
    }
    return icons.get(category, "📋")

logger = setup_logger(__name__)

# Page config
st.set_page_config(
    page_title="Requirements",
    page_icon="📋",
    layout="wide"
)

# Initialize
init_session_state()


def display_requirement_table(requirements: List[Requirement], filter_category: Optional[str], filter_priority: Optional[str]):
    """Display requirements in a sortable table with filters."""
    
    # Apply filters
    filtered = requirements
    if filter_category and filter_category != "All":
        filtered = [r for r in filtered if r.category.value == filter_category]
    if filter_priority and filter_priority != "All":
        filtered = [r for r in filtered if r.priority.value == filter_priority]
    
    if not filtered:
        st.info("No requirements match the selected filters.")
        return
    
    # Create table data
    table_data = []
    for req in filtered:
        table_data.append({
            "ID": req.id[:8] + "...",
            "Category": f"{req.get_category_icon()} {req.category.value.title()}",
            "Priority": f"<span style='color: {req.get_priority_color()}; font-weight: bold;'>{req.priority.value.upper()}</span>",
            "Description": req.description[:100] + "..." if len(req.description) > 100 else req.description,
            "Confidence": f"{req.confidence:.0%}",
            "Page": req.page_number or "—",
            "Verified": "✅" if req.verified else "❌",
            "Actions": req.id  # Store ID for actions
        })
    
    # Display table
    st.markdown(f"### 📊 Requirements Table ({len(filtered)} of {len(requirements)})")
    
    # Create columns for table display
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1, 1.5, 2, 3, 1, 0.8, 0.8, 1.5])
    
    with col1:
        st.markdown("**ID**")
    with col2:
        st.markdown("**Category**")
    with col3:
        st.markdown("**Priority**")
    with col4:
        st.markdown("**Description**")
    with col5:
        st.markdown("**Confidence**")
    with col6:
        st.markdown("**Page**")
    with col7:
        st.markdown("**Verified**")
    with col8:
        st.markdown("**Actions**")
    
    st.divider()
    
    # Display each requirement
    for i, req in enumerate(filtered):
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1, 1.5, 2, 3, 1, 0.8, 0.8, 1.5])
        
        with col1:
            st.text(req.id[:8])
        with col2:
            st.text(f"{req.get_category_icon()} {req.category.value.title()}")
        with col3:
            st.markdown(f"<span style='color: {req.get_priority_color()}; font-weight: bold;'>{req.priority.value.upper()}</span>", unsafe_allow_html=True)
        with col4:
            with st.expander(req.description[:50] + "..." if len(req.description) > 50 else req.description):
                st.text(req.description)
                if req.notes:
                    st.caption(f"📝 Notes: {req.notes}")
        with col5:
            # Color-code confidence
            if req.confidence >= 0.8:
                color = "green"
            elif req.confidence >= 0.6:
                color = "orange"
            else:
                color = "red"
            st.markdown(f"<span style='color: {color};'>{req.confidence:.0%}</span>", unsafe_allow_html=True)
        with col6:
            st.text(str(req.page_number) if req.page_number else "—")
        with col7:
            st.text("✅" if req.verified else "❌")
        with col8:
            col_edit, col_del, col_verify = st.columns(3)
            with col_edit:
                if st.button("✏️", key=f"edit_{req.id}", help="Edit requirement"):
                    st.session_state[f"editing_{req.id}"] = True
                    st.rerun()
            with col_del:
                if st.button("🗑️", key=f"delete_{req.id}", help="Delete requirement"):
                    st.session_state.requirements = [r for r in st.session_state.requirements if r.id != req.id]
                    st.success(f"Deleted requirement: {req.description[:50]}...")
                    st.rerun()
            with col_verify:
                if not req.verified:
                    if st.button("✓", key=f"verify_{req.id}", help="Mark as verified"):
                        req.verified = True
                        req.updated_at = datetime.now()
                        st.success(f"Verified requirement: {req.description[:50]}...")
                        st.rerun()
                else:
                    if st.button("✗", key=f"unverify_{req.id}", help="Unverify"):
                        req.verified = False
                        req.updated_at = datetime.now()
                        st.rerun()
        
        # Edit form (shown when edit button clicked)
        if st.session_state.get(f"editing_{req.id}", False):
            with st.expander(f"✏️ Edit Requirement: {req.description[:50]}...", expanded=True):
                with st.form(f"edit_form_{req.id}"):
                    new_description = st.text_area("Description", value=req.description, height=100)
                    new_category = st.selectbox(
                        "Category",
                        options=[c.value for c in RequirementCategory],
                        index=list(RequirementCategory).index(req.category),
                        format_func=lambda x: get_category_icon(RequirementCategory(x)) + " " + RequirementCategory(x).value.title()
                    )
                    new_priority = st.selectbox(
                        "Priority",
                        options=[p.value for p in RequirementPriority],
                        index=list(RequirementPriority).index(req.priority),
                        format_func=lambda x: RequirementPriority(x).value.upper()
                    )
                    new_notes = st.text_area("Notes", value=req.notes or "", height=50)
                    
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.form_submit_button("💾 Save", type="primary"):
                            req.update(
                                description=new_description,
                                category=RequirementCategory(new_category),
                                priority=RequirementPriority(new_priority),
                                notes=new_notes
                            )
                            st.session_state[f"editing_{req.id}"] = False
                            st.success("Requirement updated!")
                            st.rerun()
                    with col_cancel:
                        if st.form_submit_button("❌ Cancel"):
                            st.session_state[f"editing_{req.id}"] = False
                            st.rerun()


def display_add_requirement_form():
    """Display form to add a new requirement manually."""
    with st.expander("➕ Add Manual Requirement", expanded=False):
        with st.form("add_requirement_form"):
            description = st.text_area("Description *", height=100, help="Enter the requirement description")
            col1, col2 = st.columns(2)
            with col1:
                category = st.selectbox(
                    "Category *",
                    options=[c.value for c in RequirementCategory],
                    format_func=lambda x: get_category_icon(RequirementCategory(x)) + " " + RequirementCategory(x).value.title()
                )
            with col2:
                priority = st.selectbox(
                    "Priority *",
                    options=[p.value for p in RequirementPriority],
                    format_func=lambda x: RequirementPriority(x).value.upper()
                )
            
            col3, col4 = st.columns(2)
            with col3:
                page_number = st.number_input("Page Number", min_value=1, value=None, step=1)
            with col4:
                confidence = st.slider("Confidence", min_value=0.0, max_value=1.0, value=0.8, step=0.1)
            
            notes = st.text_area("Notes", height=50)
            
            if st.form_submit_button("➕ Add Requirement", type="primary"):
                if not description.strip():
                    st.error("Description is required!")
                else:
                    rfp = get_current_rfp()
                    if not rfp:
                        st.error("No RFP loaded. Please upload an RFP first.")
                    else:
                        new_req = Requirement(
                            rfp_id=rfp.id,
                            description=description.strip(),
                            category=RequirementCategory(category),
                            priority=RequirementPriority(priority),
                            confidence=confidence,
                            page_number=int(page_number) if page_number else None,
                            notes=notes.strip() if notes else "",
                            verified=False
                        )
                        st.session_state.requirements.append(new_req)
                        st.success(f"Added requirement: {new_req.description[:50]}...")
                        st.rerun()


def display_extraction_controls():
    """Display controls for extracting requirements."""
    rfp = get_current_rfp()
    
    if not rfp:
        st.warning("⚠️ No RFP uploaded yet. Please upload an RFP first.")
        if st.button("📤 Go to Upload", key="btn_go_to_upload"):
            st.switch_page("pages/1_📤_Upload_RFP.py")
        return False
    
    st.info(f"📄 **Current RFP:** {rfp.title} | {rfp.total_pages} pages | {len(rfp.extracted_text.split()) if rfp.extracted_text else 0} words")
    
    # Check if already extracted
    if st.session_state.requirements:
        st.success(f"✅ {len(st.session_state.requirements)} requirements already extracted.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 Re-extract Requirements", key="btn_re_extract", help="Clear existing and extract again"):
                st.session_state.requirements = []
                st.rerun()
        with col2:
            if st.button("🔍 Check Duplicates", key="btn_check_duplicates", help="Find similar/duplicate requirements"):
                check_duplicates()
    
    # Extraction settings
    with st.expander("⚙️ Extraction Settings", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            # Get available providers
            available_providers = get_available_provider_names()
            
            if not available_providers:
                st.error("❌ **No LLM Providers Configured**")
                st.info("""
                Please configure at least one LLM provider in your `.env` file:
                
                - **Gemini**: Set `GEMINI_API_KEY=your_api_key`
                  Get key at: https://makersuite.google.com/app/apikey
                
                - **Groq**: Set `GROQ_API_KEY=your_api_key`
                  Get key at: https://console.groq.com/keys
                
                - **Ollama**: Install with `pip install ollama` and ensure Ollama is running locally
                """)
                return False
            
            llm_provider = st.selectbox(
                "LLM Provider",
                options=available_providers,
                index=0,
                key="llm_provider_extract",
                help=f"Select the LLM provider to use for extraction ({len(available_providers)} available)"
            )
        with col2:
            min_confidence = st.slider(
                "Minimum Confidence",
                min_value=0.0,
                max_value=1.0,
                value=0.3,
                step=0.1,
                key="min_confidence_extract",
                help="Only include requirements with confidence above this threshold"
            )
    
    # Extract button
    if st.button("🤖 Extract Requirements with AI", type="primary", key="btn_extract_requirements", use_container_width=True):
        if not rfp.extracted_text:
            st.error("❌ RFP has no extracted text. Please re-upload the PDF.")
            return False
        
        extract_requirements_ui(rfp, llm_provider, min_confidence)
        return True
    
    return False


@handle_errors(show_ui=True, allow_retry=True, context={"page": "requirements", "function": "extract_requirements"})
def extract_requirements_ui(rfp: RFP, llm_provider: LLMProvider, min_confidence: float):
    """Extract requirements with comprehensive error handling."""
    
    logger.info(f"Starting requirement extraction for RFP: {rfp.id}, provider: {llm_provider.value}")
    
    with st.spinner("🤖 Extracting requirements... This may take a few moments."):
        # Create LLM client
        llm_client = create_llm_client(provider=llm_provider, fallback=True)
        
        # Extract requirements
        requirements = extract_requirements_from_rfp(
            rfp=rfp,
            llm_client=llm_client,
            min_confidence=min_confidence
        )
        
        if requirements:
            st.session_state.requirements = requirements
            st.success(f"✅ Successfully extracted {len(requirements)} requirements!")
            st.balloons()
            logger.info(f"Extracted {len(requirements)} requirements successfully")
        else:
            st.warning("⚠️ No requirements found. Try lowering the confidence threshold.")
            logger.warning(f"No requirements found for RFP: {rfp.id}")
    
    return True


def display_statistics(requirements: List[Requirement]):
    """Display statistics about extracted requirements."""
    if not requirements:
        return
    
    st.markdown("### 📊 Statistics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total", len(requirements))
    
    with col2:
        verified_count = sum(1 for r in requirements if r.verified)
        st.metric("Verified", f"{verified_count}/{len(requirements)}")
    
    with col3:
        avg_confidence = sum(r.confidence for r in requirements) / len(requirements) if requirements else 0
        st.metric("Avg Confidence", f"{avg_confidence:.0%}")
    
    with col4:
        critical_count = sum(1 for r in requirements if r.priority == RequirementPriority.CRITICAL)
        st.metric("Critical", critical_count)
    
    with col5:
        high_confidence = sum(1 for r in requirements if r.confidence >= 0.8)
        st.metric("High Confidence", high_confidence)
    
    # Category breakdown
    st.markdown("#### By Category")
    category_counts = {}
    for req in requirements:
        cat = req.category.value
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    cat_cols = st.columns(len(category_counts))
    for i, (cat, count) in enumerate(category_counts.items()):
        with cat_cols[i]:
            icon = get_category_icon(RequirementCategory(cat))
            st.metric(f"{icon} {cat.title()}", count)


def main():
    """Main requirements page."""
    # Header with AI Assistant button
    col1, col2 = st.columns([5, 1])
    with col1:
        st.title("📋 Requirements Extraction")
        st.markdown("Extract and manage requirements from your RFP using AI")
    with col2:
        if st.button("💬 Ask AI", key="btn_ask_ai_req", use_container_width=True):
            st.session_state.show_ai_chat_req = True
    
    # AI Chat Dialog
    if st.session_state.get("show_ai_chat_req", False):
        with st.container():
            st.markdown("### 💬 AI Assistant")
            
            user_question = st.text_area(
                "Ask me anything about your requirements...",
                height=100,
                key="ai_question_req"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Send", key="send_ai_req", type="primary"):
                    if user_question.strip():
                        st.info(f"🤖 Question: {user_question}")
                        st.success("AI response would appear here...")
            with col2:
                if st.button("Close", key="close_ai_req"):
                    st.session_state.show_ai_chat_req = False
                    st.rerun()
            
            st.markdown("---")
    
    st.divider()
    
    # Check if RFP is loaded
    rfp = get_current_rfp()
    if not rfp:
        st.warning("⚠️ No RFP uploaded yet. Please upload an RFP first.")
        if st.button("📤 Go to Upload", key="btn_go_to_upload_main"):
            st.switch_page("pages/1_📤_Upload_RFP.py")
        return
    
    # Display extraction controls
    if display_extraction_controls():
        st.divider()
        
        # Display statistics if requirements exist
        if st.session_state.requirements:
            display_statistics(st.session_state.requirements)
            st.divider()
        
        # Filters
        st.markdown("### 🔍 Filters")
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_category = st.selectbox(
                "Filter by Category",
                options=["All"] + [c.value for c in RequirementCategory],
                format_func=lambda x: "All" if x == "All" else get_category_icon(RequirementCategory(x)) + " " + RequirementCategory(x).value.title(),
                key="filter_category_requirements"
            )
        with col2:
            filter_priority = st.selectbox(
                "Filter by Priority",
                options=["All"] + [p.value for p in RequirementPriority],
                format_func=lambda x: "All" if x == "All" else RequirementPriority(x).value.upper(),
                key="filter_priority_requirements"
            )
        with col3:
            show_only_unverified = st.checkbox("Show only unverified", value=False, key="show_only_unverified")
        
        st.divider()
        
        # Display requirements table
        requirements_to_show = st.session_state.requirements
        if show_only_unverified:
            requirements_to_show = [r for r in requirements_to_show if not r.verified]
        
        display_requirement_table(requirements_to_show, filter_category if filter_category != "All" else None, filter_priority if filter_priority != "All" else None)
        
        st.divider()
        
        # Add manual requirement
        display_add_requirement_form()
        
        # Import/Export options
        if st.session_state.requirements:
            st.divider()
            st.markdown("### 💾 Import / Export Requirements")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### 📤 Import Requirements")
                uploaded_file = st.file_uploader(
                    "Upload JSON file with requirements",
                    type=['json'],
                    key="import_requirements_file",
                    help="Upload a previously exported requirements JSON file"
                )
                
                if uploaded_file is not None:
                    try:
                        import json
                        requirements_data = json.load(uploaded_file)
                        
                        # Validate and convert to Requirement objects
                        imported_requirements = []
                        for req_dict in requirements_data:
                            try:
                                req = Requirement.from_dict(req_dict)
                                imported_requirements.append(req)
                            except Exception as e:
                                logger.warning(f"Failed to import requirement: {e}")
                                continue
                        
                        if imported_requirements:
                            # Merge with existing requirements (avoid duplicates)
                            existing_ids = {r.id for r in st.session_state.requirements}
                            new_requirements = [r for r in imported_requirements if r.id not in existing_ids]
                            
                            if new_requirements:
                                st.session_state.requirements.extend(new_requirements)
                                st.success(f"✅ Imported {len(new_requirements)} requirements from file")
                                st.rerun()
                            else:
                                st.warning("⚠️ All requirements from file already exist")
                        else:
                            st.error("❌ No valid requirements found in file")
                            
                    except json.JSONDecodeError:
                        st.error("❌ Invalid JSON file format")
                    except Exception as e:
                        logger.error(f"Error importing requirements: {e}", exc_info=True)
                        st.error(f"❌ Error importing requirements: {str(e)}")
            
            with col2:
                st.markdown("#### 📥 Export to JSON")
                if st.button("📥 Export to JSON", key="btn_export_json", use_container_width=True):
                    import json
                    requirements_dict = [r.to_dict() for r in st.session_state.requirements]
                    st.download_button(
                        label="Download JSON",
                        data=json.dumps(requirements_dict, indent=2),
                        file_name=f"requirements_{rfp.id[:8]}.json",
                        mime="application/json"
                    )
            
            with col3:
                st.markdown("#### 📄 Export to CSV")
                if st.button("📄 Export to CSV", key="btn_export_csv", use_container_width=True):
                    import pandas as pd
                    df = pd.DataFrame([r.to_dict() for r in st.session_state.requirements])
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"requirements_{rfp.id[:8]}.csv",
                        mime="text/csv"
                    )
    
    # Navigation buttons
    render_navigation_buttons('requirements')


def check_duplicates():
    """Check for duplicate requirements using semantic similarity."""
    requirements = st.session_state.requirements
    
    if not requirements or len(requirements) < 2:
        st.info("Need at least 2 requirements to check for duplicates")
        return
    
    with st.spinner("🔍 Checking for duplicates..."):
        # Convert to dict format for detector
        req_dicts = [
            {"description": req.description, "id": req.id}
            for req in requirements
        ]
        
        # Find duplicates
        duplicate_groups = get_duplicate_requirement_groups(
            req_dicts,
            threshold=0.80
        )
        
        if not duplicate_groups:
            st.success("✅ No duplicates found!")
            return
        
        st.warning(f"⚠️ Found {len(duplicate_groups)} groups of similar requirements")
        
        for idx, group in enumerate(duplicate_groups):
            st.markdown(f"#### Group {idx + 1} (Similarity > 80%)")
            
            group_reqs = [requirements[i] for i in group]
            
            for req in group_reqs:
                with st.expander(f"📋 {req.description[:80]}...", expanded=True):
                    st.markdown(f"**Full Description:** {req.description}")
                    st.markdown(f"**Category:** {req.category.value} | **Priority:** {req.priority.value} | **Confidence:** {req.confidence:.0%}")
                    if req.page_number:
                        st.markdown(f"**Page:** {req.page_number}")
            
            # Merge options
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"🗑️ Keep First, Remove Others", key=f"merge_group_{idx}"):
                    # Keep first, remove others
                    ids_to_remove = [requirements[i].id for i in list(group)[1:]]
                    st.session_state.requirements = [
                        r for r in requirements if r.id not in ids_to_remove
                    ]
                    st.success(f"✅ Removed {len(ids_to_remove)} duplicate(s)")
                    st.rerun()
            
            with col2:
                if st.button(f"↻ Keep All", key=f"keep_all_{idx}"):
                    st.info("Kept all requirements in this group")
            
            st.markdown("---")


if __name__ == "__main__":
    main()
    # Chat functionality available via Ask AI button
