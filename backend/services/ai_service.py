import os
import json
import logging
from typing import List, Dict, Optional

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

        self.hf_vision_url = (os.getenv("HF_VISION_API_URL") or "").strip().rstrip("/")
        self.hf_token = (os.getenv("HF_API_TOKEN") or os.getenv("HUGGINGFACE_API_TOKEN") or "").strip()

        if self.hf_vision_url:
            logger.info("Vision inference: Hugging Face Space at %s", self.hf_vision_url)
        else:
            logger.info("Vision inference: Groq Vision fallback (set HF_VISION_API_URL for custom model)")

    @property
    def vision_backend(self) -> str:
        return "huggingface" if self.hf_vision_url else "groq-vision"

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

    async def _predict_via_huggingface(self, image_b64: str) -> Optional[str]:
        if not self.hf_vision_url:
            return None

        headers = {"Content-Type": "application/json"}
        if self.hf_token:
            headers["Authorization"] = f"Bearer {self.hf_token}"

        payload = {"image_base64": image_b64}
        timeout = httpx.Timeout(90.0, connect=30.0)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{self.hf_vision_url}/predict",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()
                emotion = data.get("emotion", "Neutral")
                logger.info("HF vision detected: %s", emotion)
                return EmotionEngine.normalize_face_emotion(emotion) or "Neutral"
        except httpx.HTTPStatusError as e:
            logger.error("HF vision HTTP error %s: %s", e.response.status_code, e.response.text)
        except Exception as e:
            logger.error("HF vision request failed: %s", e)
        return None

    async def get_vision_emotion(self, image_b64: str) -> str:
        """Custom model on Hugging Face Space, then Groq Vision fallback."""
        hf_emotion = await self._predict_via_huggingface(image_b64)
        if hf_emotion:
            return hf_emotion

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
