"""
Unit tests for duplicate_detector module.

Tests duplicate detection for requirements and risks.
"""

import pytest

from src.utils.duplicate_detector import (
    calculate_text_similarity,
    are_texts_similar,
    find_duplicate_requirements,
    get_duplicate_requirement_groups,
    find_duplicate_risks,
    get_duplicate_risk_groups,
    get_duplicate_summary,
    EXACT_MATCH_THRESHOLD,
    HIGH_SIMILARITY_THRESHOLD,
    MEDIUM_SIMILARITY_THRESHOLD,
    LOW_SIMILARITY_THRESHOLD
)


class TestTextSimilarity:
    """Test text similarity calculation."""
    
    def test_identical_texts(self):
        """Test that identical texts have 1.0 similarity."""
        text = "Cloud infrastructure with auto-scaling"
        similarity = calculate_text_similarity(text, text)
        assert similarity == 1.0
    
    def test_case_insensitive(self):
        """Test that comparison is case-insensitive."""
        text1 = "Cloud Infrastructure"
        text2 = "cloud infrastructure"
        similarity = calculate_text_similarity(text1, text2)
        assert similarity == 1.0
    
    def test_whitespace_normalized(self):
        """Test that whitespace is normalized."""
        text1 = "Cloud infrastructure"
        text2 = "  Cloud infrastructure  "
        similarity = calculate_text_similarity(text1, text2)
        assert similarity == 1.0
    
    def test_completely_different(self):
        """Test that completely different texts have low similarity."""
        text1 = "Cloud infrastructure"
        text2 = "xyzabc123"
        similarity = calculate_text_similarity(text1, text2)
        assert similarity < 0.3
    
    def test_similar_texts(self):
        """Test that similar texts have high similarity."""
        text1 = "Cloud infrastructure with auto-scaling"
        text2 = "Cloud infrastructure with manual-scaling"
        similarity = calculate_text_similarity(text1, text2)
        assert similarity > 0.7
    
    def test_empty_text1(self):
        """Test with empty first text."""
        similarity = calculate_text_similarity("", "something")
        assert similarity == 0.0
    
    def test_empty_text2(self):
        """Test with empty second text."""
        similarity = calculate_text_similarity("something", "")
        assert similarity == 0.0
    
    def test_both_empty(self):
        """Test with both texts empty."""
        similarity = calculate_text_similarity("", "")
        assert similarity == 0.0


class TestAreTextsSimilar:
    """Test are_texts_similar function."""
    
    def test_similar_above_threshold(self):
        """Test texts similar above threshold."""
        text1 = "Cloud infrastructure with auto-scaling"
        text2 = "Cloud infrastructure with auto-scaling capabilities"
        result = are_texts_similar(text1, text2, threshold=0.75)
        assert result is True
    
    def test_not_similar_below_threshold(self):
        """Test texts not similar below threshold."""
        text1 = "Cloud infrastructure"
        text2 = "Mobile application"
        result = are_texts_similar(text1, text2, threshold=0.75)
        assert result is False
    
    def test_custom_threshold(self):
        """Test with custom threshold."""
        text1 = "Cloud infra"
        text2 = "Cloud infrastructure"
        result = are_texts_similar(text1, text2, threshold=0.5)
        assert result is True


