"""
관련성 검증 서비스
"""
import logging

logger = logging.getLogger(__name__)


class RelevanceService:
    def __init__(self):
        pass
    
    def check_relevance(self, user_message: str) -> bool:
        """
        질문이 전시회/케이팝데몬헌터스와 관련 있는지 확인 (키워드 기반)
        
        Args:
            user_message: 사용자 질문
            
        Returns:
            bool: 관련성 여부
        """
        # 관련 키워드들 (호랑이 전시 중심)
        relevant_keywords = [
            # 호랑이 전시 관련
            '호랑이', '까치', '호랑이전시', '호랑이 전시', '까치문양', '전통', '문양',
            '국립중앙박물관', '박물관', '전시', '전시회', '전시장', '관람', '티켓', '입장', '작품', '유물',
            # 미술/예술 관련
            '미술', '예술', '화가', '그림', '조각', '디자인', '패션', '스타일', '아름다움', '창작',
            # 일반적인 질문어들
            '뭐', '무엇', '어떤', '어디', '언제', '왜', '어떻게', '알려', '설명', '궁금', '이해', '안녕'
        ]
        
        # 명확히 관련없는 키워드들
        irrelevant_keywords = [
            '날씨', '주식', '부동산', '정치', '경제', '스포츠', '게임', '영화', '드라마',
            '요리', '레시피', '건강', '의료', '병원', '약', '운동', '다이어트', '여행', '호텔',
            '쇼핑', '배송', '환불', '고객서비스', '기술지원'
        ]
        
        user_message_lower = user_message.lower()
        
        # 명확히 관련없는 키워드가 있으면 False
        for keyword in irrelevant_keywords:
            if keyword in user_message_lower:
                logger.info(f"관련성 검증: False (관련없는 키워드: {keyword}) (질문: {user_message})")
                return False
        
        # 관련 키워드가 하나라도 있으면 True
        for keyword in relevant_keywords:
            if keyword in user_message_lower:
                logger.info(f"관련성 검증: True (관련 키워드: {keyword}) (질문: {user_message})")
                return True
        
        # 키워드가 없으면 기본적으로 관련 있다고 판단 (더 관대하게)
        logger.info(f"관련성 검증: True (기본값) (질문: {user_message})")
        return True
