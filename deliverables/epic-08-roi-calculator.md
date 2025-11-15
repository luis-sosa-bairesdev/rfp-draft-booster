# Epic 8: ROI Calculator & Metrics Polish - Technical Spike

## 📋 Overview

**Epic Title:** ROI Calculator & Metrics Polish  
**Sprint:** TBD (Sprint 5 or 6)  
**Status:** Planning  
**Priority:** Medium  
**Estimated Effort:** 1 day (6-9 hours)

## 🎯 Business Goal

Add an interactive ROI calculator on the Welcome page to demonstrate quantifiable business value to prospects and users. Show real-time cost savings, time reduction, and financial impact of using RFP Draft Booster compared to manual RFP processing.

## 📐 Architecture & Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     Welcome Page (main.py)                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. HEADER & BRIEF DESCRIPTION                              │
│     • App title and value proposition                       │
│                                                              │
│  2. ROI CALCULATOR (Interactive)                            │
│     ┌─────────────────────────────────────────┐            │
│     │ User Inputs (Sliders):                  │            │
│     │  • RFP pages (1-100, default 50)       │            │
│     │  • Team hourly rate ($50-200, $100)    │            │
│     │  • Manual time/page (1-5h, 2h)         │            │
│     │                                         │            │
│     │ Computed Metrics (st.metric):           │            │
│     │  ┌──────────┬──────────┬──────────┐   │            │
│     │  │ Time     │ Cost     │ ROI      │   │            │
│     │  │ Saved    │ Savings  │ Monthly  │   │            │
│     │  │ (hours)  │ (/RFP)   │ ($)      │   │            │
│     │  │ ↓80%     │ +$X      │ 10 RFPs  │   │            │
│     │  └──────────┴──────────┴──────────┘   │            │
│     │                                         │            │
│     │ Optional Bar Chart:                     │            │
│     │  Manual vs Automated (Time/Cost)       │            │
│     │                                         │            │
│     │ [Reset Defaults] [Export ROI Report]   │            │
│     │                                         │            │
│     │ ℹ️ Calculation Assumptions (expander)  │            │
│     └─────────────────────────────────────────┘            │
│                                                              │
│  3. CALL-TO-ACTION                                          │
│     🚀 [Start Your RFP] → Upload Page                      │
│     📚 [See Example] → Load demo data                      │
│                                                              │
│  4. QUICK STATS (from session_state)                       │
│     ┌─────────────────────────────────────────┐            │
│     │ If NO RFP loaded:                       │            │
│     │   "Upload an RFP to see your stats"    │            │
│     │   + Example stats (15 reqs, 7 risks)   │            │
│     │                                         │            │
│     │ If RFP loaded:                          │            │
│     │   • Total Requirements (clickable) ───►│ Req page   │
│     │   • Risks Flagged (clickable) ─────────►│ Risk page  │
│     │   • Draft Completeness (clickable) ────►│ Draft page │
│     │   • RFP Pages Processed                │            │
│     │   • Avg Confidence Score               │            │
│     │   • Service Matches % (Epic 6)         │            │
│     └─────────────────────────────────────────┘            │
│                                                              │
│  5. EXISTING CONTENT (Progress Dashboard, etc.)            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 🧮 ROI Calculator Logic

### Input Parameters (Sliders)

```python
# User inputs via st.slider
rfp_pages = st.slider("RFP Pages", 1, 100, 50)
team_hourly_rate = st.slider("Team Hourly Rate ($)", 50, 200, 100)
manual_time_per_page = st.slider("Manual Time per Page (hours)", 1.0, 5.0, 2.0, 0.5)

# Persist in session_state
st.session_state.roi_rfp_pages = rfp_pages
st.session_state.roi_hourly_rate = team_hourly_rate
st.session_state.roi_time_per_page = manual_time_per_page
```

### Calculation Formulas

```python
# Time calculations
manual_time_total = rfp_pages * manual_time_per_page  # hours
automated_time = manual_time_total * 0.20  # 80% reduction
time_saved = manual_time_total * 0.80  # hours saved

# Cost calculations
cost_manual = manual_time_total * team_hourly_rate  # USD
cost_automated = automated_time * team_hourly_rate  # USD
cost_saved_per_rfp = cost_manual - cost_automated  # USD

# ROI calculations
roi_monthly = cost_saved_per_rfp * 10  # Assume 10 RFPs/month
roi_annual = roi_monthly * 12  # Annual ROI

# Percentage reduction
time_reduction_pct = 80  # Fixed at 80%
```

