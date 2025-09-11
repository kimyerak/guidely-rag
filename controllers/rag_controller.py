"""
RAG 컨트롤러
"""
from fastapi import APIRouter, Depends
from models.request_models import ChatRequest
from models.response_models import ChatResponse
from services.postgres_rag_service import PostgresRAGService
from services.relevance_service import RelevanceService
from characters import CHARACTER_STYLE
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["RAG"])


def get_rag_service() -> PostgresRAGService:
    """RAG 서비스 의존성 주입"""
    return PostgresRAGService()


def get_relevance_service() -> RelevanceService:
    """관련성 검증 서비스 의존성 주입"""
    return RelevanceService()


@router.post("/query", response_model=ChatResponse)
async def generate_chat_response(
    req: ChatRequest,
    rag_service: PostgresRAGService = Depends(get_rag_service),
    relevance_service: RelevanceService = Depends(get_relevance_service)
):
    """
    전시회용 인터랙티브 음성 챗봇 API
    
    유저의 메시지를 받아 관련 문서를 참고하여 자연스러운 답변을 생성합니다.
    
    **Parameters:**
    - **message**: 유저의 채팅 메시지
    - **character**: 챗봇 페르소나 (rumi, mira, zoey, jinu)
    
    **Returns:**
    - **response**: 챗봇의 자연스러운 답변
    - **sources**: 참고한 문서 출처 (있는 경우)
    
    **Example Request:**
    ```json
    {
        "message": "안녕하세요! 케이팝에 대해 알려주세요",
        "character": "rumi"
    }
    ```
    
    **Example Response:**
    ```json
    {
        "response": "안녕하세요! 케이팝에 대해 궁금하시군요. 케이팝은...",
        "sources": [
            {
                "source": "https://namu.wiki/w/케이팝",
                "content": "케이팝 관련 내용..."
            }
        ]
    }
    ```
    """
    user_message = req.message
    character = req.character
    
    # 관련성 검증
    if not relevance_service.check_relevance(user_message):
        char_style = CHARACTER_STYLE[character]
        return ChatResponse(
            response=f"안녕하세요! 저는 국립중앙박물관 호랑이 전시의 챗봇입니다! 🐅\n\n호랑이 전시에 대해 궁금한 것이 있으시면 언제든 물어보세요!✨",
            sources=[]
        )
    
    # RAG 서비스를 통한 응답 생성
    return rag_service.generate_response(user_message, character)
