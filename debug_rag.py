"""
RAG 서비스 디버깅
"""
from services.postgres_rag_service import PostgresRAGService
from database.connection import test_connection

def debug_rag():
    """RAG 서비스 디버깅"""
    print("=== RAG 서비스 디버깅 ===")
    
    # 1. 데이터베이스 연결 테스트
    print("1. 데이터베이스 연결 테스트...")
    if test_connection():
        print("✅ 데이터베이스 연결 성공!")
    else:
        print("❌ 데이터베이스 연결 실패!")
        return
    
    # 2. RAG 서비스 초기화 테스트
    print("\n2. RAG 서비스 초기화 테스트...")
    try:
        rag_service = PostgresRAGService()
        print("✅ RAG 서비스 초기화 성공!")
    except Exception as e:
        print(f"❌ RAG 서비스 초기화 실패: {e}")
        return
    
    # 3. 간단한 응답 생성 테스트
    print("\n3. 응답 생성 테스트...")
    try:
        response = rag_service.generate_response("안녕하세요", "rumi")
        print(f"✅ 응답 생성 성공: {response.response[:100]}...")
    except Exception as e:
        print(f"❌ 응답 생성 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_rag()
