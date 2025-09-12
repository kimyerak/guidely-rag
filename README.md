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
├── database/                   # 데이터베이스
│   ├── connection.py          # PostgreSQL 연결
│   ├── models.py             # 데이터 모델
│   └── document_service.py   # 문서 서비스
├── config.py                  # URL 설정
└── requirements.txt           # 의존성
```

## ⚙️ 핵심 아키텍처

### 1. 📚 문서 인덱싱 파이프라인 (최초 1회 실행)

#### 1.1 문서 수집 및 전처리
```
원본 문서 (PDF/URL/텍스트)
    ↓
텍스트 추출 (PyMuPDF, BeautifulSoup)
    ↓
문서 메타데이터 생성 (제목, 출처, 카테고리)
```

#### 1.2 청킹 (Chunking) 전략
```
전체 문서 텍스트
    ↓
청크 분할 (1200자, 200자 오버랩)
    ↓
문장 경계에서 자르기 (의미 보존)
    ↓
청크별 메타데이터 추가 (인덱스, 길이)
```

#### 1.3 임베딩 생성
```
각 청크 텍스트
    ↓
BERT 기반 sentence-transformers 모델
    ↓
384차원 벡터 임베딩 생성
    ↓
PostgreSQL pgvector에 저장
```

### 2. 🔍 RAG 검색 파이프라인 (실시간)

#### 2.1 쿼리 전처리
```
사용자 질문
    ↓
관련성 검증 (전시회/케이팝 관련성 확인)
    ↓
질문 임베딩 생성 (384차원 벡터)
```

#### 2.2 1차 검색 (Vector Search)
```
질문 임베딩
    ↓
PostgreSQL 벡터 검색 (코사인 유사도)
    ↓
Top-10 문서 청크 검색
    ↓
유사도 점수 계산 (0.0 ~ 1.0)
```

#### 2.3 키워드 가중치 적용
```
질문에서 핵심 키워드 추출
    ↓
문서 청크와 키워드 매칭 개수 계산
    ↓
키워드 매칭 개수 × 0.15 가중치 부여
    ↓
최대 0.6까지 유사도 점수 부스트
```

#### 2.4 2차 재순위 (Cross-Encoder)
```
Top-10 청크 + 질문
    ↓
Cross-Encoder 모델 (ms-marco-MiniLM-L-6-v2)
    ↓
(질문, 청크) 쌍별 관련성 점수 계산
    ↓
점수 기준 내림차순 정렬
    ↓
Top-3 최종 선정
```

#### 2.5 컨텍스트 구성 및 응답 생성
```
Top-3 청크 + 질문
    ↓
캐릭터별 프롬프트 템플릿 적용
    ↓
GPT-4o 모델로 응답 생성
    ↓
출처 정보와 함께 최종 응답 반환
```

### 3. 📊 점수 및 유사도 시스템

#### 3.1 유사도 점수 계산
- **벡터 유사도**: `1 - (embedding1 <=> embedding2)` (코사인 유사도)
- **키워드 가중치**: `min(0.6, keyword_matches × 0.15)`
- **최종 점수**: `벡터 유사도 + 키워드 가중치`

#### 3.2 랭킹 알고리즘
1. **키워드 매칭 우선**: 키워드가 매칭된 문서를 먼저 정렬
2. **키워드 개수 순**: 키워드 매칭 개수가 많은 순
3. **유사도 순**: 동일한 키워드 개수 내에서 유사도 높은 순
4. **일반 문서**: 키워드 매칭 없는 문서는 유사도 순

### 4. 🎭 캐릭터 시스템
- **4가지 페르소나**: rumi, mira, zoey, jinu
- **개별 프롬프트**: 각 캐릭터별 고유한 성격과 말투
- **동적 적용**: 사용자 선택에 따라 실시간 캐릭터 변경

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
- **Vector Store**: `PostgreSQL + pgvector`
- **Document Processing**: `PyMuPDF`, `BeautifulSoup`
- **Database**: `PostgreSQL` (Azure)

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
POSTGRES_HOST=your_postgres_host
POSTGRES_PORT=5432
POSTGRES_DB=guidely
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
```

