from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas import Snack, SnackResponse
from app.services import get_all_snacks, get_snack_by_id

router = APIRouter()

@router.get("/health", response_model=dict)
async def health_check():
    """
    Health check endpoint to verify API is running.
    """
    return {"status": "healthy", "service": "Wuhan Snacks API"}

@router.get("/snacks", response_model=SnackResponse)
async def get_snacks():
    """
    Get all Wuhan snacks.
    Returns a list of snack objects.
    """
    snacks = get_all_snacks()
    return SnackResponse(
        success=True,
        message="Snacks retrieved successfully",
        data=snacks
    )

@router.get("/snacks/{snack_id}", response_model=SnackResponse)
async def get_snack(snack_id: int):
    """
    Get a specific snack by ID.
    """
    snack = get_snack_by_id(snack_id)
    if snack is None:
        raise HTTPException(status_code=404, detail="Snack not found")
    
    return SnackResponse(
        success=True,
        message="Snack retrieved successfully",
        data=snack
    )