"""FastAPI ana uygulama"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import List
import tempfile
import os
from pathlib import Path
import time

from .routes import analyze_media, analyze_batch, health_check
from ..config import SUPPORTED_IMAGE_FORMATS, SUPPORTED_VIDEO_FORMATS

app = FastAPI(
    title="AI Detection API",
    description="Model-free AI-generated content detection system",
    version="1.0.0"
)

# CORS middleware - Frontend bağlantısı için
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da spesifik domain kullanın
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files - Frontend serve etmek için
frontend_path = Path(__file__).parent.parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")


@app.get("/")
async def root():
    """Root endpoint - Frontend'e yönlendir"""
    frontend_file = Path(__file__).parent.parent.parent / "frontend" / "app.html"
    if frontend_file.exists():
        return FileResponse(str(frontend_file))
    return {
        "message": "AI Detection API",
        "version": "1.0.0",
        "endpoints": {
            "detect": "/api/v1/detect",
            "batch": "/api/v1/detect/batch",
            "health": "/api/v1/health"
        }
    }


@app.post("/api/v1/detect")
async def detect_endpoint(
    file: UploadFile = File(...),
    fast_mode: bool = False
):
    """
    Tek dosya analizi
    
    Parameters:
    - file: Image or video file
    - fast_mode: Skip expensive tests (optional)
    """
    return await analyze_media(file, fast_mode)


@app.post("/api/v1/detect/batch")
async def detect_batch_endpoint(
    files: List[UploadFile] = File(...)
):
    """
    Batch analiz (max 10 dosya)
    
    Parameters:
    - files: Array of image/video files
    """
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed")
    
    return await analyze_batch(files)


@app.get("/api/v1/health")
async def health_endpoint():
    """Health check endpoint"""
    return health_check()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
