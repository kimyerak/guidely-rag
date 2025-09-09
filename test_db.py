"""
Simple DB Connection Test
"""
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

print("=== DB 연결 정보 ===")
print(f"Host: {os.getenv('DB_HOST', 'NOT_SET')}")
print(f"Port: {os.getenv('DB_PORT', 'NOT_SET')}")
print(f"Database: {os.getenv('DB_NAME', 'NOT_SET')}")
print(f"User: {os.getenv('DB_USER', 'NOT_SET')}")
print(f"Password: {'*' * len(os.getenv('DB_PASSWORD', '')) if os.getenv('DB_PASSWORD') else 'NOT_SET'}")
print(f"SSL: {os.getenv('DB_SSL', 'NOT_SET')}")

# DB 연결 테스트
try:
    from database import test_connection
    print("\n=== 연결 테스트 ===")
    result = test_connection()
    if result:
        print("✅ DB 연결 성공!")
    else:
        print("❌ DB 연결 실패!")
except Exception as e:
    print(f"❌ 오류: {e}")
