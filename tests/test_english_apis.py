"""
Test script for English RAG APIs
"""
import requests
import json

def test_english_rag_query():
    """Test English RAG query endpoint"""
    print("=== Testing English RAG Query ===")
    
    url = "http://localhost:8000/rag/query-english"
    
    test_cases = [
        {
            "character": "rumi",
            "message": "What is the Tiger Exhibition about?",
            "session_id": 12345
        },
        {
            "character": "mira", 
            "message": "Tell me about Hwachodo painting",
            "session_id": 12346
        },
        {
            "character": "zoey",
            "message": "What are the traditional meanings of tigers in Korean art?",
            "session_id": 12347
        },
        {
            "character": "jinu",
            "message": "How does the exhibition connect traditional and modern tiger art?",
            "session_id": 12348
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Character: {test_case['character']}")
        print(f"Message: {test_case['message']}")
        
        try:
            response = requests.post(url, json=test_case)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Response: {result['response']}")
                print(f"Sources: {result['sources']}")
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Exception: {e}")


def test_english_summary():
    """Test English conversation summary endpoint"""
    print("\n=== Testing English Summary ===")
    
    url = "http://localhost:8000/rag/summarize-english"
    
    test_conversation = {
        "session_id": 12345,
        "messages": [
            {
                "role": "user",
                "content": "What is the Tiger Exhibition about?"
            },
            {
                "role": "assistant", 
                "content": "The Tiger Exhibition showcases traditional Korean tiger artworks and their modern interpretations. It features paintings like Hwachodo and Yonghodo that represent the cultural significance of tigers in Korean art."
            },
            {
                "role": "user",
                "content": "Tell me about Hwachodo specifically"
            },
            {
                "role": "assistant",
                "content": "Hwachodo is a traditional Korean painting featuring tigers and magpies. It symbolizes good news and warding off evil spirits, and was popular among common people during the Joseon dynasty."
            },
            {
                "role": "user",
                "content": "How does this connect to modern Korean culture?"
            },
            {
                "role": "assistant",
                "content": "The exhibition shows how traditional tiger symbolism connects to modern Korean pop culture, particularly through characters like those in K-pop Demon Hunters, creating a bridge between historical art and contemporary entertainment."
            }
        ]
    }
    
    try:
        response = requests.post(url, json=test_conversation)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Session ID: {result['session_id']}")
            print(f"Summary: {result['summary']}")
            print(f"Key Topics: {result['key_topics']}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")


def test_english_health():
    """Test English API health"""
    print("\n=== Testing English API Health ===")
    
    health_url = "http://localhost:8000/health"
    
    try:
        response = requests.get(health_url)
        print(f"Health Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")


if __name__ == "__main__":
    print("🚀 Starting English RAG API Tests")
    
    # Test health first
    test_english_health()
    
    # Test RAG queries
    test_english_rag_query()
    
    # Test summary
    test_english_summary()
    
    print("\n✅ English API tests completed!")
