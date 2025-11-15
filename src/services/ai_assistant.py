"""
AI Assistant Service.

This module provides a conversational AI assistant that provides contextual help
about RFP content, requirements, risks, and best practices.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

from models import RFP, Requirement, Risk
from services.llm_client import LLMClient, create_llm_client
from utils.prompt_templates import get_ai_assistant_prompt

logger = logging.getLogger(__name__)


class AIMessage:
    """Represents a message in the AI Assistant conversation."""
    
    def __init__(self, role: str, content: str, timestamp: Optional[datetime] = None):
        """
        Initialize message.
        
        Args:
            role: 'user' or 'assistant'
            content: Message content
            timestamp: Message timestamp (defaults to now)
        """
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }


class AIAssistant:
    """
    Conversational AI Assistant for RFP context.
    
    Features:
    - Answer questions about RFP content
    - Explain requirements and risks
    - Provide best practices
    - Context-aware responses
    - Conversation history
    """
    
    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        temperature: float = 0.7,  # Higher temperature for conversational responses
    ):
        """
        Initialize AI Assistant.
        
        Args:
            llm_client: LLM client to use (creates default if not provided)
            temperature: Generation temperature (0.0-1.0)
        """
        self.llm_client = llm_client or create_llm_client(fallback=True)
        self.temperature = temperature
        self.conversation_history: List[AIMessage] = []
        
        logger.info(f"AIAssistant initialized with temperature={temperature}")
    
    def ask(
        self,
        question: str,
        rfp: Optional[RFP] = None,
        requirements: Optional[List[Requirement]] = None,
        risks: Optional[List[Risk]] = None,
        page_context: str = "",
    ) -> str:
        """
        Ask a question and get contextual answer.
        
        Args:
            question: User's question
            rfp: Current RFP context (optional)
            requirements: List of requirements (optional)
            risks: List of risks (optional)
            
        Returns:
            AI assistant's response
        """
        logger.info(f"Processing question: {question[:100]}...")
        
        # Add user message to history
        user_message = AIMessage("user", question)
        self.conversation_history.append(user_message)
        
        # Build context from RFP, requirements, and risks
        context = self._build_context(rfp, requirements, risks, page_context)
        
        # Create prompt with context and conversation history
        prompt = get_ai_assistant_prompt(
            question=question,
            context=context,
            conversation_history=self.conversation_history[-5:],  # Last 5 messages for context
            page_context=page_context
        )
        
        try:
            # Get response from LLM
            response = self.llm_client.generate(prompt, temperature=self.temperature)
            
            # Clean response (remove markdown code blocks if present)
            response = self._clean_response(response)
            
            # Add assistant message to history
            assistant_message = AIMessage("assistant", response)
            self.conversation_history.append(assistant_message)
            
            logger.info(f"Generated response: {len(response)} characters")
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            error_msg = "I apologize, but I encountered an error while processing your question. Please try again or rephrase your question."
            self.conversation_history.append(AIMessage("assistant", error_msg))
            return error_msg
    
    def _build_context(
        self,
        rfp: Optional[RFP],
        requirements: Optional[List[Requirement]],
        risks: Optional[List[Risk]],
        page_context: str = "",
    ) -> Dict[str, Any]:
        """
        Build context dictionary from RFP, requirements, and risks.
        
        Args:
            rfp: Current RFP
            requirements: List of requirements
            risks: List of risks
            
        Returns:
            Context dictionary
        """
        context = {
            "rfp_summary": "",
            "rfp_text_preview": "",
            "requirements_count": 0,
            "requirements_summary": "",
            "risks_count": 0,
            "risks_summary": "",
            "critical_risks": [],
            "page_context": page_context,
            "page_help": self._get_page_help(page_context)
        }
        
        if rfp:
            context["rfp_summary"] = f"RFP: {rfp.title or rfp.file_name or 'Untitled'}"
            # Include first 1000 chars of RFP text for context
            if rfp.extracted_text:
                context["rfp_text_preview"] = rfp.extracted_text[:1000]
        
        if requirements:
            context["requirements_count"] = len(requirements)
            # Summarize requirements by category
            by_category = {}
            for req in requirements:
                cat = req.category.value if hasattr(req.category, 'value') else str(req.category)
                by_category[cat] = by_category.get(cat, 0) + 1
            context["requirements_summary"] = ", ".join(
                [f"{count} {cat}" for cat, count in by_category.items()]
            )
        
        if risks:
            context["risks_count"] = len(risks)
            # Summarize risks by severity
            by_severity = {}
            critical_risks = []
            for risk in risks:
                sev = risk.severity.value if hasattr(risk.severity, 'value') else str(risk.severity)
                by_severity[sev] = by_severity.get(sev, 0) + 1
                if sev == "critical":
                    critical_risks.append({
                        "clause": risk.clause_text[:100],
                        "category": risk.category.value if hasattr(risk.category, 'value') else str(risk.category),
                        "recommendation": risk.recommendation[:150]
                    })
            context["risks_summary"] = ", ".join(
                [f"{count} {sev}" for sev, count in by_severity.items()]
            )
            context["critical_risks"] = critical_risks[:5]  # Top 5 critical risks
        
        return context
    
    def _get_page_help(self, page_context: str) -> str:
        """Get help text for the current page."""
        page_help_texts = {
            "upload": """
