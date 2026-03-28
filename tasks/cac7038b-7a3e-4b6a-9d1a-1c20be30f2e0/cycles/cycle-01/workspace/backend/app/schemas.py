from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ContentSection(BaseModel):
    """Schema for a content section on the webpage."""
    id: int
    title: str
    content: str
    section_type: str  # e.g., "introduction", "facts", "history"

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "title": "Introduction to Cherry Blossoms",
                "content": "Cherry blossoms, known as 'sakura' in Japan, are the flowers of several trees of genus Prunus...",
                "section_type": "introduction"
            }
        }


class ImageMetadata(BaseModel):
    """Schema for metadata of the cherry blossom image."""
    filename: str
    alt_text: str
    url: str
    size_kb: float

    class Config:
        schema_extra = {
            "example": {
                "filename": "cherry-blossom.jpg",
                "alt_text": "Beautiful pink cherry blossoms on a tree branch",
                "url": "/static/cherry-blossom.jpg",
                "size_kb": 150.5
            }
        }


class APIStatus(BaseModel):
    """Schema for API status response."""
    status: str
    message: str
    timestamp: datetime

    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "message": "Cherry Blossom API is running",
                "timestamp": "2023-04-01T12:00:00Z"
            }
        }


class ContentResponse(BaseModel):
    """Schema for content endpoint responses."""
    sections: List[ContentSection]


class HealthResponse(BaseModel):
    """Schema for health check response."""
    api: APIStatus
    dependencies: List[str]