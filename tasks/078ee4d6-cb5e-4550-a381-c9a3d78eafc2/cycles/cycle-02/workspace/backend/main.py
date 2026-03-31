from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.api import (
    users,
    categories,
    threads,
    posts,
    votes,
    notifications,
)
from app.websocket.manager import ConnectionManager
from app.core.config import settings
from app.database import engine, Base
from app.auth import get_current_user

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Forum Platform API",
    description="A modern forum platform with real-time features",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize WebSocket connection manager
manager = ConnectionManager()

# Include API routers
app.include_router(users.router, prefix="/api/auth", tags=["authentication"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(threads.router, prefix="/api/threads", tags=["threads"])
app.include_router(posts.router, prefix="/api/posts", tags=["posts"])
app.include_router(votes.router, prefix="/api/votes", tags=["votes"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])

# WebSocket endpoint for real-time notifications
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    """
    WebSocket endpoint for real-time notifications.
    Clients should connect with JWT token in query parameter.
    Example: ws://localhost:8000/ws?token=<jwt_token>
    """
    try:
        # Authenticate user from token
        if not token:
            await websocket.close(code=1008, reason="Authentication required")
            return
        
        try:
            user = await get_current_user(token)
        except Exception:
            await websocket.close(code=1008, reason="Invalid token")
            return
        
        # Accept connection
        await manager.connect(websocket, user.id)
        
        try:
            # Keep connection alive and handle messages
            while True:
                data = await websocket.receive_text()
                # Echo message back for now (can be extended for chat features)
                await manager.send_personal_message(f"Echo: {data}", user.id)
        except WebSocketDisconnect:
            manager.disconnect(user.id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": "forum-platform-api"}

# API info endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Forum Platform API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "websocket": "/ws",
    }

# Development server
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )