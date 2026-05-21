---
title: Hilary Mental Health Vision
emoji: 🧠
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# Hilary vision inference (Hugging Face Space)

Hosts `mental_health_image_model.pt` so the **Render API stays lightweight** (no PyTorch on Render).

## 1. Upload the model to the Hub (one time)

```bash
pip install -U huggingface_hub
hf auth login

# Create a model repo at https://huggingface.co/new (type: Model)
export HF_MODEL_REPO=YOUR_USERNAME/hilary-mental-health-vision
./scripts/upload_vision_model_to_hf.sh
# Or manually:
# hf upload "$HF_MODEL_REPO" ../mental_health_image_model.pt mental_health_image_model.pt --repo-type model
```

## 2. Create this Space

1. [New Space](https://huggingface.co/new-space) → **Docker** SDK.
2. Push this folder (`hf_vision_space/`) or connect your GitHub repo subdirectory.
3. **Space secrets / variables:**
   - `HF_MODEL_REPO` = `YOUR_USERNAME/hilary-mental-health-vision` (recommended; no 82MB in git)
   - Or copy `mental_health_image_model.pt` into the Space repo root and set `MODEL_PATH=mental_health_image_model.pt`.

## 3. Wire Render API

In **hilary-api** on Render, set:

| Variable | Example |
|----------|---------|
| `HF_VISION_API_URL` | `https://YOUR_USERNAME-hilary-mental-health-vision.hf.space` |
| `HF_API_TOKEN` | Hub token (only if the Space is **private**) |

Redeploy **hilary-api** after setting variables. Torch is no longer installed on Render.

## API

- `GET /` — health
- `POST /predict` — `{ "image_base64": "<base64>" }` → `{ "emotion": "Happy", "index": 0, "source": "huggingface" }`

Free Spaces sleep when idle; the first request after sleep can take 30–60s.
