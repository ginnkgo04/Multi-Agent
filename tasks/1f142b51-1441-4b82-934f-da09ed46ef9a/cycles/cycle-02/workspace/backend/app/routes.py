"""
小熊猫介绍网站 - API路由定义
为静态网站提供简单的API端点
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.schemas import (
    RedPandaBasicInfo, HabitatInfo, DietInfo, ConservationStatus,
    FunFact, RedPandaImage, RedPandaCompleteInfo, WebsiteInfo,
    HealthResponse
)
from app.services import red_panda_service, static_content_service

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """健康检查端点"""
    return HealthResponse(
        status="healthy",
        service="red-panda-website-backend",
        version="1.0.0"
    )


@router.get("/red-panda/info", response_model=RedPandaCompleteInfo)
async def get_red_panda_info() -> RedPandaCompleteInfo:
    """获取完整的小熊猫信息"""
    try:
        return red_panda_service.get_complete_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取信息失败: {str(e)}")


@router.get("/red-panda/basic", response_model=RedPandaBasicInfo)
async def get_basic_info() -> RedPandaBasicInfo:
    """获取小熊猫基本信息"""
    return red_panda_service.get_basic_info()


@router.get("/red-panda/habitat", response_model=HabitatInfo)
async def get_habitat_info() -> HabitatInfo:
    """获取栖息地信息"""
    return red_panda_service.get_habitat_info()


@router.get("/red-panda/diet", response_model=DietInfo)
async def get_diet_info() -> DietInfo:
    """获取饮食信息"""
    return red_panda_service.get_diet_info()


@router.get("/red-panda/conservation", response_model=ConservationStatus)
async def get_conservation_status() -> ConservationStatus:
    """获取保护状态"""
    return red_panda_service.get_conservation_status()


@router.get("/red-panda/fun-facts", response_model=list[FunFact])
async def get_fun_facts() -> list[FunFact]:
    """获取趣味事实"""
    return red_panda_service.get_fun_facts()


@router.get("/red-panda/images", response_model=list[RedPandaImage])
async def get_images() -> list[RedPandaImage]:
    """获取图片信息"""
    return red_panda_service.get_images()


@router.get("/website/info", response_model=WebsiteInfo)
async def get_website_info() -> WebsiteInfo:
    """获取网站信息"""
    return red_panda_service.get_website_info()


@router.get("/navigation")
async def get_navigation() -> Dict[str, Any]:
    """获取导航菜单"""
    return {
        "items": static_content_service.get_navigation_items(),
        "titles": static_content_service.get_section_titles()
    }


@router.get("/contact")
async def get_contact_info() -> Dict[str, str]:
    """获取联系信息"""
    return static_content_service.get_contact_info()


@router.get("/sections")
async def get_all_sections() -> Dict[str, Any]:
    """获取所有章节内容（简化版）"""
    try:
        complete_info = red_panda_service.get_complete_info()
        return {
            "basic": complete_info.basic_info.dict(),
            "habitat": complete_info.habitat.dict(),
            "diet": complete_info.diet.dict(),
            "conservation": complete_info.conservation.dict(),
            "fun_facts": [fact.dict() for fact in complete_info.fun_facts],
            "images": [image.dict() for image in complete_info.images]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取章节内容失败: {str(e)}")


@router.get("/")
async def root():
    """API根端点"""
    return {
        "message": "小熊猫介绍网站API服务",
        "version": "1.0.0",
        "endpoints": [
            {"path": "/api/health", "method": "GET", "description": "健康检查"},
            {"path": "/api/red-panda/info", "method": "GET", "description": "完整的小熊猫信息"},
            {"path": "/api/red-panda/basic", "method": "GET", "description": "基本信息"},
            {"path": "/api/red-panda/habitat", "method": "GET", "description": "栖息地信息"},
            {"path": "/api/red-panda/diet", "method": "GET", "description": "饮食信息"},
            {"path": "/api/red-panda/conservation", "method": "GET", "description": "保护状态"},
            {"path": "/api/red-panda/fun-facts", "method": "GET", "description": "趣味事实"},
            {"path": "/api/red-panda/images", "method": "GET", "description": "图片信息"},
            {"path": "/api/website/info", "method": "GET", "description": "网站信息"},
            {"path": "/api/navigation", "method": "GET", "description": "导航菜单"},
            {"path": "/api/contact", "method": "GET", "description": "联系信息"},
            {"path": "/api/sections", "method": "GET", "description": "所有章节内容"}
        ],
        "note": "这是一个为静态HTML/CSS网站提供数据支持的简单API服务"
    }