"""
관리자 API 테스트
"""
import requests
import json

def test_text_upload():
    """텍스트 업로드 테스트"""
    url = "http://localhost:8000/admin/documents/text"
    
    data = {
        "title": "호랑이 전시회 - 테스트",
        "content": "이것은 테스트용 텍스트입니다.",
        "category": "테스트",
        "source": "직접입력"
    }
    
    try:
        print("\n텍스트 업로드 테스트 중...")
        response = requests.post(url, data=data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success! Document ID: {result.get('document_id')}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_text_upload()
