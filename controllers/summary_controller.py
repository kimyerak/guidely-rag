"""
요약 컨트롤러
"""
from fastapi import APIRouter, Depends
from models.request_models import ConversationSummaryRequest
from models.response_models import ConversationSummaryResponse
from services.summary_service import SummaryService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["RAG"])


def get_summary_service() -> SummaryService:
    """요약 서비스 의존성 주입"""
    return SummaryService()


@router.post("/summarize", response_model=ConversationSummaryResponse)
async def summarize_conversation(
    req: ConversationSummaryRequest,
    summary_service: SummaryService = Depends(get_summary_service)
):
    """
    엔딩크레딧용 대화 요약 API
    
    대화 내용을 분석하여 감성적이고 시적인 한 줄 요약들을 생성합니다.
    
    **Parameters:**
    - **session_id**: 대화 세션 ID
    - **messages**: 대화 메시지 리스트
    - **count**: 생성할 요약 문장 개수 (1-20)
    
    **Returns:**
    - **session_id**: 대화 세션 ID
    - **total_messages**: 총 메시지 개수
    - **summaries**: 감성적인 한 줄 요약들
    """
    return summary_service.generate_summary(req.session_id, req.messages, req.count)
