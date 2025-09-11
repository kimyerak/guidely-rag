"""
Summary Statistics Controller
통계 관련 API 엔드포인트
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/summary-statistics", tags=["Summary Statistics"])


class EndingCreditsRequest(BaseModel):
    session_id: int
    messages: List[Dict[str, Any]]


class EndingCreditsResponse(BaseModel):
    summary: str
    highlights: List[str]
    word_cloud_data: List[Dict[str, Any]]


class WordFrequencyResponse(BaseModel):
    words: List[Dict[str, Any]]
    total_words: int


class ConversationResponse(BaseModel):
    conversation_id: str
    summary: str
    word_frequency: List[Dict[str, Any]]
    highlights: List[str]


@router.post("/ending-credits", response_model=EndingCreditsResponse)
async def generate_ending_credits(request: EndingCreditsRequest):
    """
    엔딩 크레딧용 요약 및 통계 생성
    """
    try:
        # 임시 데이터 - 실제로는 데이터베이스에서 가져와야 함
        mock_data = {
            "summary": "케이팝데몬헌터스 전시회에서의 멋진 대화였습니다!",
            "highlights": [
                "케이팝의 역사에 대해 깊이 있게 대화",
                "미술 작품의 아름다움을 감상",
                "전시회의 의미를 되새김"
            ],
            "word_cloud_data": [
                {"text": "케이팝", "size": 25},
                {"text": "예술", "size": 22},
                {"text": "미술", "size": 20},
                {"text": "전시회", "size": 18},
                {"text": "아름다움", "size": 16}
            ]
        }
        return EndingCreditsResponse(**mock_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/word-frequency", response_model=WordFrequencyResponse)
async def get_word_frequency():
    """
    전체 단어 빈도 통계 조회
    """
    try:
        # 임시 데이터 - 실제로는 데이터베이스에서 집계해야 함
        mock_data = {
            "words": [
                {"text": "케이팝", "frequency": 45, "size": 25},
                {"text": "예술", "frequency": 38, "size": 22},
                {"text": "미술", "frequency": 32, "size": 20},
                {"text": "전시회", "frequency": 28, "size": 18},
                {"text": "아름다움", "frequency": 25, "size": 16},
                {"text": "역사", "frequency": 22, "size": 15},
                {"text": "문화", "frequency": 20, "size": 14},
                {"text": "전통", "frequency": 18, "size": 13}
            ],
            "total_words": 228
        }
        return WordFrequencyResponse(**mock_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation_statistics(conversation_id: str):
    """
    특정 대화의 통계 조회
    """
    try:
        # 임시 데이터 - 실제로는 데이터베이스에서 조회해야 함
        mock_data = {
            "conversation_id": conversation_id,
            "summary": f"대화 {conversation_id}의 요약",
            "word_frequency": [
                {"text": "케이팝", "frequency": 12, "size": 20},
                {"text": "예술", "frequency": 8, "size": 16},
                {"text": "미술", "frequency": 6, "size": 14}
            ],
            "highlights": [
                "케이팝의 역사에 대한 대화",
                "미술 작품 감상"
            ]
        }
        return ConversationResponse(**mock_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
