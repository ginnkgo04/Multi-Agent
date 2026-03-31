from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
from pathlib import Path
from .schemas import (
    PolarBearInfo, Threat, ConservationSolution, NewsletterSubscription,
    DonationRequest, SiteStatistics, ContactMessage, ConservationStatus,
    ThreatType, ActionType
)

class ConservationDataService:
    """Service for managing conservation data and educational content"""
    
    def __init__(self):
        self.polar_bear_info = self._get_default_polar_bear_info()
        self.threats = self._get_default_threats()
        self.solutions = self._get_default_solutions()
        self.statistics = SiteStatistics()
        
    def _get_default_polar_bear_info(self) -> PolarBearInfo:
        """Get default polar bear information"""
        return PolarBearInfo()
    
    def _get_default_threats(self) -> List[Threat]:
        """Get default threats to polar bears"""
        return [
            Threat(
                id="threat_001",
                type=ThreatType.CLIMATE_CHANGE,
                title="Climate Change and Melting Ice",
                description="Arctic sea ice is melting at an unprecedented rate due to global warming, reducing polar bear hunting grounds.",
                severity=9,
                impact="Loss of habitat, reduced hunting success, increased starvation"
            ),
            Threat(
                id="threat_002",
                type=ThreatType.POLLUTION,
                title="Toxic Chemical Accumulation",
                description="Persistent organic pollutants accumulate in the Arctic food chain, affecting polar bear health.",
                severity=7,
                impact="Reproductive issues, immune system damage, developmental problems"
            ),
            Threat(
                id="threat_003",
                type=ThreatType.HABITAT_LOSS,
                title="Industrial Development",
                description="Oil and gas exploration, shipping, and mining activities disrupt Arctic ecosystems.",
                severity=6,
                impact="Habitat fragmentation, oil spill risks, increased human-bear conflicts"
            ),
            Threat(
                id="threat_004",
                type=ThreatType.FOOD_SCARCITY,
                title="Declining Seal Populations",
                description="Changing ice conditions affect seal populations, the primary food source for polar bears.",
                severity=8,
                impact="Malnutrition, reduced cub survival, increased cannibalism"
            )
        ]
    
    def _get_default_solutions(self) -> List[ConservationSolution]:
        """Get default conservation solutions"""
        return [
            ConservationSolution(
                id="solution_001",
                title="Reduce Carbon Emissions",
                description="Support and advocate for policies that reduce greenhouse gas emissions globally.",
                action_type=ActionType.ADVOCACY,
                effectiveness=9,
                resources_needed=["Policy advocacy", "Public awareness campaigns"],
                organizations=["WWF", "Greenpeace", "Sierra Club"]
            ),
            ConservationSolution(
                id="solution_002",
                title="Protect Critical Habitat",
                description="Establish and enforce protected areas in key polar bear habitats.",
                action_type=ActionType.ADVOCACY,
                effectiveness=8,
                resources_needed=["Legal protection", "Monitoring systems"],
                organizations=["IUCN", "Arctic Council", "Polar Bears International"]
            ),
            ConservationSolution(
                id="solution_003",
                title="Support Scientific Research",
                description="Fund research on polar bear populations, behavior, and adaptation strategies.",
                action_type=ActionType.RESEARCH,
                effectiveness=7,
                resources_needed=["Research funding", "Field equipment", "Scientific personnel"],
                organizations=["University of Alberta", "Norwegian Polar Institute", "USGS"]
            ),
            ConservationSolution(
                id="solution_004",
                title="Community-Based Conservation",
                description="Work with Arctic communities to reduce human-bear conflicts and promote coexistence.",
                action_type=ActionType.EDUCATION,
                effectiveness=6,
                resources_needed=["Community engagement", "Education programs", "Bear-proof infrastructure"],
                organizations=["Inuit Circumpolar Council", "Local Arctic communities"]
            )
        ]
    
    def get_polar_bear_info(self) -> PolarBearInfo:
        """Get comprehensive information about polar bears"""
        return self.polar_bear_info
    
    def get_threats(self, limit: Optional[int] = None) -> List[Threat]:
        """Get list of threats to polar bears"""
        if limit:
            return self.threats[:limit]
        return self.threats
    
    def get_threat_by_id(self, threat_id: str) -> Optional[Threat]:
        """Get a specific threat by ID"""
        for threat in self.threats:
            if threat.id == threat_id:
                return threat
        return None
    
    def get_solutions(self, limit: Optional[int] = None) -> List[ConservationSolution]:
        """Get list of conservation solutions"""
        if limit:
            return self.solutions[:limit]
        return self.solutions
    
    def get_solution_by_id(self, solution_id: str) -> Optional[ConservationSolution]:
        """Get a specific solution by ID"""
        for solution in self.solutions:
            if solution.id == solution_id:
                return solution
        return None

class NewsletterService:
    """Service for managing newsletter subscriptions"""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path("data/newsletter_subscriptions.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.subscriptions = self._load_subscriptions()
    
    def _load_subscriptions(self) -> List[NewsletterSubscription]:
        """Load subscriptions from storage"""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    return [NewsletterSubscription(**item) for item in data]
        except Exception:
            pass
        return []
    
    def _save_subscriptions(self):
        """Save subscriptions to storage"""
        try:
            with open(self.storage_path, 'w') as f:
                json_data = [sub.dict() for sub in self.subscriptions]
                json.dump(json_data, f, default=str, indent=2)
        except Exception as e:
            print(f"Error saving subscriptions: {e}")
    
    def subscribe(self, subscription: NewsletterSubscription) -> bool:
        """Add a new newsletter subscription"""
        # Check if email already exists
        for sub in self.subscriptions:
            if sub.email == subscription.email:
                return False
        
        self.subscriptions.append(subscription)
        self._save_subscriptions()
        return True
    
    def unsubscribe(self, email: str) -> bool:
        """Remove a newsletter subscription"""
        initial_count = len(self.subscriptions)
        self.subscriptions = [sub for sub in self.subscriptions if sub.email != email]
        
        if len(self.subscriptions) < initial_count:
            self._save_subscriptions()
            return True
        return False
    
    def get_subscriber_count(self) -> int:
        """Get total number of subscribers"""
        return len(self.subscriptions)
    
    def get_recent_subscriptions(self, days: int = 30) -> List[NewsletterSubscription]:
        """Get subscriptions from the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return [sub for sub in self.subscriptions if sub.subscribe_date > cutoff_date]

class StatisticsService:
    """Service for tracking website statistics"""
    
    def __init__(self):
        self.stats = SiteStatistics()
        self.visitor_log = []
    
    def record_visit(self):
        """Record a website visit"""
        self.stats.total_visitors += 1
        self.visitor_log.append(datetime.now())
    
    def record_subscription(self):
        """Record a new newsletter subscription"""
        self.stats.newsletter_subscribers += 1
    
    def record_donation(self):
        """Record a donation"""
        self.stats.donations_received += 1
    
    def record_petition(self):
        """Record a petition signature"""
        self.stats.petitions_signed += 1
    
    def get_statistics(self) -> SiteStatistics:
        """Get current statistics"""
        self.stats.last_updated = datetime.now()
        return self.stats
    
    def get_visitors_today(self) -> int:
        """Get number of visitors today"""
        today = datetime.now().date()
        return sum(1 for visit in self.visitor_log if visit.date() == today)
    
    def get_weekly_trend(self) -> Dict[str, int]:
        """Get weekly visitor trend"""
        trend = {}
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).date()
            count = sum(1 for visit in self.visitor_log if visit.date() == date)
            trend[date.strftime("%Y-%m-%d")] = count
        return trend

class ContentService:
    """Service for managing website content"""
    
    @staticmethod
    def get_hero_content() -> Dict[str, Any]:
        """Get hero section content"""
        return {
            "title": "Save Our Polar Bears",
            "subtitle": "Climate change is melting their home. Join the fight to protect these majestic Arctic giants before it's too late.",
            "cta_primary": "Take Action",
            "cta_secondary": "Learn More"
        }
    
    @staticmethod
    def get_action_items() -> List[Dict[str, Any]]:
        """Get action items for the take action section"""
        return [
            {
                "icon": "fas fa-donate",
                "title": "Make a Donation",
                "description": "Your contribution funds critical conservation efforts and research.",
                "button_text": "Donate Now"
            },
            {
                "icon": "fas fa-envelope",
                "title": "Sign Petitions",
                "description": "Join thousands in urging governments to protect Arctic habitats.",
                "button_text": "Sign Petition"
            },
            {
                "icon": "fas fa-users",
                "title": "Volunteer",
                "description": "Join local conservation groups and participate in awareness campaigns.",
                "button_text": "Get Involved"
            }
        ]
    
    @staticmethod
    def get_footer_content() -> Dict[str, Any]:
        """Get footer content"""
        return {
            "organization_name": "Protect Polar Bears",
            "description": "Dedicated to the conservation and protection of polar bears and their Arctic habitat.",
            "contact": {
                "email": "info@protectpolarbears.org",
                "phone": "+1 (555) 123-4567",
                "address": "Arctic Conservation Center"
            },
            "social_links": [
                {"platform": "facebook", "icon": "fab fa-facebook"},
                {"platform": "twitter", "icon": "fab fa-twitter"},
                {"platform": "instagram", "icon": "fab fa-instagram"},
                {"platform": "youtube", "icon": "fab fa-youtube"}
            ]
        }
