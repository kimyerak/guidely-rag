"""
rag_server.py
==============
FastAPI RAG 서버 – 전시회용 인터랙티브 음성 챗봇
유저의 채팅 메시지를 받아 관련 문서를 참고하여 자연스러운 답변을 생성합니다.
"""

import os
import tempfile
from typing import List
from urllib.parse import urlparse

import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
# (torchvision 연산자 누락 오류 방지를 위해) transformers 가 torchvision 을 import 하지 않도록 환경변수 설정
os.environ["DISABLE_TORCHVISION_IMPORTS"] = "1"
from langchain_community.embeddings import SentenceTransformerEmbeddings
from sentence_transformers import CrossEncoder
from pydantic import BaseModel, Field
from config import URLS  # URL 목록만 담고 있는 모듈
from characters import CHARACTER_STYLE  # 캐릭터 스타일 정의
import textwrap
import logging

# ---------------------------------------------------------------------------
# 로깅 설정 (모듈 상단 한 번만)
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)

load_dotenv()  # OPENAI_API_KEY 등 환경 변수 읽기

# ---------------------------------------------------------------------------
# FastAPI 인스턴스
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Guidely RAG Chatbot API",
    description="전시회용 인터랙티브 음성 챗봇 RAG 서버",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI 경로
    redoc_url="/redoc",  # ReDoc 경로
    openapi_url="/openapi.json"  # OpenAPI 스키마 경로
)

# ---------------------------------------------------------------------------
# 벡터스토어 유틸
# ---------------------------------------------------------------------------

VECTORSTORE_PATH = "faiss_index"
vectorstore: FAISS | None = None  # 전역 벡터스토어 객체
cross_encoder: CrossEncoder | None = None  # 전역 Cross-Encoder 객체

def load_pdf_from_url(url: str) -> Document:
    """PDF URL에서 텍스트를 추출하여 Document로 반환 (디버깅 로그 포함)"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(response.content)
            tmp_file_path = tmp_file.name

        try:
            doc = fitz.open(tmp_file_path)
            text_content = ""
            total_chars = 0

            for page in doc:
                raw_text = page.get_text().strip()
                cleaned_text = raw_text  # 필요하면 clean_pdf_text(raw_text)

                if cleaned_text:
                    # ────────────────────────────────────────────────
                    # 📌 ① 페이지별 길이·앞부분 미리보기 출력
                    # ────────────────────────────────────────────────
                    logger.info(
                        "Page %-3d | %5d chars | Preview: %s",
                        page.number + 1,
                        len(cleaned_text),
                        textwrap.shorten(cleaned_text, width=80, placeholder=" …"),
                    )

                    text_content += f"페이지 {page.number + 1}: {cleaned_text}\n\n"
                    total_chars += len(cleaned_text)

            

            # ────────────────────────────────────────────────────────
            # 📌 ② 전체 추출 결과 요약
            # ────────────────────────────────────────────────────────
            logger.info(
                "Finished extracting PDF (%s) → total %d chars across %d pages",
                url,
                total_chars,
                len(doc),
            )
            doc.close() 
            # arXiv 논문이면 출처 주석 추가
            if "arxiv.org" in url.lower():
                text_content = f"arXiv 논문 출처: {url}\n\n" + text_content

            return Document(page_content=text_content,
                            metadata={"source": url, "type": "pdf"})

        finally:
            os.unlink(tmp_file_path)

    except Exception as e:
        logger.exception("[ERROR] PDF %s 로딩 실패: %s", url, e)
        return Document(page_content="",
                        metadata={"source": url, "type": "pdf"})

def load_namu_page(url: str) -> Document:
    """나무위키 페이지 본문을 Document 로 로드"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        content_div = soup.find("main") or soup
        content = content_div.get_text(separator="\n", strip=True)
        return Document(page_content=content, metadata={"source": url, "type": "namu_wiki"})
    except Exception as e:
        print(f"[ERROR] {url} 로딩 실패: {e}")
        return Document(page_content="", metadata={"source": url, "type": "namu_wiki"})


def load_document_from_url(url: str) -> Document:
    """URL 타입에 따라 적절한 로더를 선택하여 Document 반환"""
    parsed_url = urlparse(url)
    
    # PDF 파일인지 확인
    if url.lower().endswith('.pdf') or 'arxiv.org/pdf/' in url.lower():
        return load_pdf_from_url(url)
    # 나무위키 페이지인지 확인
    elif 'namu.wiki' in parsed_url.netloc:
        return load_namu_page(url)
    else:
        # 기본적으로 웹 페이지로 처리
        return load_namu_page(url)


