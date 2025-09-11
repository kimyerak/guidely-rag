"""
임베딩 데이터 확인
"""
from database.connection import get_db_cursor

def check_embeddings():
    """임베딩 데이터 확인"""
    print("=== 임베딩 데이터 확인 ===")
    
    try:
        with get_db_cursor() as (cursor, conn):
            # 1. 청크 테이블 기본 정보
            cursor.execute("SELECT COUNT(*) as count FROM document_chunks")
            count = cursor.fetchone()['count']
            print(f"총 청크 수: {count}")
            
            # 2. 임베딩이 NULL이 아닌 청크 확인
            cursor.execute("""
                SELECT 
                    dc.id,
                    dc.chunk_text,
                    d.title,
                    CASE 
                        WHEN dc.embedding IS NULL THEN 'NULL'
                        ELSE 'NOT NULL'
                    END as embedding_status
                FROM document_chunks dc
                JOIN documents d ON dc.document_id = d.id
                LIMIT 5
            """)
            
            results = cursor.fetchall()
            print(f"\n임베딩 상태 확인:")
            for i, row in enumerate(results):
                print(f"  {i+1}. {row['title']} - 임베딩: {row['embedding_status']}")
                print(f"     내용: {row['chunk_text'][:100]}...")
            
            # 3. 벡터 타입 확인
            cursor.execute("""
                SELECT 
                    column_name, 
                    data_type, 
                    is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'document_chunks' 
                AND column_name = 'embedding'
            """)
            
            result = cursor.fetchone()
            if result:
                print(f"\n임베딩 컬럼 정보:")
                print(f"  컬럼명: {result['column_name']}")
                print(f"  데이터 타입: {result['data_type']}")
                print(f"  NULL 허용: {result['is_nullable']}")
            
            # 4. pgvector 확장 확인
            cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector'")
            extension = cursor.fetchone()
            if extension:
                print(f"\npgvector 확장: 설치됨")
            else:
                print(f"\npgvector 확장: 설치되지 않음!")
                
    except Exception as e:
        print(f"❌ 확인 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_embeddings()