**Upload RFP Page:**
- Upload PDF files up to 50MB
- Provide RFP title, client name, deadline, and optional notes
- The system will extract text from the PDF automatically
- After upload, navigate to Requirements or Risk Analysis pages
- Supported formats: PDF only
            """,
            "requirements": """
**Requirements Extraction Page:**
- Extract requirements using AI or manual entry
- Filter by category (Technical, Functional, Timeline, Budget, Compliance)
- Filter by priority (Critical, High, Medium, Low)
- Edit, delete, or verify requirements
- Export requirements to JSON or CSV
- Import requirements from JSON files
- Requirements are linked to specific pages in the RFP
            """,
            "service_matching": """
**Service Matching Page:**
- Automatically match RFP requirements to BairesDev services
- Uses TF-IDF vectorization and cosine similarity for matching
- View match scores (🟢 >80%, 🟡 50-80%, 🔴 <50%)
- Filter matches by category and minimum score threshold
- Approve high-confidence matches (>80%) for draft generation
- View coverage by requirement category with bar chart
- Export matches to JSON for reference
- Approved matches are automatically included in proposal drafts
- Prerequisites: RFP uploaded, requirements extracted
            """,
            "risks": """
**Risk Analysis Page:**
- Detect risks using pattern matching or AI
- Filter by category (Legal, Financial, Timeline, Technical, Compliance)
- Filter by severity (Critical, High, Medium, Low)
- Acknowledge risks with notes
- View recommendations and alternative language suggestions
- Export risks to JSON or CSV
- Import risks from JSON files
- Critical risks may block draft generation
            """,
            "draft": """
**Draft Generation Page:**
- Generate proposal drafts with customizable instructions
- Specify word count, tone, and style preferences
- Edit drafts directly in the app with real-time preview
- Regenerate specific sections without regenerating the entire draft
- Export drafts to Markdown or JSON
- Approved service matches (>80%) are automatically included
- Prerequisites: RFP uploaded, requirements extracted, risks acknowledged
            """,
            "main": """
**Main Page:**
- Overview of the RFP Draft Booster application
- Use Global Search to find content across all pages
- View Progress Dashboard to track completion status
- Navigate to different pages using the sidebar
- This is the starting point for processing RFPs
            """
        }
        return page_help_texts.get(page_context, "")
    
    def _clean_response(self, response: str) -> str:
        """
        Clean LLM response (remove markdown code blocks, etc.).
        
        Args:
            response: Raw LLM response
            
        Returns:
            Cleaned response
        """
        # Remove markdown code blocks if present
        if response.startswith("```"):
            lines = response.split("\n")
            # Remove first line (```) and last line (```)
            if len(lines) > 2:
                response = "\n".join(lines[1:-1])
        
        # Remove leading/trailing whitespace
        response = response.strip()
        
        return response
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get conversation history as list of dictionaries."""
        return [msg.to_dict() for msg in self.conversation_history]
    
    def get_last_response(self) -> Optional[str]:
        """Get the last assistant response."""
        for msg in reversed(self.conversation_history):
            if msg.role == "assistant":
                return msg.content
        return None

