"""
English relevance service for checking if user queries are related to the Tiger Exhibition
"""
import logging
from typing import List

logger = logging.getLogger(__name__)


class EnglishRelevanceService:
    """Service for checking relevance of English queries to the Tiger Exhibition"""
    
    def __init__(self):
        # English keywords related to the Tiger Exhibition
        self.relevant_keywords = [
            # Exhibition related
            "tiger", "tigers", "exhibition", "museum", "national museum", "korean museum",
            "art", "artwork", "painting", "paintings", "traditional", "culture",
            
            # Tiger art specific
            "hwachodo", "yonghodo", "sanshindo", "horyeopdo", "tiger painting",
            "tiger art", "korean tiger", "traditional tiger", "tiger symbolism",
            
            # Museum and cultural terms
            "joseon", "dynasty", "korean art", "korean culture", "traditional art",
            "folk art", "minhwa", "korean painting", "east asian art",
            
            # Character and modern connection
            "kpop demon hunters", "character", "characters", "cute tiger",
            "modern interpretation", "contemporary", "pop culture",
            
            # General museum terms
            "visit", "tour", "gallery", "display", "collection", "artifact",
            "history", "heritage", "cultural", "exhibition hall"
        ]
        
        # Non-relevant keywords that should be rejected
        self.irrelevant_keywords = [
            "weather", "restaurant", "hotel", "shopping", "transportation",
            "unrelated", "random", "test", "hello", "hi", "bye", "goodbye"
        ]
    
    def check_relevance(self, query: str) -> bool:
        """
        Check if the English query is relevant to the Tiger Exhibition
        
        Args:
            query: User query in English
            
        Returns:
            bool: True if relevant, False otherwise
        """
        if not query or not isinstance(query, str):
            logger.info("Query is empty or not a string")
            return False
        
        query_lower = query.lower().strip()
        logger.info(f"Checking relevance for query: '{query_lower}'")
        
        # Check for irrelevant keywords first
        for keyword in self.irrelevant_keywords:
            if keyword in query_lower:
                logger.info(f"Query rejected due to irrelevant keyword: {keyword}")
                return False
        
        # Check for relevant keywords
        for keyword in self.relevant_keywords:
            if keyword in query_lower:
                logger.info(f"Query accepted due to relevant keyword: {keyword}")
                return True
        
        # If no keywords match, be lenient for exhibition-related queries
        exhibition_indicators = [
            "what", "how", "when", "where", "why", "tell me", "explain",
            "show", "describe", "about", "information", "details"
        ]
        
        has_question_word = any(indicator in query_lower for indicator in exhibition_indicators)
        logger.info(f"Has question word: {has_question_word}")
        
        # Be more lenient - accept any question longer than 5 characters
        if has_question_word and len(query_lower) > 5:
            logger.info("Query accepted as general exhibition question")
            return True
        
        # Accept any query that mentions "tiger" or "exhibition" even without question words
        if "tiger" in query_lower or "exhibition" in query_lower:
            logger.info("Query accepted due to tiger/exhibition mention")
            return True
        
        logger.info(f"Query rejected as not relevant to Tiger Exhibition: {query_lower}")
        return False
    
    def get_relevant_keywords(self) -> List[str]:
        """Get list of relevant keywords"""
        return self.relevant_keywords.copy()
    
    def get_irrelevant_keywords(self) -> List[str]:
        """Get list of irrelevant keywords"""
        return self.irrelevant_keywords.copy()
