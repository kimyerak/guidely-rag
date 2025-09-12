#!/usr/bin/env python3
"""
RAG API 랭킹 정보 테스트
"""
import requests
import json

def test_korean_rag_with_ranking():
    """한국어 RAG API에서 랭킹 정보 확인"""
    url = "http://localhost:8000/rag/query"
    
    payload = {
        "character": "rumi",
        "message": "호작도는 어떤 작품이야?",
        "session_id": 12345
    }
    
    print("=== 한국어 RAG API 테스트 (랭킹 정보 포함) ===")
    print(f"요청: {payload['message']}")
    print()
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        print(f"응답: {data['response']}")
        print()
        print("=== Sources 랭킹 정보 ===")
        
        for i, source in enumerate(data['sources']):
            print(f"랭킹 {source.get('ranking', 'N/A')}: {source.get('document_title', 'N/A')}")
            print(f"  - 유사도 점수: {source.get('similarity_score', 'N/A')}")
            print(f"  - 청크 ID: {source.get('chunk_id', 'N/A')}")
            print(f"  - 내용: {source.get('content', 'N/A')[:100]}...")
            print(f"  - 출처: {source.get('source', 'N/A')}")
            print()
            
    except Exception as e:
        print(f"❌ 오류: {e}")

def test_english_rag_with_ranking():
    """영어 RAG API에서 랭킹 정보 확인"""
    url = "http://localhost:8000/rag/query-english"
    
    payload = {
        "character": "rumi",
        "message": "What is the Tiger Exhibition about?"
    }
    
    print("=== 영어 RAG API 테스트 (랭킹 정보 포함) ===")
    print(f"요청: {payload['message']}")
    print()
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        print(f"응답: {data['response']}")
        print()
        print("=== Sources 랭킹 정보 ===")
        
        for i, source in enumerate(data['sources']):
            print(f"랭킹 {source.get('ranking', 'N/A')}: {source.get('document_title', 'N/A')}")
            print(f"  - 유사도 점수: {source.get('similarity_score', 'N/A')}")
            print(f"  - 청크 ID: {source.get('chunk_id', 'N/A')}")
            print(f"  - 내용: {source.get('content', 'N/A')[:100]}...")
            print(f"  - 출처: {source.get('source', 'N/A')}")
            print()
            
    except Exception as e:
        print(f"❌ 오류: {e}")

if __name__ == "__main__":
    print("RAG API 랭킹 정보 테스트 시작")
    print("=" * 50)
    
    test_korean_rag_with_ranking()
    print("\n" + "=" * 50)
    test_english_rag_with_ranking()
    
    print("\n테스트 완료!")

