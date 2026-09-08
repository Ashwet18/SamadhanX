"""
Semantic duplicate detection using pgvector.
"""

from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.challenge import Challenge, ChallengeEmbedding
from app.services.ai.schemas import DuplicateCandidate


class DuplicateDetector:
    """Semantic duplicate detection service."""
    
    # Similarity thresholds
    HIGH_CONFIDENCE_THRESHOLD = 0.90
    POSSIBLE_DUPLICATE_THRESHOLD = 0.80
    
    def __init__(self, db: Session):
        """
        Initialize duplicate detector.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def find_duplicates(
        self,
        embedding: List[float],
        challenge_id: UUID,
        threshold: float = 0.80,
        limit: int = 5
    ) -> List[DuplicateCandidate]:
        """
        Find similar challenges using cosine similarity.
        
        Args:
            embedding: Query embedding vector
            challenge_id: Current challenge ID (to exclude self)
            threshold: Minimum similarity threshold
            limit: Maximum number of results
            
        Returns:
            List of duplicate candidates
        """
        
        # Use pgvector cosine similarity
        # Cosine similarity: 1 - (embedding <=> query_embedding)
        query = text("""
            SELECT 
                c.id,
                c.challenge_code,
                c.title,
                1 - (ce.embedding <=> :embedding) as similarity
            FROM challenge_embeddings ce
            JOIN challenges c ON ce.challenge_id = c.id
            WHERE ce.challenge_id != :challenge_id
            AND 1 - (ce.embedding <=> :embedding) >= :threshold
            ORDER BY similarity DESC
            LIMIT :limit
        """)
        
        # Convert embedding to string format for pgvector
        embedding_str = f"[{','.join(map(str, embedding))}]"
        
        result = self.db.execute(
            query,
            {
                "embedding": embedding_str,
                "challenge_id": str(challenge_id),
                "threshold": threshold,
                "limit": limit
            }
        )
        
        # Build duplicate candidates
        candidates = []
        for row in result:
            candidates.append(DuplicateCandidate(
                challenge_id=str(row.id),
                challenge_code=row.challenge_code,
                title=row.title,
                similarity_score=float(row.similarity)
            ))
        
        return candidates
    
    def classify_similarity(self, score: float) -> str:
        """
        Classify similarity score.
        
        Args:
            score: Similarity score
            
        Returns:
            Classification: HIGH_CONFIDENCE, POSSIBLE, or LOW
        """
        if score >= self.HIGH_CONFIDENCE_THRESHOLD:
            return "HIGH_CONFIDENCE"
        elif score >= self.POSSIBLE_DUPLICATE_THRESHOLD:
            return "POSSIBLE"
        else:
            return "LOW"
