"""
Pinecone client for vector database operations.
"""

from pinecone import Pinecone, ServerlessSpec
from config import settings
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PineconeClient:
    """Handles Pinecone vector database operations."""
    
    def __init__(self):
        self.api_key = settings.pinecone_api_key
        self.environment = settings.pinecone_environment
        self.index_name = settings.pinecone_index_name
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=self.api_key)
        self.index = None
        
        # Initialize index
        self._ensure_index_exists()
    
    def _ensure_index_exists(self):
        """Create index if it doesn't exist."""
        try:
            # Check if index exists
            existing_indexes = self.pc.list_indexes().names()
            
            if self.index_name not in existing_indexes:
                logger.info(f"Creating Pinecone index: {self.index_name}")
                
                # Create index with serverless spec
                self.pc.create_index(
                    name=self.index_name,
                    dimension=768,  # Google embedding dimension
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
                logger.info(f"Created index: {self.index_name}")
            
            # Connect to index
            self.index = self.pc.Index(self.index_name)
            logger.info(f"Connected to Pinecone index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone index: {str(e)}")
            raise
    
    def upsert_chunks(
        self,
        chunks: List[Dict[str, Any]],
        batch_size: int = 100
    ) -> int:
        """
        Upsert document chunks with embeddings.
        
        Args:
            chunks: List of dicts with 'id', 'embedding', and 'metadata'
            batch_size: Number of vectors to upsert at once
        
        Returns:
            Number of vectors upserted
        """
        try:
            total_upserted = 0
            
            # Process in batches
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                
                # Format for Pinecone
                vectors = [
                    {
                        'id': chunk['id'],
                        'values': chunk['embedding'],
                        'metadata': chunk.get('metadata', {})
                    }
                    for chunk in batch
                ]
                
                # Upsert batch
                self.index.upsert(vectors=vectors)
                total_upserted += len(vectors)
                
                logger.info(f"Upserted batch {i//batch_size + 1}, total: {total_upserted}")
            
            logger.info(f"Successfully upserted {total_upserted} vectors")
            return total_upserted
            
        except Exception as e:
            logger.error(f"Failed to upsert chunks: {str(e)}")
            raise
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            filter_dict: Optional metadata filter
        
        Returns:
            List of matches with metadata and scores
        """
        try:
            # Query index
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )
            
            # Format results
            matches = []
            for match in results.matches:
                matches.append({
                    'id': match.id,
                    'score': match.score,
                    'metadata': match.metadata,
                    'text': match.metadata.get('text', '')
                })
            
            logger.info(f"Found {len(matches)} matches")
            return matches
            
        except Exception as e:
            logger.error(f"Failed to search: {str(e)}")
            return []
    
    def delete_all(self):
        """Delete all vectors from the index."""
        try:
            self.index.delete(delete_all=True)
            logger.info("Deleted all vectors from index")
        except Exception as e:
            logger.error(f"Failed to delete vectors: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        try:
            stats = self.index.describe_index_stats()
            return {
                'total_vectors': stats.total_vector_count,
                'dimension': stats.dimension
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {str(e)}")
            return {}

# Global client instance (lazy initialization)
_pinecone_client_instance = None


def get_pinecone_client() -> Optional[PineconeClient]:
    """Get or create Pinecone client instance (lazy initialization)."""
    global _pinecone_client_instance
    
    if _pinecone_client_instance is None:
        try:
            # Check if we have valid credentials
            if (settings.pinecone_api_key.startswith("dummy_") or 
                settings.pinecone_environment.startswith("dummy_")):
                logger.warning("Pinecone not configured - using dummy credentials. RAG features will be disabled.")
                return None
            
            _pinecone_client_instance = PineconeClient()
            logger.info("Pinecone client initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Pinecone client: {e}. RAG features will be disabled.")
            return None
    
    return _pinecone_client_instance


# For backward compatibility
pinecone_client = get_pinecone_client()
