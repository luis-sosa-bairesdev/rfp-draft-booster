"""
Prompt templates for LLM-based requirement extraction.

This module contains carefully crafted prompts for extracting requirements
from RFP documents using LLMs like Gemini, Claude, or Groq.
"""

REQUIREMENT_EXTRACTION_PROMPT = """You are an expert at analyzing Request for Proposals (RFPs) and extracting key requirements.

Your task is to analyze the following RFP text and extract ALL requirements mentioned or implied.

## RFP Text:
{rfp_text}

## Instructions:

For EACH requirement you find, provide:
1. **description**: A clear, complete description of the requirement (be specific)
2. **category**: One of: technical, functional, timeline, budget, compliance
3. **priority**: One of: critical, high, medium, low
4. **confidence**: Your confidence in this extraction as a decimal (0.0 to 1.0)
5. **page_number**: The page number where this requirement appears (if available: {page_info})

## Categorization Guidelines:

- **technical**: Performance specs, architecture, technology stack, integrations, infrastructure
  Examples: "99.9% uptime", "AWS infrastructure", "REST API integration", "PostgreSQL database"

- **functional**: Features, capabilities, user stories, use cases, workflows
  Examples: "Generate monthly reports", "User authentication", "Dashboard with analytics"

- **timeline**: Deadlines, milestones, delivery schedules, project phases
  Examples: "Complete in 60 days", "Phase 1 by January 2026", "Weekly sprint reviews"

- **budget**: Pricing, cost constraints, payment terms, financial requirements
  Examples: "Not exceed $500K", "Payment within 30 days", "Include 3-year support cost"

- **compliance**: Legal requirements, regulations, certifications, standards
  Examples: "HIPAA compliant", "SOC 2 Type II certified", "GDPR requirements", "ISO 27001"

## Priority Guidelines:

- **critical**: Must-have, deal-breaker, explicitly required
- **high**: Very important, significant business value, explicitly mentioned
- **medium**: Important but not critical, standard requirement
- **low**: Nice-to-have, optional, or implied requirement

## Confidence Guidelines:

- **0.9-1.0**: Explicitly stated, clear and unambiguous
- **0.7-0.9**: Clearly implied, strong indicators
- **0.5-0.7**: Somewhat implied, moderate indicators
- **0.3-0.5**: Weakly implied, could be interpreted differently
- **0.0-0.3**: Very uncertain, might not be a real requirement

## Output Format:

Return ONLY a valid JSON array (no markdown, no code blocks, no explanation). Each requirement must follow this structure:

[
  {{
    "description": "Solution must support 99.9% uptime SLA",
    "category": "technical",
    "priority": "critical",
    "confidence": 0.95,
    "page_number": 3
  }},
  {{
    "description": "Project completion within 60 calendar days from kickoff",
    "category": "timeline",
    "priority": "high",
    "confidence": 0.90,
    "page_number": 5
  }},
  {{
    "description": "Total project cost not to exceed $500,000 USD",
    "category": "budget",
    "priority": "high",
    "confidence": 0.92,
    "page_number": 8
  }}
]

## IMPORTANT:
- Extract EVERY requirement you find (be thorough)
- Be specific and complete in descriptions (don't summarize too much)
- Use ONLY the exact category and priority values listed above
- Provide realistic confidence scores based on how clearly the requirement is stated
- Return ONLY valid JSON (no additional text, no code blocks, no markdown)
- If no requirements found, return an empty array: []

Now analyze the RFP text and extract all requirements:
"""


REQUIREMENT_REFINEMENT_PROMPT = """You are an expert at refining and improving requirement descriptions.

Given this requirement extracted from an RFP:

**Original Description:** {description}
**Category:** {category}
**Priority:** {priority}

Your task is to:
1. Make the description more specific and actionable
2. Ensure it's clear what is being required
3. Remove ambiguity while preserving the original intent
4. Keep it concise (1-2 sentences maximum)

Return ONLY the improved description, nothing else."""


REQUIREMENT_CATEGORIZATION_PROMPT = """You are an expert at categorizing RFP requirements.

Given this requirement description:

"{description}"

Determine the BEST category from these options:
- technical (performance, architecture, technology, integrations)
- functional (features, capabilities, workflows)
- timeline (deadlines, milestones, schedules)
- budget (pricing, costs, payment terms)
- compliance (legal, regulations, certifications)

Return ONLY the category name, nothing else."""


REQUIREMENT_PRIORITIZATION_PROMPT = """You are an expert at prioritizing RFP requirements.

Given this requirement:

"{description}"

Determine the priority level from these options:
- critical (must-have, deal-breaker, explicitly required)
- high (very important, significant value, clearly stated)
- medium (important but not critical, standard requirement)
- low (nice-to-have, optional, implied)

Return ONLY the priority level, nothing else."""


# Chunk size for processing large RFPs
MAX_CHUNK_SIZE = 4000  # characters per chunk (to fit within LLM context limits)
CHUNK_OVERLAP = 200  # characters overlap between chunks to avoid missing requirements


def get_extraction_prompt(rfp_text: str, page_number: int = None) -> str:
    """
    Generate extraction prompt for given RFP text.
    
    Args:
        rfp_text: The RFP text to analyze
        page_number: Optional page number for reference
        
    Returns:
        Formatted prompt ready for LLM
    """
    page_info = f"page {page_number}" if page_number else "unknown"
    return REQUIREMENT_EXTRACTION_PROMPT.format(
        rfp_text=rfp_text,
        page_info=page_info
    )


def get_refinement_prompt(requirement: dict) -> str:
    """
    Generate refinement prompt for a requirement.
    
    Args:
        requirement: Dictionary with description, category, priority
        
    Returns:
        Formatted prompt ready for LLM
    """
    return REQUIREMENT_REFINEMENT_PROMPT.format(**requirement)


def get_categorization_prompt(description: str) -> str:
    """
    Generate categorization prompt for a requirement.
    
    Args:
        description: Requirement description
        
    Returns:
        Formatted prompt ready for LLM
    """
    return REQUIREMENT_CATEGORIZATION_PROMPT.format(description=description)


def get_prioritization_prompt(description: str) -> str:
    """
    Generate prioritization prompt for a requirement.
    
    Args:
        description: Requirement description
        
    Returns:
        Formatted prompt ready for LLM
    """
    return REQUIREMENT_PRIORITIZATION_PROMPT.format(description=description)

