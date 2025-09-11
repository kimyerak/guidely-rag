"""
PDF를 Base64로 변환하여 업로드 테스트
"""
import base64
import requests
import json

def test_pdf_upload():
    # PDF 파일을 Base64로 인코딩
    pdf_path = "국립중앙박물관 호랑이 전시.pdf"
    
    try:
        with open(pdf_path, "rb") as pdf_file:
            pdf_content = pdf_file.read()
            base64_content = base64.b64encode(pdf_content).decode('utf-8')
        
        # JSON 요청 데이터
        request_data = {
            "title": "pdf - 제목까지 다 있는거2",
            "content": base64_content,
            "category": "배경과 작품목록",
            "source": "국중박 공식 사이트"
        }
        
        # API 호출
        response = requests.post(
            "http://localhost:8000/admin/documents/pdf",
            headers={"Content-Type": "application/json"},
            json=request_data
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
    except FileNotFoundError:
        print(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    test_pdf_upload()
