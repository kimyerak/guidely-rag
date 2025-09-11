"""
RAG 서비스
"""
from typing import List
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from sentence_transformers import CrossEncoder
from characters import CHARACTER_STYLE
from models.response_models import ChatResponse
import logging

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self, vectorstore: FAISS, cross_encoder: CrossEncoder):
        self.vectorstore = vectorstore
        self.cross_encoder = cross_encoder
        self.llm = ChatOpenAI(model_name="gpt-4o", temperature=0.7)
    
    def generate_response(self, user_message: str, character: str) -> ChatResponse:
        """
        RAG를 사용하여 챗봇 응답 생성
        
        Args:
            user_message: 사용자 메시지
            character: 캐릭터 이름
            
        Returns:
            ChatResponse: 생성된 응답
        """
        logger.info(f"User message: {user_message}")
        logger.info(f"Character: {character}")

        # 캐릭터 스타일 가져오기
        char_style = CHARACTER_STYLE[character]

        # ----------------- 1) 문맥 검색 (2-stage: Retriever + Reranker) -----------------
        # 1-1) 1차 검색 (Retriever): FAISS에서 Top-10 문서 가져오기
        logger.info("1단계: FAISS에서 관련 문서 10개 검색")
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 10})
        retrieved_docs = retriever.get_relevant_documents(user_message)
        logger.info(f"  -> {len(retrieved_docs)}개 문서 검색 완료.")

        # 1-2) 2차 검색 (Reranker): Cross-encoder로 관련성 높은 Top-3 문서 재선정
        logger.info("2단계: Cross-encoder로 재점수화하여 Top-3 선정")
        # 쿼리와 문서 내용으로 페어 생성
        pairs = [[user_message, doc.page_content] for doc in retrieved_docs]

        # Cross-encoder로 점수 계산
        scores = self.cross_encoder.predict(pairs, show_progress_bar=True)

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
                "당신은 국립중앙박물관의 '호랑이 전시'에서 방문객과 대화하는 챗봇입니다.\n\n"
                
                "## 전시회 배경\n"
                "국립중앙박물관에서 '호랑이 전시'를 개최하여 전통 문양의 호랑이와 현대적인 호랑이의 만남을 보여주고 있습니다.\n\n"
                
                "## 주어진 정보\n"
                "**유저 메시지:**\n{message}\n\n"
                "**참고 자료 (호랑이 전시 관련 문서):**\n{context}\n\n"
                
                "## 캐릭터 설정\n"
                "- **이름**: {char_style[name]}\n"
                "  - **성격**: {char_style[style]}\n"
                "  - **말투**: {char_style[voice]}\n"
                "  - **예시**: \"{char_style[example]}\"\n\n"
                
                "## 임무\n"
                "호랑이 전시에 대해 방문객에게 친근하고 재미있게 설명해주세요. 전통 호랑이 문양과 현대적인 호랑이의 연결점을 자연스럽게 언급하며, "
                "전시품에 대한 정보를 제공하세요.\n\n"
                
                "## 답변 지침\n"
                "1. **캐릭터 유지**: 귀엽고 친근한 말투 유지\n"
                "2. **호랑이 전시 중심**: 전시품, 호랑이 문양, 전통과 현대의 만남에 집중\n"
                "3. **정보 활용**: 참고 자료의 전시품 정보를 자연스럽게 활용\n"
                "4. **재미있게**: 방문객이 즐겁게 관람할 수 있도록 유머와 재미 요소 포함\n\n"
                
                "## 주의사항\n"
                "- 답변만 출력하고 다른 설명 금지\n"
                "- 한국어로 자연스럽게 작성\n"
                "- 호랑이 전시와 관련없는 질문에는 전시로 자연스럽게 유도\n"
                "- 환각이나 추측성 정보 절대 금지"
            ),
        )

        final_prompt = prompt.format(
            message=user_message,
            context=context,
            character=character,
            char_style=char_style
        )
        response = self.llm.invoke(final_prompt)

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
