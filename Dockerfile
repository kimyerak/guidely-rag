FROM python:3.11-slim

WORKDIR /app

# 시스템 패키지 (PyMuPDF 등 필요)
RUN apt-get update && apt-get install -y \
    build-essential \
    libfreetype6-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# requirements 설치 (Guidely_RAG 안에 있음)
COPY Guidely_RAG/requirements.txt .
RUN pip install -r requirements.txt


# KT 믿음 모델 requirements (선택적)
COPY Guidely_RAG/KTrequirements.txt .
RUN pip install -r KTrequirements.txt

# 소스 코드 전체 복사
COPY . .

EXPOSE 8000

# main.py는 Guidely_RAG 폴더 안에 있으므로 모듈 경로 맞추기
CMD ["uvicorn", "Guidely_RAG.main:app", "--host", "0.0.0.0", "--port", "8000"]
