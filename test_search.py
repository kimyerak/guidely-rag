"""
검색 기능 직접 테스트
"""
from services.postgres_rag_service import PostgresRAGService
from database.document_service import ChunkService
from sentence_transformers import SentenceTransformer
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_search():
    """검색 기능 테스트"""
    print("=== 검색 기능 테스트 ===")
    
    try:
        # 서비스 초기화
        rag_service = PostgresRAGService()
        chunk_service = ChunkService()
        embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        
        # 쿼리 임베딩 생성
        query = "호작도는 어떤 작품이야?"
        print(f"쿼리: {query}")
        
        query_embedding = embedding_model.encode(query).tolist()
        print(f"임베딩 차원: {len(query_embedding)}")
        
        # 벡터 검색
        print("\n벡터 검색 실행...")
        search_results = chunk_service.search_similar_chunks(
            query_embedding=query_embedding,
            match_threshold=0.3,
            match_count=5
        )
        
        print(f"검색 결과: {len(search_results)}개")
        
        for i, result in enumerate(search_results):
            print(f"\n--- 결과 {i+1} ---")
            print(f"문서: {result.document_title}")
            print(f"유사도: {result.similarity:.4f}")
            print(f"내용: {result.chunk_text[:200]}...")
            print(f"소스 URL: {result.source_url}")
        
        if not search_results:
            print("❌ 검색 결과가 없습니다!")
            
            # 데이터베이스에 청크가 있는지 확인
            print("\n데이터베이스 청크 확인...")
            from database.connection import get_db_cursor
            with get_db_cursor() as (cursor, conn):
                cursor.execute("SELECT COUNT(*) as count FROM document_chunks")
                count = cursor.fetchone()['count']
                print(f"총 청크 수: {count}")
                
                if count > 0:
                    cursor.execute("SELECT chunk_text FROM document_chunks LIMIT 3")
                    chunks = cursor.fetchall()
                    print("샘플 청크:")
                    for i, chunk in enumerate(chunks):
                        print(f"  {i+1}: {chunk['chunk_text'][:100]}...")
        else:
            print("✅ 검색 성공!")
            
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_search()
