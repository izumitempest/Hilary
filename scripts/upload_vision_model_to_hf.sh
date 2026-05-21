#!/usr/bin/env bash
# Upload mental_health_image_model.pt to a Hugging Face model repo.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MODEL_FILE="${ROOT}/mental_health_image_model.pt"

if [[ -z "${HF_MODEL_REPO:-}" ]]; then
  echo "Usage: HF_MODEL_REPO=your-username/hilary-mental-health-vision $0"
  exit 1
fi

if [[ ! -f "$MODEL_FILE" ]]; then
  echo "Missing $MODEL_FILE"
  exit 1
fi

HF_CMD=""
if command -v hf >/dev/null 2>&1; then
  HF_CMD=hf
elif [[ -x "${ROOT}/.venv/bin/hf" ]]; then
  HF_CMD="${ROOT}/.venv/bin/hf"
fi

if [[ -z "$HF_CMD" ]]; thenhf upload dvn404/hilary-mental-health-vision mental_health_image_model.pt mental_health_image_model.pt --repo-type model
  echo "Install the Hugging Face CLI: pip install -U huggingface_hub"
  echo "Then log in: hf auth login"
  exit 1
fi

"$HF_CMD" upload "$HF_MODEL_REPO" "$MODEL_FILE" mental_health_image_model.pt --repo-type model
echo "Uploaded to https://huggingface.co/${HF_MODEL_REPO}"
