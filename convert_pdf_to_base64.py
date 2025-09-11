"""
PDF를 Base64로 변환하는 스크립트
"""
import base64
import os

def convert_pdf_to_base64(pdf_path):
    """PDF 파일을 Base64로 변환"""
    try:
        with open(pdf_path, "rb") as pdf_file:
            pdf_content = pdf_file.read()
            base64_content = base64.b64encode(pdf_content).decode('utf-8')
            return base64_content
    except FileNotFoundError:
        print(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")
        return None
    except Exception as e:
        print(f"변환 오류: {e}")
        return None

def create_postman_json(base64_content, title="호랑이 전시 PDF"):
    """Postman용 JSON 생성"""
    json_data = {
        "title": title,
        "content": base64_content,
        "category": "전시품",
        "source": "admin_upload"
    }
    return json_data

if __name__ == "__main__":
    # PDF 파일 경로 (실제 파일 경로로 변경)
    pdf_path = "국립중앙박물관 호랑이 전시.pdf"
    
    # Base64 변환
    base64_content = convert_pdf_to_base64(pdf_path)
    
    if base64_content:
        # Postman용 JSON 생성
        json_data = create_postman_json(base64_content)
        
        print("=== Postman용 JSON ===")
        import json
        print(json.dumps(json_data, indent=2, ensure_ascii=False))
        
        print(f"\n=== Base64 길이: {len(base64_content)} 문자 ===")
        print(f"=== Base64 미리보기 (처음 100자): {base64_content[:100]}... ===")
    else:
        print("PDF 파일을 찾을 수 없습니다. 파일 경로를 확인해주세요.")
