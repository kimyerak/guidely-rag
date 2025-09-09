"""
앱 설정
"""
import os
from dotenv import load_dotenv

load_dotenv()

# 벡터스토어 설정
VECTORSTORE_PATH = "faiss_index"

# 임베딩 모델 설정
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# LLM 설정
LLM_MODEL = "gpt-4o"
LLM_TEMPERATURE = 0.7

# 검색 설정
RETRIEVAL_K = 10  # 1차 검색 문서 수
RERANK_K = 3      # 2차 재점수화 후 선택 문서 수

# 청크 설정
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200
BATCH_SIZE = 500
