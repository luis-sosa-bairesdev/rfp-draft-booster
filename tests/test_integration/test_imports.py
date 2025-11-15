"""
Integration tests for module imports.

These tests verify that all modules can be imported correctly and that
there are no circular dependencies or missing imports. This helps catch
regression issues when refactoring or adding new modules.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestModelImports:
    """Test that all models can be imported correctly."""
    
    def test_import_models_package(self):
        """Test importing the models package."""
        from models import (
            RFP,
            RFPStatus,
            Requirement,
            RequirementCategory,
            RequirementPriority,
            Service,
            ServiceCategory,
            Risk,
            RiskCategory,
            RiskSeverity,
            Draft,
            DraftStatus,
            DraftSection,
        )
        # ServiceMatch is in services.service_matcher, not models
        
        # Verify all imports are not None
        assert RFP is not None
        assert RFPStatus is not None
        assert Requirement is not None
        assert RequirementCategory is not None
        assert RequirementPriority is not None
        assert Service is not None
        assert ServiceCategory is not None
        assert Risk is not None
        assert RiskCategory is not None
        assert RiskSeverity is not None
        assert Draft is not None
        assert DraftStatus is not None
        assert DraftSection is not None
    
    def test_import_individual_model_modules(self):
        """Test importing individual model modules."""
        from models.rfp import RFP, RFPStatus
        from models.requirement import Requirement, RequirementCategory, RequirementPriority
        from models.risk import Risk, RiskCategory, RiskSeverity
        from models.service import Service, ServiceCategory
        from models.draft import Draft, DraftStatus, DraftSection
        # ServiceMatch is in services.service_matcher
        
        assert RFP is not None
        assert Requirement is not None
        assert Risk is not None
        assert Service is not None
        assert Draft is not None
    
    def test_import_risk_model_specifically(self):
        """Test that Risk model can be imported (regression test for RiskClause issue)."""
        from models import Risk, RiskCategory, RiskSeverity
        from models.risk import Risk as RiskDirect, RiskCategory as RiskCategoryDirect
        
        assert Risk is not None
        assert RiskCategory is not None
        assert RiskSeverity is not None
        assert RiskDirect is not None
        assert RiskCategoryDirect is not None
        
        # Verify Risk is actually the Risk class, not RiskClause
        assert Risk.__name__ == "Risk"
        assert RiskDirect.__name__ == "Risk"


class TestServiceImports:
    """Test that all services can be imported correctly."""
    
    def test_import_llm_client(self):
        """Test importing LLM client."""
        from services.llm_client import LLMClient, create_llm_client, LLMProvider
        
        assert LLMClient is not None
        assert create_llm_client is not None
        assert LLMProvider is not None
    
    def test_import_requirement_extractor(self):
        """Test importing requirement extractor."""
        from services.requirement_extractor import RequirementExtractor, extract_requirements_from_rfp
        
        assert RequirementExtractor is not None
        assert extract_requirements_from_rfp is not None
    
    def test_import_risk_detector(self):
        """Test importing risk detector."""
        from services.risk_detector import RiskDetector, detect_risks_from_rfp
        
        assert RiskDetector is not None
        assert detect_risks_from_rfp is not None
    
    def test_import_pdf_processor(self):
        """Test importing PDF processor."""
        from services.pdf_processor import PDFProcessor
        
        assert PDFProcessor is not None


class TestUtilsImports:
    """Test that all utility modules can be imported correctly."""
    
    def test_import_session_utils(self):
        """Test importing session utilities."""
        from utils.session import (
            init_session_state,
            reset_session,
            get_current_rfp,
            set_current_rfp,
            has_current_rfp,
        )
        
        assert init_session_state is not None
        assert reset_session is not None
        assert get_current_rfp is not None
        assert set_current_rfp is not None
        assert has_current_rfp is not None
    
    def test_import_prompt_templates(self):
        """Test importing prompt templates."""
        from utils.prompt_templates import (
            get_extraction_prompt,
            get_refinement_prompt,
            get_categorization_prompt,
            get_prioritization_prompt,
            get_risk_detection_prompt,
            MAX_CHUNK_SIZE,
            CHUNK_OVERLAP,
        )
        
        assert get_extraction_prompt is not None
        assert get_refinement_prompt is not None
        assert get_categorization_prompt is not None
        assert get_prioritization_prompt is not None
        assert get_risk_detection_prompt is not None
        assert MAX_CHUNK_SIZE is not None
        assert CHUNK_OVERLAP is not None
    
    def test_session_imports_risk_correctly(self):
        """Test that session.py imports Risk correctly (not RiskClause)."""
        from utils.session import init_session_state
        from models import Risk
        
        # This should not raise ImportError
        assert Risk is not None
        
        # Verify the import in session.py is correct
        import utils.session as session_module
        import inspect
        
        # Check that session.py imports Risk, not RiskClause
        source = inspect.getsource(session_module)
        assert "from models import" in source
        assert "Risk" in source or "Risk," in source or ", Risk" in source
        assert "RiskClause" not in source or "#" in source.split("RiskClause")[0]  # Allow if commented


class TestExceptionImports:
    """Test that all exceptions can be imported correctly."""
    
    def test_import_exceptions(self):
        """Test importing custom exceptions."""
        from exceptions import (
            LLMGenerationError,
            LLMConnectionError,
            PDFProcessingError,
            RequirementExtractionError,
        )
        
        assert LLMGenerationError is not None
        assert LLMConnectionError is not None
        assert PDFProcessingError is not None
        assert RequirementExtractionError is not None


class TestConfigImports:
    """Test that configuration can be imported correctly."""
    
    def test_import_config(self):
        """Test importing configuration."""
        from config import settings
        
        assert settings is not None
        assert hasattr(settings, 'app_name')
        assert hasattr(settings, 'version')


class TestIntegrationImports:
    """Test integration between modules."""
    
    def test_models_can_be_used_together(self):
        """Test that models can be used together without conflicts."""
        from models import RFP, Requirement, Risk
        
        # Create instances
        rfp = RFP(id="test-rfp", file_name="test.pdf")
        requirement = Requirement(rfp_id=rfp.id, description="Test requirement")
        risk = Risk(rfp_id=rfp.id, clause_text="Test risk")
        
        assert rfp.id == requirement.rfp_id
        assert rfp.id == risk.rfp_id
    
    def test_services_can_use_models(self):
        """Test that services can import and use models."""
        from services.requirement_extractor import RequirementExtractor
        from services.risk_detector import RiskDetector
        from models import RFP
        
        # Verify services can reference models
        assert RequirementExtractor is not None
        assert RiskDetector is not None
        assert RFP is not None
    
    def test_utils_can_use_models(self):
        """Test that utilities can import and use models."""
        from utils.session import init_session_state
        from models import RFP, Requirement, Risk
        
        # Verify utils can reference models
        assert init_session_state is not None
        assert RFP is not None
        assert Requirement is not None
        assert Risk is not None


class TestRegressionImports:
    """Regression tests for specific import issues."""
    
    def test_no_riskclause_import(self):
        """Regression test: Ensure RiskClause is not imported anywhere."""
        import importlib
        import os
        from pathlib import Path
        
        src_path = Path(__file__).parent.parent.parent / "src"
        
        # Check all Python files in src
        python_files = list(src_path.rglob("*.py"))
        
        for py_file in python_files:
            if "__pycache__" in str(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check for RiskClause imports (but allow in comments)
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        stripped = line.strip()
                        # Skip comments and docstrings
                        if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                            continue
                        
                        # Check for RiskClause in import statements
                        if 'import' in stripped and 'RiskClause' in stripped:
                            # This should not happen
                            pytest.fail(
                                f"Found RiskClause import in {py_file.relative_to(src_path)} "
                                f"at line {i}: {line.strip()}"
                            )
            except Exception as e:
                # Skip files that can't be read
                continue
    
    def test_all_models_in_init(self):
        """Test that all models are exported in __init__.py."""
        from models import __all__ as models_all
        
        expected_models = [
            "RFP",
            "RFPStatus",
            "Requirement",
            "RequirementCategory",
            "RequirementPriority",
            "Service",
            "ServiceCategory",  # ServiceMatch is in services.service_matcher
            "Risk",
            "RiskCategory",
            "RiskSeverity",
            "Draft",
            "DraftStatus",
            "DraftSection",
            "GenerationMethod",
        ]
        
        for model in expected_models:
            assert model in models_all, f"{model} not exported in models.__init__.py"
        
        # Verify Risk is exported, not RiskClause
        assert "Risk" in models_all
        assert "RiskClause" not in models_all

