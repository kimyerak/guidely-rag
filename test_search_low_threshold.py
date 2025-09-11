"""
낮은 임계값으로 검색 테스트
"""
from database.document_service import ChunkService
from sentence_transformers import SentenceTransformer
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_search_with_low_threshold():
    """낮은 임계값으로 검색 테스트"""
    print("=== 낮은 임계값 검색 테스트 ===")
    
    try:
        chunk_service = ChunkService()
        embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        
        # 쿼리 임베딩 생성
        query = "호작도"
        print(f"쿼리: {query}")
        
        query_embedding = embedding_model.encode(query).tolist()
        
        # 매우 낮은 임계값으로 검색
        thresholds = [0.1, 0.05, 0.01, 0.001]
        
        for threshold in thresholds:
            print(f"\n임계값 {threshold}로 검색...")
            search_results = chunk_service.search_similar_chunks(
                query_embedding=query_embedding,
                match_threshold=threshold,
                match_count=10
            )
            
            print(f"결과: {len(search_results)}개")
            
            if search_results:
                for i, result in enumerate(search_results[:3]):
                    print(f"  {i+1}. {result.document_title} (유사도: {result.similarity:.4f})")
                    print(f"     내용: {result.chunk_text[:100]}...")
                break
            else:
                print("  결과 없음")
        
        # 모든 청크의 유사도 확인
        print("\n=== 모든 청크 유사도 확인 ===")
        from database.connection import get_db_cursor
        with get_db_cursor() as (cursor, conn):
            cursor.execute("""
                SELECT 
                    dc.id,
                    dc.chunk_text,
                    d.title,
                    1 - (dc.embedding <=> %s::vector) as similarity
                FROM document_chunks dc
                JOIN documents d ON dc.document_id = d.id
                ORDER BY dc.embedding <=> %s::vector
                LIMIT 5
            """, (query_embedding, query_embedding))
            
            results = cursor.fetchall()
            print(f"상위 5개 청크의 유사도:")
            for i, row in enumerate(results):
                print(f"  {i+1}. {row['title']} (유사도: {row['similarity']:.4f})")
                print(f"     내용: {row['chunk_text'][:100]}...")
                
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_search_with_low_threshold()
