from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

from app.core.config import settings
from app.api import auth, users, categories, threads, posts, votes

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 设置CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 添加可信主机中间件
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # 生产环境应限制为特定域名
)

# 注册API路由
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["authentication"]
)

app.include_router(
    users.router,
    prefix=f"{settings.API_V1_STR}/users",
    tags=["users"]
)

app.include_router(
    categories.router,
    prefix=f"{settings.API_V1_STR}/categories",
    tags=["categories"]
)

app.include_router(
    threads.router,
    prefix=f"{settings.API_V1_STR}/threads",
    tags=["threads"]
)

app.include_router(
    posts.router,
    prefix=f"{settings.API_V1_STR}/posts",
    tags=["posts"]
)

app.include_router(
    votes.router,
    prefix=f"{settings.API_V1_STR}/votes",
    tags=["votes"]
)


@app.get("/")
async def root():
    """
    根端点
    """
    return {
        "message": "Welcome to Forum Platform API",
        "version": settings.PROJECT_VERSION,
        "docs": "/docs",
        "api_v1": settings.API_V1_STR
    }


@app.get("/health")
async def health_check():
    """
    健康检查端点
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )