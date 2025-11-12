"""
LLM Client for requirement extraction.

This module provides a unified interface for interacting with different LLM providers
(Gemini, Groq, Ollama) for requirement extraction from RFPs.
"""

import json
import logging
import os
from typing import Optional, List, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    GEMINI = "gemini"
    GROQ = "groq"
    OLLAMA = "ollama"


class LLMClient:
    """
    Unified client for LLM providers.
    
    Supports multiple providers with automatic fallback:
    1. Google Gemini (primary, free tier available)
    2. Groq (fallback, fast inference)
    3. Ollama (local fallback, privacy-focused)
    """
    
    def __init__(
        self,
        provider: LLMProvider = LLMProvider.GEMINI,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.1,  # Low temperature for consistent extraction
    ):
        """
        Initialize LLM client.
        
        Args:
            provider: LLM provider to use
            api_key: API key (will use env var if not provided)
            model: Specific model to use (uses default if not provided)
            temperature: Generation temperature (0.0-1.0)
        """
        self.provider = provider
        self.temperature = temperature
        
        # Get API key from env if not provided
        if api_key is None:
            if provider == LLMProvider.GEMINI:
                api_key = os.getenv("GEMINI_API_KEY")
            elif provider == LLMProvider.GROQ:
                api_key = os.getenv("GROQ_API_KEY")
        
        self.api_key = api_key
        
        # Set default models
        self.model = model or self._get_default_model()
        
        # Initialize provider-specific client
        self._client = None
        self._initialize_client()
        
        logger.info(f"LLM Client initialized: provider={provider}, model={self.model}")
    
    def _get_default_model(self) -> str:
        """Get default model for provider."""
        defaults = {
            LLMProvider.GEMINI: "gemini-pro",
            LLMProvider.GROQ: "mixtral-8x7b-32768",
            LLMProvider.OLLAMA: "llama2",
        }
        return defaults.get(self.provider, "gemini-pro")
    
    def _initialize_client(self):
        """Initialize provider-specific client."""
        try:
            if self.provider == LLMProvider.GEMINI:
                self._initialize_gemini()
            elif self.provider == LLMProvider.GROQ:
                self._initialize_groq()
            elif self.provider == LLMProvider.OLLAMA:
                self._initialize_ollama()
        except Exception as e:
            logger.error(f"Failed to initialize {self.provider} client: {e}")
            raise
    
    def _initialize_gemini(self):
        """Initialize Google Gemini client."""
        try:
            import google.generativeai as genai
            
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY not found in environment")
            
            genai.configure(api_key=self.api_key)
            self._client = genai.GenerativeModel(self.model)
            
            logger.info("Gemini client initialized successfully")
        except ImportError:
            raise ImportError(
                "google-generativeai not installed. "
                "Install with: pip install google-generativeai"
            )
    
    def _initialize_groq(self):
        """Initialize Groq client."""
        try:
            from groq import Groq
            
            if not self.api_key:
                raise ValueError("GROQ_API_KEY not found in environment")
            
            self._client = Groq(api_key=self.api_key)
            
            logger.info("Groq client initialized successfully")
        except ImportError:
            raise ImportError(
                "groq not installed. "
                "Install with: pip install groq"
            )
    
    def _initialize_ollama(self):
        """Initialize Ollama client (local)."""
        try:
            import ollama
            self._client = ollama
            
            logger.info("Ollama client initialized successfully")
        except ImportError:
            raise ImportError(
                "ollama not installed. "
                "Install with: pip install ollama"
            )
    
    def generate(self, prompt: str, max_tokens: int = 4096) -> str:
        """
        Generate text using the LLM.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
            
        Raises:
            Exception: If generation fails
        """
        try:
            if self.provider == LLMProvider.GEMINI:
                return self._generate_gemini(prompt)
            elif self.provider == LLMProvider.GROQ:
                return self._generate_groq(prompt, max_tokens)
            elif self.provider == LLMProvider.OLLAMA:
                return self._generate_ollama(prompt)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise
    
    def _generate_gemini(self, prompt: str) -> str:
        """Generate with Gemini."""
        response = self._client.generate_content(
            prompt,
            generation_config={
                "temperature": self.temperature,
                "max_output_tokens": 4096,
            }
        )
        return response.text
    
    def _generate_groq(self, prompt: str, max_tokens: int) -> str:
        """Generate with Groq."""
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    
    def _generate_ollama(self, prompt: str) -> str:
        """Generate with Ollama (local)."""
        response = self._client.generate(
            model=self.model,
            prompt=prompt,
            options={"temperature": self.temperature}
        )
        return response["response"]
    
    def extract_json(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract JSON from LLM response.
        
        Handles various formats:
        - Raw JSON array
        - JSON in markdown code blocks
        - JSON with additional text
        
        Args:
            text: LLM response text
            
        Returns:
            Parsed JSON as list of dictionaries
            
        Raises:
            ValueError: If no valid JSON found
        """
        # Remove markdown code blocks if present
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            text = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            text = text[start:end].strip()
        
        # Find JSON array
        start_idx = text.find("[")
        end_idx = text.rfind("]") + 1
        
        if start_idx == -1 or end_idx == 0:
            # Try to find single JSON object and wrap in array
            start_idx = text.find("{")
            end_idx = text.rfind("}") + 1
            if start_idx != -1 and end_idx != 0:
                json_text = "[" + text[start_idx:end_idx] + "]"
            else:
                raise ValueError("No JSON found in response")
        else:
            json_text = text[start_idx:end_idx]
        
        try:
            data = json.loads(json_text)
            if not isinstance(data, list):
                data = [data]
            return data
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}\nText: {json_text[:200]}")
            raise ValueError(f"Invalid JSON in response: {e}")
    
    def test_connection(self) -> bool:
        """
        Test connection to LLM provider.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.generate("Hello, respond with 'OK'")
            return len(response) > 0
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


def create_llm_client(
    provider: Optional[str] = None,
    fallback: bool = True
) -> LLMClient:
    """
    Create LLM client with automatic fallback.
    
    Args:
        provider: Preferred provider (gemini, groq, ollama)
        fallback: Whether to try fallback providers
        
    Returns:
        Initialized LLM client
        
    Raises:
        RuntimeError: If all providers fail
    """
    # Try providers in order of preference
    providers_to_try = []
    
    if provider:
        providers_to_try.append(LLMProvider(provider))
    
    if fallback:
        # Add all providers as fallbacks
        for p in [LLMProvider.GEMINI, LLMProvider.GROQ, LLMProvider.OLLAMA]:
            if p not in providers_to_try:
                providers_to_try.append(p)
    
    last_error = None
    for prov in providers_to_try:
        try:
            client = LLMClient(provider=prov)
            if client.test_connection():
                logger.info(f"Successfully connected to {prov}")
                return client
            else:
                logger.warning(f"Connection test failed for {prov}")
        except Exception as e:
            logger.warning(f"Failed to initialize {prov}: {e}")
            last_error = e
            continue
    
    # All providers failed
    raise RuntimeError(
        f"Failed to connect to any LLM provider. Last error: {last_error}. "
        "Please check your API keys and network connection."
    )