### Display Metrics

```python
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="⏱️ Time Saved",
        value=f"{time_saved:.1f} hours",
        delta=f"↓{time_reduction_pct}% faster",
        delta_color="normal"  # Green
    )

with col2:
    st.metric(
        label="💰 Cost Savings",
        value=f"${cost_saved_per_rfp:,.0f} /RFP",
        delta=f"+${cost_saved_per_rfp:,.0f}",
        delta_color="normal"  # Green
    )

with col3:
    st.metric(
        label="📈 ROI Monthly",
        value=f"${roi_monthly:,.0f}",
        delta="10 RFPs/month",
        delta_color="normal"  # Green
    )

# Optional: Show annual ROI
st.caption(f"💡 **Annual ROI:** ${roi_annual:,.0f} (120 RFPs/year)")
```

## 📊 Quick Stats Section

### Data Sources

```python
def get_quick_stats() -> dict:
    """Get current RFP statistics from session_state."""
    
    # Check if RFP loaded
    if not st.session_state.get("rfp"):
        return None
    
    rfp = st.session_state.rfp
    requirements = st.session_state.requirements or []
    risks = st.session_state.risks or []
    draft = st.session_state.draft
    
    # Calculate stats
    stats = {
        "total_requirements": len(requirements),
        "risks_flagged": len([r for r in risks if r.severity in [RiskSeverity.CRITICAL, RiskSeverity.HIGH]]),
        "draft_completeness": draft.completeness_score if draft else 0,
        "rfp_pages": rfp.page_count if hasattr(rfp, 'page_count') else len(rfp.text.split('\n\n')),
        "avg_confidence": sum(r.confidence for r in requirements) / len(requirements) if requirements else 0.0,
    }
    
    # If Epic 6 implemented
    if "service_matches" in st.session_state and st.session_state.service_matches:
        matches = st.session_state.service_matches
        approved = [m for m in matches if m.get("approved", False) and m.get("fit_percentage", 0) > 80]
        stats["service_matches_pct"] = (len(approved) / len(matches) * 100) if matches else 0
    
    return stats
```

### Display Logic

```python
st.subheader("📊 Quick Stats")

stats = get_quick_stats()

if stats is None:
    # No RFP loaded - show placeholder
    st.info("📤 **Upload an RFP** to see your project statistics")
    
    # Show example stats
    with st.expander("📝 Example Stats (Demo RFP)"):
        col1, col2, col3 = st.columns(3)
        col1.metric("Requirements", "15")
        col2.metric("Risks Flagged", "7")
        col3.metric("Draft Complete", "100%")
else:
    # RFP loaded - show real stats with clickable links
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Requirements", stats["total_requirements"])
        if st.button("View Requirements →", key="stats_goto_reqs"):
            st.switch_page("pages/2_📋_Requirements.py")
    
    with col2:
        st.metric("Risks Flagged", stats["risks_flagged"])
        if st.button("View Risks →", key="stats_goto_risks"):
            st.switch_page("pages/3_⚠️_Risk_Analysis.py")
    
    with col3:
        st.metric("Draft Completeness", f"{stats['draft_completeness']:.0f}%")
        if st.button("View Draft →", key="stats_goto_draft"):
            st.switch_page("pages/4_✍️_Draft_Generation.py")
    
    # Additional stats row
    col4, col5, col6 = st.columns(3)
    col4.metric("RFP Pages", stats["rfp_pages"])
    col5.metric("Avg Confidence", f"{stats['avg_confidence']:.1%}")
    
    if "service_matches_pct" in stats:
        col6.metric("Service Matches", f"{stats['service_matches_pct']:.0f}%")
```

## 🎨 UI Components

### 1. ROI Calculator Section

