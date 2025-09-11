"""
간단한 데이터베이스 확인
"""
import sys
sys.path.append('.')

from database.connection import get_db_cursor

with get_db_cursor() as (cursor, conn):
    cursor.execute("SELECT id, title, LEFT(content, 100) as preview FROM documents ORDER BY id")
    docs = cursor.fetchall()
    
    print("=== 데이터베이스 문서 목록 ===")
    for doc in docs:
        print(f"ID: {doc[0]}")
        print(f"Title: {doc[1]}")
        print(f"Preview: {doc[2]}")
        print("-" * 50)
    
    # 언어 추정
    korean_count = 0
    english_count = 0
    
    for doc in docs:
        content = doc[2].lower()
        if any(char in content for char in '가나다라마바사아자차카타파하'):
            korean_count += 1
        elif any(char in content for char in 'abcdefghijklmnopqrstuvwxyz'):
            english_count += 1
    
    print(f"\n한국어 문서: {korean_count}개")
    print(f"영어 문서: {english_count}개")
