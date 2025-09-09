"""
Guidely RAG Server - 메인 애플리케이션
전시회용 인터랙티브 음성 챗봇을 위한 RAG 서버
"""
import os
from fastapi import FastAPI
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from sentence_transformers import CrossEncoder
from dotenv import load_dotenv

from config.app_config import VECTORSTORE_PATH, EMBEDDING_MODEL, CROSS_ENCODER_MODEL
from utils.document_loader import load_document_from_url
from utils.vectorstore import create_faiss_vectorstore
from controllers.rag_controller import router as rag_router
from controllers.summary_controller import router as summary_router
# DB 연결 제거 - RAG 서비스는 stateless
import config as config_module
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 환경 변수 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(
    title="Guidely RAG Chatbot API",
    description="전시회용 인터랙티브 음성 챗봇 RAG 서버",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 전역 변수
vectorstore: FAISS | None = None
cross_encoder: CrossEncoder | None = None


@app.on_event("startup")
def startup_event():
    """애플리케이션 시작시 벡터스토어 초기화"""
    global vectorstore, cross_encoder
    
    # 임베딩 모델 로드
    embeddings = SentenceTransformerEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
    )

    print("===== RAG 서비스 초기화 중 =====")

    print("===== Cross-encoder 모델 로드 중 =====")
    cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL)
    print("===== Cross-encoder 모델 로드 완료 =====")

    if os.path.exists(VECTORSTORE_PATH):
        print("===== 기존 벡터스토어 로드 중 =====")
        vectorstore = FAISS.load_local(
            VECTORSTORE_PATH,
            embeddings,
            allow_dangerous_deserialization=True,
        )
        print("===== 벡터스토어 로드 완료 =====")
    else:
        print("===== 벡터스토어 새로 생성 중 =====")
        # 1) URL → HTML → Document
        documents = [load_document_from_url(url) for url in config_module.URLS]
        documents = [doc for doc in documents if doc.page_content.strip()]
        # 2) Document → 작은 조각
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200, chunk_overlap=200
        )
        docs = splitter.split_documents(documents)
        # 3) FAISS 인덱싱
        vectorstore = create_faiss_vectorstore(docs, embeddings)
        # 4) 디스크 저장
        vectorstore.save_local(VECTORSTORE_PATH)
        print("===== 벡터스토어 생성 및 저장 완료 =====")


@app.get("/", tags=["System"])
async def root():
    """RAG 서비스 루트 엔드포인트"""
    return {
        "message": "Guidely RAG Service",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", tags=["System"])
async def health_check():
    """RAG 서비스 헬스체크 - 빠른 응답"""
    return {
        "status": "healthy",
        "service": "Guidely RAG Service"
    }

@app.get("/health/detailed", tags=["System"])
async def detailed_health_check():
    """RAG 서비스 상세 헬스체크"""
    return {
        "status": "healthy",
        "service": "Guidely RAG Service",
        "vectorstore_ready": vectorstore is not None,
        "cross_encoder_ready": cross_encoder is not None,
        "description": "Stateless RAG service for exhibition chatbot"
    }


# 라우터 등록
app.include_router(rag_router)
app.include_router(summary_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