### 3. 서버 실행

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 📡 API 엔드포인트

### 🤖 RAG 쿼리
- **POST** `/rag/query` - 한국어 챗봇 대화 생성
- **POST** `/rag/query-english` - 영어 챗봇 대화 생성

### 📝 요약 생성
- **POST** `/rag/summarize` - 한국어 대화 요약 생성
- **POST** `/rag/summarize-english` - 영어 대화 요약 생성

### 📊 통계 및 분석
- **POST** `/api/v1/summary-statistics/ending-credits` - 엔딩크레딧용 요약 및 통계
- **GET** `/api/v1/summary-statistics/word-frequency` - 단어 빈도 통계

### 📄 문서 관리 (관리자)
- **POST** `/documents/text` - 텍스트 문서 업로드
- **POST** `/documents/pdf` - PDF 문서 업로드 (Base64)
- **POST** `/documents/pdf-upload` - PDF 파일 직접 업로드
- **GET** `/documents` - 문서 목록 조회
- **DELETE** `/documents/{document_id}` - 문서 삭제

### 🔍 상태 확인
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

### 1. 🎯 관련성 검증
- 전시회/케이팝과 관련 없는 질문에 대해 친근하게 안내
- 캐릭터별 맞춤 안내 메시지 제공

### 2. 🔍 하이브리드 검색 시스템
- **벡터 검색**: 의미적 유사도 기반 검색
- **키워드 검색**: 정확한 키워드 매칭
- **가중치 조합**: 두 방식의 점수를 결합하여 정확도 향상

### 3. 🎭 멀티 캐릭터 시스템
- **4가지 페르소나**: rumi, mira, zoey, jinu
- **개별 성격**: 각 캐릭터별 고유한 말투와 성격
- **동적 전환**: 사용자 선택에 따라 실시간 캐릭터 변경

### 4. 📝 지능형 요약 생성
- **감성적 요약**: 대화를 시적이고 감성적인 한 줄로 변환
- **엔딩크레딧**: 전시회 종료 시 사용할 요약 생성
- **다국어 지원**: 한국어/영어 요약 모두 지원

### 5. 📊 실시간 통계 및 분석
- **단어 빈도**: 대화에서 자주 언급된 키워드 분석
- **세션 추적**: 사용자별 대화 세션 관리
- **성능 모니터링**: 검색 정확도 및 응답 시간 추적

## 📊 성능 최적화

### 벡터 검색 최적화
- **ivfflat 인덱스**: PostgreSQL pgvector의 고성능 인덱스
- **배치 임베딩**: 대용량 문서 처리 시 배치 단위로 임베딩 생성
- **메모리 효율성**: 청크 단위로 처리하여 메모리 사용량 최적화

### 검색 정확도 향상
- **키워드 가중치**: 질문 키워드 매칭 시 유사도 점수 부스트
- **2단계 검색**: 벡터 검색 + Cross-Encoder 재순위
- **문맥 보존**: 청킹 시 문장 경계를 고려한 의미 보존

### 시스템 성능
- **비동기 처리**: FastAPI 비동기 지원으로 동시 요청 처리
- **연결 풀링**: PostgreSQL 연결 풀을 통한 효율적인 DB 접근
- **로깅 시스템**: 상세한 디버깅 정보로 성능 모니터링


### 새로운 캐릭터 추가
1. `characters.py`의 `CHARACTER_STYLE` 딕셔너리에 추가
2. 캐릭터별 고유한 성격, 말투, 예시 대화 정의
3. 영어/한국어 프롬프트 템플릿 업데이트

### 새로운 문서 소스 추가
1. `config.py`의 `URLS` 리스트에 URL 추가
2. 문서 타입별 파싱 로직 구현 (필요시)
3. 서버 재시작 시 자동으로 인덱싱

### API 확장
1. `controllers/`에 새 컨트롤러 추가
2. `services/`에 비즈니스 로직 구현
3. `models/`에 요청/응답 모델 정의
4. `main.py`에 라우터 등록