class TestRequirementDuplicates:
    """Test requirement duplicate detection."""
    
    def test_no_duplicates(self):
        """Test with no duplicate requirements."""
        requirements = [
            {"description": "Cloud infrastructure with 99.9% uptime"},
            {"description": "Multi-factor authentication for users"},
            {"description": "Project completion within 6 months"}
        ]
        
        duplicates = find_duplicate_requirements(requirements, threshold=0.75)
        assert len(duplicates) == 0
    
    def test_exact_duplicates(self):
        """Test with exact duplicate requirements."""
        requirements = [
            {"description": "Cloud infrastructure"},
            {"description": "Cloud infrastructure"},
            {"description": "Other requirement"}
        ]
        
        duplicates = find_duplicate_requirements(requirements, threshold=0.75)
        assert len(duplicates) == 1
        assert duplicates[0][0] == 0
        assert duplicates[0][1] == 1
        assert duplicates[0][2] == 1.0
    
    def test_similar_requirements(self):
        """Test with similar requirements."""
        requirements = [
            {"description": "Cloud infrastructure with auto-scaling"},
            {"description": "Cloud infrastructure with manual-scaling"},
            {"description": "Completely different requirement"}
        ]
        
        duplicates = find_duplicate_requirements(requirements, threshold=0.75)
        assert len(duplicates) >= 1
        assert duplicates[0][0] == 0
        assert duplicates[0][1] == 1
    
    def test_multiple_duplicate_pairs(self):
        """Test with multiple duplicate pairs."""
        requirements = [
            {"description": "Cloud infrastructure requirement"},
            {"description": "Cloud infrastructure requirement"},
            {"description": "Security authentication requirement"},
            {"description": "Security authentication requirement"}
        ]
        
        duplicates = find_duplicate_requirements(requirements, threshold=0.75)
        assert len(duplicates) >= 2  # At least (0,1) and (2,3)
    
    def test_threshold_sensitivity(self):
        """Test that threshold affects results."""
        requirements = [
            {"description": "Cloud infrastructure"},
            {"description": "Cloud infra"}
        ]
        
        # With high threshold, should not match
        duplicates_high = find_duplicate_requirements(requirements, threshold=0.95)
        assert len(duplicates_high) == 0
        
        # With low threshold, should match
        duplicates_low = find_duplicate_requirements(requirements, threshold=0.50)
        assert len(duplicates_low) >= 1


class TestRequirementGroups:
    """Test requirement duplicate grouping."""
    
    def test_no_groups(self):
        """Test with no duplicate groups."""
        requirements = [
            {"description": "Cloud infrastructure with auto-scaling"},
            {"description": "Multi-factor authentication for users"},
            {"description": "Project completion within 6 months"}
        ]
        
        groups = get_duplicate_requirement_groups(requirements, threshold=0.75)
        assert len(groups) == 0
    
    def test_single_group(self):
        """Test with one group of duplicates."""
        requirements = [
            {"description": "Same requirement"},
            {"description": "Same requirement"},
            {"description": "Different requirement"}
        ]
        
        groups = get_duplicate_requirement_groups(requirements, threshold=0.75)
        assert len(groups) == 1
        assert len(groups[0]) == 2
        assert 0 in groups[0]
        assert 1 in groups[0]
    
    def test_multiple_groups(self):
        """Test with multiple groups of duplicates."""
        requirements = [
            {"description": "Cloud infrastructure with auto-scaling capabilities"},
            {"description": "Cloud infrastructure with auto-scaling capabilities"},
            {"description": "Multi-factor authentication for all users"},
            {"description": "Multi-factor authentication for all users"}
        ]
        
        groups = get_duplicate_requirement_groups(requirements, threshold=0.75)
        assert len(groups) >= 2  # At least 2 groups
    
    def test_chain_of_similarities(self):
        """Test chain of similar requirements grouped together."""
        requirements = [
            {"description": "Cloud infrastructure with scaling"},
            {"description": "Cloud infrastructure with auto-scaling"},
            {"description": "Cloud infra with auto-scaling"}
        ]
        
        groups = get_duplicate_requirement_groups(requirements, threshold=0.70)
        # All three should be in one group if similarities chain
        assert len(groups) >= 1


class TestRiskDuplicates:
    """Test risk duplicate detection."""
    
    def test_no_duplicates(self):
        """Test with no duplicate risks."""
        risks = [
            {"clause_text": "Unlimited liability for data breaches"},
            {"clause_text": "Fixed-price contract with no changes"},
            {"clause_text": "100% feature completion required"}
        ]
        
        duplicates = find_duplicate_risks(risks, threshold=0.75)
        assert len(duplicates) == 0
    
    def test_exact_duplicates(self):
        """Test with exact duplicate risks."""
        risks = [
            {"clause_text": "Unlimited liability"},
            {"clause_text": "Unlimited liability"},
            {"clause_text": "Other clause"}
        ]
        
        duplicates = find_duplicate_risks(risks, threshold=0.75)
        assert len(duplicates) == 1
        assert duplicates[0][2] == 1.0
    
    def test_similar_risks(self):
        """Test with similar risks."""
        risks = [
            {"clause_text": "Unlimited liability for data breaches and security incidents"},
            {"clause_text": "Unlimited liability for data breaches and security failures"},
            {"clause_text": "Fixed-price contract with no changes allowed"}
        ]
        
        duplicates = find_duplicate_risks(risks, threshold=0.75)
        assert len(duplicates) >= 1


