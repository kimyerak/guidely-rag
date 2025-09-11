"""
PostgreSQL 연결 테스트
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def test_postgres_connection():
    """PostgreSQL 연결 테스트"""
    print("=== PostgreSQL 연결 테스트 ===")
    
    # 환경변수 확인
    print(f"POSTGRES_HOST: {os.getenv('POSTGRES_HOST')}")
    print(f"POSTGRES_PORT: {os.getenv('POSTGRES_PORT')}")
    print(f"POSTGRES_DB: {os.getenv('POSTGRES_DB')}")
    print(f"POSTGRES_USER: {os.getenv('POSTGRES_USER')}")
    print(f"POSTGRES_PASSWORD: {'SET' if os.getenv('POSTGRES_PASSWORD') else 'NOT_SET'}")
    print(f"POSTGRES_SSLMODE: {os.getenv('POSTGRES_SSLMODE')}")
    
    # 연결 시도
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT'),
            database=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            sslmode=os.getenv('POSTGRES_SSLMODE')
        )
        
        print("✅ PostgreSQL 연결 성공!")
        
        # 간단한 쿼리 테스트
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"PostgreSQL 버전: {version[0]}")
        
        # 데이터베이스 목록 확인
        cursor.execute("SELECT datname FROM pg_database;")
        databases = cursor.fetchall()
        print(f"사용 가능한 데이터베이스: {[db[0] for db in databases]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ PostgreSQL 연결 실패: {e}")
        print(f"에러 타입: {type(e).__name__}")

if __name__ == "__main__":
    test_postgres_connection()
