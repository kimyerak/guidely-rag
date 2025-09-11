"""
English response models for RAG API
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class EnglishRAGQueryResponse(BaseModel):
    """English RAG query response model"""
    response: str = Field(..., description="AI response in English")
    sources: List[str] = Field(default=[], description="Source documents")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "The Tiger Exhibition showcases traditional Korean tiger artworks and their modern interpretations...",
                "sources": ["National Museum Tiger Exhibition Guide", "Traditional Korean Art Collection"]
            }
        }


class EnglishConversationSummaryResponse(BaseModel):
    """English conversation summary response model"""
    session_id: int = Field(..., description="Session ID", example=12345)
    total_messages: int = Field(..., description="Total number of messages")
    summaries: List[str] = Field(..., description="Conversation summary sentences")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": 12345,
                "total_messages": 12,
                "summaries": [
                    "Tiger patterns, wings reborn in tradition",
                    "Imagination spread endlessly through the questions asked",
                    "A feast of light blossomed from Monet's brushstrokes",
                    "Discovered the innovative vision of Impressionist artists"
                ]
            }
        }


class EnglishDocumentUploadResponse(BaseModel):
    """English document upload response model"""
    success: bool = Field(..., description="Upload success status")
    message: str = Field(..., description="Response message")
    document_id: Optional[int] = Field(None, description="Created document ID")
    chunks_created: Optional[int] = Field(None, description="Number of chunks created")
    extracted_text_length: Optional[int] = Field(None, description="Extracted text length")


class EnglishDocumentListResponse(BaseModel):
    """English document list response model"""
    documents: List[dict] = Field(..., description="List of documents")
    total_count: int = Field(..., description="Total document count")


class EnglishHealthResponse(BaseModel):
    """English health check response model"""
    status: str = Field(..., description="Service status")
    message: str = Field(..., description="Status message")
    timestamp: str = Field(..., description="Response timestamp")
    services: dict = Field(..., description="Service status details")
