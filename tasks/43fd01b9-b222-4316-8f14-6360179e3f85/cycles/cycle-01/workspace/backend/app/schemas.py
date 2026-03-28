from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class PigCharacteristic(BaseModel):
    """Model for pig characteristics"""
    title: str = Field(..., description="Characteristic title")
    description: str = Field(..., description="Detailed description")
    icon: Optional[str] = Field(None, description="Icon name or URL")


class FunFact(BaseModel):
    """Model for fun facts about pigs"""
    fact: str = Field(..., description="The fun fact text")
    category: str = Field(..., description="Category of the fact")
    is_surprising: bool = Field(default=False, description="Whether this is a surprising fact")


class PigContent(BaseModel):
    """Main content model for the pink pig website"""
    name: str = Field(..., description="Name of the pink pig")
    tagline: str = Field(..., description="Short tagline or motto")
    description: str = Field(..., description="Main description text")
    
    # Images
    main_image_url: str = Field(..., description="URL to main pig image")
    secondary_images: List[str] = Field(default_factory=list, description="Additional images")
    
    # Characteristics
    characteristics: List[PigCharacteristic] = Field(default_factory=list, description="Pig characteristics")
    
    # Fun facts
    fun_facts: List[FunFact] = Field(default_factory=list, description="Fun facts about pigs")
    
    # Colors
    primary_color: str = Field(default="#FFB6C1", description="Primary pink color")
    secondary_color: str = Field(default="#FFE4E1", description="Secondary pastel color")
    accent_color: str = Field(default="#FF69B4", description="Accent color")
    
    # Social links
    social_links: dict = Field(default_factory=dict, description="Social media links")


class ContentUpdate(BaseModel):
    """Model for updating content"""
    name: Optional[str] = None
    tagline: Optional[str] = None
    description: Optional[str] = None
    main_image_url: Optional[str] = None


class APIResponse(BaseModel):
    """Standard API response model"""
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Response message")
    data: Optional[dict] = Field(None, description="Response data")