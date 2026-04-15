import os
import json
import logging
from groq import Groq
from typing import List, Dict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GroqService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.warning("GROQ_API_KEY not found in environment variables.")
            self.api_key = "PLEASE_SET_YOUR_GROQ_API_KEY"
        
        self.client = Groq(api_key=self.api_key)
        # Use a highly capable model for therapeutic reasoning
        self.model = "llama-3.3-70b-versatile"

    async def get_therapist_response(self, messages: List[Dict[str, str]], current_state: str) -> Dict:
        """
        Queries the Groq API to get a therapeutic response and sentiment analysis.
        Returns a dictionary with keys: response, detected_sentiment, intensity, insights.
        """
        system_prompt = f"""
        You are Hilary, a world-class AI psychotherapist. 
        Your goal is to provide deep, empathetic, and evidence-based support.

        USER CONTEXT:
        The current detected emotional state is: "{current_state}".

        INSTRUCTIONS:
        1. Respond with warmth and empathy.
        2. Detect the user's current emotion precisely.
        3. Provide a brief 'insight' or observation about their progress or current state.
        
        OUTPUT:
        You MUST return a JSON object. No other text.
        Structure:
        {{
          "response": "string",
          "detected_sentiment": "Critical Distress" | "Distressed/Anxious" | "Neutral" | "Calm/Content" | "Positive/Happy",
          "intensity": float (1.0 - 10.0),
          "insights": "string"
        }}
        """
        
        # Ensure we only send valid roles to the API
        processed_messages = []
        for msg in messages:
            if msg.get("role") in ["user", "assistant"]:
                processed_messages.append({"role": msg["role"], "content": msg["content"]})

        full_messages = [{"role": "system", "content": system_prompt}] + processed_messages
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=full_messages,
                model=self.model,
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=1024
            )
            
            raw_content = chat_completion.choices[0].message.content
            logger.info(f"AI raw response: {raw_content}")
            
            data = json.loads(raw_content)
            
            # Simple validation of keys
            if "response" not in data:
                data["response"] = raw_content # fallback if it's not JSON despite the instruction
                
            return data
            
        except Exception as e:
            logger.error(f"AI Service Error: {str(e)}")
            return {
                "response": "I'm processing what you've shared. It sounds like you're going through a lot right now. Could you tell me more?",
                "detected_sentiment": "Neutral",
                "intensity": 5.0,
                "insights": "Thinking deeply about our conversation..."
            }

    async def get_vision_emotion(self, image_b64: str) -> str:
        """Analyze base64 image using Groq Vision model."""
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Analyze the facial expression and body language in this image. Output only the detected emotion (e.g., Happy, Sad, Anxious, Neutral)."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_b64}",
                                },
                            },
                        ],
                    }
                ],
                temperature=0,
                max_tokens=50
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Vision Emotion Error: {e}")
            return "Neutral"

    async def get_audio_transcription(self, file_path: str) -> str:
        """Transcribe audio file using Groq Whisper model."""
        try:
            with open(file_path, "rb") as file:
                transcription = self.client.audio.transcriptions.create(
                    file=(file_path, file.read()),
                    model="whisper-large-v3",
                    response_format="json",
                )
            return transcription.text
        except Exception as e:
            logger.error(f"Transcription Error: {e}")
            return ""

ai_service = GroqService()
