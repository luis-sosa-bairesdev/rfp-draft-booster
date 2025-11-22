"""Navigation Flow Component - Guide users through the RFP processing workflow."""

import streamlit as st


def render_navigation_buttons(current_page: str):
    """
    Render navigation flow buttons to guide users through pages.
    
    Args:
        current_page: Current page identifier ('upload', 'requirements', 'matching', 'risk', 'draft')
    """
    # Define workflow order
    workflow = {
        'upload': {'next': 'requirements', 'label': '📋 Extract Requirements', 'icon': '→'},
        'requirements': {'prev': 'upload', 'next': 'matching', 'label': '🔗 Match Services', 'icon': '→'},
        'matching': {'prev': 'requirements', 'next': 'risk', 'label': '⚠️ Analyze Risks', 'icon': '→'},
        'risk': {'prev': 'matching', 'next': 'draft', 'label': '✍️ Generate Draft', 'icon': '→'},
        'draft': {'prev': 'risk', 'label': '✅ Complete', 'icon': '🎉'}
    }
    
    if current_page not in workflow:
        return
    
    st.markdown("---")
    st.markdown("### 🗺️ Workflow Navigation")
    
    config = workflow[current_page]
    cols = st.columns([1, 2, 1])
    
    # Previous button
    with cols[0]:
        if 'prev' in config:
            prev_page = config['prev']
            prev_label = workflow[prev_page].get('label', 'Previous')
            if st.button(f"← {prev_label.split()[1] if len(prev_label.split()) > 1 else 'Back'}", 
                        key=f"nav_prev_{current_page}",
                        use_container_width=True):
                navigate_to(prev_page)
    
    # Current status
    with cols[1]:
        st.info(f"**Current Step:** {get_page_label(current_page)}")
    
    # Next button
    with cols[2]:
        if 'next' in config:
            next_page = config['next']
            next_label = config['label']
            if st.button(f"{next_label} {config['icon']}", 
                        key=f"nav_next_{current_page}",
                        use_container_width=True,
                        type="primary"):
                navigate_to(next_page)
        elif current_page == 'draft':
            st.success("🎉 Workflow Complete!")


def navigate_to(page: str):
    """Navigate to a specific page."""
    page_map = {
        'upload': 'pages/1_📤_Upload_RFP.py',
        'requirements': 'pages/2_📋_Requirements.py',
        'matching': 'pages/3_🔗_Service_Matching.py',
        'risk': 'pages/4_⚠️_Risk_Analysis.py',
        'draft': 'pages/5_✍️_Draft_Generation.py'
    }
    
    if page in page_map:
        st.switch_page(page_map[page])


def get_page_label(page: str) -> str:
    """Get display label for a page."""
    labels = {
        'upload': '📤 Upload RFP',
        'requirements': '📋 Requirements Extraction',
        'matching': '🔗 Service Matching',
        'risk': '⚠️ Risk Analysis',
        'draft': '✍️ Draft Generation'
    }
    return labels.get(page, page.title())


def render_workflow_progress():
    """Render a visual progress indicator for the workflow."""
    # Check what steps are complete
    has_rfp = st.session_state.get('rfp') is not None
    has_requirements = len(st.session_state.get('requirements', [])) > 0
    has_matches = len(st.session_state.get('service_matches', [])) > 0
    has_risks = len(st.session_state.get('risks', [])) > 0
    has_draft = st.session_state.get('draft') is not None
    
    steps = [
        ('📤 Upload', has_rfp),
        ('📋 Requirements', has_requirements),
        ('🔗 Matching', has_matches),
        ('⚠️ Risks', has_risks),
        ('✍️ Draft', has_draft)
    ]
    
    st.markdown("### 📊 Workflow Progress")
    
    cols = st.columns(len(steps))
    for idx, (col, (label, completed)) in enumerate(zip(cols, steps)):
        with col:
            if completed:
                st.success(f"✅ {label}")
            else:
                st.info(f"⏳ {label}")

