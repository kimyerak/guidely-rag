"""
문서 업로드 스크립트
"""
import os
import requests
from database.document_service import DocumentService, ChunkService
from utils.document_loader import load_document_from_url
from sentence_transformers import SentenceTransformer
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upload_namu_wiki():
    """나무위키 문서 업로드"""
    print("=== 나무위키 문서 업로드 ===")
    
    url = "https://namu.wiki/w/%EC%BC%80%EC%9D%B4%ED%8C%9D%20%EB%8D%B0%EB%AA%AC%20%ED%97%8C%ED%84%B0%EC%8A%A4"
    
    try:
        # 문서 로드
        print("나무위키 문서 로드 중...")
        content = load_document_from_url(url)
        
        if not content:
            print("❌ 문서 로드 실패")
            return False
            
        # 문서 서비스 초기화
        doc_service = DocumentService()
        chunk_service = ChunkService()
        embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        
        # 문서 저장
        print("문서 저장 중...")
        from database.models import Document
        document = Document(
            title="케이팝데몬헌터스 - 나무위키",
            file_name="kpop_demon_hunters_namu_wiki.html",
            file_type="html",
            content=content,
            source_url=url,
            metadata={"source": "namu_wiki", "category": "kpop_group"}
        )
        document_id = doc_service.create_document(document)
        
        print(f"✅ 문서 저장 완료: ID {document_id}")
        
        # 청크 생성 및 임베딩
        print("청크 생성 및 임베딩 중...")
        chunk_ids = chunk_service.create_chunks_for_document(
            document_id, 
            content, 
            embedding_model,
            chunk_size=500,
            chunk_overlap=50
        )
        
        print(f"✅ 청크 생성 완료: {len(chunk_ids)}개")
        return True
        
    except Exception as e:
        print(f"❌ 나무위키 업로드 실패: {e}")
        return False

def upload_pdf_file(pdf_path: str):
    """PDF 파일 업로드"""
    print(f"=== PDF 파일 업로드: {pdf_path} ===")
    
    if not os.path.exists(pdf_path):
        print(f"❌ 파일을 찾을 수 없습니다: {pdf_path}")
        return False
    
    try:
        # PDF 로드
        print("PDF 문서 로드 중...")
        content = load_document_from_url(pdf_path)
        
        if not content:
            print("❌ PDF 로드 실패")
            return False
            
        # 문서 서비스 초기화
        doc_service = DocumentService()
        chunk_service = ChunkService()
        embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        
        # 문서 저장
        print("문서 저장 중...")
        from database.models import Document
        document = Document(
            title="국립중앙박물관 호랑이 전시",
            file_name=os.path.basename(pdf_path),
            file_type="pdf",
            content=content,
            source_url=f"file://{pdf_path}",
            metadata={"source": "local_pdf", "category": "exhibition", "museum": "국립중앙박물관"}
        )
        document_id = doc_service.create_document(document)
        
        print(f"✅ 문서 저장 완료: ID {document_id}")
        
        # 청크 생성 및 임베딩
        print("청크 생성 및 임베딩 중...")
        chunk_ids = chunk_service.create_chunks_for_document(
            document_id, 
            content, 
            embedding_model,
            chunk_size=500,
            chunk_overlap=50
        )
        
        print(f"✅ 청크 생성 완료: {len(chunk_ids)}개")
        return True
        
    except Exception as e:
        print(f"❌ PDF 업로드 실패: {e}")
        return False

def main():
    """메인 함수"""
    print("=== 문서 업로드 시작 ===")
    
    # 1. 나무위키 업로드
    success1 = upload_namu_wiki()
    
    # 2. PDF 파일 경로 입력 받기
    pdf_path = input("\nPDF 파일 경로를 입력하세요 (예: C:/path/to/tiger_exhibition.pdf): ").strip()
    
    if pdf_path:
        success2 = upload_pdf_file(pdf_path)
    else:
        print("PDF 파일 경로가 입력되지 않았습니다.")
        success2 = False
    
    # 결과 출력
    print("\n=== 업로드 결과 ===")
    print(f"나무위키: {'✅ 성공' if success1 else '❌ 실패'}")
    print(f"PDF 파일: {'✅ 성공' if success2 else '❌ 실패'}")
    
    if success1 or success2:
        print("\n🎉 문서 업로드가 완료되었습니다!")
        print("이제 RAG API에서 더 풍부한 응답을 받을 수 있습니다.")
    else:
        print("\n❌ 모든 문서 업로드가 실패했습니다.")

if __name__ == "__main__":
    main()
