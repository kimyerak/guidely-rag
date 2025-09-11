"""
S3에 올린 PDF를 다운로드하여 RAG 시스템에 업로드
"""
import requests
import base64
import json

def download_and_upload_pdf():
    """S3 PDF를 다운로드하여 RAG 시스템에 업로드"""
    
    # S3 PDF URL
    pdf_url = "https://couple-letter.s3.ap-northeast-2.amazonaws.com/%EA%B5%AD%EB%A6%BD%EC%A4%91%EC%95%99%EB%B0%95%EB%AC%BC%EA%B4%80+%ED%98%B8%EB%9E%91%EC%9D%B4+%EC%A0%84%EC%8B%9C.pdf"
    
    # RAG API URL (로컬 또는 배포된 서버)
    api_url = "http://localhost:8000/admin/documents/pdf"  # 로컬
    # api_url = "https://guidely-rag-g3bbgzd8gye2bnea.koreacentral-01.azurewebsites.net/admin/documents/pdf"  # 배포된 서버
    
    try:
        print("=== S3 PDF 다운로드 중 ===")
        response = requests.get(pdf_url)
        response.raise_for_status()
        
        print(f"다운로드 완료: {len(response.content)} bytes")
        
        # Base64 인코딩
        print("=== Base64 인코딩 중 ===")
        base64_content = base64.b64encode(response.content).decode('utf-8')
        print(f"Base64 길이: {len(base64_content)} 문자")
        
        # RAG 시스템에 업로드
        print("=== RAG 시스템에 업로드 중 ===")
        upload_data = {
            "title": "국립중앙박물관 호랑이 전시 (S3)",
            "content": base64_content,
            "category": "전시품",
            "source": "s3_upload"
        }
        
        upload_response = requests.post(
            api_url,
            headers={"Content-Type": "application/json"},
            json=upload_data
        )
        
        print(f"업로드 응답: {upload_response.status_code}")
        print(f"응답 내용: {upload_response.text}")
        
        if upload_response.status_code == 200:
            result = upload_response.json()
            print(f"✅ 업로드 성공!")
            print(f"문서 ID: {result.get('document_id')}")
            print(f"청크 개수: {result.get('chunks_created')}")
            print(f"텍스트 길이: {result.get('extracted_text_length')}")
        else:
            print(f"❌ 업로드 실패: {upload_response.text}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    download_and_upload_pdf()

