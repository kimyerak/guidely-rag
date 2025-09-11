"""
PostgreSQL 테이블 존재 확인
"""
from database.connection import get_db_cursor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_postgres_tables():
    """PostgreSQL 테이블 존재 확인"""
    try:
        with get_db_cursor() as (cursor, conn):
            # 1. 현재 데이터베이스 확인
            cursor.execute("SELECT current_database();")
            db_name = cursor.fetchone()[0]
            print(f"현재 데이터베이스: {db_name}")
            
            # 2. 테이블 목록 확인
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            print(f"\n테이블 목록:")
            for table in tables:
                print(f"  - {table[0]}")
            
            # 3. documents 테이블 구조 확인
            if any('documents' in str(table) for table in tables):
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = 'documents'
                    ORDER BY ordinal_position;
                """)
                columns = cursor.fetchall()
                print(f"\ndocuments 테이블 구조:")
                for col in columns:
                    print(f"  - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
            
            # 4. document_chunks 테이블 구조 확인
            if any('document_chunks' in str(table) for table in tables):
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = 'document_chunks'
                    ORDER BY ordinal_position;
                """)
                columns = cursor.fetchall()
                print(f"\ndocument_chunks 테이블 구조:")
                for col in columns:
                    print(f"  - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
            
            # 5. pgvector 확장 확인
            cursor.execute("""
                SELECT extname, extversion 
                FROM pg_extension 
                WHERE extname = 'vector';
            """)
            vector_ext = cursor.fetchone()
            if vector_ext:
                print(f"\npgvector 확장: {vector_ext[0]} v{vector_ext[1]}")
            else:
                print("\n❌ pgvector 확장이 설치되지 않음!")
            
            # 6. 데이터 개수 확인
            cursor.execute("SELECT COUNT(*) FROM documents;")
            doc_count = cursor.fetchone()[0]
            print(f"\n문서 개수: {doc_count}")
            
            cursor.execute("SELECT COUNT(*) FROM document_chunks;")
            chunk_count = cursor.fetchone()[0]
            print(f"청크 개수: {chunk_count}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_postgres_tables()
