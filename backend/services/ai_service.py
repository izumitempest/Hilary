import os
import json
import logging
from groq import Groq
from typing import List, Dict, Optional
from .emotion_engine import EmotionEngine
import base64
from io import BytesIO
from PIL import Image

try:
    import torch
    import torchvision.transforms as transforms
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

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
        
        # Load custom PyTorch model for visual sentiment analysis
        self.custom_vision_model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu") if TORCH_AVAILABLE else None
        
        if TORCH_AVAILABLE:
            try:
                # Assuming the model is in the project root
                model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "mental_health_image_model.pt")
                if os.path.exists(model_path):
                    logger.info(f"Loading custom mental health image model from {model_path}...")
                    self.custom_vision_model = torch.load(model_path, map_location=self.device)
                    # We might need to set it to eval mode if it's a module
                    if hasattr(self.custom_vision_model, 'eval'):
                        self.custom_vision_model.eval()
                    logger.info("Custom model loaded successfully.")
                else:
                    logger.warning(f"Custom model not found at {model_path}")
            except Exception as e:
                logger.error(f"Failed to load custom model: {e}")
                
        # Define standard transforms for Image models (like ResNet)
        if TORCH_AVAILABLE:
            self.transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])

    async def get_therapist_response(
        self,
        messages: List[Dict[str, str]],
        current_state: str,
        face_emotion: Optional[str] = None,
    ) -> Dict:
        """
        Queries the Groq API to get a therapeutic response and sentiment analysis.
        Returns a dictionary with keys: response, detected_sentiment, intensity, insights.
        """
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
        """Analyze base64 image using custom PyTorch model or fallback to Groq Vision model."""
        if self.custom_vision_model and TORCH_AVAILABLE:
            try:
                # Decode base64 and process
                image_data = base64.b64decode(image_b64)
                image = Image.open(BytesIO(image_data)).convert('RGB')
                
                # Prepare tensor
                input_tensor = self.transform(image).unsqueeze(0).to(self.device)
                
                # Run inference
                with torch.no_grad():
                    output = self.custom_vision_model(input_tensor)
                    
                # Assuming standard output where index maps to emotion
                # We'll map the top prediction to a sentiment string
                emotions = ["Happy", "Sad", "Anxious", "Neutral", "Angry", "Surprised"]
                
                # Get the index of max log-probability
                if hasattr(output, 'logits'):
                    pred = output.logits.argmax(dim=1, keepdim=True)
                else:
                    pred = output.argmax(dim=1, keepdim=True)
                    
                idx = pred.item()
                detected = emotions[idx] if idx < len(emotions) else "Neutral"
                detected = EmotionEngine.normalize_face_emotion(detected) or "Neutral"
                logger.info(f"Custom model detected emotion: {detected}")
                return detected
                
            except Exception as e:
                logger.error(f"Custom Vision Model Error: {e}")
                logger.info("Falling back to Groq Vision model...")
                
        # Fallback to Groq Vision
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
            raw = completion.choices[0].message.content.strip()
            return EmotionEngine.normalize_face_emotion(raw) or "Neutral"
        except Exception as e:
            logger.error(f"Groq Vision Emotion Error: {e}")
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
