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
            # 전시회 관련 용어들 (데이터베이스에 없을 수 있지만 관련성은 있음)
            '맹호도', '용호도', '산신도', '호작도', '작호도', '호호도', '까치호랑이', '호랑이그림', '호랑이문양',
            # 일반적인 질문어들 (단독으로는 관련성 판단하지 않음)
            '안녕'
        ]
        
        # 구체적인 질문어들 (다른 키워드와 함께 있을 때만 관련성 인정)
        question_words = [
            '뭐', '무엇', '어떤', '어디', '언제', '왜', '어떻게', '알려', '설명', '궁금', '이해'
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
        
        # 관련 키워드가 하나라도 있으면 True (부분 매칭 포함)
        for keyword in relevant_keywords:
            if keyword in user_message_lower:
                logger.info(f"관련성 검증: True (관련 키워드: {keyword}) (질문: {user_message})")
                return True
        
        # 조사가 붙은 경우도 확인 (예: "작호도가", "맹호도는")
        for keyword in relevant_keywords:
            if len(keyword) >= 3:  # 3글자 이상인 키워드만
                for particle in ['가', '는', '은', '을', '를', '의', '에', '에서', '로', '으로', '와', '과', '도', '만']:
                    if f"{keyword}{particle}" in user_message_lower:
                        logger.info(f"관련성 검증: True (관련 키워드+조사: {keyword}{particle}) (질문: {user_message})")
                        return True
        
        # 질문어만 있고 관련 키워드가 없으면 False (더 엄격하게)
        has_question_word = any(word in user_message_lower for word in question_words)
        if has_question_word:
            logger.info(f"관련성 검증: False (질문어만 있고 관련 키워드 없음) (질문: {user_message})")
            return False
        
        # 키워드가 없으면 기본적으로 관련 없다고 판단 (더 엄격하게)
        logger.info(f"관련성 검증: False (기본값) (질문: {user_message})")
        return False
