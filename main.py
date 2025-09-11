"""
Guidely RAG Server - 메인 애플리케이션
전시회용 인터랙티브 음성 챗봇을 위한 RAG 서버
"""
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import CrossEncoder
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(level=logging.INFO)

from config.app_config import CROSS_ENCODER_MODEL
from controllers.rag_controller import router as rag_router
from controllers.summary_controller import router as summary_router
from controllers.admin_controller import router as admin_router
from controllers.english_rag_controller import router as english_rag_router
from controllers.english_summary_controller import router as english_summary_router
# PostgreSQL 기반 RAG 서비스


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

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발용 - 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 변수
cross_encoder: CrossEncoder | None = None


@app.on_event("startup")
def startup_event():
    """애플리케이션 시작시 초기화"""
    global cross_encoder
    
    print("===== RAG 서비스 초기화 중 =====")
    
    # 환경변수 확인
    print("=== 환경변수 확인 ===")
    print(f"POSTGRES_HOST: {os.getenv('POSTGRES_HOST', 'NOT_SET')}")
    print(f"POSTGRES_DB: {os.getenv('POSTGRES_DB', 'NOT_SET')}")
    print(f"POSTGRES_USER: {os.getenv('POSTGRES_USER', 'NOT_SET')}")
    print(f"OPENAI_API_KEY: {'SET' if os.getenv('OPENAI_API_KEY') else 'NOT_SET'}")

    try:
        print("===== Cross-encoder 모델 로드 중 =====")
        cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL)
        print("===== Cross-encoder 모델 로드 완료 =====")
        
        # PostgreSQL 연결 테스트
        print("===== PostgreSQL 연결 테스트 =====")
        from database.connection import get_db_cursor
        with get_db_cursor() as (cursor, conn):
            cursor.execute("SELECT 1")
            print("PostgreSQL 연결 성공")
        
        print("===== PostgreSQL RAG 서비스 준비 완료 =====")
    except Exception as e:
        print(f"❌ 초기화 실패: {e}")
        import traceback
        traceback.print_exc()


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
        "postgres_ready": True,
        "cross_encoder_ready": cross_encoder is not None,
        "description": "PostgreSQL-based RAG service for exhibition chatbot"
    }


# 라우터 등록
app.include_router(rag_router)
app.include_router(summary_router)
app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(english_rag_router)
app.include_router(english_summary_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