```python
def render_roi_calculator():
    """Render interactive ROI calculator."""
    
    st.subheader("💰 ROI Calculator")
    st.markdown("**Estimate your savings** with AI-powered RFP processing")
    
    # Initialize session_state defaults
    if "roi_rfp_pages" not in st.session_state:
        st.session_state.roi_rfp_pages = 50
    if "roi_hourly_rate" not in st.session_state:
        st.session_state.roi_hourly_rate = 100
    if "roi_time_per_page" not in st.session_state:
        st.session_state.roi_time_per_page = 2.0
    
    # Input sliders
    col1, col2, col3 = st.columns(3)
    
    with col1:
        rfp_pages = st.slider(
            "📄 RFP Pages",
            min_value=1,
            max_value=100,
            value=st.session_state.roi_rfp_pages,
            key="slider_rfp_pages"
        )
    
    with col2:
        hourly_rate = st.slider(
            "💵 Team Hourly Rate ($)",
            min_value=50,
            max_value=200,
            value=st.session_state.roi_hourly_rate,
            step=10,
            key="slider_hourly_rate"
        )
    
    with col3:
        time_per_page = st.slider(
            "⏱️ Manual Time per Page (hours)",
            min_value=1.0,
            max_value=5.0,
            value=st.session_state.roi_time_per_page,
            step=0.5,
            key="slider_time_per_page"
        )
    
    # Update session_state
    st.session_state.roi_rfp_pages = rfp_pages
    st.session_state.roi_hourly_rate = hourly_rate
    st.session_state.roi_time_per_page = time_per_page
    
    # Calculate ROI
    manual_time = rfp_pages * time_per_page
    automated_time = manual_time * 0.20
    time_saved = manual_time * 0.80
    
    cost_manual = manual_time * hourly_rate
    cost_automated = automated_time * hourly_rate
    cost_saved = cost_manual - cost_automated
    
    roi_monthly = cost_saved * 10
    roi_annual = roi_monthly * 12
    
    # Display metrics
    st.markdown("---")
    st.markdown("### 📈 Your Estimated Savings")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="⏱️ Time Saved",
            value=f"{time_saved:.1f} hours",
            delta="↓80% faster",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            label="💰 Cost Savings",
            value=f"${cost_saved:,.0f} /RFP",
            delta=f"+${cost_saved:,.0f}",
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            label="📈 ROI Monthly",
            value=f"${roi_monthly:,.0f}",
            delta="10 RFPs/month",
            delta_color="normal"
        )
    
    # Show annual ROI
    st.caption(f"💡 **Annual ROI:** ${roi_annual:,.0f} (120 RFPs/year)")
    
    # Optional: Bar chart comparison
    if st.checkbox("Show visual comparison", value=False):
        import pandas as pd
        
        comparison_data = pd.DataFrame({
            "Process": ["Manual", "Automated"],
            "Time (hours)": [manual_time, automated_time],
            "Cost (USD)": [cost_manual, cost_automated]
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.bar_chart(comparison_data.set_index("Process")["Time (hours)"])
            st.caption("⏱️ Time Comparison")
        
        with col2:
            st.bar_chart(comparison_data.set_index("Process")["Cost (USD)"])
            st.caption("💰 Cost Comparison")
    
    # Action buttons
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if st.button("🔄 Reset to Defaults", key="btn_reset_roi"):
            st.session_state.roi_rfp_pages = 50
            st.session_state.roi_hourly_rate = 100
            st.session_state.roi_time_per_page = 2.0
            st.rerun()
    
    with col2:
        # Export ROI report
        import pandas as pd
        
        report_data = {
            "Metric": [
                "RFP Pages",
                "Team Hourly Rate",
                "Manual Time per Page",
                "Manual Time Total",
                "Automated Time",
                "Time Saved",
                "Manual Cost",
                "Automated Cost",
                "Cost Saved per RFP",
                "ROI Monthly (10 RFPs)",
                "ROI Annual (120 RFPs)"
            ],
            "Value": [
                f"{rfp_pages} pages",
                f"${hourly_rate}/hour",
                f"{time_per_page} hours/page",
                f"{manual_time:.1f} hours",
                f"{automated_time:.1f} hours",
                f"{time_saved:.1f} hours (80%)",
                f"${cost_manual:,.0f}",
                f"${cost_automated:,.0f}",
                f"${cost_saved:,.0f}",
                f"${roi_monthly:,.0f}",
                f"${roi_annual:,.0f}"
            ]
        }
        
        df_report = pd.DataFrame(report_data)
        csv = df_report.to_csv(index=False)
        
        st.download_button(
            label="📥 Export ROI Report",
            data=csv,
            file_name="rfp_booster_roi_report.csv",
            mime="text/csv",
            key="btn_export_roi"
        )
    
    # Assumptions expander
    with st.expander("ℹ️ Calculation Assumptions"):
        st.markdown("""
        **How we calculate your savings:**
        
        - **80% time reduction:** Based on industry benchmarks for AI-assisted document processing
        - **10 RFPs per month:** Average for B2B sales teams and proposal departments
        - **Manual process includes:** 
          - Document review and extraction
          - Requirement identification and categorization
          - Risk assessment and analysis
          - Draft proposal writing
          - Multiple review cycles
        - **Automated process (20% time):** 
          - AI-powered extraction and analysis
          - Human review and validation
          - Final edits and approval
        
        **Note:** Actual savings may vary based on RFP complexity, team experience, and specific use cases.
        """)
```

