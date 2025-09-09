"""
벡터스토어 유틸리티
"""
from typing import List
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
import textwrap
import logging

logger = logging.getLogger(__name__)


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
