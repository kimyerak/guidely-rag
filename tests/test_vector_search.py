"""
벡터 검색 테스트
"""
from database.document_service import ChunkService
from sentence_transformers import SentenceTransformer
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_vector_search():
    """벡터 검색 테스트"""
    print("=== 벡터 검색 테스트 ===")
    
    try:
        chunk_service = ChunkService()
        embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        
        # 다양한 쿼리로 테스트
        queries = [
            "호작도",
            "호작도는 어떤 작품이야?",
            "호랑이와 까치 그림",
            "조선시대 호랑이 그림",
            "용호도"
        ]
        
        for query in queries:
            print(f"\n=== 쿼리: '{query}' ===")
            
            # 쿼리 임베딩 생성
            query_embedding = embedding_model.encode(query).tolist()
            
            # 벡터 검색
            search_results = chunk_service.search_similar_chunks(
                query_embedding=query_embedding,
                match_threshold=0.1,
                match_count=3
            )
            
            print(f"검색 결과: {len(search_results)}개")
            
            for i, result in enumerate(search_results):
                print(f"  {i+1}. {result.document_title} (유사도: {result.similarity:.4f})")
                print(f"     내용: {result.chunk_text[:100]}...")
                print(f"     소스: {result.source_url}")
                
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vector_search()
