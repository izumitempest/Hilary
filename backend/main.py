import os
import sys
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Configure logging to catch startup errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hilary-backend")

try:
    from .database import create_db_and_tables
    from . import models
    from .routes import auth, behavior, chat, multimodal, dashboard
except Exception as e:
    logger.error(f"CRITICAL IMPORT ERROR: {str(e)}")
    # If we are on Render, this logs to the console before the silent exit
    print(f"FATAL: {e}", file=sys.stderr)
    sys.exit(3)

load_dotenv()

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(
    title="MindScape AI Mental Health API",
    description="Backend for the MindScape AI Therapist assistant.",
    version="1.0.0",
    lifespan=lifespan
)

def _cors_origins() -> list[str]:
    """Explicit origins required when allow_credentials=True (wildcard is invalid)."""
    defaults = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://hilary-frontend.onrender.com",
    ]
    extra = os.getenv("CORS_ORIGINS", os.getenv("FRONTEND_URL", ""))
    if extra:
        for origin in extra.split(","):
            origin = origin.strip().rstrip("/")
            if origin and origin not in defaults:
                defaults.append(origin)
    return defaults


# JWT is sent via Authorization header (not cookies); explicit origins fix Render CORS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(behavior.router)
app.include_router(chat.router)
app.include_router(multimodal.router)
app.include_router(dashboard.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Hilary AI Mental Health API", "status": "active"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
