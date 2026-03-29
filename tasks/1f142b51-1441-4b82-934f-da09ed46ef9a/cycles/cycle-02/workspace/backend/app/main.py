"""
小熊猫介绍网站 - 后端服务主入口
提供静态文件服务和简单的API端点
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

from app.routes import router as api_router

# 创建FastAPI应用
app = FastAPI(
    title="小熊猫介绍网站 API",
    description="为小熊猫介绍网站提供静态文件服务和简单API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含API路由
app.include_router(api_router, prefix="/api")

# 静态文件目录配置
static_dir = os.path.join(os.path.dirname(__file__), "../../frontend")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
else:
    # 如果前端目录不存在，创建简单的响应
    @app.get("/")
    async def root():
        return {"message": "小熊猫介绍网站后端服务正在运行", "status": "请将前端文件放置在frontend目录中"}

# 健康检查端点
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "red-panda-website-backend",
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