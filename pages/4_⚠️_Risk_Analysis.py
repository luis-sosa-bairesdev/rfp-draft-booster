"""Risk Analysis Page - Epic 4: Risk Detection & Analysis."""

import streamlit as st
from datetime import datetime
from typing import List, Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.rfp import RFP
from models.risk import Risk, RiskCategory, RiskSeverity, get_category_display_names, get_severity_display_names
from services.risk_detector import RiskDetector, detect_risks_from_rfp
from services.llm_client import LLMClient, create_llm_client, LLMProvider, get_available_provider_names
from src.utils.error_handler import LLMError, ValidationError, handle_errors, handle_error
from src.utils.logger import setup_logger
from utils.session import init_session_state, get_current_rfp
from components.navigation_flow import render_navigation_buttons
from components.ai_assistant import render_ai_assistant_button, render_ai_assistant_modal


def get_category_icon(category: RiskCategory) -> str:
    """Get emoji icon for a category."""
    icons = {
        RiskCategory.LEGAL: "⚖️",
        RiskCategory.FINANCIAL: "💰",
        RiskCategory.TIMELINE: "⏰",
        RiskCategory.TECHNICAL: "🔧",
        RiskCategory.COMPLIANCE: "📋",
    }
    return icons.get(category, "⚠️")


logger = setup_logger(__name__)

# Page config
st.set_page_config(
    page_title="Risk Analysis",
    page_icon="⚠️",
    layout="wide"
)

# Initialize
init_session_state()

# Initialize risks in session state if not present
if "risks" not in st.session_state:
    st.session_state.risks = []
# show_ai_assistant is initialized in init_session_state()


def display_risk_table(risks: List[Risk], filter_category: Optional[str], filter_severity: Optional[str], show_acknowledged: bool):
    """Display risks in a sortable table with filters."""
    
    # Apply filters
    filtered = risks
    if filter_category and filter_category != "All":
        filtered = [r for r in filtered if r.category.value == filter_category]
    if filter_severity and filter_severity != "All":
        filtered = [r for r in filtered if r.severity.value == filter_severity]
    if not show_acknowledged:
        filtered = [r for r in filtered if not r.acknowledged]
    
    if not filtered:
        st.info("No risks match the selected filters.")
        return
    
    # Display table header
    st.markdown(f"### 📊 Risks Table ({len(filtered)} of {len(risks)})")
    
    # Create columns for table display
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1, 1.5, 2, 3, 1, 0.8, 0.8, 1.5])
    
    with col1:
        st.markdown("**ID**")
    with col2:
        st.markdown("**Category**")
    with col3:
        st.markdown("**Severity**")
    with col4:
        st.markdown("**Clause Text**")
    with col5:
        st.markdown("**Confidence**")
    with col6:
        st.markdown("**Page**")
    with col7:
        st.markdown("**Status**")
    with col8:
        st.markdown("**Actions**")
    
    st.divider()
    
    # Display each risk
    for i, risk in enumerate(filtered):
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1, 1.5, 2, 3, 1, 0.8, 0.8, 1.5])
        
        with col1:
            st.text(risk.id[:8] + "...")
        
        with col2:
            st.markdown(f"{get_category_icon(risk.category)} {risk.category.value.title()}")
        
        with col3:
            severity_color = risk.get_severity_color()
            st.markdown(
                f"<span style='color: {severity_color}; font-weight: bold;'>{risk.severity.value.upper()}</span>",
                unsafe_allow_html=True
            )
        
        with col4:
            clause_preview = risk.clause_text[:100] + "..." if len(risk.clause_text) > 100 else risk.clause_text
            with st.expander(clause_preview):
                st.text(risk.clause_text)
                if risk.recommendation:
                    st.markdown("**💡 Recommendation:**")
                    st.info(risk.recommendation)
                if risk.alternative_language:
                    st.markdown("**✏️ Alternative Language:**")
                    st.code(risk.alternative_language, language=None)
        
        with col5:
            confidence_label = risk.get_confidence_label()
            confidence_color = "#4CAF50" if risk.confidence >= 0.75 else "#FFBB00" if risk.confidence >= 0.5 else "#FF4444"
            st.markdown(
                f"<span style='color: {confidence_color};'>{risk.confidence:.0%}</span>",
                unsafe_allow_html=True
            )
            st.caption(confidence_label)
        
        with col6:
            st.text(risk.page_number or "—")
        
        with col7:
            if risk.acknowledged:
                st.success("✅ Acknowledged")
            else:
                st.warning("⚠️ Pending")
        
        with col8:
            if not risk.acknowledged:
                ack_key = f"ack_{risk.id}"
                if ack_key not in st.session_state:
                    st.session_state[ack_key] = False
                
                if st.button("Acknowledge", key=f"btn_{risk.id}", type="primary"):
                    st.session_state[ack_key] = True
                    st.rerun()
                
                if st.session_state.get(ack_key, False):
                    notes = st.text_input(
                        "Add notes (optional):",
                        key=f"notes_{risk.id}",
                        placeholder="How will you address this risk?"
                    )
                    col_confirm, col_cancel = st.columns(2)
                    with col_confirm:
                        if st.button("Confirm", key=f"confirm_{risk.id}"):
                            risk.acknowledge(notes)
                            st.session_state.risks = [r for r in st.session_state.risks if r.id != risk.id] + [risk]
                            st.session_state[ack_key] = False
                            st.rerun()
                    with col_cancel:
                        if st.button("Cancel", key=f"cancel_{risk.id}"):
                            st.session_state[ack_key] = False
                            st.rerun()
            else:
                st.info("✅ Acknowledged")
                if risk.acknowledgment_notes:
                    with st.expander("📝 Notes"):
                        st.text(risk.acknowledgment_notes)
        
        st.divider()


