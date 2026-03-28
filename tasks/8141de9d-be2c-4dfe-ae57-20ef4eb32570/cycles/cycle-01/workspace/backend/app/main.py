from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router

app = FastAPI(
    title="Wuhan Snacks API",
    description="API for Wuhan specialty snacks information",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "Welcome to Wuhan Snacks API",
        "endpoints": {
            "health": "/api/health",
            "all_snacks": "/api/snacks",
            "single_snack": "/api/snacks/{id}"
        },
        "documentation": "/docs"
    }