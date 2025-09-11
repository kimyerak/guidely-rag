"""
English summary controller for handling English conversation summaries
"""
import logging
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from models.english_request_models import EnglishConversationSummaryRequest
from models.english_response_models import EnglishConversationSummaryResponse
from services.english_summary_service import EnglishSummaryService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/rag", tags=["English Summary"])

# Initialize service
summary_service = EnglishSummaryService()


@router.post("/summarize-english", response_model=EnglishConversationSummaryResponse)
async def summarize_english_conversation(request: EnglishConversationSummaryRequest) -> EnglishConversationSummaryResponse:
    """
    Generate English summary of conversation about the Tiger Exhibition
    
    Args:
        request: English conversation summary request
        
    Returns:
        EnglishConversationSummaryResponse: Summary with key topics
    """
    try:
        logger.info(f"English summary request received for session {request.session_id}")
        
        # Generate summary
        result = summary_service.generate_summary(
            messages=request.messages,
            session_id=request.session_id
        )
        
        logger.info(f"English summary generated: {result['summary'][:100]}...")
        
        return EnglishConversationSummaryResponse(
            session_id=result["session_id"],
            summary=result["summary"],
            key_topics=result["key_topics"]
        )
        
    except Exception as e:
        logger.error(f"Error in English summary generation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating English summary: {str(e)}"
        )
