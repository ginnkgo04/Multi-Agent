from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional
from uuid import UUID

from app import schemas, services
from app.dependencies import get_snack_service

router = APIRouter(prefix="/api/v1/snacks", tags=["snacks"])


@router.get("/", response_model=List[schemas.SnackResponse])
async def get_snacks(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of items to return"),
    category: Optional[str] = Query(None, description="Filter by snack category"),
    snack_service: services.SnackService = Depends(get_snack_service),
):
    """
    Retrieve a list of Wuhan specialty snacks.
    
    Parameters:
    - skip: Number of items to skip (for pagination)
    - limit: Maximum number of items to return
    - category: Optional filter by snack category
    
    Returns:
    - List of snack objects
    """
    snacks = snack_service.get_snacks(skip=skip, limit=limit, category=category)
    return snacks


@router.get("/{snack_id}", response_model=schemas.SnackResponse)
async def get_snack_by_id(
    snack_id: UUID,
    snack_service: services.SnackService = Depends(get_snack_service),
):
    """
    Retrieve a specific snack by its ID.
    
    Parameters:
    - snack_id: The unique identifier of the snack
    
    Returns:
    - Snack object if found
    
    Raises:
    - HTTPException 404 if snack not found
    """
    snack = snack_service.get_snack_by_id(snack_id)
    if not snack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snack with id {snack_id} not found"
        )
    return snack


@router.post("/", response_model=schemas.SnackResponse, status_code=status.HTTP_201_CREATED)
async def create_snack(
    snack_data: schemas.SnackCreate,
    snack_service: services.SnackService = Depends(get_snack_service),
):
    """
    Create a new snack entry.
    
    Parameters:
    - snack_data: The snack data to create
    
    Returns:
    - The created snack object
    """
    snack = snack_service.create_snack(snack_data)
    return snack


@router.put("/{snack_id}", response_model=schemas.SnackResponse)
async def update_snack(
    snack_id: UUID,
    snack_data: schemas.SnackUpdate,
    snack_service: services.SnackService = Depends(get_snack_service),
):
    """
    Update an existing snack.
    
    Parameters:
    - snack_id: The unique identifier of the snack to update
    - snack_data: The updated snack data
    
    Returns:
    - The updated snack object
    
    Raises:
    - HTTPException 404 if snack not found
    """
    snack = snack_service.update_snack(snack_id, snack_data)
    if not snack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snack with id {snack_id} not found"
        )
    return snack


@router.delete("/{snack_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_snack(
    snack_id: UUID,
    snack_service: services.SnackService = Depends(get_snack_service),
):
    """
    Delete a snack by its ID.
    
    Parameters:
    - snack_id: The unique identifier of the snack to delete
    
    Returns:
    - No content on successful deletion
    
    Raises:
    - HTTPException 404 if snack not found
    """
    deleted = snack_service.delete_snack(snack_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snack with id {snack_id} not found"
        )


@router.get("/categories/", response_model=List[str])
async def get_categories(
    snack_service: services.SnackService = Depends(get_snack_service),
):
    """
    Retrieve all available snack categories.
    
    Returns:
    - List of unique snack categories
    """
    categories = snack_service.get_categories()
    return categories


@router.get("/search/", response_model=List[schemas.SnackResponse])
async def search_snacks(
    q: str = Query(..., min_length=1, description="Search query"),
    snack_service: services.SnackService = Depends(get_snack_service),
):
    """
    Search snacks by name or description.
    
    Parameters:
    - q: Search query string
    
    Returns:
    - List of matching snack objects
    """
    snacks = snack_service.search_snacks(q)
    return snacks