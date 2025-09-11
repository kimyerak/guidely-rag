"""
PostgreSQL 데이터베이스 연결 테스트
"""
import os
from dotenv import load_dotenv
from database.connection import test_connection, get_db_cursor

# 환경변수 로드
load_dotenv()

def test_database_connection():
    """데이터베이스 연결 테스트"""
    print("=== PostgreSQL 데이터베이스 연결 테스트 ===")
    
    # 1. 기본 연결 테스트
    print("1. 기본 연결 테스트...")
    if test_connection():
        print("✅ 데이터베이스 연결 성공!")
    else:
        print("❌ 데이터베이스 연결 실패!")
        return False
    
    # 2. 테이블 생성 테스트
    print("\n2. 테이블 생성 테스트...")
    try:
        with get_db_cursor() as (cursor, conn):
            # 간단한 테스트 테이블 생성
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_table (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            print("✅ 테이블 생성 성공!")
            
            # 테스트 데이터 삽입
            cursor.execute("INSERT INTO test_table (name) VALUES (%s)", ("테스트 데이터",))
            conn.commit()
            print("✅ 데이터 삽입 성공!")
            
            # 데이터 조회
            cursor.execute("SELECT * FROM test_table")
            results = cursor.fetchall()
            print(f"✅ 데이터 조회 성공! 조회된 행 수: {len(results)}")
            
            # 테스트 테이블 삭제
            cursor.execute("DROP TABLE test_table")
            conn.commit()
            print("✅ 테스트 테이블 정리 완료!")
            
    except Exception as e:
        print(f"❌ 테이블 작업 실패: {e}")
        return False
    
    # 3. pgvector 확장 테스트
    print("\n3. pgvector 확장 테스트...")
    try:
        with get_db_cursor() as (cursor, conn):
            # pgvector 확장 확인
            cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector'")
            result = cursor.fetchone()
            if result:
                print("✅ pgvector 확장 설치 확인!")
            else:
                print("❌ pgvector 확장이 설치되지 않음!")
                return False
                
            # 벡터 테이블 생성 테스트
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_vectors (
                    id SERIAL PRIMARY KEY,
                    embedding VECTOR(384)
                )
            """)
            conn.commit()
            print("✅ 벡터 테이블 생성 성공!")
            
            # 테스트 벡터 삽입
            test_vector = [0.1] * 384  # 384차원 테스트 벡터
            cursor.execute("INSERT INTO test_vectors (embedding) VALUES (%s)", (test_vector,))
            conn.commit()
            print("✅ 벡터 데이터 삽입 성공!")
            
            # 벡터 유사도 검색 테스트
            cursor.execute("""
                SELECT id, embedding <-> %s::vector as distance 
                FROM test_vectors 
                ORDER BY embedding <-> %s::vector 
                LIMIT 1
            """, (test_vector, test_vector))
            result = cursor.fetchone()
            if result:
                print(f"✅ 벡터 검색 성공! 거리: {result['distance']}")
            
            # 테스트 테이블 삭제
            cursor.execute("DROP TABLE test_vectors")
            conn.commit()
            print("✅ 벡터 테이블 정리 완료!")
            
    except Exception as e:
        print(f"❌ pgvector 테스트 실패: {e}")
        return False
    
    print("\n🎉 모든 테스트 통과! RAG 시스템을 사용할 준비가 완료되었습니다!")
    return True

if __name__ == "__main__":
    test_database_connection()
