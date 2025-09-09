import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# 데이터베이스 연결 설정 (실제 Cursor 연결 정보)
DB_HOST = os.getenv("DB_HOST", "dbguidey2.mysql.database.azure.com")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_NAME = os.getenv("DB_NAME", "guidely2")
DB_USER = os.getenv("DB_USER", "mysqladmin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Strongpassword@")
DB_SSL = os.getenv("DB_SSL", "false").lower() == "true"  # Cursor에서 SSL 없이 연결됨

# 연결 문자열 (Azure MySQL - SSL 비활성화, 방화벽 규칙으로 보안)
DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?ssl_disabled=true"

# SQLAlchemy 엔진 생성
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """데이터베이스 세션 생성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    """데이터베이스 연결 테스트"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ 데이터베이스 연결 성공!")
            return True
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        return False