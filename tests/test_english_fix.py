"""
영어 RAG 수정 후 테스트
"""
import requests
import json

def test_english_rag():
    """영어 RAG 테스트"""
    url = "http://localhost:8000/rag/query-english"
    
    test_data = {
        "character": "rumi",
        "message": "How did koreans considered tiger in the past?",
        "session_id": 12345
    }
    
    try:
        response = requests.post(url, json=test_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result['response']}")
            print(f"Sources: {result['sources']}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_english_rag()
