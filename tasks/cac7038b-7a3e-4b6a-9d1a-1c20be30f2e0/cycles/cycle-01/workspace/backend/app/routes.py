from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas import ContentSection, ImageMetadata, APIStatus
from app.services import (
    get_introduction_content,
    get_facts_content,
    get_all_sections,
    get_image_metadata,
    get_api_status
)

router = APIRouter()

@router.get("/", response_model=APIStatus)
async def root():
    """
    Root endpoint returning API status.
    """
    return get_api_status()

@router.get("/content/introduction", response_model=ContentSection)
async def get_introduction():
    """
    Get introduction content for cherry blossoms.
    """
    content = get_introduction_content()
    if not content:
        raise HTTPException(status_code=404, detail="Introduction content not found")
    return content

@router.get("/content/facts", response_model=ContentSection)
async def get_facts():
    """
    Get facts about cherry blossoms.
    """
    content = get_facts_content()
    if not content:
        raise HTTPException(status_code=404, detail="Facts content not found")
    return content

@router.get("/content/sections", response_model=List[ContentSection])
async def get_sections():
    """
    Get all content sections.
    """
    sections = get_all_sections()
    if not sections:
        raise HTTPException(status_code=404, detail="No content sections found")
    return sections

@router.get("/image", response_model=ImageMetadata)
async def get_image():
    """
    Serve cherry blossom image metadata.
    """
    metadata = get_image_metadata()
    if not metadata:
        raise HTTPException(status_code=404, detail="Image metadata not found")
    return metadata

@router.get("/health", response_model=APIStatus)
async def health_check():
    """
    Health check endpoint.
    """
    return get_api_status()