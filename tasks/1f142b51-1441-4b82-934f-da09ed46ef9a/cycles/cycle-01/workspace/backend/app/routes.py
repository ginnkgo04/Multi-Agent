from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.schemas import (
    RedPandaInfo, RedPandaFact, RedPandaImage, 
    FunFact, ConservationOrganization, APIResponse
)
from app.services import RedPandaService

router = APIRouter()
service = RedPandaService()

@router.get("/health", response_model=APIResponse)
async def health_check():
    """Health check endpoint"""
    return APIResponse(
        success=True,
        message="Red Panda API is healthy",
        data={"status": "operational", "version": "1.0.0"}
    )

@router.get("/red-panda/info", response_model=APIResponse)
async def get_red_panda_info():
    """Get comprehensive red panda information"""
    info = service.get_red_panda_info()
    return APIResponse(
        success=True,
        data={"info": info.dict()}
    )

@router.get("/red-panda/facts", response_model=APIResponse)
async def get_facts(
    category: Optional[str] = Query(None, description="Filter facts by category")
):
    """Get red panda facts"""
    facts = service.get_facts(category)
    return APIResponse(
        success=True,
        data={"facts": [fact.dict() for fact in facts], "count": len(facts)}
    )

@router.get("/red-panda/facts/search", response_model=APIResponse)
async def search_facts(
    q: str = Query(..., description="Search query")
):
    """Search red panda facts by keyword"""
    if not q or len(q.strip()) < 2:
        raise HTTPException(
            status_code=400, 
            detail="Search query must be at least 2 characters long"
        )
    
    results = service.search_facts(q.strip())
    return APIResponse(
        success=True,
        data={"results": [fact.dict() for fact in results], "count": len(results)}
    )

@router.get("/red-panda/fun-facts", response_model=APIResponse)
async def get_fun_facts(
    limit: Optional[int] = Query(None, ge=1, le=20, description="Limit number of facts returned")
):
    """Get fun facts about red pandas"""
    facts = service.get_fun_facts(limit)
    return APIResponse(
        success=True,
        data={"fun_facts": [fact.dict() for fact in facts], "count": len(facts)}
    )

@router.get("/red-panda/images", response_model=APIResponse)
async def get_images():
    """Get red panda images"""
    images = service.get_images()
    return APIResponse(
        success=True,
        data={"images": [img.dict() for img in images], "count": len(images)}
    )

@router.get("/red-panda/conservation/organizations", response_model=APIResponse)
async def get_conservation_organizations():
    """Get conservation organizations"""
    orgs = service.get_conservation_organizations()
    return APIResponse(
        success=True,
        data={"organizations": [org.dict() for org in orgs], "count": len(orgs)}
    )

@router.get("/red-panda/statistics", response_model=APIResponse)
async def get_statistics():
    """Get red panda statistics"""
    stats = service.get_statistics()
    return APIResponse(
        success=True,
        data={"statistics": stats}
    )

@router.get("/red-panda/sections", response_model=APIResponse)
async def get_website_sections():
    """Get website section structure for frontend integration"""
    sections = [
        {
            "id": "introduction",
            "title": "Introduction",
            "description": "Basic information about red pandas",
            "endpoint": "/api/red-panda/info"
        },
        {
            "id": "facts",
            "title": "Facts & Information",
            "description": "Detailed facts about red pandas",
            "endpoint": "/api/red-panda/facts"
        },
        {
            "id": "fun-facts",
            "title": "Fun Facts",
            "description": "Interesting and fun facts",
            "endpoint": "/api/red-panda/fun-facts"
        },
        {
            "id": "gallery",
            "title": "Photo Gallery",
            "description": "Images of red pandas",
            "endpoint": "/api/red-panda/images"
        },
        {
            "id": "conservation",
            "title": "Conservation",
            "description": "Conservation status and organizations",
            "endpoint": "/api/red-panda/conservation/organizations"
        }
    ]
    
    return APIResponse(
        success=True,
        data={"sections": sections}
    )

@router.get("/red-panda/quick-info", response_model=APIResponse)
async def get_quick_info():
    """Get quick summary information for homepage display"""
    info = service.get_red_panda_info()
    fun_facts = service.get_fun_facts(limit=3)
    images = service.get_images()[:2]
    
    return APIResponse(
        success=True,
        data={
            "scientific_name": info.scientific_name,
            "common_names": info.common_names,
            "conservation_status": info.conservation_status.value,
            "size": info.size,
            "habitat": info.habitat,
            "fun_facts": [fact.dict() for fact in fun_facts],
            "sample_images": [img.dict() for img in images]
        }
    )