def display_statistics(risks: List[Risk]):
    """Display risk statistics dashboard."""
    if not risks:
        return
    
    st.markdown("### 📈 Risk Statistics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Risks", len(risks))
    
    with col2:
        critical_count = len([r for r in risks if r.severity == RiskSeverity.CRITICAL])
        st.metric("Critical", critical_count, delta=None, delta_color="inverse")
    
    with col3:
        acknowledged_count = len([r for r in risks if r.acknowledged])
        st.metric("Acknowledged", acknowledged_count, f"{acknowledged_count}/{len(risks)}")
    
    with col4:
        avg_confidence = sum(r.confidence for r in risks) / len(risks) if risks else 0
        st.metric("Avg Confidence", f"{avg_confidence:.0%}")
    
    with col5:
        high_confidence_count = len([r for r in risks if r.confidence >= 0.75])
        st.metric("High Confidence", high_confidence_count)
    
    # Category breakdown
    st.markdown("#### Category Breakdown")
    category_counts = {}
    for category in RiskCategory:
        category_counts[category.value] = len([r for r in risks if r.category == category])
    
    col1, col2, col3, col4, col5 = st.columns(5)
    categories = list(RiskCategory)
    for i, category in enumerate(categories):
        with [col1, col2, col3, col4, col5][i]:
            count = category_counts[category.value]
            st.metric(
                f"{get_category_icon(category)} {category.value.title()}",
                count
            )


def main():
    """Main page content."""
    # Render AI Assistant modal FIRST if open (so it's visible at top)
    if st.session_state.get("show_ai_assistant", False):
        render_ai_assistant_modal(key_suffix="risks", page_context="risks")
        st.markdown("---")
    
    # Header with AI Assistant button
    col1, col2 = st.columns([5, 1])
    with col1:
        st.title("⚠️ Risk Detection & Analysis")
        st.markdown("Identify and analyze potentially problematic clauses in RFPs")
    with col2:
        render_ai_assistant_button(key_suffix="risks")
    
    # Get current RFP
    rfp = get_current_rfp()
    
    if not rfp:
        st.warning("⚠️ No RFP uploaded yet. Please upload an RFP first.")
        if st.button("📤 Go to Upload", key="btn_go_to_upload"):
            st.switch_page("pages/1_📤_Upload_RFP.py")
        return
    
    if not rfp.extracted_text:
        st.error("❌ RFP text not extracted. Please process the RFP first.")
        if st.button("📋 Go to Requirements", key="btn_go_to_requirements"):
            st.switch_page("pages/2_📋_Requirements.py")
        return
    
    st.success(f"✅ Current RFP: **{rfp.title}**")
    st.info(f"📄 {rfp.total_pages} pages ready for risk analysis")
    
    # Detection controls
    st.markdown("---")
    st.markdown("### 🔍 Risk Detection")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        use_patterns = st.checkbox("Use Pattern Detection", value=True, key="use_patterns", help="Detect common risk patterns using regex")
        use_ai = st.checkbox("Use AI Detection", value=True, key="use_ai", help="Detect complex risks using LLM analysis")
    
    with col2:
        min_confidence = st.slider(
            "Minimum Confidence",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
            step=0.1,
            key="min_confidence",
            help="Only show risks above this confidence threshold"
        )
    
    with col3:
        # Get available providers
        available_providers = get_available_provider_names()
        
        if not available_providers:
            st.warning("⚠️ **No LLM Providers Configured**")
            st.info("""
            AI-powered risk detection requires a configured LLM provider.
            
            Please configure at least one in your `.env` file:
            - **Gemini**: `GEMINI_API_KEY=your_key` (https://makersuite.google.com/app/apikey)
            - **Groq**: `GROQ_API_KEY=your_key` (https://console.groq.com/keys)
            - **Ollama**: Install with `pip install ollama` and run locally
            """)
            st.info("💡 You can still use pattern-based detection (toggle above)")
            llm_provider = None
        else:
            llm_provider = st.selectbox(
                "LLM Provider",
                options=available_providers,
                index=0,
                key="llm_provider",
                help=f"Select LLM provider for AI detection ({len(available_providers)} available)"
            )
    
    # Detection button
    if st.button("🚀 Detect Risks", type="primary", key="btn_detect_risks", use_container_width=True):
        if not use_patterns and not use_ai:
            st.error("Please enable at least one detection method (Pattern or AI)")
            return
        
        detect_risks_ui(rfp, use_ai, use_patterns, llm_provider, min_confidence)


