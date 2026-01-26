"""
Google Gemini service for AI response generation.
"""

import google.generativeai as genai
from config import settings
from typing import List, Dict, Optional
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv(override=True)

class GeminiService:
    """Handles AI response generation using Google Gemini."""
    
    def __init__(self):
        genai.configure(api_key=settings.google_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        
        # System prompt for insurance assistant
        self.system_prompt = """You are a Compliance-First AI Assistant for a licensed health insurance agent.
Your goal is to retrieve authoritative regulatory text and surface safe, citable answers.

Core Rules:
1. ONLY use the provided "CONTEXT FROM INSURANCE DOCUMENTS" to answer.
2. If the answer is NOT in the context, state: "Information not found in authoritative sources. Needs verification."
3. DO NOT guess, extrapolate, or use outside knowledge to fill gaps.
4. DO NOT provide specific pricing or plan details unless explicitly in the text.
5. If the context is ambiguous, recommend escalation to a specialist.
6. Keep answers short, professional, and point to the source if possible.

Format your response as:
ANSWER: [your concise answer]
FOLLOW_UP: [suggested follow-up question]
CONFIDENCE: [LOW/MEDIUM/HIGH]
"""
    
    def generate_response(
        self,
        query: str,
        context_chunks: List[Dict[str, any]],
        conversation_history: Optional[List[str]] = None
    ) -> Dict[str, any]:
        """
        Generate AI response based on query and RAG context.
        
        Args:
            query: Customer's question
            context_chunks: Retrieved context from Pinecone
            conversation_history: Optional previous conversation
        
        Returns:
            Dict with answer, follow_up, and confidence
        """
        try:
            # Build context from chunks
            context_text = "\n\n".join([
                f"Source: {chunk.get('metadata', {}).get('source', 'Unknown')}\n{chunk.get('text', '')}"
                for chunk in context_chunks
            ])
            
            # Build prompt
            prompt = f"""{self.system_prompt}

CONTEXT FROM INSURANCE DOCUMENTS:
{context_text}

CUSTOMER QUESTION:
{query}

Provide your response following the exact format specified above.
"""
            
            # Add conversation history if available
            if conversation_history:
                history_text = "\n".join(conversation_history[-5:])  # Last 5 exchanges
                prompt += f"\n\nRECENT CONVERSATION:\n{history_text}\n"
            
            # Generate response
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Parse response
            answer = ""
            follow_up = ""
            confidence = "MEDIUM"
            
            for line in response_text.split('\n'):
                if line.startswith('ANSWER:'):
                    answer = line.replace('ANSWER:', '').strip()
                elif line.startswith('FOLLOW_UP:'):
                    follow_up = line.replace('FOLLOW_UP:', '').strip()
                elif line.startswith('CONFIDENCE:'):
                    confidence = line.replace('CONFIDENCE:', '').strip()
            
            # Fallback if parsing fails
            if not answer:
                answer = response_text
            
            # Map confidence to numeric
            confidence_map = {"LOW": 0.5, "MEDIUM": 0.75, "HIGH": 0.95}
            confidence_score = confidence_map.get(confidence, 0.75)
            
            logger.info(f"Generated AI response for query: {query[:50]}...")
            
            return {
                'answer': answer,
                'follow_up_question': follow_up,
                'confidence': confidence_score,
                'raw_response': response_text
            }
            
        except Exception as e:
            logger.error(f"Failed to generate AI response: {str(e)}")
            return {
                'answer': f"I'm having trouble processing that question right now. Error details: {str(e)}",
                'follow_up_question': "What specific aspect of insurance coverage are you interested in?",
                'confidence': 0.0,
                'error': str(e)
            }
    
    def generate_summary(
        self,
        conversation_transcript: str
    ) -> str:
        """
        Generate a summary of the conversation.
        
        Args:
            conversation_transcript: Full conversation text
        
        Returns:
            Summary text
        """
        try:
            prompt = f"""Summarize the following insurance consultation conversation. 
Include key topics discussed, customer concerns, and any action items.

CONVERSATION:
{conversation_transcript}

Provide a concise summary in 3-5 bullet points."""
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {str(e)}")
            return "Summary generation failed."

    def complete(self, prompt: str) -> str:
        """Raw completion for utility tasks."""
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception:
            return ""


# Global service instance logic
if settings.ai_provider == "openai":
    try:
        from services.openai_service import OpenAIService
        logger.info("Using OpenAI Service Provider")
        print("DEBUG: Initializing OpenAI Service...")
        gemini_service = OpenAIService()
        print("DEBUG: OpenAI Service Initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI Service: {e}")
        print(f"DEBUG: Failed to initialize OpenAI Service: {e}")
        # Fallback to Gemini
        print("DEBUG: Falling back to Gemini...")
        gemini_service = GeminiService()
else:
    logger.info("Using Gemini Service Provider")
    print(f"DEBUG: Using Gemini Service Provider (Config: {settings.ai_provider})")
    gemini_service = GeminiService()

