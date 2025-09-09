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
                "response": "안녕하세요! 케이팝에 대해 궁금하시군요. 케이팝은...",
                "sources": [
                    {
                        "source": "https://namu.wiki/w/케이팝",
                        "content": "케이팝 관련 내용..."
                    }
                ]
            }
        }


class ConversationSummaryResponse(BaseModel):
    session_id: str = Field(..., description="대화 세션 ID")
    total_messages: int = Field(..., description="총 메시지 개수")
    summaries: List[str] = Field(..., description="대화 요약 문장들")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "total_messages": 12,
                "summaries": [
                    "까치 문양, 전통 속에서 되살아난 날개짓",
                    "미라가 던진 질문에 상상력이 끝없이 번져갔어",
                    "모네의 붓끝에서 피어난 빛의 향연을 만났길",
                    "인상주의 화가들의 혁신적인 시선을 발견하다"
                ]
            }
        }
