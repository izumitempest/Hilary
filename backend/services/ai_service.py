import json
import logging
import os
from typing import Dict, List, Optional

import httpx
from groq import Groq
from .emotion_engine import EmotionEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GroqService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.warning("GROQ_API_KEY not found in environment variables.")
            self.api_key = "PLEASE_SET_YOUR_GROQ_API_KEY"

        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"
        self.vision_provider = (os.getenv("VISION_PROVIDER") or "groq").strip().lower()
        self.gemini_api_key = (os.getenv("GEMINI_API_KEY") or "").strip()
        self.gemini_model = os.getenv("GEMINI_VISION_MODEL", "gemini-1.5-flash")
        if self.vision_provider == "gemini" and not self.gemini_api_key:
            logger.warning("VISION_PROVIDER=gemini but GEMINI_API_KEY is missing. Falling back to Groq.")
            self.vision_provider = "groq"

    @property
    def vision_backend(self) -> str:
        return self.vision_provider

    async def get_therapist_response(
        self,
        messages: List[Dict[str, str]],
        current_state: str,
        face_emotion: Optional[str] = None,
    ) -> Dict:
        system_prompt = f"""
        You are Hilary, a world-class AI psychotherapist. 
        Your goal is to provide deep, empathetic, and evidence-based support.

        USER CONTEXT:
        The current detected emotional state is: "{current_state}".
        {f'Facial expression analysis from the user photo: "{face_emotion}". Factor this into your assessment.' if face_emotion else ''}

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
                max_tokens=1024,
            )

            raw_content = chat_completion.choices[0].message.content
            logger.info("AI raw response: %s", raw_content)
            data = json.loads(raw_content)

            if "response" not in data:
                data["response"] = raw_content

            return data

        except Exception as e:
            logger.error("AI Service Error: %s", e)
            return {
                "response": "I'm processing what you've shared. It sounds like you're going through a lot right now. Could you tell me more?",
                "detected_sentiment": "Neutral",
                "intensity": 5.0,
                "insights": "Thinking deeply about our conversation...",
            }

    async def _predict_via_groq(self, image_b64: str) -> Optional[str]:
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze the facial expression and body language in this image. Output only the detected emotion (e.g., Happy, Sad, Anxious, Neutral).",
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                            },
                        ],
                    }
                ],
                temperature=0,
                max_tokens=50,
            )
            raw = completion.choices[0].message.content.strip()
            return EmotionEngine.normalize_face_emotion(raw) or "Neutral"
        except Exception as e:
            logger.error("Groq Vision Emotion Error: %s", e)
        return None

    async def _predict_via_gemini(self, image_b64: str) -> Optional[str]:
        if not self.gemini_api_key:
            return None
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent"
            f"?key={self.gemini_api_key}"
        )
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": "Analyze facial expression and output only one emotion: Happy, Sad, Anxious, Neutral, Angry, or Surprised."},
                        {"inline_data": {"mime_type": "image/jpeg", "data": image_b64}},
                    ]
                }
            ],
            "generationConfig": {"temperature": 0, "maxOutputTokens": 20},
        }
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=20.0)) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    return None
                parts = candidates[0].get("content", {}).get("parts", [])
                text = " ".join([p.get("text", "") for p in parts]).strip()
                return EmotionEngine.normalize_face_emotion(text) or "Neutral"
        except Exception as e:
            logger.error("Gemini Vision Emotion Error: %s", e)
            return None

    async def get_vision_emotion(self, image_b64: str) -> str:
        if self.vision_provider == "gemini":
            emotion = await self._predict_via_gemini(image_b64)
            if emotion:
                return emotion
            fallback = await self._predict_via_groq(image_b64)
            return fallback or "Neutral"

        emotion = await self._predict_via_groq(image_b64)
        if emotion:
            return emotion
        if self.gemini_api_key:
            backup = await self._predict_via_gemini(image_b64)
            if backup:
                return backup
        return "Neutral"

    async def get_audio_transcription(self, file_path: str) -> str:
        try:
            with open(file_path, "rb") as file:
                transcription = self.client.audio.transcriptions.create(
                    file=(file_path, file.read()),
                    model="whisper-large-v3",
                    response_format="json",
                )
            return transcription.text
        except Exception as e:
            logger.error("Transcription Error: %s", e)
            return ""


ai_service = GroqService()
