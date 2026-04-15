import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import create_db_and_tables
from .routes import auth, behavior, chat, multimodal, dashboard
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Hilary AI Mental Health API",
    description="Backend for the Hilary AI Therapist assistant.",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set this to your frontend URL in production
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
