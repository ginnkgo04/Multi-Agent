from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path

from app.routes import router
from app.services import RedPandaService

app = FastAPI(
    title="Red Panda Information Website",
    description="A backend service for the red panda informational website",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = Path(__file__).parent.parent.parent / "frontend"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include API routes
app.include_router(router, prefix="/api")

# Initialize services
red_panda_service = RedPandaService()

@app.get("/", response_class=HTMLResponse)
async def serve_homepage():
    """Serve the main HTML page"""
    html_path = static_dir / "index.html" if static_dir.exists() else None
    
    if html_path and html_path.exists():
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    
    # Fallback HTML if static files not found
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Red Panda Information</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            h1 { color: #d35400; }
            .message { background: #f8f9fa; padding: 20px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>Red Panda Information Website</h1>
        <div class="message">
            <p>The red panda website backend is running. Frontend files should be placed in the frontend directory.</p>
            <p>Visit <a href="/api/health">/api/health</a> to check API status.</p>
            <p>Visit <a href="/api/red-panda/facts">/api/red-panda/facts</a> for red panda facts.</p>
        </div>
    </body>
    </html>
    """)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "red-panda-website",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)