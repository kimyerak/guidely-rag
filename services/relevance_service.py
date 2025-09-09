"""
관련성 검증 서비스
"""
from langchain_openai import ChatOpenAI
import logging

logger = logging.getLogger(__name__)


class RelevanceService:
    def __init__(self):
        self.llm = ChatOpenAI(model_name="gpt-4o", temperature=0.1)
    
    def check_relevance(self, user_message: str) -> bool:
        """
        질문이 전시회/케이팝데몬헌터스와 관련 있는지 확인
        
        Args:
            user_message: 사용자 질문
            
        Returns:
            bool: 관련성 여부
        """
        relevance_prompt = f"""
        다음 질문이 국립중앙박물관의 케이팝데몬헌터스 전시회와 관련이 있는지 판단해주세요.

        **질문**: {user_message}

        **관련성 기준**:
        - 케이팝(K-POP) 관련 질문
        - 전시회, 박물관, 미술, 예술 관련 질문
        - 케이팝데몬헌터스 전시회 관련 질문
        - 인상주의, 미술사, 화가 관련 질문
        - 전시회에서 볼 수 있는 작품이나 내용 관련 질문

        **관련성 판단**:
        - 관련 있음: "YES"
        - 관련 없음: "NO"

        **응답 형식**:
        YES 또는 NO만 출력해주세요.
        """
        
        try:
            response = self.llm.invoke(relevance_prompt)
            is_relevant = response.content.strip().upper() == "YES"
            logger.info(f"관련성 검증: {is_relevant} (질문: {user_message})")
            return is_relevant
        except Exception as e:
            logger.error(f"관련성 검증 오류: {e}")
            # 오류 발생시 기본적으로 관련 있다고 판단
            return True
