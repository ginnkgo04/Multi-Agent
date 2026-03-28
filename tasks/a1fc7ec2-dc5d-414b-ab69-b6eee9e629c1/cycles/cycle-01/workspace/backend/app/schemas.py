"""
Data schemas for Shaxian Snacks website
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class DishCategory(str, Enum):
    """Categories for Shaxian Snacks dishes"""
    NOODLES = "noodles"
    DUMPLINGS = "dumplings"
    RICE = "rice"
    SOUP = "soup"
    SIDES = "sides"
    DRINKS = "drinks"


class MenuItem(BaseModel):
    """Schema for a menu item"""
    id: int = Field(..., description="Unique identifier for the menu item")
    name: str = Field(..., description="Name of the dish")
    description: str = Field(..., description="Description of the dish")
    price: float = Field(..., description="Price in CNY")
    category: DishCategory = Field(..., description="Category of the dish")
    is_popular: bool = Field(default=False, description="Whether this is a popular dish")
    image_url: Optional[str] = Field(None, description="URL to dish image")


class Location(BaseModel):
    """Schema for a restaurant location"""
    id: int = Field(..., description="Unique identifier for the location")
    name: str = Field(..., description="Name of the location")
    address: str = Field(..., description="Full address")
    city: str = Field(..., description="City")
    phone: Optional[str] = Field(None, description="Contact phone number")
    opening_hours: str = Field(..., description="Opening hours")
    latitude: Optional[float] = Field(None, description="Latitude for maps")
    longitude: Optional[float] = Field(None, description="Longitude for maps")


class Testimonial(BaseModel):
    """Schema for customer testimonials"""
    id: int = Field(..., description="Unique identifier for the testimonial")
    customer_name: str = Field(..., description="Name of the customer")
    content: str = Field(..., description="Testimonial content")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    date: str = Field(..., description="Date of the testimonial")


class WebsiteContent(BaseModel):
    """Complete website content schema"""
    introduction: str = Field(..., description="Introduction text about Shaxian Snacks")
    menu_highlights: List[MenuItem] = Field(..., description="Highlighted menu items")
    locations: List[Location] = Field(..., description="Restaurant locations")
    testimonials: Optional[List[Testimonial]] = Field(None, description="Customer testimonials")
    contact_email: Optional[str] = Field(None, description="Contact email address")
    social_media: Optional[dict] = Field(None, description="Social media links")


class HealthResponse(BaseModel):
    """Health check response schema"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="API version")


class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code for debugging")