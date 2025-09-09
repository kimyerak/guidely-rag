"""
Azure App Service용 app.py (표준 진입점)
"""
import os
import sys

# 현재 디렉토리를 Python path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# main 모듈에서 app 객체 import
from main import app

# Azure App Service에서 사용하는 포트
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
