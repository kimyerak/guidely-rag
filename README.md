# 🧠 Guidely RAG Server

전시회용 인터랙티브 음성 챗봇을 위한 **고급 RAG(Retrieval-Augmented Generation)** 서버입니다.  
케이팝데몬헌터스 전시회와 관련된 질문에 대해 4가지 캐릭터의 페르소나로 자연스러운 답변을 생성합니다.

## 🏗️ 프로젝트 구조

```
guidely-rag/
├── main.py                     # FastAPI 메인 애플리케이션
├── controllers/                # API 컨트롤러
│   ├── rag_controller.py      # RAG 쿼리 API
│   └── summary_controller.py  # 대화 요약 API
├── services/                   # 비즈니스 로직
│   ├── rag_service.py         # RAG 핵심 로직
│   ├── summary_service.py     # 요약 생성 로직
│   └── relevance_service.py   # 관련성 검증
├── models/                     # 데이터 모델
│   ├── request_models.py      # 요청 모델
│   └── response_models.py     # 응답 모델
├── utils/                      # 유틸리티
│   ├── vectorstore.py         # 벡터스토어 관리
│   └── document_loader.py     # 문서 로더
├── config/                     # 설정
│   └── app_config.py          # 앱 설정
├── characters.py              # 캐릭터 정의
├── database.py                # DB 연결
├── config.py                  # URL 설정
└── requirements.txt           # 의존성
```

## ⚙️ 핵심 아키텍처

### 1. 문서 인덱싱 (최초 1회 실행)
- **문서 로드**: `config.py`에 정의된 URL 목록에서 문서를 로드
- **분할**: 문서를 1200자 청크로 분할 (200자 오버랩)
- **임베딩**: `paraphrase-multilingual-MiniLM-L12-v2` 모델로 벡터화
- **저장**: FAISS 인덱스에 저장 (`faiss_index/` 디렉토리)

### 2. RAG 파이프라인 (`/rag/query` 엔드포인트)
1. **관련성 검증**: 질문이 전시회/케이팝과 관련 있는지 확인
2. **1차 검색**: FAISS에서 관련 문서 10개 검색
3. **2차 재순위**: Cross-Encoder로 Top-3 문서 선정
4. **캐릭터 적용**: 선택된 캐릭터의 페르소나 적용
5. **답변 생성**: GPT-4o로 최종 답변 생성

### 3. 요약 생성 (`/rag/summarize` 엔드포인트)
- 대화 내용을 감성적이고 시적인 한 줄 요약으로 변환
- 엔딩크레딧용 요약 생성

## 🎭 지원 캐릭터

| 캐릭터 | 이름 | 성격 | 말투 |
|--------|------|------|------|
| `rumi` | 루미 | 호기심 많고 활발한 | "와! 정말 신기해!" |
| `mira` | 미라 | 차분하고 지적인 | "흥미로운 관점이네요" |
| `zoey` | 조이 | 친근하고 유쾌한 | "우와! 대박!" |
| `jinu` | 지누 | 진지하고 전문적인 | "정확히 말씀드리면..." |

## 🛠️ 기술 스택

- **Web Framework**: `FastAPI`
- **LLM**: `OpenAI GPT-4o`
- **Embedding**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **Reranker**: `cross-encoder/ms-marco-MiniLM-L-6-v2`
- **Vector Store**: `FAISS`
- **Document Processing**: `PyMuPDF`, `BeautifulSoup`
- **Database**: `MySQL` (Azure)

## 🚀 시작하기

### 1. 환경 설정

```bash
git clone <repository-url>
cd guidely-rag
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 입력하세요:

```env
OPENAI_API_KEY=your_openai_api_key_here
DB_HOST=dbguidey2.mysql.database.azure.com
DB_PORT=3306
DB_NAME=guidely2
DB_USER=mysqladmin
DB_PASSWORD=Strongpassword@
DB_SSL=false
```

### 3. 서버 실행

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 📡 API 엔드포인트

### RAG 쿼리
- **POST** `/rag/query` - 챗봇 대화 생성
- **POST** `/rag/summarize` - 대화 요약 생성
- **GET** `/health` - 서비스 상태 확인

### 요청 예시

```json
POST /rag/query
{
  "message": "케이팝에 대해 알려주세요",
  "character": "rumi"
}
```

### 응답 예시

```json
{
  "response": "안녕하세요! 케이팝에 대해 궁금하시군요. 케이팝은...",
  "sources": [
    {
      "source": "https://namu.wiki/w/케이팝",
      "content": "케이팝 관련 내용..."
    }
  ]
}
```

## 🔧 주요 기능

### 1. 관련성 검증
- 전시회/케이팝과 관련 없는 질문에 대해 친근하게 안내
- 캐릭터별 맞춤 안내 메시지

### 2. 2단계 검색 시스템
- **1차**: FAISS로 빠른 후보 검색
- **2차**: Cross-Encoder로 정확한 재순위

### 3. 캐릭터 시스템
- 4가지 페르소나 지원
- 각 캐릭터별 고유한 말투와 성격

### 4. 요약 생성
- 대화를 감성적인 한 줄 요약으로 변환
- 엔딩크레딧용 시적 표현

## 📊 성능 최적화

- **배치 임베딩**: 대용량 문서 처리 최적화
- **캐싱**: 벡터스토어 로컬 저장
- **비동기 처리**: FastAPI 비동기 지원
- **로깅**: 상세한 디버깅 정보

## 🐳 Docker 지원

```bash
docker build -t guidely-rag .
docker run -p 8000:8000 guidely-rag
```

## 📝 개발 가이드

### 새로운 캐릭터 추가
1. `characters.py`에 캐릭터 정의 추가
2. `CHARACTER_STYLE` 딕셔너리에 추가

### 새로운 문서 소스 추가
1. `config.py`의 `URLS` 리스트에 URL 추가
2. 서버 재시작시 자동으로 인덱싱

### API 확장
1. `controllers/`에 새 컨트롤러 추가
2. `services/`에 비즈니스 로직 구현
3. `models/`에 요청/응답 모델 정의

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다.