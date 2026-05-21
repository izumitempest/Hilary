"""
Hugging Face Space — mental health image emotion inference.
Expose POST /predict with JSON {"image_base64": "..."} for the Render API.
"""
import base64
import os
from io import BytesIO

import torch
import torchvision.transforms as transforms
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from huggingface_hub import hf_hub_download
from PIL import Image
from pydantic import BaseModel

EMOTIONS = ["Happy", "Sad", "Anxious", "Neutral", "Angry", "Surprised"]

app = FastAPI(title="Hilary Vision API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

model = None
device = torch.device("cpu")


def _resolve_model_path() -> str:
    local = os.getenv("MODEL_PATH", "mental_health_image_model.pt")
    if os.path.isfile(local):
        return local
    repo = os.getenv("HF_MODEL_REPO")
    if not repo:
        raise FileNotFoundError(
            "Set HF_MODEL_REPO (e.g. your-username/hilary-mental-health-vision) "
            "or place mental_health_image_model.pt in the Space root."
        )
    return hf_hub_download(repo_id=repo, filename="mental_health_image_model.pt")


@app.on_event("startup")
def load_model():
    global model
    path = _resolve_model_path()
    model = torch.load(path, map_location=device, weights_only=False)
    if hasattr(model, "eval"):
        model.eval()


class PredictRequest(BaseModel):
    image_base64: str


class PredictResponse(BaseModel):
    emotion: str
    index: int
    source: str = "huggingface"


@app.get("/")
def health():
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "labels": EMOTIONS,
    }


@app.post("/predict", response_model=PredictResponse)
def predict(body: PredictRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")

    try:
        raw = body.image_base64
        if "," in raw:
            raw = raw.split(",", 1)[1]
        image_data = base64.b64decode(raw)
        image = Image.open(BytesIO(image_data)).convert("RGB")
        tensor = transform(image).unsqueeze(0).to(device)

        with torch.no_grad():
            output = model(tensor)

        if hasattr(output, "logits"):
            idx = int(output.logits.argmax(dim=1).item())
        else:
            idx = int(output.argmax(dim=1).item())

        emotion = EMOTIONS[idx] if idx < len(EMOTIONS) else "Neutral"
        return PredictResponse(emotion=emotion, index=idx)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
