"""
벡터 검색 쿼리 직접 테스트
"""
from database.connection import get_db_cursor
from sentence_transformers import SentenceTransformer
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_direct_vector_query():
    """벡터 검색 쿼리 직접 테스트"""
    print("=== 벡터 검색 쿼리 직접 테스트 ===")
    
    try:
        embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        
        query = "호작도는 어떤 작품이야?"
        print(f"쿼리: {query}")
        
        # 쿼리 임베딩 생성
        query_embedding = embedding_model.encode(query).tolist()
        print(f"임베딩 차원: {len(query_embedding)}")
        print(f"임베딩 샘플: {query_embedding[:5]}")
        
        # 직접 SQL 쿼리 실행
        with get_db_cursor() as (cursor, conn):
            print("\n=== 직접 SQL 쿼리 실행 ===")
            
            # 1. 기본 벡터 검색
            cursor.execute("""
                SELECT 
                    dc.id,
                    dc.chunk_text,
                    d.title,
                    1 - (dc.embedding <=> %s::vector) as similarity
                FROM document_chunks dc
                JOIN documents d ON dc.document_id = d.id
                WHERE d.is_active = TRUE
                ORDER BY dc.embedding <=> %s::vector
                LIMIT 5
            """, (query_embedding, query_embedding))
            
            results = cursor.fetchall()
            print(f"기본 벡터 검색 결과: {len(results)}개")
            
            for i, row in enumerate(results):
                print(f"  {i+1}. {row['title']} (유사도: {row['similarity']:.4f})")
                print(f"     내용: {row['chunk_text'][:100]}...")
                if "호작도" in row['chunk_text']:
                    print(f"     ✅ 호작도 포함!")
            
            # 2. 임계값 없이 모든 결과
            print("\n=== 임계값 없이 모든 결과 ===")
            cursor.execute("""
                SELECT 
                    dc.id,
                    dc.chunk_text,
                    d.title,
                    1 - (dc.embedding <=> %s::vector) as similarity
                FROM document_chunks dc
                JOIN documents d ON dc.document_id = d.id
                WHERE d.is_active = TRUE
                AND 1 - (dc.embedding <=> %s::vector) > 0.0
                ORDER BY dc.embedding <=> %s::vector
                LIMIT 10
            """, (query_embedding, query_embedding, query_embedding))
            
            results = cursor.fetchall()
            print(f"임계값 0.0 결과: {len(results)}개")
            
            for i, row in enumerate(results):
                print(f"  {i+1}. {row['title']} (유사도: {row['similarity']:.4f})")
                print(f"     내용: {row['chunk_text'][:100]}...")
                if "호작도" in row['chunk_text']:
                    print(f"     ✅ 호작도 포함!")
                    
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_vector_query()
