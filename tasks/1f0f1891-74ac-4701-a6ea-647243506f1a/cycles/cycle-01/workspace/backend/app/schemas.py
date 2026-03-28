from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class SnackBase(BaseModel):
    """Base schema for snack data"""
    name: str = Field(..., min_length=1, max_length=100, description="Name of the snack")
    description: str = Field(..., min_length=10, max_length=500, description="Description of the snack")
    ingredients: List[str] = Field(default_factory=list, description="List of main ingredients")
    origin_story: Optional[str] = Field(None, max_length=1000, description="Historical or cultural background")
    spice_level: int = Field(1, ge=1, le=5, description="Spice level from 1 (mild) to 5 (very spicy)")
    is_vegetarian: bool = Field(False, description="Whether the snack is vegetarian-friendly")
    estimated_calories: Optional[int] = Field(None, ge=0, description="Estimated calories per serving")


class SnackCreate(SnackBase):
    """Schema for creating a new snack"""
    pass


class SnackUpdate(BaseModel):
    """Schema for updating snack data"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=10, max_length=500)
    ingredients: Optional[List[str]] = None
    origin_story: Optional[str] = Field(None, max_length=1000)
    spice_level: Optional[int] = Field(None, ge=1, le=5)
    is_vegetarian: Optional[bool] = None
    estimated_calories: Optional[int] = Field(None, ge=0)


class SnackInDB(SnackBase):
    """Schema for snack data stored in database"""
    id: str = Field(..., description="Unique identifier for the snack")
    created_at: datetime = Field(..., description="Timestamp when the snack was created")
    updated_at: datetime = Field(..., description="Timestamp when the snack was last updated")
    image_url: Optional[str] = Field(None, description="URL to snack image")
    
    class Config:
        from_attributes = True


class SnackResponse(SnackInDB):
    """Schema for snack API responses"""
    pass


class SnackListResponse(BaseModel):
    """Schema for list of snacks API response"""
    snacks: List[SnackResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class HealthCheck(BaseModel):
    """Schema for health check response"""
    status: str
    timestamp: datetime
    service: str = "Wuhan Snacks API"
    version: str = "1.0.0"