@handle_errors(show_ui=True, allow_retry=True, context={"page": "risk_analysis", "function": "detect_risks"})
def detect_risks_ui(rfp: RFP, use_ai: bool, use_patterns: bool, llm_provider: str, min_confidence: float):
    """Detect risks with comprehensive error handling."""
    
    logger.info(f"Starting risk detection for RFP: {rfp.id}, AI: {use_ai}, Patterns: {use_patterns}")
    
    with st.spinner("Detecting risks... This may take a moment."):
        llm_client = None
        if use_ai:
            if not llm_provider:
                raise ValidationError("LLM provider required for AI detection", field="llm_provider")
            llm_client = create_llm_client(provider=LLMProvider(llm_provider), fallback=True)
        
        risks = detect_risks_from_rfp(
            rfp,
            llm_client=llm_client,
            min_confidence=min_confidence,
            use_patterns=use_patterns,
            use_ai=use_ai and llm_client is not None
        )
        
        st.session_state.risks = risks
        st.success(f"✅ Detected {len(risks)} risks")
        logger.info(f"Detected {len(risks)} risks successfully")
        st.rerun()
    
    # Display existing risks
    if st.session_state.risks:
        st.markdown("---")
        
        # Action buttons row
        col1, col2, col3 = st.columns([2, 2, 2])
        with col1:
            if st.button("➕ Add Manual Risk", key="btn_add_manual_risk", use_container_width=True):
                st.session_state.show_add_risk_modal = True
                st.rerun()
        
        # Statistics
        display_statistics(st.session_state.risks)
        
        st.markdown("---")
        
        # Manual Risk Addition Modal
        if st.session_state.get("show_add_risk_modal", False):
            render_add_risk_modal()
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            category_filter = st.selectbox(
                "Filter by Category",
                options=["All"] + list(get_category_display_names().values()),
                key="filter_category"
            )
            category_filter_value = None
            if category_filter != "All":
                # Find the key for this display name
                for key, value in get_category_display_names().items():
                    if value == category_filter:
                        category_filter_value = key
                        break
        
        with col2:
            severity_filter = st.selectbox(
                "Filter by Severity",
                options=["All"] + list(get_severity_display_names().values()),
                key="filter_severity"
            )
            severity_filter_value = None
            if severity_filter != "All":
                # Find the key for this display name
                for key, value in get_severity_display_names().items():
                    if value == severity_filter:
                        severity_filter_value = key
                        break
        
        with col3:
            show_acknowledged = st.checkbox("Show Acknowledged", value=True, key="show_acknowledged")
        
        # Display table
        display_risk_table(
            st.session_state.risks,
            category_filter_value,
            severity_filter_value,
            show_acknowledged
        )
        
        # Import/Export options
        st.markdown("---")
        st.markdown("### 📥 Import / Export Risks")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 📤 Import Risks")
            uploaded_file = st.file_uploader(
                "Upload JSON file with risks",
                type=['json'],
                key="import_risks_file",
                help="Upload a previously exported risks JSON file"
            )
            
            if uploaded_file is not None:
                try:
                    import json
                    risks_data = json.load(uploaded_file)
                    
                    # Validate and convert to Risk objects
                    imported_risks = []
                    for risk_dict in risks_data:
                        try:
                            risk = Risk.from_dict(risk_dict)
                            imported_risks.append(risk)
                        except Exception as e:
                            logger.warning(f"Failed to import risk: {e}")
                            continue
                    
                    if imported_risks:
                        # Merge with existing risks (avoid duplicates)
                        existing_ids = {r.id for r in st.session_state.risks}
                        new_risks = [r for r in imported_risks if r.id not in existing_ids]
                        
                        if new_risks:
                            st.session_state.risks.extend(new_risks)
                            st.success(f"✅ Imported {len(new_risks)} risks from file")
                            st.rerun()
                        else:
                            st.warning("⚠️ All risks from file already exist")
                    else:
                        st.error("❌ No valid risks found in file")
                        
                except json.JSONDecodeError:
                    st.error("❌ Invalid JSON file format")
                except Exception as e:
                    logger.error(f"Error importing risks: {e}", exc_info=True)
                    st.error(f"❌ Error importing risks: {str(e)}")
        
        with col2:
            st.markdown("#### 📄 Export to JSON")
            if st.button("📄 Export to JSON", key="btn_export_json", use_container_width=True):
                import json
                risks_json = json.dumps([r.to_dict() for r in st.session_state.risks], indent=2)
                st.download_button(
                    label="Download JSON",
                    data=risks_json,
                    file_name=f"risks_{rfp.id[:8]}.json",
                    mime="application/json"
                )
        
        with col3:
            st.markdown("#### 📊 Export to CSV")
            if st.button("📊 Export to CSV", key="btn_export_csv", use_container_width=True):
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow([
                    "ID", "Category", "Severity", "Clause Text", "Confidence",
                    "Page", "Recommendation", "Alternative Language", "Acknowledged", "Notes"
                ])
                
                for risk in st.session_state.risks:
                    writer.writerow([
                        risk.id,
                        risk.category.value,
                        risk.severity.value,
                        risk.clause_text,
                        risk.confidence,
                        risk.page_number or "",
                        risk.recommendation,
                        risk.alternative_language,
                        risk.acknowledged,
                        risk.acknowledgment_notes
                    ])
                
                st.download_button(
                    label="Download CSV",
                    data=output.getvalue(),
                    file_name=f"risks_{rfp.id[:8]}.csv",
                    mime="text/csv"
                )
    else:
        st.info("👆 Click 'Detect Risks' to start analyzing the RFP for problematic clauses.")
    
    # Navigation buttons
    render_navigation_buttons('risk')