class TestRiskGroups:
    """Test risk duplicate grouping."""
    
    def test_no_groups(self):
        """Test with no duplicate groups."""
        risks = [
            {"clause_text": "Unlimited liability for data breaches and security"},
            {"clause_text": "Fixed-price contract with no changes allowed"},
            {"clause_text": "Project completion requires 100% feature coverage"}
        ]
        
        groups = get_duplicate_risk_groups(risks, threshold=0.75)
        assert len(groups) == 0
    
    def test_single_group(self):
        """Test with one group of duplicates."""
        risks = [
            {"clause_text": "Same clause"},
            {"clause_text": "Same clause"},
            {"clause_text": "Different clause"}
        ]
        
        groups = get_duplicate_risk_groups(risks, threshold=0.75)
        assert len(groups) == 1
        assert len(groups[0]) == 2


class TestDuplicateSummary:
    """Test duplicate summary function."""
    
    def test_empty_summary(self):
        """Test summary with no data."""
        summary = get_duplicate_summary()
        assert summary["requirement_duplicates"] == 0
        assert summary["risk_duplicates"] == 0
        assert summary["total_duplicates"] == 0
    
    def test_requirements_only(self):
        """Test summary with only requirements."""
        requirements = [
            {"description": "Same requirement"},
            {"description": "Same requirement"}
        ]
        
        summary = get_duplicate_summary(requirements=requirements, threshold=0.75)
        assert summary["requirement_duplicates"] == 1
        assert summary["risk_duplicates"] == 0
        assert summary["total_duplicates"] == 1
        assert len(summary["requirement_groups"]) == 1
    
    def test_risks_only(self):
        """Test summary with only risks."""
        risks = [
            {"clause_text": "Same clause"},
            {"clause_text": "Same clause"}
        ]
        
        summary = get_duplicate_summary(risks=risks, threshold=0.75)
        assert summary["requirement_duplicates"] == 0
        assert summary["risk_duplicates"] == 1
        assert summary["total_duplicates"] == 1
        assert len(summary["risk_groups"]) == 1
    
    def test_both_requirements_and_risks(self):
        """Test summary with both requirements and risks."""
        requirements = [
            {"description": "Req A"},
            {"description": "Req A"}
        ]
        risks = [
            {"clause_text": "Clause X"},
            {"clause_text": "Clause X"}
        ]
        
        summary = get_duplicate_summary(
            requirements=requirements,
            risks=risks,
            threshold=0.75
        )
        
        assert summary["requirement_duplicates"] == 1
        assert summary["risk_duplicates"] == 1
        assert summary["total_duplicates"] == 2
        assert len(summary["requirement_groups"]) == 1
        assert len(summary["risk_groups"]) == 1


class TestThresholds:
    """Test threshold constants."""
    
    def test_threshold_values(self):
        """Test that threshold constants are valid."""
        assert EXACT_MATCH_THRESHOLD == 1.0
        assert 0.0 < HIGH_SIMILARITY_THRESHOLD < 1.0
        assert 0.0 < MEDIUM_SIMILARITY_THRESHOLD < 1.0
        assert 0.0 < LOW_SIMILARITY_THRESHOLD < 1.0
        
        # Verify ordering
        assert HIGH_SIMILARITY_THRESHOLD > MEDIUM_SIMILARITY_THRESHOLD
        assert MEDIUM_SIMILARITY_THRESHOLD > LOW_SIMILARITY_THRESHOLD