### 2. Call-to-Action Section

```python
def render_cta_section():
    """Render call-to-action buttons."""
    
    st.markdown("---")
    st.markdown("### 🚀 Ready to Get Started?")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if st.button("📤 Start Your First RFP", type="primary", use_container_width=True):
            st.switch_page("pages/1_📤_Upload_RFP.py")
    
    with col2:
        if st.button("📚 See Example RFP", use_container_width=True):
            # Load demo data
            load_demo_rfp()
            st.success("✅ Demo RFP loaded! Check Quick Stats below.")
            st.rerun()

def load_demo_rfp():
    """Load demo RFP data for Quick Stats preview."""
    from models import RFP, Requirement, Risk, RequirementCategory, RequirementPriority, RiskCategory, RiskSeverity
    from datetime import datetime, timedelta
    
    # Create demo RFP
    demo_rfp = RFP(
        file_name="demo_rfp_software_development.pdf",
        title="Software Development RFP - Demo",
        client_name="ABC Corp",
        deadline=datetime.now() + timedelta(days=30),
        notes="This is a demo RFP for preview purposes",
        text="Sample RFP text for demonstration...",
        uploaded_at=datetime.now()
    )
    
    # Create demo requirements
    demo_requirements = [
        Requirement(
            description="Cloud-based microservices architecture required",
            category=RequirementCategory.TECHNICAL,
            priority=RequirementPriority.CRITICAL,
            page_number=5,
            confidence=0.95,
            verified=True
        ),
        Requirement(
            description="99.9% uptime SLA guarantee",
            category=RequirementCategory.FUNCTIONAL,
            priority=RequirementPriority.HIGH,
            page_number=7,
            confidence=0.92,
            verified=True
        ),
        # ... add 13 more demo requirements ...
    ]
    
    # Create demo risks
    demo_risks = [
        Risk(
            clause_text="Payment terms net-90 days",
            category=RiskCategory.FINANCIAL,
            severity=RiskSeverity.HIGH,
            confidence=0.88,
            page_number=12,
            recommendation="Negotiate for net-30 terms",
            acknowledged=False
        ),
        # ... add 6 more demo risks ...
    ]
    
    # Update session_state
    st.session_state.rfp = demo_rfp
    st.session_state.requirements = demo_requirements
    st.session_state.risks = demo_risks
```

## 🗂️ File Structure

```
src/
├── components/
│   └── roi_calculator.py          # NEW: ROI calculator component
│       ├── render_roi_calculator()
│       ├── calculate_roi()
│       └── export_roi_report()
│
├── components/
│   └── quick_stats.py              # NEW: Quick stats component
│       ├── render_quick_stats()
│       ├── get_quick_stats()
│       └── load_demo_rfp()
│
└── utils/
    └── calculations.py             # NEW: ROI calculation utilities
        ├── calculate_time_savings()
        ├── calculate_cost_savings()
        └── calculate_roi()

main.py                              # MODIFIED: Add ROI calculator + Quick Stats
    ├── render_roi_calculator()     # After header
    ├── render_cta_section()        # After calculator
    └── render_quick_stats()        # After CTA

tests/
└── test_ui/
    └── test_roi_calculator.py      # NEW: ROI calculator tests
        ├── test_calculator_logic()
        ├── test_slider_persistence()
        ├── test_export_report()
        └── test_quick_stats()
```

## 🧪 Testing Strategy

### Unit Tests

