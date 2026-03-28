from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import snacks, health

app = FastAPI(
    title="Wuhan Snacks API",
    description="API for Wuhan specialty snacks data",
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

# Include routers
app.include_router(snacks.router, prefix="/api/v1/snacks", tags=["snacks"])
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Wuhan Snacks API",
        "docs": "/docs",
        "redoc": "/redoc"
    }