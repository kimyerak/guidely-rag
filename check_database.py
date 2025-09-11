"""
데이터베이스 확인 스크립트
"""
from database.connection import get_db_cursor
import json

def check_documents():
    """문서 테이블 확인"""
    print("=== 문서 테이블 확인 ===")
    try:
        with get_db_cursor() as (cursor, conn):
            # 모든 문서 조회
            cursor.execute("""
                SELECT id, title, file_name, file_type, source_url, 
                       upload_date, is_active, 
                       jsonb_pretty(metadata) as metadata
                FROM documents 
                ORDER BY upload_date DESC
            """)
            documents = cursor.fetchall()
            
            print(f"총 문서 수: {len(documents)}")
            print("-" * 80)
            
            for doc in documents:
                print(f"ID: {doc['id']}")
                print(f"제목: {doc['title']}")
                print(f"파일명: {doc['file_name']}")
                print(f"타입: {doc['file_type']}")
                print(f"소스 URL: {doc['source_url']}")
                print(f"업로드 날짜: {doc['upload_date']}")
                print(f"활성화: {doc['is_active']}")
                print(f"메타데이터: {doc['metadata']}")
                print("-" * 80)
                
    except Exception as e:
        print(f"문서 조회 실패: {e}")

def check_chunks():
    """청크 테이블 확인"""
    print("\n=== 청크 테이블 확인 ===")
    try:
        with get_db_cursor() as (cursor, conn):
            # 청크 통계
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_chunks,
                    COUNT(DISTINCT document_id) as documents_with_chunks
                FROM document_chunks
            """)
            stats = cursor.fetchone()
            
            print(f"총 청크 수: {stats['total_chunks']}")
            print(f"청크가 있는 문서 수: {stats['documents_with_chunks']}")
            
            # 문서별 청크 수
            cursor.execute("""
                SELECT 
                    d.title,
                    d.file_type,
                    COUNT(dc.id) as chunk_count
                FROM documents d
                LEFT JOIN document_chunks dc ON d.id = dc.document_id
                GROUP BY d.id, d.title, d.file_type
                ORDER BY chunk_count DESC
            """)
            chunk_counts = cursor.fetchall()
            
            print("\n문서별 청크 수:")
            print("-" * 50)
            for row in chunk_counts:
                print(f"{row['title']} ({row['file_type']}): {row['chunk_count']}개")
                
    except Exception as e:
        print(f"청크 조회 실패: {e}")

def check_sample_chunks():
    """샘플 청크 내용 확인"""
    print("\n=== 샘플 청크 내용 ===")
    try:
        with get_db_cursor() as (cursor, conn):
            cursor.execute("""
                SELECT 
                    dc.id,
                    dc.chunk_text,
                    dc.chunk_index,
                    d.title as document_title
                FROM document_chunks dc
                JOIN documents d ON dc.document_id = d.id
                ORDER BY dc.id
                LIMIT 3
            """)
            chunks = cursor.fetchall()
            
            for chunk in chunks:
                print(f"청크 ID: {chunk['id']}")
                print(f"문서: {chunk['document_title']}")
                print(f"인덱스: {chunk['chunk_index']}")
                print(f"내용: {chunk['chunk_text'][:200]}...")
                print("-" * 50)
                
    except Exception as e:
        print(f"샘플 청크 조회 실패: {e}")

if __name__ == "__main__":
    check_documents()
    check_chunks()
    check_sample_chunks()
