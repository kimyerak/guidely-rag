"""
관리자 API 컨트롤러
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
import logging
from database.document_service import DocumentService, ChunkService
from database.models import Document
from sentence_transformers import SentenceTransformer
import os

logger = logging.getLogger(__name__)
router = APIRouter()

# 임베딩 모델 초기화
embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

@router.post("/documents/text")
async def upload_text_document(
    title: str = Form(...),
    content: str = Form(...),
    category: str = Form("general"),
    source: str = Form("admin_upload")
):
    """
    텍스트 문서 업로드 (할루시네이션 방지용 정보)
    """
    try:
        # 문서 서비스 초기화
        doc_service = DocumentService()
        chunk_service = ChunkService()
        
        # 문서 생성
        document = Document(
            title=title,
            file_name=f"{title}.txt",
            file_type="text",
            content=content,
            source_url=f"admin://text/{title}",
            metadata={
                "source": source,
                "category": category,
                "upload_type": "text"
            }
        )
        
        # 문서 저장
        document_id = doc_service.create_document(document)
        
        # 청크 생성 및 임베딩
        chunk_ids = chunk_service.create_chunks_for_document(
            document_id,
            content,
            embedding_model,
            chunk_size=500,
            chunk_overlap=50
        )
        
        return {
            "success": True,
            "message": "텍스트 문서가 성공적으로 업로드되었습니다.",
            "document_id": document_id,
            "chunks_created": len(chunk_ids)
        }
        
    except Exception as e:
        logger.error(f"텍스트 문서 업로드 실패: {e}")
        raise HTTPException(status_code=500, detail=f"문서 업로드 실패: {str(e)}")

@router.post("/documents/pdf")
async def upload_pdf_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form("general"),
    source: str = Form("admin_upload")
):
    """
    PDF 문서 업로드 (할루시네이션 방지용 정보)
    """
    try:
        # PDF 파일 읽기
        content = await file.read()
        
        # PDF 텍스트 추출 (간단한 방법)
        # 실제로는 PyPDF2나 pdfplumber 등을 사용하는 것이 좋습니다
        try:
            import PyPDF2
            import io
            
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
        except ImportError:
            # PyPDF2가 없으면 기본 텍스트로 처리
            text_content = content.decode('utf-8', errors='ignore')
        
        if not text_content.strip():
            raise HTTPException(status_code=400, detail="PDF에서 텍스트를 추출할 수 없습니다.")
        
        # 문서 서비스 초기화
        doc_service = DocumentService()
        chunk_service = ChunkService()
        
        # 문서 생성
        document = Document(
            title=title,
            file_name=file.filename,
            file_type="pdf",
            content=text_content,
            source_url=f"admin://pdf/{file.filename}",
            metadata={
                "source": source,
                "category": category,
                "upload_type": "pdf",
                "original_filename": file.filename
            }
        )
        
        # 문서 저장
        document_id = doc_service.create_document(document)
        
        # 청크 생성 및 임베딩
        chunk_ids = chunk_service.create_chunks_for_document(
            document_id,
            text_content,
            embedding_model,
            chunk_size=500,
            chunk_overlap=50
        )
        
        return {
            "success": True,
            "message": "PDF 문서가 성공적으로 업로드되었습니다.",
            "document_id": document_id,
            "chunks_created": len(chunk_ids),
            "extracted_text_length": len(text_content)
        }
        
    except Exception as e:
        logger.error(f"PDF 문서 업로드 실패: {e}")
        raise HTTPException(status_code=500, detail=f"PDF 업로드 실패: {str(e)}")

@router.get("/documents")
async def list_documents():
    """
    업로드된 문서 목록 조회
    """
    try:
        doc_service = DocumentService()
        documents = doc_service.get_all_documents()
        
        return {
            "success": True,
            "documents": [
                {
                    "id": doc.id,
                    "title": doc.title,
                    "file_name": doc.file_name,
                    "file_type": doc.file_type,
                    "source_url": doc.source_url,
                    "upload_date": doc.upload_date.isoformat() if doc.upload_date else None,
                    "metadata": doc.metadata,
                    "is_active": doc.is_active
                }
                for doc in documents
            ]
        }
        
    except Exception as e:
        logger.error(f"문서 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"문서 목록 조회 실패: {str(e)}")

@router.delete("/documents/{document_id}")
async def delete_document(document_id: int):
    """
    문서 삭제
    """
    try:
        doc_service = DocumentService()
        
        # 문서 비활성화 (실제 삭제 대신)
        document = doc_service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다.")
        
        document.is_active = False
        doc_service.update_document(document)
        
        return {
            "success": True,
            "message": f"문서 ID {document_id}가 비활성화되었습니다."
        }
        
    except Exception as e:
        logger.error(f"문서 삭제 실패: {e}")
        raise HTTPException(status_code=500, detail=f"문서 삭제 실패: {str(e)}")