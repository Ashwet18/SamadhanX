"""
AI provider abstraction for challenge analysis.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
import json
from openai import OpenAI

from app.core.config import settings
from app.services.ai.schemas import AIAnalysisResult
from app.services.ai.prompts import SYSTEM_PROMPT, build_analysis_prompt


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    def analyze_challenge(
        self,
        title: str,
        description: str,
        district: str,
        categories: List[str]
    ) -> AIAnalysisResult:
        """
        Analyze a challenge and return structured results.
        
        Args:
            title: Challenge title
            description: Challenge description
            district: District name
            categories: Existing categories
            
        Returns:
            AI analysis result
        """
        pass
    
    @abstractmethod
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        pass
    
    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """
        Get embedding dimension for this provider.
        
        Returns:
            Embedding dimension
        """
        pass


class OpenAIProvider(AIProvider):
    """OpenAI implementation of AI provider."""
    
    def __init__(self, api_key: str, model: str, embedding_model: str):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            model: LLM model name
            embedding_model: Embedding model name
        """
        self.api_key = api_key
        self.model = model
        self.embedding_model = embedding_model
        
        # Configure OpenAI client
        self.client = OpenAI(api_key=api_key)
        
        # Set embedding dimension based on model
        self.embedding_dimensions = {
            "text-embedding-ada-002": 1536,
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072
        }
    
    def analyze_challenge(
        self,
        title: str,
        description: str,
        district: str,
        categories: List[str]
    ) -> AIAnalysisResult:
        """Analyze challenge using OpenAI."""
        
        # Build prompt
        user_prompt = build_analysis_prompt(title, description, district, categories)
        
        try:
            # Call OpenAI API (new SDK v1.x)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=settings.AI_TEMPERATURE,
                max_tokens=settings.MAX_TOKENS,
                response_format={"type": "json_object"}  # Force JSON mode
            )
            
            # Extract response
            result_text = response.choices[0].message.content
            result_json = json.loads(result_text)
            
            # Validate and parse with Pydantic
            analysis = AIAnalysisResult(**result_json)
            
            return analysis
            
        except json.JSONDecodeError as e:
            raise ValueError(f"AI returned invalid JSON: {e}")
        except Exception as e:
            raise RuntimeError(f"AI analysis failed: {e}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI."""
        
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            
            embedding = response.data[0].embedding
            return embedding
            
        except Exception as e:
            raise RuntimeError(f"Embedding generation failed: {e}")
    
    def get_embedding_dimension(self) -> int:
        """Get embedding dimension."""
        return self.embedding_dimensions.get(self.embedding_model, 1536)


class MockAIProvider(AIProvider):
    """Mock provider for testing without API key."""
    
    def __init__(self):
        """Initialize mock provider."""
        self.calls = []
    
    def analyze_challenge(
        self,
        title: str,
        description: str,
        district: str,
        categories: List[str]
    ) -> AIAnalysisResult:
        """Return mock analysis."""
        
        self.calls.append(("analyze", title))
        
        # Deterministic mock response
        return AIAnalysisResult(
            summary=f"Mock analysis for: {title[:50]}",
            detected_language="en",
            classification={
                "primary_domain": categories[0] if categories else "Water Management",
                "secondary_domains": [],
                "confidence_score": 0.85,
                "classification_reason": "Mock classification for testing"
            },
            severity={
                "severity_score": 75,
                "severity_reason": "Mock severity assessment"
            },
            urgency={
                "urgency_score": 70,
                "urgency_reason": "Mock urgency assessment"
            },
            skills=[
                {"name": "IoT", "confidence": 0.9},
                {"name": "Data Science", "confidence": 0.8}
            ],
            solution_types=[
                {"type": "IoT monitoring system", "confidence": 0.85}
            ],
            affected_population_estimate=None,
            confidence_score=0.80
        )
    
    def generate_embedding(self, text: str) -> List[float]:
        """Return mock embedding."""
        
        self.calls.append(("embed", text[:30]))
        
        # Return deterministic mock embedding (1536 dimensions)
        import hashlib
        hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
        
        # Generate pseudo-random but deterministic embedding
        embedding = []
        for i in range(1536):
            val = ((hash_val + i) % 10000) / 10000.0 - 0.5
            embedding.append(val)
        
        return embedding
    
    def get_embedding_dimension(self) -> int:
        """Get embedding dimension."""
        return 1536


def get_ai_provider() -> AIProvider:
    """
    Get configured AI provider instance.
    
    Returns:
        AI provider
        
    Raises:
        ValueError: If AI is not properly configured
    """
    
    # Check if OpenAI is configured
    if settings.OPENAI_API_KEY:
        return OpenAIProvider(
            api_key=settings.OPENAI_API_KEY,
            model=settings.LLM_MODEL,
            embedding_model=settings.EMBEDDING_MODEL
        )
    
    # Fall back to mock provider for development
    # WARNING: This should never be used in production
    print("WARNING: No AI API key configured. Using MockAIProvider for testing only.")
    return MockAIProvider()
