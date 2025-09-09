"""
Azure App Service용 startup 스크립트
"""
import os
import sys

# 현재 디렉토리를 Python path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# main 모듈 import 및 실행
if __name__ == "__main__":
    import uvicorn
    from main import app
    
    # Azure App Service에서 사용하는 포트 (환경변수에서 가져오거나 기본값 8000)
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    )
