from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional
import asyncio
from datetime import datetime

from .schemas import (
    PolarBearInfo, Threat, ConservationSolution, NewsletterSubscription,
    DonationRequest, SiteStatistics, ContactMessage, APIResponse,
    HealthCheckResponse
)
from .services import (
    ConservationDataService, NewsletterService, StatisticsService, ContentService
)

router = APIRouter()

# Initialize services
conservation_service = ConservationDataService()
newsletter_service = NewsletterService()
stats_service = StatisticsService()

def get_conservation_service() -> ConservationDataService:
    """Dependency for conservation service"""
    return conservation_service

def get_newsletter_service() -> NewsletterService:
    """Dependency for newsletter service"""
    return newsletter_service

def get_stats_service() -> StatisticsService:
    """Dependency for statistics service"""
    return stats_service

@router.get("/", include_in_schema=False)
async def root():
    """Root endpoint redirects to main documentation"""
    return {"message": "Polar Bear Conservation API", "docs": "/docs"}

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    stats_service.record_visit()
    return HealthCheckResponse(
        status="healthy",
        service="polar-bear-conservation-api",
        version="1.0.0",
        timestamp=datetime.now()
    )

@router.get("/api/polar-bear-info", response_model=PolarBearInfo)
async def get_polar_bear_info(
    service: ConservationDataService = Depends(get_conservation_service)
):
    """Get comprehensive information about polar bears"""
    stats_service.record_visit()
    return service.get_polar_bear_info()

@router.get("/api/threats", response_model=List[Threat])
async def get_threats(
    limit: Optional[int] = None,
    service: ConservationDataService = Depends(get_conservation_service)
):
    """Get list of threats to polar bears"""
    stats_service.record_visit()
    return service.get_threats(limit)

@router.get("/api/threats/{threat_id}", response_model=Threat)
async def get_threat(
    threat_id: str,
    service: ConservationDataService = Depends(get_conservation_service)
):
    """Get specific threat by ID"""
    stats_service.record_visit()
    threat = service.get_threat_by_id(threat_id)
    if not threat:
        raise HTTPException(status_code=404, detail=f"Threat with ID {threat_id} not found")
    return threat

@router.get("/api/solutions", response_model=List[ConservationSolution])
async def get_solutions(
    limit: Optional[int] = None,
    service: ConservationDataService = Depends(get_conservation_service)
):
    """Get list of conservation solutions"""
    stats_service.record_visit()
    return service.get_solutions(limit)

@router.get("/api/solutions/{solution_id}", response_model=ConservationSolution)
async def get_solution(
    solution_id: str,
    service: ConservationDataService = Depends(get_conservation_service)
):
    """Get specific solution by ID"""
    stats_service.record_visit()
    solution = service.get_solution_by_id(solution_id)
    if not solution:
        raise HTTPException(status_code=404, detail=f"Solution with ID {solution_id} not found")
    return solution

@router.post("/api/newsletter/subscribe", response_model=APIResponse)
async def subscribe_newsletter(
    subscription: NewsletterSubscription,
    background_tasks: BackgroundTasks,
    newsletter_service: NewsletterService = Depends(get_newsletter_service),
    stats_service: StatisticsService = Depends(get_stats_service)
):
    """Subscribe to newsletter"""
    stats_service.record_visit()
    
    success = newsletter_service.subscribe(subscription)
    if success:
        stats_service.record_subscription()
        
        # Simulate sending welcome email in background
        background_tasks.add_task(send_welcome_email, subscription.email)
        
        return APIResponse(
            success=True,
            message="Successfully subscribed to newsletter",
            data={"email": subscription.email, "subscription_date": subscription.subscribe_date}
        )
    else:
        return APIResponse(
            success=False,
            message="Email already subscribed",
            data={"email": subscription.email}
        )

@router.post("/api/newsletter/unsubscribe", response_model=APIResponse)
async def unsubscribe_newsletter(
    email: str,
    newsletter_service: NewsletterService = Depends(get_newsletter_service)
):
    """Unsubscribe from newsletter"""
    success = newsletter_service.unsubscribe(email)
    if success:
        return APIResponse(
            success=True,
            message="Successfully unsubscribed from newsletter",
            data={"email": email}
        )
    else:
        return APIResponse(
            success=False,
            message="Email not found in subscriptions",
            data={"email": email}
        )

