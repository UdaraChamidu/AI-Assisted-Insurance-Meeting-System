
import google.generativeai as genai
from config import settings
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    """Handles AI response generation using Google Gemini."""
    
    def __init__(self):
        if not settings.google_api_key or "placeholder" in settings.google_api_key:
            logger.warning("Google API Key is missing or invalid placeholder.")
            self.model = None
        else:
            genai.configure(api_key=settings.google_api_key)
            self.model = genai.GenerativeModel(settings.gemini_model)
            
        # System prompt for insurance assistant
        self.system_prompt = """You are a helpful and professional AI insurance assistant.

Your role:
- Answer customer questions clearly and continuously
- You can use your general knowledge to explain insurance concepts, terms, and general practices
- Be polite, empathetic, and professional
- Maintain a helpful tone, like a knowledgeable implementation consultant
- Keep answers concise (2-3 sentences)

Format your response as:
ANSWER: [your concise answer]
FOLLOW_UP: [suggested follow-up question]
CONFIDENCE: [LOW/MEDIUM/HIGH]

Rules:
- If context is provided, prioritize it.
- If NO context is provided (empty), you MUST answer using your general insurance knowledge.
- Explain terms and concepts helpfully.
- Do not make up specific policy details (like exact prices) unless explicitly provided
- Focus on being a helpful guide
- IMPORTANT: Do not say "I cannot answer" just because documents are missing. Be a general chatbot.
"""
    
    def generate_response(
        self,
        query: str,
        context_chunks: List[Dict[str, any]],
        conversation_history: Optional[List[str]] = None
    ) -> Dict[str, any]:
        """
        Generate AI response based on query and RAG context using Gemini.
        """
        try:
            if not self.model:
                raise ValueError("Google API Key not configured.")

            # Build context from chunks
            context_text = "\n\n".join([
                f"Source: {chunk.get('metadata', {}).get('source', 'Unknown')}\n{chunk.get('text', '')}"
                for chunk in context_chunks
            ])
            
            # Construct Prompt
            full_prompt = f"""{self.system_prompt}

CONTEXT FROM INSURANCE DOCUMENTS:
{context_text}

CUSTOMER QUESTION:
{query}

Provide your response following the exact format specified above.
"""
            # Add history if available
            if conversation_history:
                history_text = "\n".join(conversation_history[-5:])
                full_prompt += f"\n\nRECENT CONVERSATION:\n{history_text}\n"

            # Generate response
            response = self.model.generate_content(full_prompt)
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
            
            logger.info(f"Generated Gemini response for query: {query[:50]}...")
            
            return {
                'answer': answer,
                'follow_up_question': follow_up,
                'confidence': confidence_score,
                'raw_response': response_text
            }
            
        except Exception as e:
            logger.error(f"Failed to generate Gemini response: {str(e)}")
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
        """
        try:
            if not self.model:
                return "Gemini not configured."

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
            if not self.model:
                return ""
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception:
            return ""
