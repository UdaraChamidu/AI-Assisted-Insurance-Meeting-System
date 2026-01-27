import google.generativeai as genai
from openai import OpenAI
from config import settings
from typing import List, Dict, Any
import hashlib
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Handles text embedding generation."""
    
    def __init__(self):
        self.provider = settings.ai_provider.lower()
        self.dimension = 1024 if self.provider == 'openai' else 768
        
        if self.provider == 'openai':
            self.client = OpenAI(api_key=settings.openai_api_key)
            self.model_name = 'text-embedding-3-small'
            logger.info("Initialized EmbeddingService with OpenAI (1024 dims)")
        else:
            genai.configure(api_key=settings.google_api_key)
            self.model_name = 'models/embedding-001'
            logger.info("Initialized EmbeddingService with Google Gemini (768 dims)")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        """
        try:
            if self.provider == 'openai':
                resp = self.client.embeddings.create(
                    input=text,
                    model=self.model_name,
                    dimensions=1024
                )
                return resp.data[0].embedding
            else:
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
        """
        try:
            if self.provider == 'openai':
                resp = self.client.embeddings.create(
                    input=query,
                    model=self.model_name,
                    dimensions=1024
                )
                return resp.data[0].embedding
            else:
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
        """
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                # Process batch
                if self.provider == 'openai':
                     resp = self.client.embeddings.create(
                        input=batch,
                        model=self.model_name,
                        dimensions=1024
                    )
                     # OpenAI returns list of embedding objects in order
                     batch_embeddings = [d.embedding for d in resp.data]
                     embeddings.extend(batch_embeddings)
                else:
                    # Google doesn't have a clean batch API in this SDK setup easily, 
                    # so we loop (as before) or improved logic. Keeping loop for safety.
                    for text in batch:
                        embedding = self.embed_text(text)
                        embeddings.append(embedding)
                
                logger.info(f"Embedded batch {i//batch_size + 1}, total: {len(embeddings)}")
                
            except Exception as e:
                logger.error(f"Failed to embed batch: {str(e)}")
                # Add empty embedding for failed items
                embeddings.extend([[0.0] * self.dimension] * len(batch))
        
        return embeddings


def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100
) -> List[str]:
    """
    Split text into overlapping chunks.
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
    """
    content = f"{source}:{index}:{text[:100]}"
    return hashlib.md5(content.encode()).hexdigest()


# Global service instance
embedding_service = EmbeddingService()
