"""Session state management for Streamlit."""

import streamlit as st
from typing import Optional, List, Dict, Any
from models import RFP, Requirement, Service, Risk, Draft
# ServiceMatch imported locally to avoid circular dependency


def init_session_state() -> None:
    """Initialize all session state variables."""
    
    # Current RFP
    if "rfp" not in st.session_state:
        st.session_state["rfp"] = None
    
    # Requirements
    if "requirements" not in st.session_state:
        st.session_state["requirements"] = []
    
    # Service catalog
    if "services" not in st.session_state:
        st.session_state["services"] = []
    
    # Service matches (all computed matches)
    if "service_matches" not in st.session_state:
        st.session_state["service_matches"] = []  # List[ServiceMatch]
    
    # Approved matches (subset of service_matches where approved=True)
    if "approved_matches" not in st.session_state:
        st.session_state["approved_matches"] = []  # List[ServiceMatch]
    
    # Risk clauses
    if "risks" not in st.session_state:
        st.session_state["risks"] = []
    
    # Draft
    if "draft" not in st.session_state:
        st.session_state["draft"] = None
    
    # UI state
    if "editing_mode" not in st.session_state:
        st.session_state["editing_mode"] = False
    
    if "processing" not in st.session_state:
        st.session_state["processing"] = False
    
    # AI Assistant state
    if "show_ai_assistant" not in st.session_state:
        st.session_state["show_ai_assistant"] = False
    
    # Config
    if "config" not in st.session_state:
        st.session_state["config"] = {
            "llm_provider": "gemini",
            "temperature": 0.7,
            "match_threshold": 0.5,  # Default 50% minimum match
        }


def reset_session() -> None:
    """Reset session state for new RFP."""
    st.session_state["rfp"] = None
    st.session_state["requirements"] = []
    st.session_state["services"] = []
    st.session_state["service_matches"] = []
    st.session_state["approved_matches"] = []
    st.session_state["risks"] = []
    st.session_state["draft"] = None
    st.session_state["editing_mode"] = False
    st.session_state["processing"] = False


def get_current_rfp() -> Optional[RFP]:
    """Get current RFP from session state."""
    return st.session_state.get("rfp")


def set_current_rfp(rfp: RFP) -> None:
    """Set current RFP in session state."""
    st.session_state["rfp"] = rfp


def has_current_rfp() -> bool:
    """Check if there is a current RFP."""
    return st.session_state.get("rfp") is not None


def get_approved_matches():
    """Get approved service matches from session state."""
    return [m for m in st.session_state.get("service_matches", []) if m.approved]


def update_approved_matches():
    """Update approved_matches list based on service_matches approval status."""
    st.session_state["approved_matches"] = get_approved_matches()

