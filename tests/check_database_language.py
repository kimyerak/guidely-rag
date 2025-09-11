"""
데이터베이스의 문서 언어 확인
"""
from database.connection import get_db_cursor

def check_database_language():
    """데이터베이스의 문서 언어 확인"""
    try:
        with get_db_cursor() as (cursor, conn):
            # 문서 목록 조회
            cursor.execute("""
                SELECT id, title, file_name, file_type, source, 
                       LEFT(content, 100) as content_preview
                FROM documents 
                ORDER BY id
            """)
            
            documents = cursor.fetchall()
            
            print("=== 데이터베이스 문서 목록 ===")
            for doc in documents:
                print(f"ID: {doc[0]}")
                print(f"Title: {doc[1]}")
                print(f"File: {doc[2]}")
                print(f"Type: {doc[3]}")
                print(f"Source: {doc[4]}")
                print(f"Content Preview: {doc[5]}")
                print("-" * 50)
            
            # 청크 개수 확인
            cursor.execute("SELECT COUNT(*) FROM document_chunks")
            chunk_count = cursor.fetchone()[0]
            print(f"\n총 청크 개수: {chunk_count}")
            
            # 언어별 문서 개수 (간단한 추정)
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN content ~ '[가-힣]' THEN 'Korean'
                        WHEN content ~ '[a-zA-Z]' THEN 'English'
                        ELSE 'Other'
                    END as language,
                    COUNT(*) as count
                FROM documents 
                GROUP BY language
            """)
            
            language_stats = cursor.fetchall()
            print(f"\n=== 언어별 문서 통계 ===")
            for lang, count in language_stats:
                print(f"{lang}: {count}개")
                
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    check_database_language()
