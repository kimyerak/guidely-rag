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
            Dict containing session_id, total_messages, and summaries array
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
            prompt = f"""Please analyze this conversation about the Tiger Exhibition and create {count} poetic, emotional summary sentences for ending credits.

Conversation:
{conversation_text}

Please create {count} short, poetic summary sentences that capture:
- The emotional experience of the visitor
- Key discoveries or insights from the conversation
- The artistic and cultural atmosphere of the exhibition
- The connection between traditional and modern Korean art

Each summary should be:
- One sentence or short phrase
- Emotional and poetic
- Independent but harmonious with others
- Focused on the visitor's experience and discoveries

Format your response as JSON:
{{
    "summaries": [
        "First poetic summary sentence",
        "Second poetic summary sentence",
        "Third poetic summary sentence"
    ]
}}

Return only the JSON response:"""
            
            # Generate summary
            messages = [
                SystemMessage(content="You are an expert at creating poetic, emotional summaries for museum exhibition conversations. Create beautiful, concise summaries that capture the visitor's emotional journey and discoveries."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            response_text = response.content.strip()
            
            # Parse JSON response
            import json
            import re
            
            # Extract JSON from response
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response_text.strip()
            
            try:
                summary_data = json.loads(json_str)
                summaries = summary_data.get("summaries", [])
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                summaries = [
                    "Meaningful discoveries in the conversation",
                    "Special moments shared at the exhibition"
                ]
            
            logger.info(f"Generated {len(summaries)} English summary sentences")
            
            return {
                "session_id": session_id,
                "total_messages": len(messages),
                "summaries": summaries
            }
            
        except Exception as e:
            logger.error(f"Error generating English summary: {e}")
            return {
                "session_id": session_id,
                "total_messages": len(messages) if 'messages' in locals() else 0,
                "summaries": [
                    "Meaningful discoveries in the conversation",
                    "Special moments shared at the exhibition"
                ]
            }
