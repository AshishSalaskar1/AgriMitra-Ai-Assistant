from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn
import os
from dotenv import load_dotenv
import logging
from api.routes import chat, speech, market, schemes
from core.config import settings

# Load environment variables
load_dotenv()  # This will look for .env file first, then fall back to .env.example

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AgriMitra API",
    description="AI-powered agricultural assistant backend",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(speech.router, prefix="/api/speech", tags=["speech"])
app.include_router(market.router, prefix="/api/market", tags=["market"])
app.include_router(schemes.router, prefix="/api/schemes", tags=["schemes"])

@app.get("/")
async def root():
    return {"message": "AgriMitra API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AgriMitra Backend"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
