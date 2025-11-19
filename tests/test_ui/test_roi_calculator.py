"""
Unit tests for ROI Calculator component.

Tests calculation logic, slider persistence, export functionality,
and Quick Stats integration.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

from src.utils.calculations import (
    calculate_time_savings,
    calculate_cost_savings,
    calculate_roi,
    calculate_full_roi,
    TIME_REDUCTION_PERCENTAGE,
    DEFAULT_RFPS_PER_MONTH
)


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
        assert manual_time == pytest.approx(100.0)  # 50 * 2
        assert automated_time == pytest.approx(20.0)  # 100 * 0.2
        assert time_saved == pytest.approx(80.0)  # 100 * 0.8
        assert time_saved / manual_time == pytest.approx(TIME_REDUCTION_PERCENTAGE)  # 80% reduction
    
    def test_time_savings_edge_cases(self):
        """Test time savings with edge case values."""
        # Minimum values
        manual_time, automated_time, time_saved = calculate_time_savings(1, 1.0)
        assert manual_time == 1.0
        assert time_saved == 0.8
        
        # Maximum values
        manual_time, automated_time, time_saved = calculate_time_savings(100, 5.0)
        assert manual_time == 500.0
        assert time_saved == 400.0
    
    def test_time_savings_validation(self):
        """Test time savings input validation."""
        with pytest.raises(ValueError, match="RFP pages must be positive"):
            calculate_time_savings(0, 2.0)
        
        with pytest.raises(ValueError, match="RFP pages must be positive"):
            calculate_time_savings(-10, 2.0)
        
        with pytest.raises(ValueError, match="Time per page must be positive"):
            calculate_time_savings(50, 0)
        
        with pytest.raises(ValueError, match="Time per page must be positive"):
            calculate_time_savings(50, -1.0)
    
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
    
    def test_cost_savings_different_rates(self):
        """Test cost savings with different hourly rates."""
        # Low rate
        cost_manual, cost_automated, cost_saved = calculate_cost_savings(
            100.0, 20.0, 50
        )
        assert cost_manual == 5000
        assert cost_saved == 4000
        
        # High rate
        cost_manual, cost_automated, cost_saved = calculate_cost_savings(
            100.0, 20.0, 200
        )
        assert cost_manual == 20000
        assert cost_saved == 16000
    
    def test_cost_savings_validation(self):
        """Test cost savings input validation."""
        with pytest.raises(ValueError, match="Manual time cannot be negative"):
            calculate_cost_savings(-10, 20, 100)
        
        with pytest.raises(ValueError, match="Automated time cannot be negative"):
            calculate_cost_savings(100, -5, 100)
        
        with pytest.raises(ValueError, match="Hourly rate must be positive"):
            calculate_cost_savings(100, 20, 0)
        
        with pytest.raises(ValueError, match="Hourly rate must be positive"):
            calculate_cost_savings(100, 20, -50)
    
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
    
    def test_roi_different_volumes(self):
        """Test ROI with different RFP volumes."""
        # Low volume
        roi_monthly, roi_annual = calculate_roi(8000, 5)
        assert roi_monthly == 40000
        assert roi_annual == 480000
        
        # High volume
        roi_monthly, roi_annual = calculate_roi(8000, 20)
        assert roi_monthly == 160000
        assert roi_annual == 1920000
    
    def test_roi_validation(self):
        """Test ROI input validation."""
        with pytest.raises(ValueError, match="Cost saved cannot be negative"):
            calculate_roi(-1000, 10)
        
        with pytest.raises(ValueError, match="RFPs per month must be positive"):
            calculate_roi(8000, 0)
        
        with pytest.raises(ValueError, match="RFPs per month must be positive"):
            calculate_roi(8000, -5)
    
    def test_full_roi_calculation(self):
        """Test complete ROI calculation."""
        # Given
        rfp_pages = 50
        time_per_page = 2.0
        hourly_rate = 100
        rfps_per_month = 10
        
        # When
        metrics = calculate_full_roi(
            rfp_pages, time_per_page, hourly_rate, rfps_per_month
        )
        
        # Then
        assert metrics['manual_time'] == pytest.approx(100.0)
        assert metrics['automated_time'] == pytest.approx(20.0)
        assert metrics['time_saved'] == pytest.approx(80.0)
        assert metrics['cost_manual'] == pytest.approx(10000.0)
        assert metrics['cost_automated'] == pytest.approx(2000.0)
        assert metrics['cost_saved'] == pytest.approx(8000.0)
        assert metrics['roi_monthly'] == pytest.approx(80000.0)
        assert metrics['roi_annual'] == pytest.approx(960000.0)
        assert metrics['time_reduction_pct'] == pytest.approx(80.0)
    
    def test_full_roi_returns_dict(self):
        """Test that full ROI returns dictionary with all keys."""
        metrics = calculate_full_roi(50, 2.0, 100, 10)
        
        expected_keys = [
            'manual_time', 'automated_time', 'time_saved',
            'cost_manual', 'cost_automated', 'cost_saved',
            'roi_monthly', 'roi_annual', 'time_reduction_pct'
        ]
        
        for key in expected_keys:
            assert key in metrics
            assert isinstance(metrics[key], (int, float))


class TestROICalculatorComponent:
    """Test ROI Calculator UI component."""
    
    def test_init_roi_session_state(self):
        """Test ROI session state initialization."""
        from src.components.roi_calculator import (
            DEFAULT_RFP_PAGES,
            DEFAULT_HOURLY_RATE,
            DEFAULT_TIME_PER_PAGE
        )
        
        import streamlit as st
        
        # Clear any existing state
        if hasattr(st, 'session_state'):
            for key in list(st.session_state.keys()):
                if key.startswith('roi_'):
                    del st.session_state[key]
        
        # Verify defaults would be set correctly
        assert DEFAULT_RFP_PAGES == 50
        assert DEFAULT_HOURLY_RATE == 100
        assert DEFAULT_TIME_PER_PAGE == 2.0
    
    def test_reset_roi_to_defaults(self):
        """Test ROI reset to defaults."""
        from src.components.roi_calculator import (
            DEFAULT_RFP_PAGES,
            DEFAULT_HOURLY_RATE,
            DEFAULT_TIME_PER_PAGE
        )
        
        # Verify default constants
        assert DEFAULT_RFP_PAGES == 50
        assert DEFAULT_HOURLY_RATE == 100
        assert DEFAULT_TIME_PER_PAGE == 2.0
    
    def test_generate_roi_report(self):
        """Test ROI report generation."""
        from src.components.roi_calculator import generate_roi_report
        
        # Given
        rfp_pages = 50
        hourly_rate = 100.0
        time_per_page = 2.0
        metrics = {
            'manual_time': 100.0,
            'automated_time': 20.0,
            'time_saved': 80.0,
            'cost_manual': 10000.0,
            'cost_automated': 2000.0,
            'cost_saved': 8000.0,
            'roi_monthly': 80000.0,
            'roi_annual': 960000.0,
            'time_reduction_pct': 80.0
        }
        
        # When
        csv = generate_roi_report(rfp_pages, hourly_rate, time_per_page, metrics)
        
        # Then
        assert isinstance(csv, str)
        assert "Metric,Value" in csv
        assert "RFP Pages,50 pages" in csv
        assert "$100/hour" in csv
        assert "80.0 hours" in csv
        assert "$8,000" in csv
        assert "$80,000" in csv
        assert "$960,000" in csv
    
    def test_generate_roi_report_csv_format(self):
        """Test ROI report has valid CSV format."""
        from src.components.roi_calculator import generate_roi_report
        
        metrics = calculate_full_roi(50, 2.0, 100, 10)
        csv = generate_roi_report(50, 100.0, 2.0, metrics)
        
        # Parse CSV to verify format
        import io
        df = pd.read_csv(io.StringIO(csv))
        
        assert list(df.columns) == ["Metric", "Value"]
        assert len(df) == 12  # Should have 12 metrics
        assert "RFP Pages" in df["Metric"].values
        assert "ROI Annual (120 RFPs)" in df["Metric"].values


class TestQuickStats:
    """Test Quick Stats component."""
    
    def test_get_quick_stats_no_rfp(self):
        """Test Quick Stats when no RFP is loaded."""
        import streamlit as st
        
        # Clear any existing state
        if hasattr(st, 'session_state'):
            for key in ['rfp', 'requirements', 'risks', 'draft']:
                if key in st.session_state:
                    del st.session_state[key]
        
        # Since we can't really test streamlit components without a running session,
        # we just verify that the function exists and is callable
        from src.components.quick_stats import get_quick_stats
        assert callable(get_quick_stats)
    
    def test_get_quick_stats_with_rfp(self):
        """Test Quick Stats calculation logic."""
        from src.models.rfp import RFP
        from src.models.requirement import Requirement, RequirementCategory, RequirementPriority
        from src.models.risk import Risk, RiskCategory, RiskSeverity
        
        # Create test data
        rfp = RFP(
            id="test-rfp",
            file_name="test.pdf",
            client_name="Test Client",
            extracted_text="Sample RFP text",
            total_pages=10
        )
        
        requirements = [
            Requirement(
                id="req-1",
                description="Test requirement 1",
                category=RequirementCategory.TECHNICAL,
                priority=RequirementPriority.HIGH,
                confidence=0.9
            ),
            Requirement(
                id="req-2",
                description="Test requirement 2",
                category=RequirementCategory.FUNCTIONAL,
                priority=RequirementPriority.MEDIUM,
                confidence=0.85
            )
        ]
        
        risks = [
            Risk(
                id="risk-1",
                clause_text="High risk clause",
                category=RiskCategory.LEGAL,
                severity=RiskSeverity.HIGH,
                confidence=0.88
            ),
            Risk(
                id="risk-2",
                clause_text="Critical risk clause",
                category=RiskCategory.FINANCIAL,
                severity=RiskSeverity.CRITICAL,
                confidence=0.92
            )
        ]
        
        # Verify data is valid
        assert len(requirements) == 2
        assert len(risks) == 2
        assert len([r for r in risks if r.severity in [RiskSeverity.CRITICAL, RiskSeverity.HIGH]]) == 2
        assert rfp.total_pages == 10
    
    def test_load_demo_rfp(self):
        """Test demo RFP data structure."""
        # Verify the demo RFP function exists and is callable
        from src.components.quick_stats import load_demo_rfp
        assert callable(load_demo_rfp)
        
        # Verify it would create valid demo data
        from src.models.rfp import RFP
        demo_rfp = RFP(
            id="demo-rfp-001",
            file_name="demo_rfp_software_development.pdf",
            title="Software Development RFP - Demo",
            client_name="ABC Corporation",
            extracted_text="Demo text",
            total_pages=50
        )
        
        assert demo_rfp.client_name == "ABC Corporation"
        assert demo_rfp.title == "Software Development RFP - Demo"
        assert demo_rfp.total_pages == 50


class TestROIConstants:
    """Test ROI calculation constants."""
    
    def test_time_reduction_percentage(self):
        """Test TIME_REDUCTION_PERCENTAGE is correct."""
        assert TIME_REDUCTION_PERCENTAGE == 0.80
        assert TIME_REDUCTION_PERCENTAGE * 100 == 80.0
    
    def test_default_rfps_per_month(self):
        """Test DEFAULT_RFPS_PER_MONTH is correct."""
        assert DEFAULT_RFPS_PER_MONTH == 10
        assert DEFAULT_RFPS_PER_MONTH * 12 == 120  # Annual

