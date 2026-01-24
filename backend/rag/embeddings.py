"""
Document embedding service using Google's embedding models.
"""

import google.generativeai as genai
from config import settings
from typing import List, Dict, Any
import hashlib
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Handles text embedding generation."""
    
    def __init__(self):
        genai.configure(api_key=settings.google_api_key)
        self.model_name = 'models/embedding-001'
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector
        """
        try:
            result = genai.embed_content(
                model=self.model_name,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Failed to embed text: {str(e)}")
            raise
    
    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a search query.
        
        Args:
            query: Query text
        
        Returns:
            Embedding vector
        """
        try:
            result = genai.embed_content(
                model=self.model_name,
                content=query,
                task_type="retrieval_query"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Failed to embed query: {str(e)}")
            raise
    
    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts per batch
        
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                # Process batch
                for text in batch:
                    embedding = self.embed_text(text)
                    embeddings.append(embedding)
                
                logger.info(f"Embedded batch {i//batch_size + 1}, total: {len(embeddings)}")
                
            except Exception as e:
                logger.error(f"Failed to embed batch: {str(e)}")
                # Add empty embedding for failed items
                embeddings.extend([[0.0] * 768] * len(batch))
        
        return embeddings


def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100
) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Text to chunk
        chunk_size: Target chunk size in characters
        chunk_overlap: Overlap between chunks
    
    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to break at sentence boundary
        if end < text_length:
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            break_point = max(last_period, last_newline)
            
            if break_point > chunk_size // 2:  # Only break if not too early
                chunk = chunk[:break_point + 1]
                end = start + break_point + 1
        
        chunks.append(chunk.strip())
        start = end - chunk_overlap
    
    return [c for c in chunks if c]  # Remove empty chunks


def generate_chunk_id(text: str, source: str, index: int) -> str:
    """
    Generate a unique ID for a chunk.
    
    Args:
        text: Chunk text
        source: Source document name
        index: Chunk index
    
    Returns:
        Unique chunk ID
    """
    content = f"{source}:{index}:{text[:100]}"
    return hashlib.md5(content.encode()).hexdigest()


# Global service instance
embedding_service = EmbeddingService()
