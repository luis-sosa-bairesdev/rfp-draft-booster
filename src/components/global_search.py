"""
Global Search Component - Search across all RFP content.
"""

import streamlit as st
from typing import List, Optional, Dict, Any
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import Requirement, Risk, RFP


class SearchResult:
    """Represents a search result."""
    
    def __init__(self, result_type: str, title: str, content: str, metadata: Dict[str, Any]):
        self.result_type = result_type
        self.title = title
        self.content = content
        self.metadata = metadata


def search_content(
    query: str,
    rfp: Optional[RFP] = None,
    requirements: Optional[List[Requirement]] = None,
    risks: Optional[List[Risk]] = None,
    filter_type: Optional[str] = None
) -> List[SearchResult]:
    """
    Search across all content.
    
    Args:
        query: Search query
        rfp: Current RFP
        requirements: List of requirements
        risks: List of risks
        filter_type: Filter by type ('requirements', 'risks', 'text', or None for all)
    
    Returns:
        List of SearchResult objects
    """
    results = []
    query_lower = query.lower()
    
    # Search requirements
    if not filter_type or filter_type == "requirements":
        if requirements:
            for req in requirements:
                if query_lower in req.description.lower():
                    results.append(SearchResult(
                        result_type="requirement",
                        title=f"Requirement: {req.description[:50]}...",
                        content=req.description,
                        metadata={
                            "id": req.id,
                            "category": req.category.value if hasattr(req.category, 'value') else str(req.category),
                            "priority": req.priority.value if hasattr(req.priority, 'value') else str(req.priority),
                            "page": req.page_number
                        }
                    ))
    
    # Search risks
    if not filter_type or filter_type == "risks":
        if risks:
            for risk in risks:
                if (query_lower in risk.clause_text.lower() or 
                    query_lower in risk.recommendation.lower()):
                    results.append(SearchResult(
                        result_type="risk",
                        title=f"Risk: {risk.clause_text[:50]}...",
                        content=risk.clause_text,
                        metadata={
                            "id": risk.id,
                            "category": risk.category.value if hasattr(risk.category, 'value') else str(risk.category),
                            "severity": risk.severity.value if hasattr(risk.severity, 'value') else str(risk.severity),
                            "page": risk.page_number
                        }
                    ))
    
    # Search RFP text
    if not filter_type or filter_type == "text":
        if rfp and rfp.extracted_text:
            # Simple text search - find occurrences
            text_lower = rfp.extracted_text.lower()
            if query_lower in text_lower:
                # Find context around matches
                idx = text_lower.find(query_lower)
                start = max(0, idx - 100)
                end = min(len(rfp.extracted_text), idx + len(query) + 100)
                context = rfp.extracted_text[start:end]
                
                results.append(SearchResult(
                    result_type="text",
                    title="RFP Text Match",
                    content=context,
                    metadata={
                        "position": idx,
                        "page": None  # Could be enhanced to find page number
                    }
                ))
    
    return results


def render_global_search(
    rfp: Optional[RFP] = None,
    requirements: Optional[List[Requirement]] = None,
    risks: Optional[List[Risk]] = None
):
    """Render global search interface."""
    
    # Search input
    col1, col2 = st.columns([4, 1])
    
    with col1:
        search_query = st.text_input(
            "🔍 Search",
            key="global_search_input",
            placeholder="Search requirements, risks, or RFP text...",
            help="Press Enter or click Search"
        )
    
    with col2:
        filter_type = st.selectbox(
            "Filter",
            options=["All", "Requirements", "Risks", "Text"],
            key="global_search_filter"
        )
    
    # Search button
    if st.button("🔍 Search", key="btn_global_search", use_container_width=True) or search_query:
        if search_query:
            filter_val = None if filter_type == "All" else filter_type.lower()
            results = search_content(
                query=search_query,
                rfp=rfp,
                requirements=requirements,
                risks=risks,
                filter_type=filter_val
            )
            
            if results:
                st.markdown(f"### 📊 Search Results ({len(results)} found)")
                
                for i, result in enumerate(results):
                    with st.expander(f"{i+1}. {result.title}", expanded=i == 0):
                        # Type badge
                        type_colors = {
                            "requirement": "🔵",
                            "risk": "🔴",
                            "text": "🟢"
                        }
                        st.markdown(f"**Type:** {type_colors.get(result.result_type, '📄')} {result.result_type.title()}")
                        
                        # Content
                        st.markdown("**Content:**")
                        st.write(result.content[:500] + "..." if len(result.content) > 500 else result.content)
                        
                        # Metadata
                        if result.metadata:
                            metadata_str = ", ".join([f"{k}: {v}" for k, v in result.metadata.items() if v])
                            st.caption(f"Metadata: {metadata_str}")
            else:
                st.info("No results found. Try a different search term.")
        else:
            st.info("Enter a search query to begin.")

