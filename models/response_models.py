"""
응답 모델 정의
"""
from typing import List
from pydantic import BaseModel, Field


class ChatResponse(BaseModel):
    response: str = Field(..., description="챗봇의 자연스러운 답변")
    sources: List[dict] = Field(..., description="참고한 문서 출처")

    class Config:
        json_schema_extra = {
            "example": {
                "response": "안녕하세요! 호랑이 전시에 대해 궁금하시군요. 호랑이는...",
                "sources": [
                    {
                        "source": "문서: 국립중앙박물관 호랑이 전시",
                        "content": "호랑이 전시회에 대한 내용...",
                        "ranking": 1,
                        "similarity_score": 0.8234,
                        "document_title": "국립중앙박물관 호랑이 전시",
                        "chunk_id": 123
                    },
                    {
                        "source": "문서: 호작도 작품 설명",
                        "content": "호작도는 까치와 호랑이 그림으로...",
                        "ranking": 2,
                        "similarity_score": 0.7891,
                        "document_title": "호작도 작품 설명",
                        "chunk_id": 124
                    }
                ]
            }
        }


class ConversationSummaryResponse(BaseModel):
    session_id: int = Field(..., description="대화 세션 ID")
    total_messages: int = Field(..., description="총 메시지 개수")
    summaries: List[str] = Field(..., description="대화 요약 문장들")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": 12345,
                "total_messages": 12,
                "summaries": [
                    "까치 문양, 전통 속에서 되살아난 날개짓",
                    "미라가 던진 질문에 상상력이 끝없이 번져갔어",
                    "모네의 붓끝에서 피어난 빛의 향연을 만났길",
                    "인상주의 화가들의 혁신적인 시선을 발견하다"
                ]
            }
        }
