"""
Business logic and data services for Shaxian Snacks website
"""

from typing import List, Optional
from .schemas import MenuItem, Location, Testimonial, WebsiteContent, DishCategory


class DataService:
    """Service for managing Shaxian Snacks data"""
    
    def __init__(self):
        self._initialize_data()
    
    def _initialize_data(self):
        """Initialize sample data for the website"""
        self.menu_items = [
            MenuItem(
                id=1,
                name="沙县拌面 (Shaxian Mixed Noodles)",
                description="Signature wheat noodles tossed in savory sesame sauce with minced pork and vegetables",
                price=15.0,
                category=DishCategory.NOODLES,
                is_popular=True,
                image_url="/images/noodles.jpg"
            ),
            MenuItem(
                id=2,
                name="蒸饺 (Steamed Dumplings)",
                description="Delicate pork and vegetable dumplings steamed to perfection, served with vinegar dipping sauce",
                price=12.0,
                category=DishCategory.DUMPLINGS,
                is_popular=True,
                image_url="/images/dumplings.jpg"
            ),
            MenuItem(
                id=3,
                name="扁肉 (Wonton Soup)",
                description="Light pork wontons in clear broth with green onions and seaweed",
                price=10.0,
                category=DishCategory.SOUP,
                is_popular=True,
                image_url="/images/wonton.jpg"
            ),
            MenuItem(
                id=4,
                name="炒饭 (Fried Rice)",
                description="Classic Chinese fried rice with eggs, vegetables, and choice of meat",
                price=18.0,
                category=DishCategory.RICE,
                is_popular=False,
                image_url="/images/fried-rice.jpg"
            ),
            MenuItem(
                id=5,
                name="卤味拼盘 (Braised Platter)",
                description="Assortment of braised meats and tofu in aromatic soy-based sauce",
                price=25.0,
                category=DishCategory.SIDES,
                is_popular=False,
                image_url="/images/braised.jpg"
            ),
        ]
        
        self.locations = [
            Location(
                id=1,
                name="沙县小吃总店 (Main Store)",
                address="123 Food Street, Shaxian District",
                city="Sanming, Fujian",
                phone="+86 591 1234 5678",
                opening_hours="8:00 AM - 10:00 PM Daily",
                latitude=26.2656,
                longitude=117.6300
            ),
            Location(
                id=2,
                name="沙县小吃北京分店 (Beijing Branch)",
                address="456 Wangfujing Street, Dongcheng District",
                city="Beijing",
                phone="+86 10 8765 4321",
                opening_hours="9:00 AM - 11:00 PM Daily",
                latitude=39.9042,
                longitude=116.4074
            ),
            Location(
                id=3,
                name="沙县小吃上海分店 (Shanghai Branch)",
                address="789 Nanjing Road, Huangpu District",
                city="Shanghai",
                phone="+86 21 2345 6789",
                opening_hours="10:00 AM - 10:00 PM Daily",
                latitude=31.2304,
                longitude=121.4737
            ),
        ]
        
        self.testimonials = [
            Testimonial(
                id=1,
                customer_name="张先生 (Mr. Zhang)",
                content="The mixed noodles are absolutely delicious! Authentic Shaxian taste that reminds me of home.",
                rating=5,
                date="2024-01-15"
            ),
            Testimonial(
                id=2,
                customer_name="李女士 (Ms. Li)",
                content="Best value for money. The steamed dumplings are my favorite - always fresh and flavorful.",
                rating=4,
                date="2024-01-20"
            ),
            Testimonial(
                id=3,
                customer_name="王同学 (Student Wang)",
                content="Perfect for students on a budget. Great food at affordable prices. The wonton soup is amazing!",
                rating=5,
                date="2024-01-25"
            ),
        ]
        
        self.introduction_text = """
        Shaxian Snacks (沙县小吃) is a beloved Chinese fast food chain originating from Shaxian County in Fujian Province. 
        Founded in the 1990s, it has grown to become one of China's most popular and widespread snack chains, 
        with thousands of locations across the country and internationally.
        
        Known for its affordable prices, quick service, and authentic flavors, Shaxian Snacks specializes in 
        traditional Fujianese street food. Our menu features signature dishes like mixed noodles, steamed dumplings, 
        and wonton soup, all prepared with time-honored recipes and fresh ingredients.
        
        Whether you're looking for a quick lunch, a late-night snack, or authentic Chinese street food experience, 
        Shaxian Snacks offers delicious, satisfying meals that won't break the bank.
        """
    
    def get_website_content(self) -> WebsiteContent:
        """Get complete website content"""
        return WebsiteContent(
            introduction=self.introduction_text,
            menu_highlights=[item for item in self.menu_items if item.is_popular],
            locations=self.locations,
            testimonials=self.testimonials,
            contact_email="info@shaxiansnacks.com",
            social_media={
                "wechat": "shaxian_snacks_official",
                "weibo": "@沙县小吃官方",
                "douyin": "shaxian_snacks"
            }
        )
    
    def get_all_menu_items(self) -> List[MenuItem]:
        """Get all menu items"""
        return self.menu_items
    
    def get_popular_items(self) -> List[MenuItem]:
        """Get popular menu items"""
        return [item for item in self.menu_items if item.is_popular]
    
    def get_menu_item_by_id(self, item_id: int) -> Optional[MenuItem]:
        """Get a specific menu item by ID"""
        for item in self.menu_items:
            if item.id == item_id:
                return item
        return None
    
    def get_menu_items_by_category(self, category: DishCategory) -> List[MenuItem]:
        """Get menu items by category"""
        return [item for item in self.menu_items if item.category == category]
    
    def get_all_locations(self) -> List[Location]:
        """Get all locations"""
        return self.locations
    
    def get_location_by_id(self, location_id: int) -> Optional[Location]:
        """Get a specific location by ID"""
        for location in self.locations:
            if location.id == location_id:
                return location
        return None
    
    def get_locations_by_city(self, city: str) -> List[Location]:
        """Get locations by city"""
        return [loc for loc in self.locations if loc.city.lower() == city.lower()]
    
    def get_all_testimonials(self) -> List[Testimonial]:
        """Get all testimonials"""
        return self.testimonials
    
    def get_testimonials_by_rating(self, min_rating: int = 4) -> List[Testimonial]:
        """Get testimonials with minimum rating"""
        return [t for t in self.testimonials if t.rating >= min_rating]


# Create singleton instance
data_service = DataService()