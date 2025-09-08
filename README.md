# 🧠 Advanced RAG Server with Retriever-Reranker

이 프로젝트는 FastAPI와 LangChain을 기반으로 한 **고급 RAG(Retrieval-Augmented Generation)** 서버입니다.  
뉴스 기사와 같은 사용자 입력을 기반으로, 사전에 구축된 과학 기술 자료(논문, 위키 등) 벡터 데이터베이스에서 가장 관련성 높은 정보를 찾아냅니다. 이후, 찾은 정보를 바탕으로 두 캐릭터 간의 자연스러운 Q&A 스크립트를 생성합니다.

특히, **Retriever-Reranker 파이프라인**을 도입하여 검색 정확도를 높였습니다. 1차로 후보 문서를 빠르게 찾아낸 뒤, 2차로 정교한 모델을 사용해 순위를 재조정하여 LLM에 더 정확한 컨텍스트를 제공합니다.

## ⚙️ 핵심 아키텍처

### 1. 인덱싱 (최초 1회 실행)
- **문서 로드**: `config.py`에 정의된 URL 목록(ArXiv 논문, 나무위키 등)에서 문서를 로드합니다.
- **분할**: 로드된 문서를 일정한 크기의 청크(Chunk)로 분할합니다.
- **임베딩**: `paraphrase-multilingual-MiniLM-L12-v2` 모델을 사용하여 각 문서 청크를 벡터로 변환합니다.
- **저장**: 생성된 벡터를 `FAISS` 인덱스에 저장하여, 이후 빠른 검색이 가능하도록 로컬에 보관합니다. (`faiss_index/` 디렉토리)

### 2. RAG 파이프라인 (`/rag` 엔드포인트)
1.  **1차 검색 (Retrieval)**: 사용자의 입력(전시회 관련 질문)이 들어오면, FAISS 인덱스에서 의미적으로 유사한 상위 100개의 후보 문서를 빠르게 검색합니다.
2.  **2차 재순위 (Reranking)**: 검색된 100개 문서를 `mmarco-mMiniLMv2-L12-H384-v1` Cross-Encoder 모델을 사용해 입력과의 관련도를 다시 계산합니다. 가장 관련성이 높다고 판단된 상위 4개 문서를 최종 컨텍스트로 선별합니다.
3.  **프롬프트 생성**: 최종 선별된 2개의 문서(컨텍스트), 그리고 케데헌 캐릭터의 페르소나를 조합하여 GPT-4o 모델에 전달할 프롬프트를 동적으로 생성합니다.
4.  **스크립트 생성 (Generation)**: GPT-4o 모델이 완성된 프롬프트를 기반으로 최종 스크립트를 생성합니다.
5.  **응답**: 생성된 스크립트와 함께, 컨텍스트로 사용된 문서의 출처를 JSON 형태로 반환합니다.

## 🛠️ 기술 스택

- **Web Framework**: `FastAPI`
- **LLM Orchestration**: `LangChain`
- **LLM**: `OpenAI GPT-4o`
- **Embedding Model**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **Reranker Model**: `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`
- **Vector Store**: `FAISS` (Facebook AI Similarity Search)
- **Data Loading**: `requests`, `BeautifulSoup`, `PyMuPDF`
- **Environment**: `uvicorn`, `python-dotenv`

## 🚀 시작하기

### 1. 환경 설정

먼저, 저장소를 클론하고 필요한 라이브러리를 설치합니다.

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
pip install -r requirements.txt
```

### 2. 환경 변수 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 OpenAI API 키를 입력하세요.

```env
OPENAI_API_KEY="sk-..."
```

### 3. 서버 실행

다음 명령어를 사용하여 서버를 실행합니다. 서버가 시작되면 애플리케이션 로딩 및 모델 초기화가 진행됩니다. 최초 실행 시에는 FAISS 인덱스를 생성하므로 시간이 다소 소요될 수 있습니다.

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
`--reload` 옵션은 코드 변경 시 서버를 자동으로 재시작해줍니다.

