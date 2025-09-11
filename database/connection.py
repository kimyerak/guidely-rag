"""
PostgreSQL 데이터베이스 연결 설정
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

# PostgreSQL 데이터베이스 연결 정보 (RAG용)
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'rag-vectordb.postgres.database.azure.com'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'database': os.getenv('POSTGRES_DB', 'rag_vectordb'),  # rag_vectordb 데이터베이스 사용
    'user': os.getenv('POSTGRES_USER', 'mysqladmin'),
    'password': os.getenv('POSTGRES_PASSWORD', 'Strongpassword@'),
    'sslmode': os.getenv('POSTGRES_SSLMODE', 'require')
}

@contextmanager
def get_db_connection():
    """데이터베이스 연결 컨텍스트 매니저"""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        yield conn
    except Exception as e:
        logger.error(f"데이터베이스 연결 오류: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

@contextmanager
def get_db_cursor():
    """데이터베이스 커서 컨텍스트 매니저"""
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor, conn
        except Exception as e:
            logger.error(f"데이터베이스 쿼리 오류: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()

def test_connection():
    """데이터베이스 연결 테스트"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                logger.info(f"PostgreSQL 연결 성공: {version[0]}")
                return True
    except Exception as e:
        logger.error(f"데이터베이스 연결 실패: {e}")
        return False
