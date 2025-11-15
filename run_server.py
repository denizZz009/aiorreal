"""API sunucusunu başlat"""

import uvicorn

if __name__ == "__main__":
    print("Starting AI Detection API Server...")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/api/v1/health")
    print("\nPress CTRL+C to stop\n")
    
    uvicorn.run(
        "ai_detector.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
