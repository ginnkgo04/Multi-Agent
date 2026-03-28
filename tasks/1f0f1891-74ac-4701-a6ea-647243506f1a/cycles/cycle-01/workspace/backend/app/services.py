from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4, UUID

# In-memory data store for development
_snacks_db: Dict[UUID, Dict[str, Any]] = {}

# Sample data for Wuhan specialty snacks
_sample_snacks = [
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Hot Dry Noodles (热干面)",
        "description": "A signature Wuhan breakfast dish featuring wheat noodles tossed in a savory sesame paste sauce with pickled vegetables, scallions, and chili oil.",
        "category": "Noodles",
        "origin": "Wuhan, Hubei",
        "popularity": 10,
        "spice_level": 2,
        "vegetarian": True,
        "image_url": "/images/hot-dry-noodles.jpg",
        "created_at": "2023-10-15T08:30:00Z",
        "updated_at": "2023-10-15T08:30:00Z"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "Doupi (豆皮)",
        "description": "A savory snack consisting of a crispy outer layer made from mung bean and rice flour, filled with glutinous rice, mushrooms, bamboo shoots, and pork.",
        "category": "Pastry",
        "origin": "Wuhan, Hubei",
        "popularity": 8,
        "spice_level": 1,
        "vegetarian": False,
        "image_url": "/images/doupi.jpg",
        "created_at": "2023-10-15T09:15:00Z",
        "updated_at": "2023-10-15T09:15:00Z"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "name": "Mianwo (面窝)",
        "description": "A deep-fried doughnut-like snack made from rice and soybean batter, crispy on the outside and soft on the inside, often eaten for breakfast.",
        "category": "Fried Snack",
        "origin": "Wuhan, Hubei",
        "popularity": 7,
        "spice_level": 0,
        "vegetarian": True,
        "image_url": "/images/mianwo.jpg",
        "created_at": "2023-10-15T10:00:00Z",
        "updated_at": "2023-10-15T10:00:00Z"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440003",
        "name": "Tangbao (汤包)",
        "description": "Soup dumplings with thin, delicate wrappers filled with pork and a rich, flavorful broth that bursts in your mouth.",
        "category": "Dumplings",
        "origin": "Wuhan, Hubei",
        "popularity": 9,
        "spice_level": 1,
        "vegetarian": False,
        "image_url": "/images/tangbao.jpg",
        "created_at": "2023-10-15T11:20:00Z",
        "updated_at": "2023-10-15T11:20:00Z"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440004",
        "name": "Lotus Root and Pork Rib Soup (莲藕排骨汤)",
        "description": "A comforting soup made with pork ribs, lotus root, and spices, simmered for hours until the flavors meld perfectly.",
        "category": "Soup",
        "origin": "Wuhan, Hubei",
        "popularity": 8,
        "spice_level": 0,
        "vegetarian": False,
        "image_url": "/images/lotus-root-soup.jpg",
        "created_at": "2023-10-15T12:45:00Z",
        "updated_at": "2023-10-15T12:45:00Z"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440005",
        "name": "Fried Stinky Tofu (炸臭豆腐)",
        "description": "Fermented tofu that is deep-fried until crispy and served with chili sauce and pickled vegetables. Strong aroma but delicious taste.",
        "category": "Fried Snack",
        "origin": "Wuhan, Hubei",
        "popularity": 6,
        "spice_level": 3,
        "vegetarian": True,
        "image_url": "/images/stinky-tofu.jpg",
        "created_at": "2023-10-15T14:10:00Z",
        "updated_at": "2023-10-15T14:10:00Z"
    }
]

# Initialize the in-memory database with sample data
def _initialize_db():
    """Initialize the in-memory database with sample snack data"""
    for snack in _sample_snacks:
        snack_id = UUID(snack["id"])
        snack_data = snack.copy()
        snack_data["id"] = snack_id
        snack_data["created_at"] = datetime.fromisoformat(snack["created_at"].replace("Z", "+00:00"))
        snack_data["updated_at"] = datetime.fromisoformat(snack["updated_at"].replace("Z", "+00:00"))
        _snacks_db[snack_id] = snack_data

# Initialize database on module import
_initialize_db()

class SnackService:
    """Service layer for snack business logic"""
    
    @staticmethod
    def get_all_snacks(
        category: Optional[str] = None,
        vegetarian: Optional[bool] = None,
        min_popularity: Optional[int] = None,
        max_spice_level: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all snacks with optional filtering
        
        Args:
            category: Filter by snack category
            vegetarian: Filter by vegetarian status
            min_popularity: Minimum popularity score (1-10)
            max_spice_level: Maximum spice level (0-5)
            
        Returns:
            List of snack dictionaries
        """
        snacks = list(_snacks_db.values())
        
        # Apply filters
        filtered_snacks = []
        for snack in snacks:
            # Category filter
            if category and snack.get("category") != category:
                continue
                
            # Vegetarian filter
            if vegetarian is not None and snack.get("vegetarian") != vegetarian:
                continue
                
            # Popularity filter
            if min_popularity is not None and snack.get("popularity", 0) < min_popularity:
                continue
                
            # Spice level filter
            if max_spice_level is not None and snack.get("spice_level", 5) > max_spice_level:
                continue
                
            filtered_snacks.append(snack)
        
        # Sort by popularity (descending)
        filtered_snacks.sort(key=lambda x: x.get("popularity", 0), reverse=True)
        
        return filtered_snacks
    
    @staticmethod
    def get_snack_by_id(snack_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single snack by ID
        
        Args:
            snack_id: UUID of the snack
            
        Returns:
            Snack dictionary if found, None otherwise
        """
        return _snacks_db.get(snack_id)
    
    @staticmethod
    def create_snack(snack_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new snack
        
        Args:
            snack_data: Dictionary containing snack attributes
            
        Returns:
            Created snack dictionary
        """
        snack_id = uuid4()
        now = datetime.utcnow()
        
        # Prepare snack data
        new_snack = {
            "id": snack_id,
            "created_at": now,
            "updated_at": now,
            **snack_data
        }
        
        # Validate required fields
        required_fields = ["name", "description", "category", "origin"]
        for field in required_fields:
            if field not in new_snack or not new_snack[field]:
                raise ValueError(f"Missing required field: {field}")
        
        # Set default values for optional fields
        new_snack.setdefault("popularity", 5)
        new_snack.setdefault("spice_level", 0)
        new_snack.setdefault("vegetarian", False)
        new_snack.setdefault("image_url", "/images/default-snack.jpg")
        
        # Store in database
        _snacks_db[snack_id] = new_snack
        
        return new_snack
    
    @staticmethod
    def update_snack(snack_id: UUID, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an existing snack
        
        Args:
            snack_id: UUID of the snack to update
            update_data: Dictionary containing fields to update
            
        Returns:
            Updated snack dictionary if found, None otherwise
        """
        if snack_id not in _snacks_db:
            return None
        
        # Get current snack
        snack = _snacks_db[snack_id]
        
        # Update fields
        for key, value in update_data.items():
            if key not in ["id", "created_at"]:  # Protect immutable fields
                snack[key] = value
        
        # Update timestamp
        snack["updated_at"] = datetime.utcnow()
        
        # Save back to database
        _snacks_db[snack_id] = snack
        
        return snack
    
    @staticmethod
    def delete_snack(snack_id: UUID) -> bool:
        """
        Delete a snack by ID
        
        Args:
            snack_id: UUID of the snack to delete
            
        Returns:
            True if deleted, False if not found
        """