"""
데이터베이스 모델 정의
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

@dataclass
class Document:
    id: Optional[int] = None
    title: str = ""
    file_name: Optional[str] = None
    file_type: str = "text"
    source_url: Optional[str] = None
    upload_date: Optional[datetime] = None
    content: str = ""
    metadata: Optional[Dict[str, Any]] = None
    is_active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'file_name': self.file_name,
            'file_type': self.file_type,
            'source_url': self.source_url,
            'upload_date': self.upload_date,
            'content': self.content,
            'metadata': json.dumps(self.metadata) if self.metadata else None,
            'is_active': self.is_active
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        return cls(
            id=data.get('id'),
            title=data.get('title', ''),
            file_name=data.get('file_name'),
            file_type=data.get('file_type', 'text'),
            source_url=data.get('source_url'),
            upload_date=data.get('upload_date'),
            content=data.get('content', ''),
            metadata=json.loads(data['metadata']) if data.get('metadata') else None,
            is_active=data.get('is_active', True)
        )

@dataclass
class DocumentChunk:
    id: Optional[int] = None
    document_id: int = 0
    chunk_text: str = ""
    chunk_index: int = 0
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'document_id': self.document_id,
            'chunk_text': self.chunk_text,
            'chunk_index': self.chunk_index,
            'embedding': self.embedding,
            'metadata': json.dumps(self.metadata) if self.metadata else None,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentChunk':
        return cls(
            id=data.get('id'),
            document_id=data.get('document_id', 0),
            chunk_text=data.get('chunk_text', ''),
            chunk_index=data.get('chunk_index', 0),
            embedding=data.get('embedding'),
            metadata=json.loads(data['metadata']) if data.get('metadata') else None,
            created_at=data.get('created_at')
        )

@dataclass
class SearchResult:
    chunk_id: int
    document_id: int
    chunk_text: str
    similarity: float
    metadata: Optional[Dict[str, Any]] = None
    document_title: Optional[str] = None
    source_url: Optional[str] = None