```python
# tests/test_ui/test_roi_calculator.py

import pytest
from src.utils.calculations import calculate_time_savings, calculate_cost_savings, calculate_roi

class TestROICalculations:
    """Test ROI calculation logic."""
    
    def test_time_savings_calculation(self):
        """Test time savings calculation."""
        # Given
        rfp_pages = 50
        time_per_page = 2.0
        
        # When
        manual_time, automated_time, time_saved = calculate_time_savings(
            rfp_pages, time_per_page
        )
        
        # Then
        assert manual_time == 100.0  # 50 * 2
        assert automated_time == 20.0  # 100 * 0.2
        assert time_saved == 80.0  # 100 * 0.8
        assert time_saved / manual_time == 0.8  # 80% reduction
    
    def test_cost_savings_calculation(self):
        """Test cost savings calculation."""
        # Given
        manual_time = 100.0
        automated_time = 20.0
        hourly_rate = 100
        
        # When
        cost_manual, cost_automated, cost_saved = calculate_cost_savings(
            manual_time, automated_time, hourly_rate
        )
        
        # Then
        assert cost_manual == 10000  # 100 * 100
        assert cost_automated == 2000  # 20 * 100
        assert cost_saved == 8000  # 10000 - 2000
    
    def test_roi_calculation(self):
        """Test ROI calculation."""
        # Given
        cost_saved_per_rfp = 8000
        rfps_per_month = 10
        
        # When
        roi_monthly, roi_annual = calculate_roi(cost_saved_per_rfp, rfps_per_month)
        
        # Then
        assert roi_monthly == 80000  # 8000 * 10
        assert roi_annual == 960000  # 80000 * 12
    
    def test_edge_cases(self):
        """Test edge case inputs."""
        # Minimum values
        manual_time, automated_time, time_saved = calculate_time_savings(1, 1.0)
        assert manual_time == 1.0
        assert time_saved == 0.8
        
        # Maximum values
        manual_time, automated_time, time_saved = calculate_time_savings(100, 5.0)
        assert manual_time == 500.0
        assert time_saved == 400.0

class TestQuickStats:
    """Test Quick Stats component."""
    
    def test_stats_with_no_rfp(self, mock_streamlit):
        """Test Quick Stats when no RFP is loaded."""
        mock_streamlit.session_state = {}
        
        stats = get_quick_stats()
        
        assert stats is None
    
    def test_stats_with_loaded_rfp(self, mock_streamlit, sample_rfp, sample_requirements, sample_risks):
        """Test Quick Stats with loaded RFP."""
        mock_streamlit.session_state = {
            "rfp": sample_rfp,
            "requirements": sample_requirements,
            "risks": sample_risks,
            "draft": None
        }
        
        stats = get_quick_stats()
        
        assert stats is not None
        assert stats["total_requirements"] == len(sample_requirements)
        assert "risks_flagged" in stats
        assert "avg_confidence" in stats
    
    def test_demo_rfp_loading(self, mock_streamlit):
        """Test loading demo RFP data."""
        mock_streamlit.session_state = {}
        
        load_demo_rfp()
        
        assert "rfp" in mock_streamlit.session_state
        assert "requirements" in mock_streamlit.session_state
        assert "risks" in mock_streamlit.session_state
        assert len(mock_streamlit.session_state.requirements) == 15
        assert len(mock_streamlit.session_state.risks) == 7
```

### Integration Tests

```python
# tests/test_integration/test_roi_integration.py

def test_roi_calculator_with_session_state():
    """Test ROI calculator persists values in session_state."""
    # Initialize session
    st.session_state.clear()
    
    # Set slider values
    st.session_state.roi_rfp_pages = 75
    st.session_state.roi_hourly_rate = 150
    st.session_state.roi_time_per_page = 3.0
    
    # Render calculator
    render_roi_calculator()
    
    # Verify persistence
    assert st.session_state.roi_rfp_pages == 75
    assert st.session_state.roi_hourly_rate == 150
    assert st.session_state.roi_time_per_page == 3.0

def test_quick_stats_navigation():
    """Test Quick Stats navigation links."""
    # Setup
    load_demo_rfp()
    
    # Render Quick Stats
    render_quick_stats()
    
    # Verify navigation buttons exist
    assert "stats_goto_reqs" in st.session_state
    assert "stats_goto_risks" in st.session_state
    assert "stats_goto_draft" in st.session_state
```

### Manual Testing Checklist

- [ ] ROI calculator renders correctly on welcome page
- [ ] Sliders work and update metrics in real-time
- [ ] Default values (50, $100, 2h) load correctly
- [ ] Reset button restores defaults
- [ ] Export ROI report downloads CSV with correct data
- [ ] Assumptions expander shows detailed info
- [ ] Bar chart comparison displays correctly (optional)
- [ ] Quick Stats shows placeholder when no RFP loaded
- [ ] Quick Stats shows real data when RFP loaded
- [ ] Navigation buttons in Quick Stats work
- [ ] "Start Your RFP" button navigates to Upload page
- [ ] "See Example" button loads demo data
- [ ] Calculator is responsive on mobile (stacks columns)
- [ ] Metrics display with green deltas and arrows
- [ ] Annual ROI caption shows correctly

