"""Session state management for Streamlit."""

import streamlit as st
from typing import Optional, List, Dict, Any
from src.models import RFP, Requirement, Service, ServiceMatch, RiskClause, Draft


def init_session_state() -> None:
    """Initialize all session state variables."""
    
    # Current RFP
    if "current_rfp" not in st.session_state:
        st.session_state.current_rfp: Optional[RFP] = None
    
    # Requirements
    if "requirements" not in st.session_state:
        st.session_state.requirements: List[Requirement] = []
    
    # Service catalog
    if "services" not in st.session_state:
        st.session_state.services: List[Service] = []
    
    # Service matches
    if "service_matches" not in st.session_state:
        st.session_state.service_matches: Dict[str, List[ServiceMatch]] = {}
    
    # Risk clauses
    if "risks" not in st.session_state:
        st.session_state.risks: List[RiskClause] = []
    
    # Draft
    if "draft" not in st.session_state:
        st.session_state.draft: Optional[Draft] = None
    
    # UI state
    if "editing_mode" not in st.session_state:
        st.session_state.editing_mode: bool = False
    
    if "processing" not in st.session_state:
        st.session_state.processing: bool = False
    
    # Config
    if "config" not in st.session_state:
        st.session_state.config: Dict[str, Any] = {
            "llm_provider": "gemini",
            "temperature": 0.7,
            "match_threshold": 0.7,
        }


def reset_session() -> None:
    """Reset session state for new RFP."""
    st.session_state.current_rfp = None
    st.session_state.requirements = []
    st.session_state.service_matches = {}
    st.session_state.risks = []
    st.session_state.draft = None
    st.session_state.editing_mode = False
    st.session_state.processing = False


def get_current_rfp() -> Optional[RFP]:
    """Get current RFP from session state."""
    return st.session_state.current_rfp


def set_current_rfp(rfp: RFP) -> None:
    """Set current RFP in session state."""
    st.session_state.current_rfp = rfp


def has_current_rfp() -> bool:
    """Check if there is a current RFP."""
    return st.session_state.current_rfp is not None