@router.get("/api/newsletter/stats", response_model=APIResponse)
async def get_newsletter_stats(
    newsletter_service: NewsletterService = Depends(get_newsletter_service)
):
    """Get newsletter statistics"""
    subscriber_count = newsletter_service.get_subscriber_count()
    recent_subscriptions = newsletter_service.get_recent_subscriptions(days=30)
    
    return APIResponse(
        success=True,
        message="Newsletter statistics retrieved",
        data={
            "total_subscribers": subscriber_count,
            "recent_subscriptions_30d": len(recent_subscriptions),
            "sample_recent_emails": [sub.email for sub in recent_subscriptions[:5]]
        }
    )

@router.post("/api/donate", response_model=APIResponse)
async def process_donation(
    donation: DonationRequest,
    background_tasks: BackgroundTasks,
    stats_service: StatisticsService = Depends(get_stats_service)
):
    """Process a donation (simulated)"""
    stats_service.record_visit()
    stats_service.record_donation()
    
    # Simulate payment processing
    background_tasks.add_task(process_payment, donation)
    
    return APIResponse(
        success=True,
        message="Donation processed successfully",
        data={
            "amount": donation.amount,
            "donor_email": donation.donor_email,
            "transaction_id": f"TXN_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "is_recurring": donation.is_recurring
        }
    )

@router.post("/api/contact", response_model=APIResponse)
async def submit_contact_form(
    contact: ContactMessage,
    background_tasks: BackgroundTasks
):
    """Submit contact form message"""
    # Simulate sending notification email
    background_tasks.add_task(send_contact_notification, contact)
    
    return APIResponse(
        success=True,
        message="Contact message received successfully",
        data={
            "name": contact.name,
            "email": contact.email,
            "subject": contact.subject,
            "urgency": contact.urgency
        }
    )

@router.get("/api/stats", response_model=SiteStatistics)
async def get_site_statistics(
    stats_service: StatisticsService = Depends(get_stats_service)
):
    """Get website statistics"""
    return stats_service.get_statistics()

@router.get("/api/stats/visitors-today", response_model=APIResponse)
async def get_today_visitors(
    stats_service: StatisticsService = Depends(get_stats_service)
):
    """Get today's visitor count"""
    visitors_today = stats_service.get_visitors_today()
    return APIResponse(
        success=True,
        message="Today's visitor statistics",
        data={"visitors_today": visitors_today}
    )

@router.get("/api/content/hero", response_model=APIResponse)
async def get_hero_content():
    """Get hero section content"""
    content = ContentService.get_hero_content()
    return APIResponse(
        success=True,
        message="Hero content retrieved",
        data=content
    )

@router.get("/api/content/actions", response_model=APIResponse)
async def get_action_content():
    """Get action items content"""
    actions = ContentService.get_action_items()
    return APIResponse(
        success=True,
        message="Action items retrieved",
        data={"actions": actions}
    )

@router.get("/api/content/footer", response_model=APIResponse)
async def get_footer_content():
    """Get footer content"""
    footer = ContentService.get_footer_content()
    return APIResponse(
        success=True,
        message="Footer content retrieved",
        data=footer
    )

@router.post("/api/petition/sign", response_model=APIResponse)
async def sign_petition(
    name: str,
    email: str,
    country: str,
    stats_service: StatisticsService = Depends(get_stats_service)
):
    """Sign a conservation petition (simulated)"""
    stats_service.record_visit()
    stats_service.record_petition()
    
    return APIResponse(
        success=True,
        message="Petition signed successfully",
        data={
            "name": name,
            "email": email,
            "country": country,
            "signature_number": stats_service.stats.petitions_signed,
            "timestamp": datetime.now()
        }
    )

# Background task functions
async def send_welcome_email(email: str):
    """Simulate sending welcome email"""
    await asyncio.sleep(0.5)  # Simulate email sending delay
    print(f"[Background Task] Welcome email sent to: {email}")

async def process_payment(donation: DonationRequest):
    """Simulate payment processing"""
    await asyncio.sleep(1)  # Simulate payment processing delay
    print(f"[Background Task] Payment processed for {donation.donor_email}: ${donation.amount}")

async def send_contact_notification(contact: ContactMessage):
    """Simulate sending contact notification"""
    await asyncio.sleep(0.3)  # Simulate notification sending
    print(f"[Background Task] Contact notification: {contact.name} - {contact.subject}")
