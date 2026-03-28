"""
API routes for Shaxian Snacks website
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from .schemas import (
    MenuItem, 
    Location, 
    Testimonial, 
    WebsiteContent, 
    DishCategory,
    HealthResponse,
    ErrorResponse
)
from .services import data_service

router = APIRouter(tags=["shaxian-snacks"])


@router.get(
    "/content",
    response_model=WebsiteContent,
    summary="Get complete website content",
    description="Returns all content needed for the Shaxian Snacks website"
)
async def get_website_content() -> WebsiteContent:
    """Get complete website content including introduction, menu, locations, and testimonials"""
    return data_service.get_website_content()


@router.get(
    "/menu",
    response_model=List[MenuItem],
    summary="Get all menu items",
    description="Returns all menu items available"
)
async def get_all_menu_items() -> List[MenuItem]:
    """Get all menu items"""
    return data_service.get_all_menu_items()


@router.get(
    "/menu/popular",
    response_model=List[MenuItem],
    summary="Get popular menu items",
    description="Returns only popular menu items (is_popular=True)"
)
async def get_popular_menu_items() -> List[MenuItem]:
    """Get popular menu items"""
    return data_service.get_popular_items()


@router.get(
    "/menu/{item_id}",
    response_model=MenuItem,
    summary="Get menu item by ID",
    description="Returns a specific menu item by its ID",
    responses={
        404: {"model": ErrorResponse, "description": "Menu item not found"}
    }
)
async def get_menu_item(item_id: int) -> MenuItem:
    """Get a specific menu item by ID"""
    item = data_service.get_menu_item_by_id(item_id)
    if not item:
        raise HTTPException(
            status_code=404,
            detail=f"Menu item with ID {item_id} not found"
        )
    return item


@router.get(
    "/menu/category/{category}",
    response_model=List[MenuItem],
    summary="Get menu items by category",
    description="Returns menu items filtered by category"
)
async def get_menu_items_by_category(category: DishCategory) -> List[MenuItem]:
    """Get menu items by category"""
    return data_service.get_menu_items_by_category(category)


@router.get(
    "/locations",
    response_model=List[Location],
    summary="Get all locations",
    description="Returns all Shaxian Snacks locations"
)
async def get_all_locations() -> List[Location]:
    """Get all locations"""
    return data_service.get_all_locations()


@router.get(
    "/locations/{location_id}",
    response_model=Location,
    summary="Get location by ID",
    description="Returns a specific location by its ID",
    responses={
        404: {"model": ErrorResponse, "description": "Location not found"}
    }
)
async def get_location(location_id: int) -> Location:
    """Get a specific location by ID"""
    location = data_service.get_location_by_id(location_id)
    if not location:
        raise HTTPException(
            status_code=404,
            detail=f"Location with ID {location_id} not found"
        )
    return location


@router.get(
    "/locations/city/{city}",
    response_model=List[Location],
    summary="Get locations by city",
    description="Returns locations filtered by city name"
)
async def get_locations_by_city(city: str) -> List[Location]:
    """Get locations by city"""
    return data_service.get_locations_by_city(city)


@router.get(
    "/testimonials",
    response_model=List[Testimonial],
    summary="Get all testimonials",
    description="Returns all customer testimonials"
)
async def get_all_testimonials() -> List[Testimonial]:
    """Get all testimonials"""
    return data_service.get_all_testimonials()


@router.get(
    "/testimonials/high-rated",
    response_model=List[Testimonial],
    summary="Get high-rated testimonials",
    description="Returns testimonials with minimum rating (default: 4 stars)"
)
async def get_high_rated_testimonials(
    min_rating: int = Query(4, ge=1, le=5, description="Minimum rating (1-5 stars)")
) -> List[Testimonial]:
    """Get testimonials with minimum rating"""
    return data_service.get_testimonials_by_rating(min_rating)


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns service health status"
)
async def health_check() -> HealthResponse:
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="shaxian-snacks-api",
        version="1.0.0"
    )


@router.get(
    "/categories",
    response_model=List[str],
    summary="Get all dish categories",
    description="Returns all available dish categories"
)
async def get_all_categories() -> List[str]:
    """Get all dish categories"""
    return [category.value for category in DishCategory]


# Search endpoints
@router.get(
    "/search/menu",
    response_model=List[MenuItem],
    summary="Search menu items",
    description="Search menu items by name or description"
)
async def search_menu_items(
    query: str = Query(..., description="Search query"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    category: Optional[DishCategory] = Query(None, description="Category filter")
) -> List[MenuItem]:
    """Search menu items"""
    results = []
    query_lower = query.lower()
    
    for item in data_service.get_all_menu_items():
        # Apply category filter
        if category and item.category != category:
            continue
        
        # Apply price filter
        if max_price and item.price > max_price:
            continue
        
        # Apply search query
        if (query_lower in item.name.lower() or 
            query_lower in item.description.lower()):
            results.append(item)
    
    return results