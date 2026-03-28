"""
Shaxian Snacks Website Backend
Main application entry point
"""

import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from .routes import router

# Create FastAPI app
app = FastAPI(
    title="Shaxian Snacks Website API",
    description="Backend API for Shaxian Snacks introduction website",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")

# Serve static files from the frontend directory
frontend_path = Path(__file__).parent.parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")
else:
    # Fallback: create a simple HTML response
    @app.get("/", response_class=HTMLResponse)
    async def serve_frontend():
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Shaxian Snacks</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    line-height: 1.6;
                }
                h1 { color: #333; }
                .container { text-align: center; margin-top: 50px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Shaxian Snacks Website</h1>
                <p>Frontend files are being generated. Please check back soon!</p>
                <p>API documentation is available at <a href="/api/docs">/api/docs</a></p>
            </div>
        </body>
        </html>
        """

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "shaxian-snacks-website",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )