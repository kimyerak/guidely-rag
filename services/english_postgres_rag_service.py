"""
English RAG service using PostgreSQL + pgvector for retrieval
"""
import os
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv

from sentence_transformers import SentenceTransformer
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from database.document_service import DocumentService, ChunkService
from database.models import SearchResult

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class EnglishPostgresRAGService:
    """English RAG service using PostgreSQL for retrieval"""
    
    def __init__(self):
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=os.getenv('LLM_MODEL', 'gpt-4o-mini'),
            temperature=float(os.getenv('LLM_TEMPERATURE', '0.7')),
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
        # Initialize services
        self.document_service = DocumentService()
        self.chunk_service = ChunkService()
        
        logger.info("English PostgresRAGService initialized successfully")
    
    def generate_response(self, query: str, character: str = "rumi") -> Dict[str, Any]:
        """
        Generate English response using RAG
        
        Args:
            query: User query in English
            character: Character name (rumi, yuna, etc.)
            
        Returns:
            Dict containing response and sources
        """
        try:
            logger.info(f"Generating English response for query: {query}")
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search for similar chunks using vector search
            vector_results = self.chunk_service.search_similar_chunks(
                query_embedding, 
                match_threshold=0.0,  # Low threshold for broader results
                match_count=10
            )
            
            # Search for keyword matches
            keyword_results = self.chunk_service.search_by_keywords(
                query, 
                match_count=10
            )
            
            # Combine and deduplicate results
            all_results = vector_results + keyword_results
            unique_results = {}
            for result in all_results:
                if result.chunk_id not in unique_results:
                    unique_results[result.chunk_id] = result
            
            # Sort by similarity score (higher is better)
            sorted_results = sorted(
                unique_results.values(), 
                key=lambda x: x.similarity, 
                reverse=True
            )
            
            # Take top results
            top_results = sorted_results[:5]
            
            logger.info(f"Found {len(top_results)} relevant chunks")
            
            # Check for "unknown information" - no results or low similarity
            if not top_results:
                logger.info("No search results found - generating 'unknown' response")
                return self._generate_unknown_english_response(query, character)
            
            # Check maximum similarity score
            max_similarity = max(result.similarity for result in top_results)
            logger.info(f"Maximum similarity score: {max_similarity:.4f}")
            
            # Similarity threshold (if below 0.6, generate "unknown" response)
            SIMILARITY_THRESHOLD = 0.6
            if max_similarity < SIMILARITY_THRESHOLD:
                logger.info(f"Similarity below threshold ({SIMILARITY_THRESHOLD}) - generating 'unknown' response")
                return self._generate_unknown_english_response(query, character)
            
            # Additional validation: Check if question keywords are actually in search results
            import re
            english_words = re.findall(r'[a-zA-Z]{3,}', query)
            question_keywords = english_words
            
            context_text = " ".join([result.chunk_text for result in top_results]).lower()
            keyword_found = any(keyword.lower() in context_text for keyword in question_keywords)
            
            if not keyword_found and question_keywords:
                logger.info(f"Question keywords({question_keywords}) not found in search results - generating 'unknown' response")
                return self._generate_unknown_english_response(query, character)
            
            # Build context from retrieved chunks
            context_parts = []
            sources = []
            
            for i, result in enumerate(top_results):
                context_parts.append(result.chunk_text)
                
                # Add detailed source information with ranking
                source_info = {
                    "source": result.source_url or f"Document: {result.document_title}",
                    "content": result.chunk_text[:300],
                    "ranking": i + 1,  # 1부터 시작하는 랭킹
                    "similarity_score": round(result.similarity, 4),  # 유사도 점수
                    "document_title": result.document_title,
                    "chunk_id": result.chunk_id
                }
                sources.append(source_info)
            
            context = "\n\n".join(context_parts)
            
            # Create character-specific system prompt
            character_prompts = {
                "rumi": "You are Rumi, a cheerful and knowledgeable guide for the Tiger Exhibition at the National Museum. You love sharing interesting facts about Korean tiger art and culture. Keep your responses concise (2-3 sentences) and always reference specific artworks or cultural elements when possible.",
                "mira": "You are Mira, a curious and adventurous guide for the Tiger Exhibition. You enjoy exploring new perspectives on traditional Korean art and connecting it to modern culture. Keep your responses concise (2-3 sentences) and always reference specific artworks or cultural elements when possible.",
                "zoey": "You are Zoey, an imaginative and creative guide for the Tiger Exhibition. You love using metaphors and creative explanations to help visitors understand Korean tiger art. Keep your responses concise (2-3 sentences) and always reference specific artworks or cultural elements when possible.",
                "jinu": "You are Jinu, a logical and systematic guide for the Tiger Exhibition. You focus on facts and provide clear, structured explanations about Korean tiger art and culture. Keep your responses concise (2-3 sentences) and always reference specific artworks or cultural elements when possible.",
                "default": "You are a knowledgeable guide for the Tiger Exhibition at the National Museum. You help visitors understand Korean tiger art and culture. Keep your responses concise (2-3 sentences) and always reference specific artworks or cultural elements when possible."
            }
            
            system_prompt = character_prompts.get(character, character_prompts["default"])
            
            # Create the prompt
            prompt = f"""You are a guide for the Tiger Exhibition at the National Museum. Answer the user's question about Korean tiger art and culture based on the provided context.

Context about the Tiger Exhibition:
{context}

User Question: {query}

Guidelines:
- Answer in English
- Be concise (2-3 sentences)
- Reference specific artworks, artists, or cultural elements when possible
- Focus on the connection between traditional Korean tiger art and modern interpretations
- If you don't find relevant information in the context, say you don't have specific information about that topic
- Always be helpful and encouraging about visiting the exhibition

Response:"""
            
            # Generate response
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            response_text = response.content.strip()
            
            logger.info(f"Generated English response: {response_text[:100]}...")
            
            return {
                "response": response_text,
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"Error generating English response: {e}")
            return {
                "response": "I'm sorry, I'm having trouble accessing information about the Tiger Exhibition right now. Please try again later or visit the museum for more details!",
                "sources": []
            }
    
    def _generate_unknown_english_response(self, query: str, character: str) -> Dict[str, Any]:
        """
        Generate English response for unknown information
        
        Args:
            query: User query
            character: Character name
            
        Returns:
            Dict containing "unknown" response
        """
        # Character-specific "unknown" response templates
        unknown_responses = {
            "rumi": "Hmm... I'm not sure about that! 😅 I know a lot about the Tiger Exhibition, but I still need to study more about other topics. Feel free to ask me anything about the Tiger Exhibition!",
            "mira": "Well... I'm not certain about that part. I can tell you all about the Tiger Exhibition, but I'm not sure about other subjects. Please ask me more about the exhibition!",
            "zoey": "Oh? I don't know about that either! 🤔 I know lots of interesting stories about the Tiger Exhibition, but I still need to learn about other things! Ask me anything about the exhibition!",
            "jinu": "I apologize, but I don't have accurate information about that. I can provide precise information about the Tiger Exhibition, but I'm not sure about other topics. Please ask me about the exhibition."
        }
        
        response_text = unknown_responses.get(character, unknown_responses["rumi"])
        
        logger.info(f"Generated English 'unknown' response: {response_text}")
        return {
            "response": response_text,
            "sources": []
        }
