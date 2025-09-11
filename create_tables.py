"""
데이터베이스 테이블 생성 스크립트
"""
from database.connection import get_db_connection

def create_tables():
    """데이터베이스 테이블 생성"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # SQL 스키마 읽기
                with open('database_schema.sql', 'r', encoding='utf-8') as f:
                    sql_schema = f.read()
                
                # 테이블 생성
                cursor.execute(sql_schema)
                conn.commit()
                print("✅ 테이블 생성 완료!")
                
    except Exception as e:
        print(f"❌ 테이블 생성 실패: {e}")

if __name__ == "__main__":
    create_tables()
