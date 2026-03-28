from typing import List, Optional
from fastapi import HTTPException
from .schemas import Snack, SnackResponse

# In-memory data store for Wuhan snacks
# In a real application, this would be replaced with a database
_snacks_data = [
    {
        "id": 1,
        "name": "Hot Dry Noodles (热干面)",
        "description": "Wuhan's most famous breakfast dish featuring springy noodles tossed in sesame paste, soy sauce, and chili oil.",
        "ingredients": ["Wheat noodles", "Sesame paste", "Soy sauce", "Chili oil", "Pickled vegetables", "Green onions"],
        "origin": "Wuhan, Hubei Province",
        "image_url": "/images/hot-dry-noodles.jpg"
    },
    {
        "id": 2,
        "name": "Doupi (豆皮)",
        "description": "A savory snack consisting of a crispy outer layer made from rice and mung bean flour, filled with glutinous rice, mushrooms, and pork.",
        "ingredients": ["Rice flour", "Mung bean flour", "Glutinous rice", "Mushrooms", "Pork", "Bamboo shoots"],
        "origin": "Wuhan, Hubei Province",
        "image_url": "/images/doupi.jpg"
    },
    {
        "id": 3,
        "name": "Mianwo (面窝)",
        "description": "A deep-fried dough ring made from rice and soybean batter, crispy on the outside and soft in the middle.",
        "ingredients": ["Rice flour", "Soybean flour", "Green onions", "Sesame seeds", "Salt"],
        "origin": "Wuhan, Hubei Province",
        "image_url": "/images/mianwo.jpg"
    },
    {
        "id": 4,
        "name": "Tangbao (汤包)",
        "description": "Soup dumplings with thin wrappers filled with pork and rich broth, a popular snack throughout Hubei.",
        "ingredients": ["Wheat flour", "Pork", "Pork skin jelly", "Ginger", "Green onions", "Soy sauce"],
        "origin": "Wuhan, Hubei Province",
        "image_url": "/images/tangbao.jpg"
    },
    {
        "id": 5,
        "name": "Lotus Root and Pork Rib Soup (莲藕排骨汤)",
        "description": "A nourishing soup made with pork ribs and lotus root, known for its sweet flavor and health benefits.",
        "ingredients": ["Lotus root", "Pork ribs", "Ginger", "Green onions", "Salt", "Pepper"],
        "origin": "Wuhan, Hubei Province",
        "image_url": "/images/lotus-root-soup.jpg"
    },
    {
        "id": 6,
        "name": "Fried Bean Skin (炸豆皮)",
        "description": "Crispy fried bean skin sheets often served as a street food snack or added to soups and noodles.",
        "ingredients": ["Bean skin", "Oil", "Salt", "Five-spice powder"],
        "origin": "Wuhan, Hubei Province",
        "image_url": "/images/fried-bean-skin.jpg"
    }
]

class SnackService:
    """Service layer for snack data operations"""
    
    @staticmethod
    def get_all_snacks() -> List[Snack]:
        """Retrieve all Wuhan snacks"""
        return [Snack(**snack) for snack in _snacks_data]
    
    @staticmethod
    def get_snack_by_id(snack_id: int) -> Optional[Snack]:
        """Retrieve a specific snack by ID"""
        for snack in _snacks_data:
            if snack["id"] == snack_id:
                return Snack(**snack)
        return None
    
    @staticmethod
    def get_snack_response(snack_id: Optional[int] = None) -> SnackResponse:
        """Get snack data formatted as API response"""
        if snack_id is None:
            # Return all snacks
            snacks = SnackService.get_all_snacks()
            return SnackResponse(
                success=True,
                message="Successfully retrieved all Wuhan snacks",
                data=snacks
            )
        else:
            # Return specific snack
            snack = SnackService.get_snack_by_id(snack_id)
            if snack is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Snack with ID {snack_id} not found"
                )
            return SnackResponse(
                success=True,
                message=f"Successfully retrieved snack with ID {snack_id}",
                data=snack
            )
    
    @staticmethod
    def get_snacks_count() -> int:
        """Get total number of snacks available"""
        return len(_snacks_data)
    
    @staticmethod
    def search_snacks_by_name(name_query: str) -> List[Snack]:
        """Search snacks by name (case-insensitive partial match)"""
        if not name_query:
            return SnackService.get_all_snacks()
        
        query_lower = name_query.lower()
        results = []
        for snack in _snacks_data:
            if query_lower in snack["name"].lower():
                results.append(Snack(**snack))
        return results
    
    @staticmethod
    def get_snacks_by_ingredient(ingredient: str) -> List[Snack]:
        """Find snacks that contain a specific ingredient"""
        if not ingredient:
            return SnackService.get_all_snacks()
        
        ingredient_lower = ingredient.lower()
        results = []
        for snack in _snacks_data:
            snack_ingredients = [ing.lower() for ing in snack["ingredients"]]
            if any(ingredient_lower in ing for ing in snack_ingredients):
                results.append(Snack(**snack))
        return results

# Create a singleton instance for easy import
snack_service = SnackService()