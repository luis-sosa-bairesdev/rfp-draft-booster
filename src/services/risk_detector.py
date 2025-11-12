"""
Risk Detector Service.

This module provides the main service for detecting risks in RFP documents
using pattern matching and LLM-powered analysis with categorization, severity
classification, and recommendations.
"""

import logging
import re
from typing import List, Optional
from datetime import datetime

from models import RFP, Risk, RiskCategory, RiskSeverity
from services.llm_client import LLMClient, create_llm_client
from utils.prompt_templates import get_risk_detection_prompt, MAX_CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)


# Pattern-based risk detection rules
RISK_PATTERNS = {
    RiskCategory.LEGAL: [
        (r"unlimited\s+liability", RiskSeverity.CRITICAL),
        (r"all\s+liability", RiskSeverity.CRITICAL),
        (r"indirect\s+.*\s+consequential\s+damages", RiskSeverity.CRITICAL),
        (r"without\s+limitation", RiskSeverity.HIGH),
        (r"vendor\s+assumes\s+all\s+risk", RiskSeverity.CRITICAL),
        (r"no\s+warranty", RiskSeverity.HIGH),
        (r"as\s+is\s+.*\s+as\s+available", RiskSeverity.MEDIUM),
        (r"indemnify.*against\s+all", RiskSeverity.HIGH),
    ],
    RiskCategory.FINANCIAL: [
        (r"payment\s+terms.*\s+90\s+days", RiskSeverity.HIGH),
        (r"payment\s+terms.*\s+120\s+days", RiskSeverity.CRITICAL),
        (r"penalty.*\s+per\s+day", RiskSeverity.HIGH),
        (r"late\s+delivery\s+penalty", RiskSeverity.HIGH),
        (r"liquidated\s+damages", RiskSeverity.MEDIUM),
        (r"fixed\s+price.*regardless", RiskSeverity.MEDIUM),
        (r"no\s+change\s+orders", RiskSeverity.HIGH),
        (r"cost\s+overruns.*vendor", RiskSeverity.HIGH),
    ],
    RiskCategory.TIMELINE: [
        (r"complete.*\s+30\s+days", RiskSeverity.CRITICAL),
        (r"complete.*\s+60\s+days", RiskSeverity.HIGH),
        (r"no\s+extensions", RiskSeverity.CRITICAL),
        (r"no\s+extensions\s+permitted", RiskSeverity.CRITICAL),
        (r"penalty.*missed\s+milestone", RiskSeverity.HIGH),
        (r"strict\s+deadline", RiskSeverity.MEDIUM),
        (r"time\s+is\s+of\s+the\s+essence", RiskSeverity.MEDIUM),
    ],
    RiskCategory.TECHNICAL: [
        (r"99\.9{2,}%\s+uptime", RiskSeverity.HIGH),
        (r"zero\s+downtime", RiskSeverity.CRITICAL),
        (r"proprietary\s+technology.*required", RiskSeverity.HIGH),
        (r"vendor\s+lock[-\s]?in", RiskSeverity.MEDIUM),
        (r"no\s+cloud\s+deployment", RiskSeverity.HIGH),
        (r"on[-\s]?premises\s+only", RiskSeverity.MEDIUM),
    ],
    RiskCategory.COMPLIANCE: [
        (r"unlimited\s+audit\s+rights", RiskSeverity.HIGH),
        (r"audit.*\s+at\s+any\s+time", RiskSeverity.MEDIUM),
        (r"data\s+must\s+remain\s+in\s+country", RiskSeverity.MEDIUM),
        (r"data\s+sovereignty", RiskSeverity.MEDIUM),
        (r"certification.*\s+30\s+days", RiskSeverity.HIGH),
        (r"compliance.*\s+immediately", RiskSeverity.HIGH),
    ],
}


