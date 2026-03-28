from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from .routes import router

# Create FastAPI app
app = FastAPI(
    title="粉粉猪网站后端",
    description="可爱粉色小猪介绍网站的后端API服务",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)

# Create static directory if it doesn't exist
static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
    print(f"Created static directory: {static_dir}")
    
    # Create subdirectories
    os.makedirs(os.path.join(static_dir, "images"), exist_ok=True)
    os.makedirs(os.path.join(static_dir, "css"), exist_ok=True)
    os.makedirs(os.path.join(static_dir, "js"), exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Create sample content file
content_file = "content_data.json"
if not os.path.exists(content_file):
    from .services import ContentService
    service = ContentService()
    service._save_content()
    print(f"Created sample content file: {content_file}")


@app.on_event("startup")
async def startup_event():
    """Actions to perform on application startup"""
    print("🐷 粉粉猪后端服务启动中...")
    print("服务已启动，访问以下地址：")
    print("  - 主页: http://localhost:8000")
    print("  - API文档: http://localhost:8000/api/docs")
    print("  - 内容API: http://localhost:8000/api/content")
    print("  - 健康检查: http://localhost:8000/api/health")


@app.get("/")
async def root():
    """Root endpoint redirects to homepage"""
    return {
        "message": "欢迎来到粉粉猪网站后端服务！",
        "endpoints": {
            "homepage": "/ (HTML页面)",
            "api_docs": "/api/docs",
            "get_content": "/api/content",
            "get_characteristics": "/api/characteristics",
            "get_fun_facts": "/api/fun-facts",
            "get_random_fact": "/api/random-fact",
            "health_check": "/api/health"
        },
        "instructions": "请访问 / 查看完整网站，或使用API端点获取数据"
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