from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ConservationStatus(str, Enum):
    """Conservation status of polar bears"""
    VULNERABLE = "vulnerable"
    ENDANGERED = "endangered"
    CRITICALLY_ENDANGERED = "critically_endangered"
    DATA_DEFICIENT = "data_deficient"

class ThreatType(str, Enum):
    """Types of threats to polar bears"""
    CLIMATE_CHANGE = "climate_change"
    POLLUTION = "pollution"
    HABITAT_LOSS = "habitat_loss"
    FOOD_SCARCITY = "food_scarcity"
    HUMAN_CONFLICT = "human_conflict"

class ActionType(str, Enum):
    """Types of conservation actions"""
    DONATION = "donation"
    VOLUNTEER = "volunteer"
    ADVOCACY = "advocacy"
    EDUCATION = "education"
    RESEARCH = "research"

class PolarBearInfo(BaseModel):
    """Information about polar bears for educational content"""
    scientific_name: str = Field(default="Ursus maritimus", description="Scientific name of polar bears")
    average_weight: str = Field(default="350-700 kg", description="Average weight range")
    average_lifespan: str = Field(default="25-30 years", description="Average lifespan in the wild")
    population_estimate: str = Field(default="22,000-31,000", description="Estimated global population")
    conservation_status: ConservationStatus = Field(default=ConservationStatus.VULNERABLE, description="Current conservation status")
    habitat: str = Field(default="Arctic region, sea ice", description="Primary habitat")
    diet: List[str] = Field(default=["seals", "fish", "walrus"], description="Primary diet")

class Threat(BaseModel):
    """Model representing a threat to polar bears"""
    id: str
    type: ThreatType
    title: str
    description: str
    severity: int = Field(ge=1, le=10, description="Severity level from 1-10")
    impact: str
    image_url: Optional[str] = None

class ConservationSolution(BaseModel):
    """Model representing a conservation solution"""
    id: str
    title: str
    description: str
    action_type: ActionType
    effectiveness: int = Field(ge=1, le=10, description="Effectiveness rating from 1-10")
    resources_needed: List[str]
    organizations: List[str] = Field(default=[], description="Organizations implementing this solution")

class NewsletterSubscription(BaseModel):
    """Model for newsletter subscription"""
    email: EmailStr
    name: Optional[str] = None
    subscribe_date: datetime = Field(default_factory=datetime.now)
    interests: List[str] = Field(default=["conservation_updates", "research_findings", "action_alerts"])
    consent_marketing: bool = Field(default=True, description="Consent to receive marketing emails")

class DonationRequest(BaseModel):
    """Model for donation requests"""
    amount: float = Field(gt=0, description="Donation amount in USD")
    donor_name: str
    donor_email: EmailStr
    is_recurring: bool = Field(default=False, description="Whether this is a recurring donation")
    designation: Optional[str] = Field(default="general_fund", description="Specific fund designation")
    message: Optional[str] = None

class SiteStatistics(BaseModel):
    """Model for site statistics"""
    total_visitors: int = Field(default=0, ge=0)
    newsletter_subscribers: int = Field(default=0, ge=0)
    donations_received: int = Field(default=0, ge=0)
    petitions_signed: int = Field(default=0, ge=0)
    last_updated: datetime = Field(default_factory=datetime.now)

class ContactMessage(BaseModel):
    """Model for contact form messages"""
    name: str
    email: EmailStr
    subject: str
    message: str
    urgency: str = Field(default="normal", description="Urgency level: low, normal, high")
    created_at: datetime = Field(default_factory=datetime.now)

class APIResponse(BaseModel):
    """Standard API response model"""
    success: bool
    message: str
    data: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class HealthCheckResponse(BaseModel):
    """Health check response model"""
    status: str
    service: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.now)
    uptime: Optional[float] = None
