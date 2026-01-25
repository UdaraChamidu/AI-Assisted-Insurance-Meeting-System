"""
AI query API routes.
"""

from fastapi import APIRouter, HTTPException
from models import RAGQuery, AIResponse
from rag.retriever import retriever_service
from services.gemini_service import gemini_service
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/query", response_model=AIResponse)
async def query_ai(request: RAGQuery):
    """
    Query the AI system with RAG context.
    Returns AI-generated answer with context.
    """
    try:
        logger.info(f"AI query: {request.query[:100]}")
        
        # Retrieve context
        rag_result = retriever_service.retrieve(
            query=request.query,
            top_k=request.top_k
        )
        
        # Generate AI response
        ai_result = gemini_service.generate_response(
            query=request.query,
            context_chunks=rag_result['chunks']
        )
        
        # Build response
        response = AIResponse(
            answer=ai_result['answer'],
            follow_up_question=ai_result.get('follow_up_question'),
            confidence=ai_result['confidence'],
            rag_context={
                'chunks': rag_result['chunks'],
                'query': request.query,
                'total_results': rag_result['total_results']
            },
            timestamp=datetime.utcnow()
        )
        
        return response
        
    except Exception as e:
        logger.error(f"AI query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/context/{query}")
async def get_context(query: str, top_k: int = 5):
    """
    Get RAG context only (without AI generation).
    Useful for debugging and testing retrieval.
    """
    try:
        result = retriever_service.retrieve(query=query, top_k=top_k)
        return result
    except Exception as e:
        logger.error(f"Context retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=AIResponse)
async def chat_ai(request: RAGQuery):
    """
    Simple Chat with AI (No RAG).
    Direct LLM interaction for simple queries.
    """
    try:
        logger.info(f"AI chat query: {request.query[:100]}")
        
        # Generate AI response with EMPTY context
        ai_result = gemini_service.generate_response(
            query=request.query,
            context_chunks=[] 
        )
        
        # Build response
        response = AIResponse(
            answer=ai_result['answer'],
            follow_up_question=ai_result.get('follow_up_question'),
            confidence=ai_result['confidence'],
            rag_context=None,
            timestamp=datetime.utcnow()
        )
        
        return response
        
    except Exception as e:
        logger.error(f"AI chat failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
