from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class ConservationStatus(str, Enum):
    ENDANGERED = "Endangered"
    VULNERABLE = "Vulnerable"
    NEAR_THREATENED = "Near Threatened"
    LEAST_CONCERN = "Least Concern"

class RedPandaFact(BaseModel):
    """Individual fact about red pandas"""
    id: str = Field(..., description="Unique identifier for the fact")
    title: str = Field(..., description="Title of the fact")
    description: str = Field(..., description="Detailed description")
    category: str = Field(..., description="Category: biology, habitat, diet, etc.")
    source: Optional[str] = Field(None, description="Source of the information")

class RedPandaImage(BaseModel):
    """Image information for red pandas"""
    id: str = Field(..., description="Unique identifier for the image")
    url: str = Field(..., description="URL or path to the image")
    alt_text: str = Field(..., description="Alternative text for accessibility")
    caption: Optional[str] = Field(None, description="Image caption")
    credit: Optional[str] = Field(None, description="Image credit/attribution")

class RedPandaInfo(BaseModel):
    """Comprehensive red panda information"""
    scientific_name: str = Field("Ailurus fulgens", description="Scientific name")
    common_names: List[str] = Field(["Red Panda", "Lesser Panda", "Fire Fox"], description="Common names")
    conservation_status: ConservationStatus = Field(ConservationStatus.ENDANGERED, description="Conservation status")
    
    # Basic facts
    size: str = Field(..., description="Size description")
    weight: str = Field(..., description="Weight range")
    lifespan: str = Field(..., description="Lifespan in wild/captivity")
    
    # Habitat
    habitat: List[str] = Field(..., description="Habitat types")
    geographic_range: str = Field(..., description="Geographic range")
    
    # Diet
    diet: List[str] = Field(..., description="Diet components")
    feeding_habits: str = Field(..., description="Feeding habits description")
    
    # Behavior
    behavior: List[str] = Field(..., description="Behavioral characteristics")
    activity_pattern: str = Field(..., description="Activity pattern (nocturnal/crepuscular)")
    
    # Threats
    threats: List[str] = Field(..., description="Major threats")
    population_trend: str = Field(..., description="Population trend")

class FunFact(BaseModel):
    """Fun/interesting fact about red pandas"""
    id: str = Field(..., description="Unique identifier")
    fact: str = Field(..., description="The fun fact")
    explanation: Optional[str] = Field(None, description="Explanation of the fact")

class ConservationOrganization(BaseModel):
    """Conservation organization information"""
    name: str = Field(..., description="Organization name")
    website: str = Field(..., description="Organization website")
    description: str = Field(..., description="Brief description")
    focus_areas: List[str] = Field(..., description="Focus areas")

class APIResponse(BaseModel):
    """Standard API response format"""
    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[dict] = Field(None, description="Response data")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message if any")