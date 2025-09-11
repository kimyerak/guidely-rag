"""
배포된 서버 RAG API 테스트
"""
import requests
import json

def test_deployed_rag():
    url = "https://guidely-rag-g3bbgzd8gye2bnea.koreacentral-01.azurewebsites.net/rag/query"
    
    # 테스트 데이터
    test_data = {
        "character": "rumi",
        "message": "호작도는 어떤 작품이야?"
    }
    
    try:
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=test_data
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ RAG API 작동!")
            print(f"답변: {data.get('response', 'N/A')}")
            print(f"소스 개수: {len(data.get('sources', []))}")
        else:
            print("❌ RAG API 실패!")
            
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    test_deployed_rag()
