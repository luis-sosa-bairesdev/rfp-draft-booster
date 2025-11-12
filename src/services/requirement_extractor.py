"""
Requirement Extractor Service.

This module provides the main service for extracting requirements from RFP documents
using LLM-powered analysis with categorization, prioritization, and confidence scoring.
"""

import logging
from typing import List, Optional
from datetime import datetime

from models import RFP, Requirement, RequirementCategory, RequirementPriority
from services.llm_client import LLMClient, create_llm_client
from utils.prompt_templates import get_extraction_prompt, MAX_CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)


class RequirementExtractor:
    """
    Service for extracting requirements from RFPs using LLMs.
    
    Features:
    - Automatic requirement extraction from RFP text
    - Categorization (technical, functional, timeline, budget, compliance)
    - Prioritization (critical, high, medium, low)
    - Confidence scoring (0.0-1.0)
    - Page number tracking
    - Text chunking for large RFPs
    - Deduplication of extracted requirements
    """
    
    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        min_confidence: float = 0.3,  # Minimum confidence to include a requirement
    ):
        """
        Initialize requirement extractor.
        
        Args:
            llm_client: LLM client to use (creates default if not provided)
            min_confidence: Minimum confidence threshold for requirements
        """
        self.llm_client = llm_client or create_llm_client(fallback=True)
        self.min_confidence = min_confidence
        
        logger.info(f"RequirementExtractor initialized with min_confidence={min_confidence}")
    
    def extract_from_rfp(self, rfp: RFP) -> List[Requirement]:
        """
        Extract all requirements from an RFP.
        
        Args:
            rfp: RFP object with extracted text
            
        Returns:
            List of extracted requirements
            
        Raises:
            ValueError: If RFP has no extracted text
        """
        if not rfp.extracted_text:
            raise ValueError("RFP must have extracted_text to extract requirements")
        
        logger.info(f"Starting requirement extraction for RFP: {rfp.id}")
        
        # Extract from full text or by page
        if rfp.extracted_text_by_page:
            requirements = self._extract_by_page(rfp)
        else:
            requirements = self._extract_from_text(rfp.extracted_text, rfp.id)
        
        # Filter by confidence
        filtered_requirements = [
            req for req in requirements
            if req.confidence >= self.min_confidence
        ]
        
        logger.info(
            f"Extracted {len(requirements)} requirements, "
            f"{len(filtered_requirements)} above confidence threshold"
        )
        
        return filtered_requirements
    
    def _extract_by_page(self, rfp: RFP) -> List[Requirement]:
        """Extract requirements page by page."""
        all_requirements = []
        
        for page_num, page_text in rfp.extracted_text_by_page.items():
            if not page_text.strip():
                continue
            
            logger.debug(f"Processing page {page_num}")
            
            try:
                page_requirements = self._extract_from_text(
                    page_text,
                    rfp.id,
                    page_number=page_num
                )
                all_requirements.extend(page_requirements)
            except Exception as e:
                logger.error(f"Error extracting from page {page_num}: {e}")
                continue
        
        # Deduplicate
        deduplicated = self._deduplicate_requirements(all_requirements)
        
        logger.info(
            f"Extracted {len(all_requirements)} requirements from {len(rfp.extracted_text_by_page)} pages, "
            f"{len(deduplicated)} unique"
        )
        
        return deduplicated
    
    def _extract_from_text(
        self,
        text: str,
        rfp_id: str,
        page_number: Optional[int] = None
    ) -> List[Requirement]:
        """
        Extract requirements from text using LLM.
        
        Args:
            text: Text to analyze
            rfp_id: RFP ID for linking requirements
            page_number: Optional page number for reference
            
        Returns:
            List of extracted requirements
        """
        # Handle long text by chunking
        if len(text) > MAX_CHUNK_SIZE:
            return self._extract_from_chunks(text, rfp_id, page_number)
        
        # Generate prompt
        prompt = get_extraction_prompt(text, page_number)
        
        try:
            # Call LLM
            response = self.llm_client.generate(prompt)
            
            # Parse JSON response
            requirements_data = self.llm_client.extract_json(response)
            
            # Convert to Requirement objects
            requirements = []
            for req_data in requirements_data:
                try:
                    req = self._create_requirement(req_data, rfp_id, page_number)
                    requirements.append(req)
                except Exception as e:
                    logger.warning(f"Failed to create requirement from data: {e}")
                    continue
            
            return requirements
            
        except Exception as e:
            logger.error(f"Error extracting requirements: {e}")
            return []
    
    def _extract_from_chunks(
        self,
        text: str,
        rfp_id: str,
        page_number: Optional[int]
    ) -> List[Requirement]:
        """Extract requirements from text by chunking."""
        chunks = self._chunk_text(text)
        all_requirements = []
        
        for i, chunk in enumerate(chunks):
            logger.debug(f"Processing chunk {i+1}/{len(chunks)}")
            
            chunk_requirements = self._extract_from_text(
                chunk,
                rfp_id,
                page_number
            )
            all_requirements.extend(chunk_requirements)
        
        # Deduplicate across chunks
        return self._deduplicate_requirements(all_requirements)
    
    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + MAX_CHUNK_SIZE
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for period + space within overlap window
                break_point = text.rfind(". ", start + MAX_CHUNK_SIZE - CHUNK_OVERLAP, end)
                if break_point != -1:
                    end = break_point + 1
            
            chunks.append(text[start:end])
            start = end - CHUNK_OVERLAP
        
        return chunks
    
    def _create_requirement(
        self,
        data: dict,
        rfp_id: str,
        page_number: Optional[int]
    ) -> Requirement:
        """
        Create Requirement object from LLM response data.
        
        Args:
            data: Dictionary with requirement fields
            rfp_id: RFP ID
            page_number: Optional page number
            
        Returns:
            Requirement object
            
        Raises:
            ValueError: If required fields missing or invalid
        """
        # Required fields
        description = data.get("description", "").strip()
        if not description:
            raise ValueError("Requirement must have a description")
        
        # Category (with validation)
        category_str = data.get("category", "functional").lower()
        try:
            category = RequirementCategory(category_str)
        except ValueError:
            logger.warning(f"Invalid category '{category_str}', defaulting to functional")
            category = RequirementCategory.FUNCTIONAL
        
        # Priority (with validation)
        priority_str = data.get("priority", "medium").lower()
        try:
            priority = RequirementPriority(priority_str)
        except ValueError:
            logger.warning(f"Invalid priority '{priority_str}', defaulting to medium")
            priority = RequirementPriority.MEDIUM
        
        # Confidence (with validation)
        confidence = float(data.get("confidence", 0.5))
        if not 0.0 <= confidence <= 1.0:
            logger.warning(f"Invalid confidence {confidence}, clamping to [0, 1]")
            confidence = max(0.0, min(1.0, confidence))
        
        # Page number (prefer LLM's if provided, otherwise use our page number)
        llm_page = data.get("page_number")
        final_page = llm_page if llm_page is not None else page_number
        
        return Requirement(
            rfp_id=rfp_id,
            description=description,
            category=category,
            priority=priority,
            confidence=confidence,
            page_number=final_page,
            verified=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
    
    def _deduplicate_requirements(
        self,
        requirements: List[Requirement]
    ) -> List[Requirement]:
        """
        Remove duplicate requirements based on similarity.
        
        Uses simple text similarity for now. Could be enhanced with
        embedding-based similarity in the future.
        
        Args:
            requirements: List of requirements
            
        Returns:
            Deduplicated list
        """
        if not requirements:
            return []
        
        unique_requirements = []
        seen_descriptions = set()
        
        for req in requirements:
            # Normalize description for comparison
            normalized = req.description.lower().strip()
            
            # Check for exact duplicates
            if normalized in seen_descriptions:
                logger.debug(f"Skipping duplicate: {req.description[:50]}")
                continue
            
            seen_descriptions.add(normalized)
            unique_requirements.append(req)
        
        return unique_requirements
    
    def refine_requirement(self, requirement: Requirement) -> Requirement:
        """
        Refine a requirement description using LLM.
        
        Args:
            requirement: Requirement to refine
            
        Returns:
            Requirement with refined description
        """
        from utils.prompt_templates import get_refinement_prompt
        
        prompt = get_refinement_prompt({
            "description": requirement.description,
            "category": requirement.category.value,
            "priority": requirement.priority.value,
        })
        
        try:
            refined_description = self.llm_client.generate(prompt).strip()
            requirement.update(description=refined_description)
            logger.info(f"Refined requirement: {requirement.id}")
        except Exception as e:
            logger.error(f"Failed to refine requirement: {e}")
        
        return requirement


def extract_requirements_from_rfp(
    rfp: RFP,
    llm_client: Optional[LLMClient] = None,
    min_confidence: float = 0.3
) -> List[Requirement]:
    """
    Convenience function to extract requirements from an RFP.
    
    Args:
        rfp: RFP object
        llm_client: Optional LLM client
        min_confidence: Minimum confidence threshold
        
    Returns:
        List of extracted requirements
    """
    extractor = RequirementExtractor(llm_client, min_confidence)
    return extractor.extract_from_rfp(rfp)

