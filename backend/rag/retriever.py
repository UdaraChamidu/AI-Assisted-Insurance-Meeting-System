"""
RAG retrieval service combining embeddings and Pinecone search.
"""

from typing import List, Dict, Any, Optional
from rag.embeddings import embedding_service
from rag.pinecone_client import pinecone_client
import logging

logger = logging.getLogger(__name__)


class RetrieverService:
    """Handles RAG retrieval pipeline."""
    
    def __init__(self):
        self.embedding_service = embedding_service
        self.pinecone_client = pinecone_client
    
    async def retrieve(
        self,
        query: str,
        universe: Optional[str] = None,
        top_k: int = 5,
        min_score: float = 0.7
    ) -> Dict[str, Any]:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: Search query
            universe: Regulatory Universe to filter by (optional)
            top_k: Number of results to return
            min_score: Minimum similarity score
        
        Returns:
            Dict with chunks and metadata
        """
        try:
            logger.info(f"Retrieving context for query: {query[:100]}... Universe: {universe}")
            
            # Construct Filter
            filters = {}
            if universe and universe != "NONE":
                filters['universe'] = universe
            
            # Generate query embedding
            query_embedding = self.embedding_service.embed_query(query)
            
            # Search Pinecone
            results = self.pinecone_client.search(
                query_embedding=query_embedding,
                top_k=top_k,
                filter_dict=filters
            )
            
            # Filter by minimum score
            filtered_results = [
                r for r in results
                if r['score'] >= min_score
            ]
            
            logger.info(f"Retrieved {len(filtered_results)} relevant chunks")
            
            return {
                'query': query,
                'universe': universe,
                'chunks': filtered_results,
                'total_results': len(filtered_results)
            }
            
        except Exception as e:
            logger.error(f"Failed to retrieve context: {str(e)}")
            return {
                'query': query,
                'chunks': [],
                'total_results': 0,
                'error': str(e)
            }
    
    def retrieve_and_rank(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve and rank results by relevance.
        
        Args:
            query: Search query
            top_k: Number of results
        
        Returns:
            Ranked list of chunks
        """
        result = self.retrieve(query, top_k)
        chunks = result.get('chunks', [])
        
        # Sort by score (already sorted by Pinecone, but ensure order)
        ranked_chunks = sorted(
            chunks,
            key=lambda x: x['score'],
            reverse=True
        )
        
        return ranked_chunks


# Global service instance
retriever_service = RetrieverService()
