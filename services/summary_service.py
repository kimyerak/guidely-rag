"""
요약 서비스
"""
import json
import re
from typing import List
from langchain_openai import ChatOpenAI
from models.request_models import ConversationMessage
from models.response_models import ConversationSummaryResponse
import logging

logger = logging.getLogger(__name__)


class SummaryService:
    def __init__(self):
        self.llm = ChatOpenAI(model_name="gpt-4o", temperature=0.7)
    
    def generate_summary(self, session_id: str, messages: List[ConversationMessage], count: int) -> ConversationSummaryResponse:
        """
        대화 요약 생성
        
        Args:
            session_id: 세션 ID
            messages: 대화 메시지 리스트
            count: 생성할 요약 문장 개수
            
        Returns:
            ConversationSummaryResponse: 생성된 요약
        """
        logger.info(f"대화 요약 요청: session_id={session_id}, 메시지 수={len(messages)}")
        
        # 대화 내용을 하나의 텍스트로 합치기
        conversation_text = ""
        for msg in messages:
            conversation_text += f"{msg.role}: {msg.content}\n"
        
        logger.info(f"대화 텍스트 길이: {len(conversation_text)} 문자")
        
        summary_prompt = f"""
        다음은 전시회에서 방문객과 챗봇 간의 대화입니다. 
        이 대화를 바탕으로 엔딩크레딧용 감성적이고 시적인 한 줄 요약 {count}개를 만들어주세요.

        **대화 내용:**
        {conversation_text}

        **요구사항:**
        1. 각 요약은 한 문장 또는 한 구절로 간결하게
        2. 감성적이고 시적인 표현 사용
        3. 방문객이 경험한 감동이나 새로운 발견을 담아내기
        4. 전시회의 분위기와 예술적 감성을 반영
        5. 각 요약은 독립적이면서도 전체적으로 조화로워야 함

        **예시 스타일:**
        - "까치 문양, 전통 속에서 되살아난 날개짓"
        - "미라가 던진 질문에 상상력이 끝없이 번져갔어"
        - "모네의 붓끝에서 피어난 빛의 향연을 만났어"

        **응답 형식 (JSON):**
        {{
            "summaries": [
                "첫 번째 감성적인 요약",
                "두 번째 감성적인 요약",
                "세 번째 감성적인 요약"
            ]
        }}

        JSON 형식으로만 응답해주세요:
        """
        
        try:
            response = self.llm.invoke(summary_prompt)
            
            # JSON 파싱
            json_match = re.search(r'```json\s*(.*?)\s*```', response.content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response.content.strip()
            
            summary_data = json.loads(json_str)
            summaries = summary_data.get("summaries", [])
            
            logger.info(f"대화 요약 완료: {len(summaries)}개 요약 생성")
            
            return ConversationSummaryResponse(
                session_id=session_id,
                total_messages=len(messages),
                summaries=summaries
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류: {e}")
            # 파싱 실패시 기본 응답
            return ConversationSummaryResponse(
                session_id=session_id,
                total_messages=len(messages),
                summaries=[
                    "의미있는 대화 속에서 새로운 발견을 했어",
                    "전시회에서 만난 특별한 순간들"
                ]
            )
            
        except Exception as e:
            logger.error(f"대화 요약 생성 오류: {e}")
            raise