## 📦 Dependencies

**No new dependencies required!** Epic 8 uses only existing libraries:

- `streamlit` (core UI)
- `pandas` (for CSV export)
- Existing models from `src/models/`

## 🚀 Implementation Plan

### Phase 1: ROI Calculator Component (3-4 hours)

1. **Create utility functions** (`src/utils/calculations.py`)
   - `calculate_time_savings()`
   - `calculate_cost_savings()`
   - `calculate_roi()`

2. **Create ROI component** (`src/components/roi_calculator.py`)
   - `render_roi_calculator()` with sliders
   - Session state persistence
   - Metrics display with deltas
   - Optional bar chart
   - Reset button
   - Export report button
   - Assumptions expander

3. **Write unit tests** (`tests/test_ui/test_roi_calculator.py`)
   - Test calculation logic
   - Test slider persistence
   - Test export functionality

### Phase 2: Quick Stats Component (2-3 hours)

1. **Create Quick Stats component** (`src/components/quick_stats.py`)
   - `render_quick_stats()` with conditional logic
   - `get_quick_stats()` data aggregation
   - `load_demo_rfp()` for demo data
   - Navigation buttons with `st.switch_page`

2. **Write unit tests** (`tests/test_ui/test_quick_stats.py`)
   - Test with no RFP
   - Test with loaded RFP
   - Test demo data loading
   - Test navigation links

### Phase 3: Integration with Welcome Page (1-2 hours)

1. **Modify `main.py`**
   - Add ROI calculator after header/description
   - Add CTA section
   - Add Quick Stats section
   - Adjust layout and spacing

2. **Update `src/components/__init__.py`**
   - Export new components

3. **Integration tests**
   - Test full welcome page flow
   - Verify session state interactions

### Phase 4: Testing & Polish (1-2 hours)

1. **Manual testing**
   - Test all user interactions
   - Verify calculations accuracy
   - Test navigation flows
   - Check responsive design

2. **Code coverage**
   - Ensure >80% coverage for new code
   - Run full test suite

3. **UI/UX polish**
   - Adjust spacing and alignment
   - Refine colors and styling
   - Add helpful tooltips

## 📊 Success Criteria

- [ ] ROI calculator displays on welcome page with correct layout
- [ ] All calculations are accurate (verified with test cases)
- [ ] Sliders persist values in session_state
- [ ] Metrics display with green deltas and proper formatting
- [ ] Export ROI report generates correct CSV
- [ ] Quick Stats shows correct data from session_state
- [ ] Navigation buttons work correctly
- [ ] Demo RFP loads with 15 requirements and 7 risks
- [ ] All unit tests pass with >80% coverage
- [ ] UI is responsive on mobile and desktop
- [ ] No performance issues or lag when moving sliders
- [ ] Code follows project standards and best practices

## 🔗 Related Documentation

- **Epic 5:** Draft Generation & AI Assistant (for Quick Stats integration)
- **Epic 6:** Service Matching Screen (for service matches % in Quick Stats)
- **PRD:** `deliverables/prd-rfp-draft-booster.md`
- **Welcome Page:** `main.py`

## 📝 Notes

- **No new dependencies:** Uses only existing libraries
- **Lightweight:** Simple calculations, no heavy processing
- **Reactive:** Streamlit auto-updates on slider changes
- **Modular:** Components reusable for future analytics pages
- **Demo-ready:** "See Example" button great for demos/presentations
- **Sales tool:** ROI calculator is a powerful sales enablement feature

## 🎯 Next Steps After Epic 8

1. **Epic 6:** Implement Service Matching Screen (adds service matches % to Quick Stats)
2. **Epic 7:** Implement Google Docs Export (complete draft workflow)
3. **Analytics Dashboard:** Expand ROI calculator into full analytics page (future)
4. **Multi-user stats:** Track ROI across multiple users/teams (future)

---

**Estimated Total Effort:** 1 day (6-9 hours)  
**Sprint Assignment:** TBD (Sprint 5 or 6)  
**Priority:** Medium (enhances UX and demonstrates business value)

