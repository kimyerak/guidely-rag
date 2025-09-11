"""
RAG API 테스트
"""
import requests
import json

def test_rag_api():
    """RAG API 테스트"""
    url = "http://localhost:8000/rag/query"
    
    # 테스트 데이터
    data = {
        "message": "안녕하세요",
        "character": "rumi"
    }
    
    try:
        print("RAG API 테스트 중...")
        response = requests.post(url, json=data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success! Response: {result['response']}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_rag_api()
