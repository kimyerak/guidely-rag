"""
English request models for RAG API
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class EnglishRAGQueryRequest(BaseModel):
    """English RAG query request model"""
    character: str = Field(..., description="Character name (rumi, yuna, etc.)")
    message: str = Field(..., description="User message in English")
    
    class Config:
        json_schema_extra = {
            "example": {
                "character": "rumi",
                "message": "What is the Tiger Exhibition about?"
            }
        }


class EnglishConversationSummaryRequest(BaseModel):
    """English conversation summary request model"""
    session_id: int = Field(..., description="Session ID", example=12345)
    messages: List[dict] = Field(..., description="List of conversation messages")
    count: int = Field(default=10, description="Number of summary sentences to generate", ge=1, le=20)
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": 12345,
                "messages": [
                    {"role": "user", "content": "What is the Tiger Exhibition about?"},
                    {"role": "assistant", "content": "The Tiger Exhibition showcases traditional Korean tiger artworks..."}
                ],
                "count": 10
            }
        }


class EnglishTextDocumentRequest(BaseModel):
    """English text document upload request model"""
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Document content")
    category: str = Field(default="general", description="Document category")
    source: str = Field(default="text_upload", description="Document source")


class EnglishPDFDocumentRequest(BaseModel):
    """English PDF document upload request model"""
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Base64 encoded PDF content")
    category: str = Field(default="general", description="Document category")
    source: str = Field(default="pdf_upload", description="Document source")
