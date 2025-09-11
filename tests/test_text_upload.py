"""
텍스트 업로드 테스트
"""
import requests
import json

def test_text_upload():
    # JSON 요청 데이터
    request_data = {
        "title": "호랑이 전시 정보",
        "content": "호작도는 조선시대의 대표적인 호랑이 그림입니다. 호랑이와 까치가 함께 그려진 작품으로, 기쁜 소식을 전해주고 나쁜 기운을 물리친다고 여겨졌습니다.",
        "category": "전시품",
        "source": "admin_upload"
    }
    
    try:
        # API 호출
        response = requests.post(
            "http://localhost:8000/admin/documents/text",
            headers={"Content-Type": "application/json"},
            json=request_data
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ 텍스트 업로드 성공!")
        else:
            print("❌ 텍스트 업로드 실패!")
            
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    test_text_upload()
