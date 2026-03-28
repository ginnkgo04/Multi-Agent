from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from typing import List, Optional
import os

from .schemas import PigContent, ContentUpdate, APIResponse, FunFact
from .services import content_service, static_file_service

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def get_homepage():
    """Serve the main HTML page"""
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>粉粉猪 - 可爱粉色小猪介绍</title>
        <style>
            body {
                font-family: 'Comic Sans MS', 'Arial Rounded MT Bold', sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #FFF0F5;
                color: #333;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 5px 15px rgba(255, 182, 193, 0.3);
            }
            header {
                text-align: center;
                margin-bottom: 40px;
            }
            h1 {
                color: #FF69B4;
                font-size: 3em;
                margin-bottom: 10px;
            }
            .tagline {
                color: #FFB6C1;
                font-size: 1.5em;
                margin-bottom: 30px;
            }
            .content {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
            }
            .api-info {
                background: #FFE4E1;
                padding: 20px;
                border-radius: 15px;
                margin-top: 30px;
            }
            .endpoint {
                background: white;
                padding: 10px;
                margin: 10px 0;
                border-radius: 10px;
                border-left: 5px solid #FF69B4;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🐷 粉粉猪介绍网站</h1>
                <div class="tagline">世界上最可爱的小猪！</div>
            </header>
            
            <div class="content">
                <div>
                    <h2>欢迎来到粉粉猪的世界！</h2>
                    <p>这是一个关于可爱粉色小猪的介绍网站。粉粉猪有着圆圆的眼睛、粉嫩的皮肤和永远开心的笑容。</p>
                    
                    <h3>网站特点：</h3>
                    <ul>
                        <li>响应式设计，适合各种设备</li>
                        <li>粉色和柔和的色彩搭配</li>
                        <li>圆润可爱的设计元素</li>
                        <li>交互式功能</li>
                    </ul>
                </div>
                
                <div>
                    <h2>后端API服务</h2>
                    <p>这个网站由FastAPI后端提供支持，提供以下功能：</p>
                    
                    <div class="api-info">
                        <h3>可用API端点：</h3>
                        <div class="endpoint">
                            <strong>GET /api/content</strong> - 获取粉粉猪的所有内容
                        </div>
                        <div class="endpoint">
                            <strong>GET /api/characteristics</strong> - 获取粉粉猪的特点
                        </div>
                        <div class="endpoint">
                            <strong>GET /api/fun-facts</strong> - 获取有趣的猪知识
                        </div>
                        <div class="endpoint">
                            <strong>GET /api/random-fact</strong> - 获取随机趣味知识
                        </div>
                        <div class="endpoint">
                            <strong>GET /static/{filename}</strong> - 获取静态文件
                        </div>
                    </div>
                </div>
            </div>
            
            <footer style="text-align: center; margin-top: 40px; color: #888;">
                <p>🐷 粉粉猪网站后端服务 | 使用FastAPI构建</p>
            </footer>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@router.get("/api/content", response_model=PigContent)
async def get_all_content():
    """Get all content for the pink pig website"""
    return content_service.get_content()


@router.get("/api/characteristics")
async def get_characteristics():
    """Get all characteristics of the pink pig"""
    characteristics = content_service.get_characteristics()
    return {
        "success": True,
        "count": len(characteristics),
        "characteristics": characteristics
    }


@router.get("/api/fun-facts")
async def get_fun_facts(
    category: Optional[str] = Query(None, description="Filter by category"),
    surprising_only: bool = Query(False, description="Only show surprising facts")
):
    """Get fun facts about pigs"""
    facts = content_service.get_fun_facts(category=category, surprising_only=surprising_only)
    return {
        "success": True,
        "count": len(facts),
        "filters": {
            "category": category,
            "surprising_only": surprising_only
        },
        "facts": facts
    }


@router.get("/api/random-fact", response_model=FunFact)
async def get_random_fact():
    """Get a random fun fact"""
    fact = content_service.get_random_fact()
    if not fact:
        raise HTTPException(status_code=404, detail="No facts available")
    return fact


@router.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "pink-pig-backend",
        "version": "1.0.0"
    }


@router.put("/api/content")
async def update_content(updates: ContentUpdate):
    """Update website content"""
    try:
        updated_content = content_service.update_content(updates)
        return APIResponse(
            success=True,
            message="Content updated successfully",
            data={"content": updated_content.dict()}
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"Error updating content: {str(e)}",
            data=None
        )


@router.get("/static/{filename}")
async def get_static_file(filename: str):
    """Serve static files"""
    filepath = static_file_service.get_static_file_path(filename)
    
    if not filepath:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine content type based on file extension
    _, ext = os.path.splitext(filename)
    media_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.svg': 'image/svg+xml',
        '.css': 'text/css',
        '.js': 'application/javascript',
        '.html': 'text/html'
    }
    
    media_type = media_types.get(ext.lower(), 'application/octet-stream')
    
    return FileResponse(filepath, media_type=media_type)


@router.get("/api/images")
async def list_images():
    """List all available images"""
    images = static_file_service.list_images()
    return {
        "success": True,
        "count": len(images),
        "images": images
    }