def chunk_documents(docs: List[Document], chunk_size: int = 1000):
    """문서 배열을 chunk_size 단위로 yield"""
    for i in range(0, len(docs), chunk_size):
        yield docs[i : i + chunk_size]


def create_faiss_vectorstore(
    docs: List[Document], embeddings, batch_size: int = 500
) -> FAISS:
    """배치 임베딩으로 대용량 문서를 FAISS 스토어로 인덱싱"""
    vector_store: FAISS | None = None
    doc_count = 0
    for chunked_docs in chunk_documents(docs, batch_size):
        # ────────────────────────────────────────────────────────
        # 📌 각 청크 임베딩 진행 상황 로깅
        # ────────────────────────────────────────────────────────
        logger.info(f"임베딩 중: 문서 {doc_count + 1} ~ {doc_count + len(chunked_docs)}")

        # PDF 문서가 포함되어 있는지, 있다면 몇 개인지 로깅
        pdf_docs_in_chunk = [doc for doc in chunked_docs if doc.metadata.get("type") == "pdf"]
        if pdf_docs_in_chunk:
            logger.info(f"  └ 이 청크에 PDF 문서 {len(pdf_docs_in_chunk)}개 포함:")
            for i, pdf_doc in enumerate(pdf_docs_in_chunk[:3]): # 처음 3개 PDF 소스만 로깅 (너무 많으면 생략)
                logger.info(f"    PDF [{i+1}] 소스: {pdf_doc.metadata.get('source', 'N/A')}, 내용 일부: {textwrap.shorten(pdf_doc.page_content, width=50, placeholder='...')}")
        
        partial = FAISS.from_documents(chunked_docs, embeddings)
        if vector_store is None:
            vector_store = partial
        else:
            vector_store.merge_from(partial)
        doc_count += len(chunked_docs)
    logger.info(f"총 {doc_count}개 문서 청크 임베딩 완료.")
    return vector_store


# ---------------------------------------------------------------------------
# FastAPI – 애플리케이션 시작 시 벡터스토어 준비
# ---------------------------------------------------------------------------

@app.on_event("startup")
def startup_event():
    global vectorstore, cross_encoder
    embeddings = SentenceTransformerEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        model_kwargs={"device": "cpu"},
    )

    print("===== Cross-encoder 모델 로드 중 =====")
    cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    print("===== Cross-encoder 모델 로드 완료 =====")

    if os.path.exists(VECTORSTORE_PATH):
        print("===== 기존 벡터스토어 로드 중 =====")
        vectorstore = FAISS.load_local(
            VECTORSTORE_PATH,
            embeddings,
            allow_dangerous_deserialization=True,
        )
    else:
        print("===== 벡터스토어 새로 생성 중 =====")
        # 1) URL → HTML → Document
        documents = [load_document_from_url(url) for url in URLS]
        documents = [doc for doc in documents if doc.page_content.strip()]
        # 2) Document → 작은 조각
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200, chunk_overlap=200
        )
        docs = splitter.split_documents(documents)
        # 3) FAISS 인덱싱
        vectorstore = create_faiss_vectorstore(docs, embeddings)
        # 4) 디스크 저장
        vectorstore.save_local(VECTORSTORE_PATH)
        print("===== 벡터스토어 생성 및 저장 완료 =====")


# ---------------------------------------------------------------------------
# 요청/응답 모델
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str = Field(..., description="유저의 채팅 메시지", example="안녕하세요! 케이팝에 대해 알려주세요")
    character: str = Field(default="rumi", description="챗봇 페르소나", example="rumi")

    class Config:
        schema_extra = {
            "example": {
                "message": "안녕하세요! 케이팝에 대해 알려주세요",
                "character": "rumi"
            }
        }


class ChatResponse(BaseModel):
    response: str = Field(..., description="챗봇의 자연스러운 답변")
    sources: List[dict] = Field(..., description="참고한 문서 출처")

    class Config:
        schema_extra = {
            "example": {
                "response": "안녕하세요! 케이팝에 대해 궁금하시군요. 케이팝은...",
                "sources": [
                    {
                        "source": "https://namu.wiki/w/케이팝",
                        "content": "케이팝 관련 내용..."
                    }
                ]
            }
        }


# ---------------------------------------------------------------------------
# 엔드포인트: /rag
# ---------------------------------------------------------------------------

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def generate_chat_response(req: ChatRequest):
    """
    전시회용 인터랙티브 음성 챗봇 API
    
    유저의 메시지를 받아 관련 문서를 참고하여 자연스러운 답변을 생성합니다.
    
    **Parameters:**
    - **message**: 유저의 채팅 메시지
    - **character**: 챗봇 페르소나 (rumi, mira, zoey, jinu)
    
    **Returns:**
    - **response**: 챗봇의 자연스러운 답변
    - **sources**: 참고한 문서 출처 (있는 경우)
    
    **Example Request:**
    ```json
    {
        "message": "안녕하세요! 케이팝에 대해 알려주세요",
        "character": "rumi"
    }
    ```
    
    **Example Response:**
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
    """
    global vectorstore, cross_encoder
    if vectorstore is None or cross_encoder is None:
        return {"error": "Vectorstore or CrossEncoder not initialized."}

    user_message = req.message
    character = req.character
    logger.info(f"User message: {user_message}")
    logger.info(f"Character: {character}")

    # 캐릭터 스타일 가져오기
    char_style = CHARACTER_STYLE[character]

    # ----------------- 1) 문맥 검색 (2-stage: Retriever + Reranker) -----------------
    # 1-1) 1차 검색 (Retriever): FAISS에서 Top-100 문서 가져오기
    logger.info("1단계: FAISS에서 관련 문서 10개 검색")
    retriever = vectorstore.as_retriever(search_kwargs={"k": 10})  # 100 → 10
    retrieved_docs = retriever.get_relevant_documents(user_message)
    logger.info(f"  -> {len(retrieved_docs)}개 문서 검색 완료.")

    # 1-2) 2차 검색 (Reranker): Cross-encoder로 관련성 높은 Top-3 문서 재선정
    logger.info("2단계: Cross-encoder로 재점수화하여 Top-3 선정")
    # 쿼리와 문서 내용으로 페어 생성
    pairs = [[user_message, doc.page_content] for doc in retrieved_docs]

    # Cross-encoder로 점수 계산
    scores = cross_encoder.predict(pairs, show_progress_bar=True)

    # 점수와 문서를 튜플로 묶어 점수 기준 내림차순 정렬
    scored_docs = sorted(zip(scores, retrieved_docs), key=lambda x: x[0], reverse=True)

    # 상위 3개 문서 선택
    docs = [doc for score, doc in scored_docs[:3]]
    logger.info("  -> 재점수화 후 Top-3 문서 선정 완료.")
    for i, doc in enumerate(docs):
        logger.info(f"    Top {i+1}: {doc.metadata.get('source', 'N/A')} (Score: {scored_docs[i][0]:.4f})")
    
    context = "\n\n".join(d.page_content for d in docs)

    # ----------------- 2) 프롬프트 -----------------
    prompt = PromptTemplate(
        input_variables=["message", "context", "character", "char_style"],
        template=(
            "당신은 전시회에서 방문객과 자연스럽게 대화하는 친근한 챗봇입니다.\n\n"
            
            "## 주어진 정보\n"
            "**유저 메시지:**\n{message}\n\n"
            "**참고 자료 (관련 문서):**\n{context}\n\n"
            
            "## 캐릭터 설정\n"
            "- **이름**: {char_style[name]}\n"
            "  - **성격**: {char_style[style]}\n"
            "  - **말투**: {char_style[voice]}\n"
            "  - **예시**: \"{char_style[example]}\"\n\n"
            
            "## 임무\n"
            "유저의 메시지에 대해 캐릭터의 성격에 맞게 자연스럽고 친근하게 답변해주세요.\n\n"
            
            "## 답변 지침\n"
            "1. **자연스러운 대화**: 전시회에서 실제 사람과 대화하는 것처럼 자연스럽게\n"
            "2. **캐릭터 유지**: 주어진 캐릭터의 성격과 말투를 일관되게 유지\n"
            "3. **정보 활용**: 참고 자료가 있다면 자연스럽게 활용하되, 억지스럽지 않게\n"
            "4. **친근함**: 방문객을 환영하고 도움이 되는 정보 제공\n"
            "5. **간결함**: 너무 길지 않게, 대화하기 좋은 길이로\n\n"
            
            "## 주의사항\n"
            "- 답변만 출력하고 다른 설명 금지\n"
            "- 한국어로 자연스럽게 작성\n"
            "- 참고 자료가 없어도 캐릭터답게 답변\n"
            "- 환각이나 추측성 정보 절대 금지"
        ),
    )


    llm = ChatOpenAI(model_name="gpt-4o", temperature=0.7)
    final_prompt = prompt.format(
        message=user_message,
        context=context,
        character=character,
        char_style=char_style
    )
    response = llm.invoke(final_prompt)

    # ----------------- 3) 응답 -----------------
    sources = [
        {
            "source": doc.metadata.get("source", "N/A"),
            "content": doc.page_content[:300],
        }
        for doc in docs
    ]
    logger.info(f"Generated response: {response.content.strip()}")
    return ChatResponse(
        response=response.content.strip(),
        sources=sources,
    )