class RiskDetector:
    """
    Service for detecting risks in RFPs using pattern matching and LLMs.
    
    Features:
    - Pattern-based detection for common risk clauses
    - AI-powered detection for complex/nuanced risks
    - Categorization (legal, financial, timeline, technical, compliance)
    - Severity classification (critical, high, medium, low)
    - Confidence scoring (0.0-1.0)
    - Mitigation recommendations
    - Alternative language suggestions
    - Page number tracking
    - Text chunking for large RFPs
    - Deduplication of detected risks
    """
    
    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        min_confidence: float = 0.3,  # Minimum confidence to include a risk
        use_patterns: bool = True,  # Enable pattern-based detection
        use_ai: bool = True,  # Enable AI-powered detection
    ):
        """
        Initialize risk detector.
        
        Args:
            llm_client: LLM client to use (creates default if not provided)
            min_confidence: Minimum confidence threshold for risks
            use_patterns: Whether to use pattern-based detection
            use_ai: Whether to use AI-powered detection
        """
        self.llm_client = llm_client or create_llm_client(fallback=True) if use_ai else None
        self.min_confidence = min_confidence
        self.use_patterns = use_patterns
        self.use_ai = use_ai
        
        logger.info(
            f"RiskDetector initialized with min_confidence={min_confidence}, "
            f"use_patterns={use_patterns}, use_ai={use_ai}"
        )
    
    def detect_from_rfp(self, rfp: RFP) -> List[Risk]:
        """
        Detect all risks from an RFP.
        
        Args:
            rfp: RFP object with extracted text
            
        Returns:
            List of detected risks
            
        Raises:
            ValueError: If RFP has no extracted text
        """
        if not rfp.extracted_text:
            raise ValueError("RFP must have extracted_text to detect risks")
        
        logger.info(f"Starting risk detection for RFP: {rfp.id}")
        
        all_risks = []
        
        # Pattern-based detection
        if self.use_patterns:
            pattern_risks = self._detect_by_patterns(rfp)
            all_risks.extend(pattern_risks)
            logger.info(f"Pattern detection found {len(pattern_risks)} risks")
        
        # AI-powered detection
        if self.use_ai:
            if rfp.extracted_text_by_page:
                ai_risks = self._detect_by_ai_by_page(rfp)
            else:
                ai_risks = self._detect_by_ai_from_text(rfp.extracted_text, rfp.id)
            all_risks.extend(ai_risks)
            logger.info(f"AI detection found {len(ai_risks)} risks")
        
        # Deduplicate
        deduplicated_risks = self._deduplicate_risks(all_risks)
        
        # Filter by confidence
        filtered_risks = [
            risk for risk in deduplicated_risks
            if risk.confidence >= self.min_confidence
        ]
        
        logger.info(
            f"Detected {len(all_risks)} total risks, "
            f"{len(deduplicated_risks)} unique, "
            f"{len(filtered_risks)} above confidence threshold"
        )
        
        return filtered_risks
    
    def _detect_by_patterns(self, rfp: RFP) -> List[Risk]:
        """
        Detect risks using regex patterns.
        
        Args:
            rfp: RFP object
            
        Returns:
            List of detected risks
        """
        risks = []
        text = rfp.extracted_text.lower()
        
        # Search for patterns in each category
        for category, patterns in RISK_PATTERNS.items():
            for pattern, severity in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
                
                for match in matches:
                    # Extract context around the match
                    start = max(0, match.start() - 100)
                    end = min(len(rfp.extracted_text), match.end() + 100)
                    clause_text = rfp.extracted_text[start:end].strip()
                    
                    # Try to extract full sentence
                    sentence_start = clause_text.rfind('.', 0, 100)
                    sentence_end = clause_text.find('.', 100)
                    if sentence_start != -1 or sentence_end != -1:
                        if sentence_start != -1:
                            clause_text = clause_text[sentence_start + 1:]
                        if sentence_end != -1:
                            clause_text = clause_text[:sentence_end + 1]
                    
                    # Estimate page number if available
                    page_number = None
                    if rfp.extracted_text_by_page:
                        # Find which page contains this text
                        char_pos = start
                        current_pos = 0
                        for page_num, page_text in sorted(rfp.extracted_text_by_page.items()):
                            if current_pos <= char_pos < current_pos + len(page_text):
                                page_number = page_num
                                break
                            current_pos += len(page_text)
                    
                    risk = Risk(
                        rfp_id=rfp.id,
                        clause_text=clause_text[:500],  # Limit clause text length
                        category=category,
                        severity=severity,
                        confidence=0.85,  # Pattern matches have high confidence
                        page_number=page_number,
                        recommendation=f"Review {category.value} clause: {clause_text[:100]}...",
                        alternative_language="[Review and negotiate alternative language]",
                        acknowledged=False,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                    )
                    risks.append(risk)
        
        return risks
    
    def _detect_by_ai_by_page(self, rfp: RFP) -> List[Risk]:
        """Detect risks page by page using AI."""
        all_risks = []
        
        for page_num, page_text in rfp.extracted_text_by_page.items():
            if not page_text.strip():
                continue
            
            logger.debug(f"Processing page {page_num} for AI risk detection")
            
            try:
                page_risks = self._detect_by_ai_from_text(
                    page_text,
                    rfp.id,
                    page_number=page_num
                )
                all_risks.extend(page_risks)
            except Exception as e:
                logger.error(f"Error detecting risks from page {page_num}: {e}")
                continue
        
        return all_risks
    
    def _detect_by_ai_from_text(
        self,
        text: str,
        rfp_id: str,
        page_number: Optional[int] = None
    ) -> List[Risk]:
        """
        Detect risks from text using LLM.
        
        Args:
            text: Text to analyze
            rfp_id: RFP ID for linking risks
            page_number: Optional page number for reference
            
        Returns:
            List of detected risks
        """
        # Handle long text by chunking
        if len(text) > MAX_CHUNK_SIZE:
            return self._detect_by_ai_from_chunks(text, rfp_id, page_number)
        
        # Generate prompt
        prompt = get_risk_detection_prompt(text, page_number)
        
        try:
            # Call LLM
            response = self.llm_client.generate(prompt)
            
            # Parse JSON response
            risks_data = self.llm_client.extract_json(response)
            
            # Convert to Risk objects
            risks = []
            for risk_data in risks_data:
                try:
                    risk = self._create_risk(risk_data, rfp_id, page_number)
                    risks.append(risk)
                except Exception as e:
                    logger.warning(f"Failed to create risk from data: {e}")
                    continue
            
            return risks
            
        except Exception as e:
            logger.error(f"Error detecting risks: {e}")
            return []
    
    def _detect_by_ai_from_chunks(
        self,
        text: str,
        rfp_id: str,
        page_number: Optional[int]
    ) -> List[Risk]:
        """Detect risks from text by chunking."""
        chunks = self._chunk_text(text)
        all_risks = []
        
        for i, chunk in enumerate(chunks):
            logger.debug(f"Processing chunk {i+1}/{len(chunks)} for AI risk detection")
            
            chunk_risks = self._detect_by_ai_from_text(
                chunk,
                rfp_id,
                page_number
            )
            all_risks.extend(chunk_risks)
        
        # Deduplicate across chunks
        return self._deduplicate_risks(all_risks)
    
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
    
    def _create_risk(
        self,
        data: dict,
        rfp_id: str,
        page_number: Optional[int]
    ) -> Risk:
        """
        Create Risk object from LLM response data.
        
        Args:
            data: Dictionary with risk fields
            rfp_id: RFP ID
            page_number: Optional page number
            
        Returns:
            Risk object
            
        Raises:
            ValueError: If required fields missing or invalid
        """
        # Required fields
        clause_text = data.get("clause_text", "").strip()
        if not clause_text:
            raise ValueError("Risk must have clause_text")
        
        # Category (with validation)
        category_str = data.get("category", "legal").lower()
        try:
            category = RiskCategory(category_str)
        except ValueError:
            logger.warning(f"Invalid category '{category_str}', defaulting to legal")
            category = RiskCategory.LEGAL
        
        # Severity (with validation)
        severity_str = data.get("severity", "medium").lower()
        try:
            severity = RiskSeverity(severity_str)
        except ValueError:
            logger.warning(f"Invalid severity '{severity_str}', defaulting to medium")
            severity = RiskSeverity.MEDIUM
        
        # Confidence (with validation)
        confidence = float(data.get("confidence", 0.5))
        if not 0.0 <= confidence <= 1.0:
            logger.warning(f"Invalid confidence {confidence}, clamping to [0, 1]")
            confidence = max(0.0, min(1.0, confidence))
        
        # Page number (prefer LLM's if provided, otherwise use our page number)
        llm_page = data.get("page_number")
        final_page = llm_page if llm_page is not None else page_number
        
        # Recommendations and alternatives
        recommendation = data.get("recommendation", "").strip()
        alternative_language = data.get("alternative_language", "").strip()
        
        return Risk(
            rfp_id=rfp_id,
            clause_text=clause_text[:500],  # Limit clause text length
            category=category,
            severity=severity,
            confidence=confidence,
            page_number=final_page,
            recommendation=recommendation,
            alternative_language=alternative_language,
            acknowledged=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
    
    def _deduplicate_risks(
        self,
        risks: List[Risk]
    ) -> List[Risk]:
        """
        Remove duplicate risks based on similarity.
        
        Uses simple text similarity for now. Could be enhanced with
        embedding-based similarity in the future.
        
        Args:
            risks: List of risks
            
        Returns:
            Deduplicated list
        """
        if not risks:
            return []
        
        unique_risks = []
        seen_clauses = set()
        
        for risk in risks:
            # Normalize clause text for comparison
            normalized = risk.clause_text.lower().strip()[:200]  # Use first 200 chars
            
            # Check for exact duplicates
            if normalized in seen_clauses:
                logger.debug(f"Skipping duplicate risk: {risk.clause_text[:50]}")
                continue
            
            seen_clauses.add(normalized)
            unique_risks.append(risk)
        
        return unique_risks


def detect_risks_from_rfp(
    rfp: RFP,
    llm_client: Optional[LLMClient] = None,
    min_confidence: float = 0.3,
    use_patterns: bool = True,
    use_ai: bool = True
) -> List[Risk]:
    """
    Convenience function to detect risks from an RFP.
    
    Args:
        rfp: RFP object
        llm_client: Optional LLM client
        min_confidence: Minimum confidence threshold
        use_patterns: Whether to use pattern-based detection
        use_ai: Whether to use AI-powered detection
        
    Returns:
        List of detected risks
    """
    detector = RiskDetector(llm_client, min_confidence, use_patterns, use_ai)
    return detector.detect_from_rfp(rfp)

