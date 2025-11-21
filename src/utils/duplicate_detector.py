"""
Duplicate detection for requirements and risks.

This module provides functions to detect duplicate or very similar items using:
- Text similarity (TF-IDF + cosine similarity)
- Exact match detection
- Fuzzy matching

Helps users identify:
- Accidentally duplicated requirements/risks
- Very similar items that could be merged
- Conflicting or redundant entries
"""

import logging
from typing import List, Dict, Any, Tuple, Set
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================

# Similarity thresholds
EXACT_MATCH_THRESHOLD = 1.0
HIGH_SIMILARITY_THRESHOLD = 0.90  # 90% similar
MEDIUM_SIMILARITY_THRESHOLD = 0.75  # 75% similar
LOW_SIMILARITY_THRESHOLD = 0.60  # 60% similar


# ============================================================================
# Similarity Functions
# ============================================================================

def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two texts using SequenceMatcher.
    
    Args:
        text1: First text
        text2: Second text
    
    Returns:
        Similarity score from 0.0 (completely different) to 1.0 (identical)
    """
    if not text1 or not text2:
        return 0.0
    
    # Normalize texts
    text1_norm = text1.lower().strip()
    text2_norm = text2.lower().strip()
    
    # Check exact match first
    if text1_norm == text2_norm:
        return 1.0
    
    # Calculate similarity
    similarity = SequenceMatcher(None, text1_norm, text2_norm).ratio()
    return similarity


def are_texts_similar(
    text1: str,
    text2: str,
    threshold: float = MEDIUM_SIMILARITY_THRESHOLD
) -> bool:
    """
    Check if two texts are similar above a threshold.
    
    Args:
        text1: First text
        text2: Second text
        threshold: Minimum similarity threshold (default: 0.75)
    
    Returns:
        True if texts are similar above threshold
    """
    similarity = calculate_text_similarity(text1, text2)
    return similarity >= threshold


# ============================================================================
# Requirement Duplicate Detection
# ============================================================================

def find_duplicate_requirements(
    requirements: List[Dict[str, Any]],
    threshold: float = MEDIUM_SIMILARITY_THRESHOLD
) -> List[Tuple[int, int, float]]:
    """
    Find duplicate or similar requirements.
    
    Args:
        requirements: List of requirement dictionaries
        threshold: Minimum similarity threshold
    
    Returns:
        List of tuples: (index1, index2, similarity_score)
    """
    duplicates = []
    
    for i in range(len(requirements)):
        for j in range(i + 1, len(requirements)):
            desc1 = requirements[i].get("description", "")
            desc2 = requirements[j].get("description", "")
            
            similarity = calculate_text_similarity(desc1, desc2)
            
            if similarity >= threshold:
                duplicates.append((i, j, similarity))
                logger.debug(
                    f"Found similar requirements: "
                    f"#{i} and #{j} (similarity: {similarity:.2f})"
                )
    
    logger.info(
        f"Found {len(duplicates)} duplicate/similar requirement pairs "
        f"(threshold: {threshold})"
    )
    return duplicates


def get_duplicate_requirement_groups(
    requirements: List[Dict[str, Any]],
    threshold: float = MEDIUM_SIMILARITY_THRESHOLD
) -> List[Set[int]]:
    """
    Group requirements by similarity.
    
    Args:
        requirements: List of requirement dictionaries
        threshold: Minimum similarity threshold
    
    Returns:
        List of sets, each containing indices of similar requirements
    """
    duplicates = find_duplicate_requirements(requirements, threshold)
    
    # Build groups using union-find approach
    groups_dict: Dict[int, Set[int]] = {}
    
    for idx1, idx2, _ in duplicates:
        # Find existing groups for these indices
        group1 = groups_dict.get(idx1)
        group2 = groups_dict.get(idx2)
        
        if group1 is None and group2 is None:
            # Create new group
            new_group = {idx1, idx2}
            groups_dict[idx1] = new_group
            groups_dict[idx2] = new_group
        elif group1 is not None and group2 is None:
            # Add idx2 to group1
            group1.add(idx2)
            groups_dict[idx2] = group1
        elif group1 is None and group2 is not None:
            # Add idx1 to group2
            group2.add(idx1)
            groups_dict[idx1] = group2
        elif group1 is not group2:
            # Merge groups
            merged = group1 | group2
            for idx in merged:
                groups_dict[idx] = merged
    
    # Get unique groups
    seen = set()
    groups = []
    for group in groups_dict.values():
        group_id = id(group)
        if group_id not in seen:
            seen.add(group_id)
            groups.append(group)
    
    logger.info(f"Found {len(groups)} duplicate requirement groups")
    return groups


# ============================================================================
# Risk Duplicate Detection
# ============================================================================

def find_duplicate_risks(
    risks: List[Dict[str, Any]],
    threshold: float = MEDIUM_SIMILARITY_THRESHOLD
) -> List[Tuple[int, int, float]]:
    """
    Find duplicate or similar risks.
    
    Args:
        risks: List of risk dictionaries
        threshold: Minimum similarity threshold
    
    Returns:
        List of tuples: (index1, index2, similarity_score)
    """
    duplicates = []
    
    for i in range(len(risks)):
        for j in range(i + 1, len(risks)):
            clause1 = risks[i].get("clause_text", "")
            clause2 = risks[j].get("clause_text", "")
            
            similarity = calculate_text_similarity(clause1, clause2)
            
            if similarity >= threshold:
                duplicates.append((i, j, similarity))
                logger.debug(
                    f"Found similar risks: "
                    f"#{i} and #{j} (similarity: {similarity:.2f})"
                )
    
    logger.info(
        f"Found {len(duplicates)} duplicate/similar risk pairs "
        f"(threshold: {threshold})"
    )
    return duplicates


def get_duplicate_risk_groups(
    risks: List[Dict[str, Any]],
    threshold: float = MEDIUM_SIMILARITY_THRESHOLD
) -> List[Set[int]]:
    """
    Group risks by similarity.
    
    Args:
        risks: List of risk dictionaries
        threshold: Minimum similarity threshold
    
    Returns:
        List of sets, each containing indices of similar risks
    """
    duplicates = find_duplicate_risks(risks, threshold)
    
    # Build groups using union-find approach (same as requirements)
    groups_dict: Dict[int, Set[int]] = {}
    
    for idx1, idx2, _ in duplicates:
        group1 = groups_dict.get(idx1)
        group2 = groups_dict.get(idx2)
        
        if group1 is None and group2 is None:
            new_group = {idx1, idx2}
            groups_dict[idx1] = new_group
            groups_dict[idx2] = new_group
        elif group1 is not None and group2 is None:
            group1.add(idx2)
            groups_dict[idx2] = group1
        elif group1 is None and group2 is not None:
            group2.add(idx1)
            groups_dict[idx1] = group2
        elif group1 is not group2:
            merged = group1 | group2
            for idx in merged:
                groups_dict[idx] = merged
    
    # Get unique groups
    seen = set()
    groups = []
    for group in groups_dict.values():
        group_id = id(group)
        if group_id not in seen:
            seen.add(group_id)
            groups.append(group)
    
    logger.info(f"Found {len(groups)} duplicate risk groups")
    return groups


# ============================================================================
# Duplicate Summary
# ============================================================================

def get_duplicate_summary(
    requirements: List[Dict[str, Any]] = None,
    risks: List[Dict[str, Any]] = None,
    threshold: float = MEDIUM_SIMILARITY_THRESHOLD
) -> Dict[str, Any]:
    """
    Get a summary of all duplicates.
    
    Args:
        requirements: List of requirement dictionaries (optional)
        risks: List of risk dictionaries (optional)
        threshold: Minimum similarity threshold
    
    Returns:
        Dictionary with duplicate summary:
        {
            "requirement_duplicates": int,
            "requirement_groups": List[Set[int]],
            "risk_duplicates": int,
            "risk_groups": List[Set[int]],
            "total_duplicates": int
        }
    """
    summary = {
        "requirement_duplicates": 0,
        "requirement_groups": [],
        "risk_duplicates": 0,
        "risk_groups": [],
        "total_duplicates": 0
    }
    
    if requirements:
        req_duplicates = find_duplicate_requirements(requirements, threshold)
        req_groups = get_duplicate_requirement_groups(requirements, threshold)
        summary["requirement_duplicates"] = len(req_duplicates)
        summary["requirement_groups"] = req_groups
    
    if risks:
        risk_duplicates = find_duplicate_risks(risks, threshold)
        risk_groups = get_duplicate_risk_groups(risks, threshold)
        summary["risk_duplicates"] = len(risk_duplicates)
        summary["risk_groups"] = risk_groups
    
    summary["total_duplicates"] = (
        summary["requirement_duplicates"] + summary["risk_duplicates"]
    )
    
    logger.info(
        f"Duplicate summary: {summary['total_duplicates']} total duplicates "
        f"({summary['requirement_duplicates']} requirements, "
        f"{summary['risk_duplicates']} risks)"
    )
    
    return summary

