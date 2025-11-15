"""Service matching engine using TF-IDF and cosine similarity.

This module provides the ServiceMatcher class for matching RFP requirements
to BairesDev services using text similarity algorithms.
"""

from typing import List, Dict, Tuple, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

from models import Service, Requirement, ServiceCategory, RequirementCategory

logger = logging.getLogger(__name__)


class ServiceMatch:
    """Represents a match between a requirement and a service."""
    
    def __init__(
        self,
        requirement_id: str,
        requirement_description: str,
        requirement_category: RequirementCategory,
        service_id: str,
        service_name: str,
        service_category: ServiceCategory,
        score: float,
        reasoning: str = "",
        approved: bool = False
    ):
        self.requirement_id = requirement_id
        self.requirement_description = requirement_description
        self.requirement_category = requirement_category
        self.service_id = service_id
        self.service_name = service_name
        self.service_category = service_category
        self.score = score
        self.reasoning = reasoning
        self.approved = approved
    
    def to_dict(self) -> dict:
        """Convert match to dictionary."""
        return {
            "requirement_id": self.requirement_id,
            "requirement_description": self.requirement_description,
            "requirement_category": self.requirement_category.value,
            "service_id": self.service_id,
            "service_name": self.service_name,
            "service_category": self.service_category.value,
            "score": self.score,
            "reasoning": self.reasoning,
            "approved": self.approved
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ServiceMatch":
        """Create match from dictionary."""
        return cls(
            requirement_id=data["requirement_id"],
            requirement_description=data["requirement_description"],
            requirement_category=RequirementCategory(data["requirement_category"]),
            service_id=data["service_id"],
            service_name=data["service_name"],
            service_category=ServiceCategory(data["service_category"]),
            score=data["score"],
            reasoning=data.get("reasoning", ""),
            approved=data.get("approved", False)
        )


class ServiceMatcher:
    """Match requirements to services using TF-IDF and cosine similarity."""
    
    def __init__(self, services: List[Service]):
        """Initialize matcher with service catalog.
        
        Args:
            services: List of available services
        """
        self.services = services
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.service_vectors: Optional[np.ndarray] = None
        
        # Initialize vectorizer
        self._initialize_vectorizer()
        
        logger.info(f"ServiceMatcher initialized with {len(services)} services")
    
    def _initialize_vectorizer(self):
        """Initialize TF-IDF vectorizer and compute service vectors."""
        if not self.services:
            logger.warning("No services provided to ServiceMatcher")
            return
        
        # Create vectorizer optimized for technical keyword matching
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            lowercase=True,
            max_features=1000,
            ngram_range=(1, 2),  # unigrams and bigrams
            min_df=1,  # Keep even rare terms (technical keywords)
            norm='l2',
            # Use smooth_idf to prevent zero divisions
            smooth_idf=True,
            # Don't use sublinear_tf - we want technical terms to have high weight
            sublinear_tf=False
        )
        
        # Get service texts
        service_texts = [service.get_full_text() for service in self.services]
        
        # Fit and transform
        self.service_vectors = self.vectorizer.fit_transform(service_texts)
        
        logger.debug(f"Vectorizer initialized with vocabulary size: {len(self.vectorizer.vocabulary_)}")
    
    def match_requirement(
        self,
        requirement: Requirement,
        top_n: int = 3,
        min_score: float = 0.0
    ) -> List[ServiceMatch]:
        """Match a single requirement to services.
        
        Args:
            requirement: Requirement to match
            top_n: Number of top matches to return (default: 3)
            min_score: Minimum similarity score (0.0-1.0, default: 0.0)
            
        Returns:
            List of ServiceMatch objects sorted by score (highest first)
        """
        if not self.services or self.vectorizer is None or self.service_vectors is None:
            logger.warning("ServiceMatcher not properly initialized")
            return []
        
        # Vectorize requirement
        req_text = requirement.description
        req_vector = self.vectorizer.transform([req_text])
        
        # Compute cosine similarity
        similarities = cosine_similarity(req_vector, self.service_vectors)[0]
        
        # Apply category bonus: +15% boost if categories match
        # This helps prioritize services in the same domain but doesn't overwhelm text similarity
        adjusted_similarities = similarities.copy()
        for idx, service in enumerate(self.services):
            if requirement.category.value == service.category.value:
                # Add 15% bonus but cap at 1.0
                adjusted_similarities[idx] = min(1.0, similarities[idx] + 0.15)
        
        # Get top N matches (use adjusted scores for ranking)
        top_indices = np.argsort(adjusted_similarities)[::-1][:top_n]
        
        matches = []
        for idx in top_indices:
            score = float(adjusted_similarities[idx])
            base_score = float(similarities[idx])
            
            # Skip if below minimum score
            if score < min_score:
                continue
            
            service = self.services[idx]
            
            # Generate reasoning (include bonus info if category matched)
            category_bonus = score - base_score if score > base_score else 0.0
            reasoning = self._generate_reasoning(
                requirement,
                service,
                score,
                category_bonus
            )
            
            # Create match
            match = ServiceMatch(
                requirement_id=requirement.id,
                requirement_description=requirement.description,
                requirement_category=requirement.category,
                service_id=service.id,
                service_name=service.name,
                service_category=service.category,
                score=score,
                reasoning=reasoning,
                approved=(score >= 0.80)  # Auto-approve high matches
            )
            
            matches.append(match)
        
        logger.debug(f"Matched requirement '{requirement.description[:50]}...' to {len(matches)} services")
        
        return matches
    
    def match_all_requirements(
        self,
        requirements: List[Requirement],
        top_n: int = 5,  # Increased to show more potential matches
        min_score: float = 0.25  # Lowered to be more permissive
    ) -> List[ServiceMatch]:
        """Match all requirements to services (batch processing).
        
        Args:
            requirements: List of requirements to match
            top_n: Number of top matches per requirement
            min_score: Minimum similarity score (default: 0.3 = 30%)
            
        Returns:
            List of all matches across all requirements
        """
        if not requirements:
            logger.warning("No requirements provided to match")
            return []
        
        all_matches = []
        
        for requirement in requirements:
            matches = self.match_requirement(
                requirement,
                top_n=top_n,
                min_score=min_score
            )
            all_matches.extend(matches)
        
        logger.info(f"Matched {len(requirements)} requirements, generated {len(all_matches)} matches")
        
        return all_matches
    
    def _generate_reasoning(
        self,
        requirement: Requirement,
        service: Service,
        score: float,
        category_bonus: float = 0.0
    ) -> str:
        """Generate human-readable reasoning for a match.
        
        Args:
            requirement: Matched requirement
            service: Matched service
            score: Final similarity score (after bonuses)
            category_bonus: Bonus applied for category match
            
        Returns:
            Reasoning text
        """
        # Find common keywords (simple approach)
        req_words = set(requirement.description.lower().split())
        service_words = set(service.get_full_text().lower().split())
        common_words = req_words.intersection(service_words)
        
        # Filter out stopwords (basic filter)
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        common_keywords = [w for w in common_words if w not in stopwords and len(w) > 3]
        
        # Build reasoning
        if score >= 0.80:
            strength = "Strong match"
        elif score >= 0.50:
            strength = "Moderate match"
        else:
            strength = "Weak match"
        
        reasoning_parts = [
            f"{strength} ({score:.0%})."
        ]
        
        # Show category bonus if applied
        if category_bonus > 0.01:
            base_score = score - category_bonus
            reasoning_parts.append(f"Base similarity: {base_score:.0%}, +{category_bonus:.0%} category bonus.")
        
        if common_keywords:
            top_keywords = sorted(common_keywords)[:5]
            reasoning_parts.append(f"Common keywords: {', '.join(top_keywords)}.")
        
        # Category match info
        if requirement.category.value == service.category.value:
            reasoning_parts.append(f"Category alignment: both {requirement.category.value}.")
        
        return " ".join(reasoning_parts)
    
    def calculate_coverage_by_category(
        self,
        matches: List[ServiceMatch]
    ) -> Dict[str, float]:
        """Calculate average match score by requirement category.
        
        Args:
            matches: List of service matches
            
        Returns:
            Dict mapping category name to average match score (0.0-1.0)
        """
        if not matches:
            return {}
        
        # Group matches by requirement category
        category_scores: Dict[str, List[float]] = {}
        
        for match in matches:
            category = match.requirement_category.value
            if category not in category_scores:
                category_scores[category] = []
            category_scores[category].append(match.score)
        
        # Calculate averages
        coverage = {}
        for category, scores in category_scores.items():
            coverage[category] = sum(scores) / len(scores) if scores else 0.0
        
        return coverage
    
    def get_overall_coverage(self, matches: List[ServiceMatch]) -> float:
        """Get overall average match score across all matches.
        
        Args:
            matches: List of service matches
            
        Returns:
            Average match score (0.0-1.0)
        """
        if not matches:
            return 0.0
        
        return sum(match.score for match in matches) / len(matches)
    
    def count_approved_matches(self, matches: List[ServiceMatch]) -> Tuple[int, int]:
        """Count approved vs. total matches.
        
        Args:
            matches: List of service matches
            
        Returns:
            Tuple of (approved_count, total_count)
        """
        approved = sum(1 for match in matches if match.approved)
        total = len(matches)
        return approved, total
    
    @staticmethod
    def color_for_score(score: float) -> str:
        """Get color emoji/indicator for match score.
        
        Args:
            score: Match score (0.0-1.0)
            
        Returns:
            Color indicator: 🟢 (green), 🟡 (yellow), or 🔴 (red)
        """
        if score >= 0.80:
            return "🟢"  # Green - Strong match
        elif score >= 0.50:
            return "🟡"  # Yellow - Moderate match
        else:
            return "🔴"  # Red - Weak match

