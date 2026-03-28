from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
from . import schemas, services
from .routes import snacks_router

app = FastAPI(
    title="Wuhan Snacks API",
    description="A RESTful API for managing Wuhan specialty snacks",
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

# Include routers
app.include_router(snacks_router, prefix="/api/v1", tags=["snacks"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Wuhan Snacks API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "snacks": "/api/v1/snacks",
            "snack_detail": "/api/v1/snacks/{id}"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}