def render_add_risk_modal():
    """Render modal for manually adding a risk."""
    st.markdown("### ➕ Add Manual Risk")
    st.markdown("Add a risk that you've identified manually.")
    
    with st.form("add_risk_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            category = st.selectbox(
                "Risk Category",
                options=[cat.value for cat in RiskCategory],
                format_func=lambda x: get_category_display_names().get(RiskCategory(x), x),
                key="manual_risk_category"
            )
            
            severity = st.selectbox(
                "Severity Level",
                options=[sev.value for sev in RiskSeverity],
                format_func=lambda x: get_severity_display_names().get(RiskSeverity(x), x),
                key="manual_risk_severity"
            )
        
        with col2:
            likelihood = st.selectbox(
                "Likelihood",
                options=["HIGH", "MEDIUM", "LOW"],
                index=1,
                key="manual_risk_likelihood"
            )
            
            page_number = st.number_input(
                "Page Number (optional)",
                min_value=1,
                value=1,
                key="manual_risk_page"
            )
        
        clause_text = st.text_area(
            "Risk Description / Clause Text",
            placeholder="Describe the risk or paste the problematic clause...",
            height=100,
            key="manual_risk_clause"
        )
        
        impact = st.text_area(
            "Impact",
            placeholder="What is the potential impact of this risk?",
            height=80,
            key="manual_risk_impact"
        )
        
        recommendation = st.text_area(
            "Recommendation",
            placeholder="What should be done to mitigate this risk?",
            height=80,
            key="manual_risk_recommendation"
        )
        
        alternative_language = st.text_area(
            "Alternative Language (optional)",
            placeholder="Suggested alternative wording for the clause...",
            height=60,
            key="manual_risk_alternative"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("✅ Add Risk", type="primary", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("✕ Cancel", use_container_width=True)
        
        if cancel:
            st.session_state.show_add_risk_modal = False
            st.rerun()
        
        if submit:
            if not clause_text.strip():
                st.error("❌ Risk description is required")
                return
            
            if not impact.strip():
                st.error("❌ Impact description is required")
                return
            
            if not recommendation.strip():
                st.error("❌ Recommendation is required")
                return
            
            # Create new risk
            from datetime import datetime
            new_risk = Risk(
                rfp_id=st.session_state.rfp.id,
                clause_text=clause_text.strip(),
                category=RiskCategory(category),
                severity=RiskSeverity(severity),
                likelihood=likelihood,
                impact=impact.strip(),
                recommendation=recommendation.strip(),
                alternative_language=alternative_language.strip() if alternative_language.strip() else None,
                confidence=1.0,  # Manual risks have 100% confidence
                page_number=page_number,
                detected_by="manual",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Add to session state
            if "risks" not in st.session_state:
                st.session_state.risks = []
            st.session_state.risks.append(new_risk)
            
            # Close modal
            st.session_state.show_add_risk_modal = False
            
            st.success(f"✅ Risk added successfully!")
            st.rerun()


if __name__ == "__main__":
    main()
