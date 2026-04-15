import os
import json
from groq import Groq
from typing import List, Dict

class GroqService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            # Fallback for dev env if env var is missing
            self.api_key = "PLEASE_SET_YOUR_GROQ_API_KEY"
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"

    async def get_therapist_response(self, messages: List[Dict[str, str]], current_state: str) -> Dict:
        system_prompt = f\"\"\"
        You are Hilary, a world-class AI psychotherapist and behavioral health specialist. 
        Your goal is to provide deep, empathetic, and evidence-based support (CBT, DBT, and humanistic approaches).

        CONTEXT:
        The patient's current emotional state is detected as: \"{current_state}\".

        GUIDELINES:
        1. Empathy First: Validate the patient's feelings immediately.
        2. Depth: Don't just give advice; explore the root causes and feelings.
        3. Professionalism: Maintain a calm, safe, and clinical yet warm tone.
        4. Safety: If you detect high risk (suicide, self-harm), prioritize safety resources and encourage professional help.
        5. Analysis: Observe patterns in their speech.

        OUTPUT FORMAT:
        You MUST respond in a valid JSON format with the following keys:
        - "response": Your empathetic therapeutic response.
        - "detected_sentiment": A string representing the user's emotion (e.g., "Critical Distress", "Distressed/Anxious", "Neutral", "Calm/Content", "Positive/Happy").
        - "intensity": A float from 1.0 to 10.0 indicating the intensity of the emotion.
        - "insights": A brief analytical observation about the user's current mental state.

        Example:
        {{
          "response": "I hear how much pain you are in...",
          "detected_sentiment": "Critical Distress",
          "intensity": 9.5,
          "insights": "User is expressing profound hopelessness and withdrawal."
        }}
        \"\"\"
        
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=full_messages,
                model=self.model,
                response_format={"type": "json_object"}
            )
            content = chat_completion.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            print(f"AI Service Error: {e}")
            # Fallback
            return {
                "response": "I'm here for you. Can you tell me more about what's on your mind?",
                "detected_sentiment": "Neutral",
                "intensity": 5.0,
                "insights": "Error in AI processing."
            }

    async def get_vision_emotion(self, image_b64: str) -> str:
        # Placeholder for Llama 3.2 Vision
        return "Neutral"

    async def get_audio_transcription(self, audio_bytes: bytes) -> str:
        # Placeholder for Whisper
        return ""

ai_service = GroqService()
