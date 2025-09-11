"""
English summary service for conversation summaries
"""
import os
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class EnglishSummaryService:
    """Service for generating English conversation summaries"""
    
    def __init__(self):
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=os.getenv('LLM_MODEL', 'gpt-4o-mini'),
            temperature=float(os.getenv('LLM_TEMPERATURE', '0.7')),
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
        logger.info("English SummaryService initialized successfully")
    
    def generate_summary(self, messages: List[Dict[str, str]], session_id: int, count: int = 10) -> Dict[str, Any]:
        """
        Generate English conversation summary
        
        Args:
            messages: List of conversation messages
            session_id: Session ID
            count: Number of summary sentences to generate (default: 10)
            
        Returns:
            Dict containing summary and key topics
        """
        try:
            logger.info(f"Generating English summary for session {session_id}")
            
            # Format messages for the prompt
            conversation_text = ""
            for msg in messages:
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                conversation_text += f"{role}: {content}\n"
            
            # Create the prompt
            prompt = f"""Please analyze this conversation about the Tiger Exhibition and create a concise summary.

Conversation:
{conversation_text}

Please provide:
1. A brief summary (approximately {count} sentences) of what was discussed
2. Key topics that were covered (list 3-5 main topics)

Focus on:
- Tiger Exhibition content and artworks
- Korean tiger art and culture
- Traditional vs modern interpretations
- Museum visit information
- Any specific questions or interests expressed

Format your response as:
SUMMARY: [your summary here]
KEY_TOPICS: [topic1, topic2, topic3, topic4, topic5]"""
            
            # Generate summary
            messages = [
                SystemMessage(content="You are an expert at analyzing conversations about museum exhibitions and Korean art. Create concise, informative summaries that capture the main points and topics discussed."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            response_text = response.content.strip()
            
            # Parse the response
            summary = ""
            key_topics = []
            
            lines = response_text.split('\n')
            for line in lines:
                if line.startswith('SUMMARY:'):
                    summary = line.replace('SUMMARY:', '').strip()
                elif line.startswith('KEY_TOPICS:'):
                    topics_text = line.replace('KEY_TOPICS:', '').strip()
                    key_topics = [topic.strip() for topic in topics_text.split(',') if topic.strip()]
            
            # Fallback if parsing fails
            if not summary:
                summary = response_text
            if not key_topics:
                key_topics = ["Tiger Exhibition", "Korean Art", "Museum Visit"]
            
            logger.info(f"Generated English summary: {summary[:100]}...")
            logger.info(f"Key topics: {key_topics}")
            
            return {
                "session_id": session_id,
                "summary": summary,
                "key_topics": key_topics
            }
            
        except Exception as e:
            logger.error(f"Error generating English summary: {e}")
            return {
                "session_id": session_id,
                "summary": "Unable to generate summary at this time. The conversation covered topics related to the Tiger Exhibition and Korean art.",
                "key_topics": ["Tiger Exhibition", "Korean Art", "Museum Visit"]
            }
