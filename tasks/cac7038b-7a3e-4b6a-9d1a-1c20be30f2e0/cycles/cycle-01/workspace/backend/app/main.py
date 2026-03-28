from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router

app = FastAPI(
    title="Cherry Blossom API",
    description="API for serving content for the Cherry Blossom introduction webpage",
    version="1.0.0"
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5500", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Cherry Blossom API is running",
        "timestamp": "2024-01-01T00:00:00Z",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "API status"},
            {"path": "/content/introduction", "method": "GET", "description": "Get introduction content"},
            {"path": "/content/facts", "method": "GET", "description": "Get facts about cherry blossoms"},
            {"path": "/content/sections", "method": "GET", "description": "Get all content sections"},
            {"path": "/image", "method": "GET", "description": "Get image metadata"},
            {"path": "/health", "method": "GET", "description": "Health check"}
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}