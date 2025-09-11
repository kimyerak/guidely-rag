"""
PostgreSQL + pgvector 기반 RAG 서비스
"""
import logging
import os
from typing import List
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from database.document_service import DocumentService, ChunkService
from database.models import Document, DocumentChunk, SearchResult
from models.response_models import ChatResponse
from characters import CHARACTER_STYLE

# 환경변수 로드
load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class PostgresRAGService:
    """PostgreSQL 기반 RAG 서비스"""
    
    def __init__(self):
        self.embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        self.llm = ChatOpenAI(
            model="gpt-4o-mini", 
            temperature=0.7,
            api_key=os.getenv('OPENAI_API_KEY')
        )
        self.document_service = DocumentService()
        self.chunk_service = ChunkService()
    
    def generate_response(self, user_message: str, character: str) -> ChatResponse:
        """
        PostgreSQL RAG를 사용하여 챗봇 응답 생성
        
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

        # ----------------- 1) 쿼리 임베딩 생성 -----------------
        logger.info("1단계: 쿼리 임베딩 생성")
        query_embedding = self.embedding_model.encode(user_message).tolist()

        # ----------------- 2) 벡터 검색 + 키워드 검색 -----------------
        logger.info("2단계: PostgreSQL 벡터 검색 + 키워드 검색")
        
        # 벡터 검색
        vector_results = self.chunk_service.search_similar_chunks(
            query_embedding=query_embedding,
            match_threshold=0.0,
            match_count=5
        )
        
        # 키워드 검색 (호작도, 용호도, 산신도 등)
        keyword_results = self.chunk_service.search_by_keywords(
            user_message, match_count=5
        )
        
        # 결과 합치기 (중복 제거)
        all_results = vector_results + keyword_results
        seen_ids = set()
        search_results = []
        for result in all_results:
            if result.chunk_id not in seen_ids:
                seen_ids.add(result.chunk_id)
                search_results.append(result)
        
        # 키워드 매칭 가중치 적용 (질문 기반 동적 키워드 추출)
        user_message_lower = user_message.lower()
        logger.info(f"키워드 매칭 가중치 적용 시작 - 검색 결과 {len(search_results)}개")
        
        # 질문에서 핵심 키워드 추출 (2글자 이상)
        import re
        question_keywords = []
        
        # 한글 키워드 추출 (조사 제거)
        korean_words = re.findall(r'[가-힣]{2,}', user_message)
        # 조사 제거: '의', '은', '는', '이', '가', '을', '를', '에', '에서' 등
        particles = ['의', '은', '는', '이', '가', '을', '를', '에', '에서', '로', '으로', '와', '과', '도', '만', '부터', '까지']
        
        for word in korean_words:
            # 조사 제거
            clean_word = word
            for particle in particles:
                if clean_word.endswith(particle):
                    clean_word = clean_word[:-len(particle)]
                    break
            
            if len(clean_word) >= 2:  # 조사 제거 후 2글자 이상인 경우만
                question_keywords.append(clean_word)
        
        # 영어 키워드 추출
        english_words = re.findall(r'[a-zA-Z]{3,}', user_message)
        question_keywords.extend(english_words)
        
        # 숫자 포함 키워드도 추출
        number_words = re.findall(r'[가-힣a-zA-Z]*\d+[가-힣a-zA-Z]*', user_message)
        question_keywords.extend(number_words)
        
        # 중복 제거
        question_keywords = list(set(question_keywords))
        
        logger.info(f"질문: '{user_message}'")
        logger.info(f"질문에서 추출된 키워드: {question_keywords}")
        
        for i, result in enumerate(search_results):
            chunk_text_lower = result.chunk_text.lower()
            
            # 질문 키워드가 문서에 포함된 개수 계산
            keyword_matches = 0
            matched_keywords = []
            
            for keyword in question_keywords:
                if keyword.lower() in chunk_text_lower:
                    keyword_matches += 1
                    matched_keywords.append(keyword)
            
            # 키워드 매칭 개수를 result 객체에 저장
            result.keyword_matches = keyword_matches
            
            logger.info(f"문서 {i+1}: {result.document_title} - 키워드 매칭: {keyword_matches}개")
            if keyword_matches > 0:
                logger.info(f"  매칭된 키워드: {matched_keywords}")
                
                # 키워드 매칭 개수에 비례하여 가중치 부여 (최대 0.6까지)
                boost = min(0.6, keyword_matches * 0.15)
                original_similarity = result.similarity
                result.similarity += boost
                logger.info(f"  가중치 적용: {original_similarity:.4f} + {boost:.3f} = {result.similarity:.4f}")
        
        # 키워드 매칭 우선 정렬
        # 1) 키워드 매칭된 문서를 먼저 정렬 (유사도 내림차순)
        keyword_matches = [r for r in search_results if hasattr(r, 'keyword_matches') and r.keyword_matches > 0]
        other_results = [r for r in search_results if not hasattr(r, 'keyword_matches') or r.keyword_matches == 0]
        
        # 키워드 매칭된 문서들을 키워드 개수 우선, 그 다음 유사도 순으로 정렬
        keyword_matches.sort(key=lambda x: (-x.keyword_matches, -x.similarity))
        other_results.sort(key=lambda x: x.similarity, reverse=True)
        
        # 최종 결과: 키워드 매칭 문서 + 나머지 문서
        search_results = keyword_matches + other_results
        
        logger.info(f"키워드 매칭 우선 정렬 완료: {len(keyword_matches)}개 키워드 매칭, {len(other_results)}개 일반")
        
        logger.info(f"  -> {len(search_results)}개 청크 검색 완료")
        for i, result in enumerate(search_results):
            logger.info(f"    Top {i+1}: {result.document_title} (Similarity: {result.similarity:.4f})")
            logger.info(f"    Content: {result.chunk_text[:100]}...")

        # ----------------- 3) 컨텍스트 구성 -----------------
        context = "\n\n".join([
            f"[{result.document_title}] {result.chunk_text}" 
            for result in search_results
        ])

        # ----------------- 4) 프롬프트 생성 -----------------
        prompt = PromptTemplate(
            input_variables=["message", "context", "character", "char_style"],
            template=(
                "당신은 국립중앙박물관의 '호랑이 전시'에서 방문객과 대화하는 케이팝데몬헌터스 캐릭터 챗봇입니다.\n\n"
                
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
                "1. **간결하게**: 2-3문장으로 간단명료하게 답변\n"
                "2. **정확한 정보**: 참고 자료를 바탕으로 정확한 정보 제공\n"
                "3. **캐릭터 유지**: 귀엽고 친근한 말투 유지\n"
            
                
                "## 주의사항\n"
                "- 답변만 출력하고 다른 설명 금지\n"
                "- 한국어로 자연스럽게 작성\n"
                "- 환각이나 추측성 정보 절대 금지"
            ),
        )

        final_prompt = prompt.format(
            message=user_message,
            context=context,
            character=character,
            char_style=char_style
        )
        
        # ----------------- 5) LLM 응답 생성 -----------------
        response = self.llm.invoke(final_prompt)

        # ----------------- 6) 응답 구성 -----------------
        sources = [
            {
                "source": result.source_url or f"문서: {result.document_title}",
                "content": result.chunk_text[:300],
                "ranking": i + 1,  # 1부터 시작하는 랭킹
                "similarity_score": round(result.similarity, 4),  # 유사도 점수 (소수점 4자리)
                "document_title": result.document_title,
                "chunk_id": result.chunk_id
            }
            for i, result in enumerate(search_results)
        ]
        
        logger.info(f"Generated response: {response.content.strip()}")
        return ChatResponse(
            response=response.content.strip(),
            sources=sources,
        )

    def add_document(self, title: str, content: str, file_type: str = "text", 
                    source_url: str = None, metadata: dict = None) -> int:
        """
        새 문서를 데이터베이스에 추가하고 청크로 분할
        
        Args:
            title: 문서 제목
            content: 문서 내용
            file_type: 파일 타입
            source_url: 원본 URL
            metadata: 메타데이터
            
        Returns:
            int: 생성된 문서 ID
        """
        # 1) 문서 생성
        document = Document(
            title=title,
            file_type=file_type,
            source_url=source_url,
            content=content,
            metadata=metadata or {}
        )
        document_id = self.document_service.create_document(document)
        
        # 2) 청크 분할
        chunks = self._split_into_chunks(content)
        
        # 3) 청크 임베딩 생성 및 저장
        chunk_objects = []
        for i, chunk_text in enumerate(chunks):
            embedding = self.embedding_model.encode(chunk_text).tolist()
            chunk_obj = DocumentChunk(
                chunk_text=chunk_text,
                chunk_index=i,
                embedding=embedding,
                metadata={"chunk_length": len(chunk_text)}
            )
            chunk_objects.append(chunk_obj)
        
        # 4) 청크 저장
        self.chunk_service.create_chunks(document_id, chunk_objects)
        
        logger.info(f"문서 추가 완료: {title} (ID: {document_id}, 청크: {len(chunks)}개)")
        return document_id

    def _split_into_chunks(self, text: str, chunk_size: int = 1200, overlap: int = 200) -> List[str]:
        """텍스트를 청크로 분할"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # 문장 경계에서 자르기
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                cut_point = max(last_period, last_newline)
                if cut_point > start + chunk_size // 2:  # 너무 짧게 자르지 않도록
                    chunk = chunk[:cut_point + 1]
                    end = start + cut_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap
            
            if start >= len(text):
                break
        
        return [chunk for chunk in chunks if chunk.strip()]
