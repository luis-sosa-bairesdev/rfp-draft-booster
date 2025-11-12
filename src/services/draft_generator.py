"""
Draft Generator Service.

This module provides the main service for generating proposal drafts from RFP data,
requirements, service matches, and risks using LLM-powered content generation.
"""

import logging
import re
import time
from typing import List, Optional, Dict, Any
from datetime import datetime

from models import RFP, Requirement, Risk, Draft, DraftSection, DraftStatus, GenerationMethod
from services.llm_client import LLMClient, create_llm_client
from utils.prompt_templates import (
    get_draft_generation_prompt,
    get_section_regeneration_prompt
)

logger = logging.getLogger(__name__)


class DraftGenerator:
    """
    Service for generating proposal drafts using LLMs.
    
    Features:
    - Generate complete proposal drafts with customizable instructions
    - Section-by-section generation
    - Regenerate individual sections
    - Use requirements and risks in context
    - Validate critical risks are acknowledged
    """
    
    # Standard draft sections
    STANDARD_SECTIONS = [
        {"type": "executive_summary", "title": "Executive Summary", "order": 1, "word_count": 250},
        {"type": "approach", "title": "Approach", "order": 2, "word_count": 400},
        {"type": "services", "title": "Services & Solutions", "order": 3, "word_count": 500},
        {"type": "timeline", "title": "Timeline", "order": 4, "word_count": 200},
        {"type": "pricing", "title": "Pricing", "order": 5, "word_count": 250},
        {"type": "risk_mitigation", "title": "Risk Mitigation", "order": 6, "word_count": 300},
    ]
    
    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        temperature: float = 0.7,
    ):
        """
        Initialize draft generator.
        
        Args:
            llm_client: LLM client to use (creates default if not provided)
            temperature: Generation temperature (0.0-1.0)
        """
        self.llm_client = llm_client or create_llm_client(fallback=True)
        self.temperature = temperature
        
        logger.info(f"DraftGenerator initialized with temperature={temperature}")
    
    def generate_draft(
        self,
        rfp: RFP,
        requirements: List[Requirement],
        risks: List[Risk],
        service_matches: Optional[List[Any]] = None,
        instructions: str = "",
        tone: str = "professional",
        audience: str = "enterprise",
        word_count: int = 2000,
        min_word_count: int = 500,
        max_word_count: int = 10000,
    ) -> Draft:
        """
        Generate complete proposal draft.
        
        Args:
            rfp: RFP object
            requirements: List of requirements
            risks: List of risks
            service_matches: List of service matches (optional)
            instructions: Custom AI instructions
            tone: Writing tone (professional, friendly, formal)
            audience: Target audience (enterprise, SMB, etc.)
            word_count: Target word count
            min_word_count: Minimum word count (default 500)
            max_word_count: Maximum word count (default 10000)
            
        Returns:
            Generated Draft object
            
        Raises:
            ValueError: If critical risks not acknowledged or invalid word count
        """
        # Validate critical risks are acknowledged
        critical_risks = [r for r in risks if r.severity.value == "critical" and not r.acknowledged]
        if critical_risks:
            raise ValueError(
                f"Cannot generate draft: {len(critical_risks)} critical risk(s) not acknowledged. "
                "Please acknowledge all critical risks before generating draft."
            )
        
        # Validate word count
        if word_count < min_word_count or word_count > max_word_count:
            raise ValueError(
                f"Word count must be between {min_word_count} and {max_word_count}, got {word_count}"
            )
        
        logger.info(f"Starting draft generation for RFP: {rfp.id}")
        start_time = time.time()
        
        # Build summaries
        rfp_info = self._build_rfp_info(rfp)
        requirements_summary = self._build_requirements_summary(requirements)
        service_matches_summary = self._build_service_matches_summary(service_matches or [])
        risks_summary = self._build_risks_summary(risks)
        
        # Generate prompt
        prompt = get_draft_generation_prompt(
            rfp_info=rfp_info,
            requirements_summary=requirements_summary,
            service_matches=service_matches_summary,
            risks_summary=risks_summary,
            instructions=instructions,
            tone=tone,
            audience=audience,
            word_count=word_count
        )
        
        try:
            # Generate draft content
            draft_content = self.llm_client.generate(prompt, temperature=self.temperature)
            
            # Clean and parse content
            draft_content = self._clean_draft_content(draft_content)
            
            # Parse sections from content
            sections = self._parse_sections(draft_content)
            
            # Calculate metrics
            total_word_count = len(draft_content.split())
            generation_time = time.time() - start_time
            
            # Create Draft object
            draft = Draft(
                rfp_id=rfp.id,
                content=draft_content,
                sections=sections,
                title=f"Proposal Draft for {rfp.title or rfp.filename or 'RFP'}",
                generated_by=GenerationMethod.AI,
                llm_provider=self.llm_client.provider.value,
                generation_time=generation_time,
                word_count=total_word_count,
                section_count=len(sections),
                status=DraftStatus.GENERATED,
                completeness_score=self._calculate_completeness(sections),
            )
            
            logger.info(
                f"Draft generated successfully: {total_word_count} words, "
                f"{len(sections)} sections, {generation_time:.2f}s"
            )
            
            return draft
            
        except Exception as e:
            logger.error(f"Error generating draft: {e}")
            raise
    
    def regenerate_section(
        self,
        draft: Draft,
        section_type: str,
        rfp: RFP,
        requirements: List[Requirement],
        risks: List[Risk],
        service_matches: Optional[List[Any]] = None,
        instructions: str = "",
        tone: str = "professional",
        audience: str = "enterprise",
    ) -> DraftSection:
        """
        Regenerate a specific section of the draft.
        
        Args:
            draft: Current draft
            section_type: Type of section to regenerate
            rfp: RFP object
            requirements: List of requirements
            risks: List of risks
            service_matches: List of service matches (optional)
            instructions: Custom instructions
            tone: Writing tone
            audience: Target audience
            
        Returns:
            Updated DraftSection
        """
        logger.info(f"Regenerating section: {section_type}")
        
        # Find section
        section = draft.get_section_by_type(section_type)
        if not section:
            raise ValueError(f"Section {section_type} not found in draft")
        
        # Get other sections for context
        other_sections = self._get_other_sections_content(draft, section_type)
        
        # Build summaries
        rfp_info = self._build_rfp_info(rfp)
        requirements_summary = self._build_requirements_summary(requirements)
        service_matches_summary = self._build_service_matches_summary(service_matches or [])
        risks_summary = self._build_risks_summary(risks)
        
        # Find section config
        section_config = next(
            (s for s in self.STANDARD_SECTIONS if s["type"] == section_type),
            {"title": section.title, "word_count": 300}
        )
        
        # Generate prompt
        prompt = get_section_regeneration_prompt(
            section_type=section_type,
            section_title=section_config["title"],
            rfp_info=rfp_info,
            requirements_summary=requirements_summary,
            service_matches=service_matches_summary,
            risks_summary=risks_summary,
            other_sections=other_sections,
            instructions=instructions,
            tone=tone,
            audience=audience,
            word_count=section_config.get("word_count", 300)
        )
        
        try:
            # Generate section content
            section_content = self.llm_client.generate(prompt, temperature=self.temperature)
            section_content = self._clean_draft_content(section_content)
            
            # Update section
            section.content = section_content
            section.word_count = len(section_content.split())
            section.user_edited = False  # Reset since regenerated
            
            logger.info(f"Section {section_type} regenerated: {section.word_count} words")
            
            return section
            
        except Exception as e:
            logger.error(f"Error regenerating section: {e}")
            raise
    
    def _build_rfp_info(self, rfp: RFP) -> str:
        """Build RFP information summary."""
        parts = []
        if rfp.title:
            parts.append(f"Title: {rfp.title}")
        if rfp.file_name:
            parts.append(f"Filename: {rfp.file_name}")
        if rfp.extracted_text:
            preview = rfp.extracted_text[:500]
            parts.append(f"Content Preview: {preview}...")
        return "\n".join(parts) if parts else "RFP information not available"
    
    def _build_requirements_summary(self, requirements: List[Requirement]) -> str:
        """Build requirements summary."""
        if not requirements:
            return "No requirements extracted yet."
        
        # Group by category
        by_category = {}
        for req in requirements:
            cat = req.category.value if hasattr(req.category, 'value') else str(req.category)
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(req.description)
        
        summary_parts = [f"Total Requirements: {len(requirements)}"]
        for cat, descs in by_category.items():
            summary_parts.append(f"\n{cat.capitalize()} ({len(descs)}):")
            for desc in descs[:5]:  # Top 5 per category
                summary_parts.append(f"- {desc[:150]}")
            if len(descs) > 5:
                summary_parts.append(f"  ... and {len(descs) - 5} more")
        
        return "\n".join(summary_parts)
    
    def _build_service_matches_summary(self, service_matches: List[Any]) -> str:
        """Build service matches summary."""
        if not service_matches:
            return "No service matches available. Describe your standard service offerings."
        
        # If service_matches is a list of ServiceMatch objects
        summary_parts = [f"Service Matches: {len(service_matches)}"]
        for match in service_matches[:10]:  # Top 10 matches
            if hasattr(match, 'service') and hasattr(match, 'match_score'):
                service_name = match.service.name if hasattr(match.service, 'name') else str(match.service)
                score = match.match_score if hasattr(match, 'match_score') else 0.0
                summary_parts.append(f"- {service_name} (match: {score:.2f})")
        
        return "\n".join(summary_parts)
    
    def _build_risks_summary(self, risks: List[Risk]) -> str:
        """Build risks summary."""
        if not risks:
            return "No risks detected."
        
        # Group by severity
        by_severity = {}
        for risk in risks:
            sev = risk.severity.value if hasattr(risk.severity, 'value') else str(risk.severity)
            if sev not in by_severity:
                by_severity[sev] = []
            by_severity[sev].append({
                "clause": risk.clause_text[:100],
                "category": risk.category.value if hasattr(risk.category, 'value') else str(risk.category),
                "recommendation": risk.recommendation[:150]
            })
        
        summary_parts = [f"Total Risks Detected: {len(risks)}"]
        for sev in ["critical", "high", "medium", "low"]:
            if sev in by_severity:
                risks_list = by_severity[sev]
                summary_parts.append(f"\n{sev.capitalize()} Risks ({len(risks_list)}):")
                for risk_info in risks_list[:3]:  # Top 3 per severity
                    summary_parts.append(
                        f"- {risk_info['clause']}... ({risk_info['category']}): "
                        f"{risk_info['recommendation']}"
                    )
        
        return "\n".join(summary_parts)
    
    def _clean_draft_content(self, content: str) -> str:
        """Clean draft content (remove markdown code blocks, etc.)."""
        # Remove markdown code blocks if present
        if content.startswith("```"):
            lines = content.split("\n")
            if len(lines) > 2 and lines[-1].strip() == "```":
                content = "\n".join(lines[1:-1])
            elif len(lines) > 1:
                content = "\n".join(lines[1:])
        
        # Remove leading/trailing whitespace
        content = content.strip()
        
        return content
    
    def _parse_sections(self, content: str) -> List[DraftSection]:
        """
        Parse draft content into sections.
        
        Looks for markdown headings (# Title) and creates sections.
        """
        sections = []
        lines = content.split("\n")
        
        current_section = None
        current_content = []
        
        for line in lines:
            # Check for markdown heading (## or ###)
            heading_match = re.match(r'^#{2,3}\s+(.+)$', line.strip())
            if heading_match:
                # Save previous section
                if current_section:
                    current_section.content = "\n".join(current_content).strip()
                    current_section.word_count = len(current_section.content.split())
                    sections.append(current_section)
                
                # Start new section
                title = heading_match.group(1).strip()
                section_type = self._map_title_to_section_type(title)
                current_section = DraftSection(
                    section_type=section_type,
                    title=title,
                    order=len(sections) + 1,
                    generated_by="ai"
                )
                current_content = []
            else:
                if current_section:
                    current_content.append(line)
                else:
                    # Content before first heading goes to executive summary
                    if not current_section:
                        current_section = DraftSection(
                            section_type="executive_summary",
                            title="Executive Summary",
                            order=1,
                            generated_by="ai"
                        )
                    current_content.append(line)
        
        # Save last section
        if current_section:
            current_section.content = "\n".join(current_content).strip()
            current_section.word_count = len(current_section.content.split())
            sections.append(current_section)
        
        # If no sections found, create one section with all content
        if not sections:
            sections.append(DraftSection(
                section_type="executive_summary",
                title="Executive Summary",
                content=content,
                word_count=len(content.split()),
                order=1,
                generated_by="ai"
            ))
        
        return sections
    
    def _map_title_to_section_type(self, title: str) -> str:
        """Map section title to section type."""
        title_lower = title.lower()
        
        if "executive" in title_lower or "summary" in title_lower:
            return "executive_summary"
        elif "approach" in title_lower or "methodology" in title_lower:
            return "approach"
        elif "service" in title_lower or "solution" in title_lower:
            return "services"
        elif "timeline" in title_lower or "schedule" in title_lower:
            return "timeline"
        elif "pricing" in title_lower or "cost" in title_lower or "price" in title_lower:
            return "pricing"
        elif "risk" in title_lower or "mitigation" in title_lower:
            return "risk_mitigation"
        else:
            return "other"
    
    def _get_other_sections_content(self, draft: Draft, exclude_type: str) -> str:
        """Get content of other sections for context."""
        other_sections = [s for s in draft.sections if s.section_type != exclude_type]
        if not other_sections:
            return "No other sections available."
        
        content_parts = []
        for section in other_sections:
            content_parts.append(f"## {section.title}")
            content_parts.append(section.content[:500])  # First 500 chars
        
        return "\n\n".join(content_parts)
    
    def _calculate_completeness(self, sections: List[DraftSection]) -> float:
        """Calculate draft completeness score."""
        required_types = ["executive_summary", "services", "pricing"]
        present_types = {s.section_type for s in sections}
        present_count = sum(1 for req_type in required_types if req_type in present_types)
        return present_count / len(required_types)

