"""
요청 모델 정의
"""
from typing import List
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., description="유저의 채팅 메시지", example="안녕하세요! 케이팝에 대해 알려주세요")
    character: str = Field(default="rumi", description="챗봇 페르소나", example="rumi")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "안녕하세요! 케이팝에 대해 알려주세요",
                "character": "rumi"
            }
        }


class ConversationMessage(BaseModel):
    role: str = Field(..., description="메시지 역할 (user, assistant, system)")
    content: str = Field(..., description="메시지 내용")
    timestamp: str = Field(None, description="메시지 시간 (선택사항)")


class ConversationSummaryRequest(BaseModel):
    session_id: str = Field(..., description="대화 세션 ID")
    messages: List[ConversationMessage] = Field(..., description="대화 메시지 리스트")
    count: int = Field(default=10, description="생성할 요약 문장 개수", ge=1, le=20)

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "messages": [
                    {
                        "role": "user",
                        "content": "안녕하세요! 이번 전시 테마에에 대해 알려주세요",
                        "timestamp": "2024-01-01T10:00:00Z"
                    },
                    {
                        "role": "assistant", 
                        "content": "안녕하세요! 이번 전시는 ~~~...",
                        "timestamp": "2024-01-01T10:00:30Z"
                    }
                ],
                "count": 10
            }
        }
