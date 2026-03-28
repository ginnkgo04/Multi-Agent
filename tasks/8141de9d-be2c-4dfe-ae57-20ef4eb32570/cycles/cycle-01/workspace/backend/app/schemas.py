from pydantic import BaseModel
from typing import List, Optional


class SnackBase(BaseModel):
    """Base schema for snack data."""
    name: str
    description: str
    ingredients: List[str]
    origin: str
    image_url: str


class SnackCreate(SnackBase):
    """Schema for creating a new snack."""
    pass


class Snack(SnackBase):
    """Schema for snack response, includes ID."""
    id: int

    class Config:
        from_attributes = True


class SnackResponse(BaseModel):
    """Standard response schema for snack endpoints."""
    success: bool
    message: str
    data: Optional[Snack] = None


class SnackListResponse(BaseModel):
    """Response schema for list of snacks."""
    success: bool
    message: str
    data: List[Snack]