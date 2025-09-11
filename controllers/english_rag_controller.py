"""
English RAG controller for handling English queries
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from models.english_request_models import EnglishRAGQueryRequest
from models.english_response_models import EnglishRAGQueryResponse
from services.english_relevance_service import EnglishRelevanceService
from services.english_postgres_rag_service import EnglishPostgresRAGService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/rag", tags=["English RAG"])

# Initialize services
relevance_service = EnglishRelevanceService()
rag_service = EnglishPostgresRAGService()


@router.post("/query-english", response_model=EnglishRAGQueryResponse)
async def query_english_rag(request: EnglishRAGQueryRequest) -> EnglishRAGQueryResponse:
    """
    Handle English RAG queries for the Tiger Exhibition
    
    Args:
        request: English RAG query request
        
    Returns:
        EnglishRAGQueryResponse: AI response with sources
    """
    try:
        logger.info(f"English RAG query received: {request.message}")
        
        # Check relevance
        is_relevant = relevance_service.check_relevance(request.message)
        
        if not is_relevant:
            logger.info("Query not relevant to Tiger Exhibition")
            return EnglishRAGQueryResponse(
                response="I'm here to help with questions about the Tiger Exhibition at the National Museum! Please ask me about Korean tiger art, traditional paintings, or the exhibition itself. I'd love to share information about the beautiful tiger artworks on display! 🐯",
                sources=[]
            )
        
        # Generate response using RAG
        result = rag_service.generate_response(
            query=request.message,
            character=request.character
        )
        
        logger.info(f"English RAG response generated: {result['response'][:100]}...")
        
        return EnglishRAGQueryResponse(
            response=result["response"],
            sources=result["sources"]
        )
        
    except Exception as e:
        logger.error(f"Error in English RAG query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing English query: {str(e)}"
        )
