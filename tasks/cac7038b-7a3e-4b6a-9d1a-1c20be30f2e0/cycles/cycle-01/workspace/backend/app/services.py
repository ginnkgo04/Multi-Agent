from typing import List, Dict, Any
from datetime import datetime
from fastapi import HTTPException

# In-memory data storage (simulating a database)
content_sections = [
    {
        "id": 1,
        "title": "Introduction to Cherry Blossoms",
        "content": "Cherry blossoms, known as 'sakura' in Japan, are the flowers of several trees of genus Prunus. They are widely celebrated for their stunning beauty and brief blooming period, which symbolizes the transient nature of life. Cherry blossoms typically bloom in spring, creating breathtaking pink and white landscapes that attract millions of visitors worldwide.",
        "section_type": "introduction"
    },
    {
        "id": 2,
        "title": "Interesting Facts About Cherry Blossoms",
        "content": "1. Cherry blossoms have a very short blooming period, usually lasting only about one to two weeks. 2. The practice of cherry blossom viewing is called 'hanami' in Japan, where people gather under blooming trees. 3. There are over 200 varieties of cherry blossom trees. 4. The cherry blossom is Japan's national flower. 5. Some cherry blossom trees can live for hundreds of years. 6. The color of cherry blossoms can range from white to deep pink.",
        "section_type": "facts"
    },
    {
        "id": 3,
        "title": "Cultural Significance",
        "content": "Cherry blossoms hold deep cultural significance in many East Asian countries, particularly Japan. They represent beauty, renewal, and the fleeting nature of life—a concept known as 'mono no aware' in Japanese philosophy. The annual cherry blossom festivals celebrate spring's arrival and bring communities together for picnics and celebrations under the blooming trees.",
        "section_type": "culture"
    },
    {
        "id": 4,
        "title": "Best Viewing Locations",
        "content": "Some of the most famous cherry blossom viewing spots include: Tokyo's Ueno Park and Shinjuku Gyoen, Kyoto's Philosopher's Path, Washington D.C.'s Tidal Basin, Vancouver's Stanley Park, and Paris' Parc de Sceaux. Each location offers unique experiences with different varieties of cherry trees blooming at slightly different times.",
        "section_type": "locations"
    }
]

image_metadata = {
    "filename": "cherry-blossom.jpg",
    "alt_text": "Beautiful pink cherry blossoms in full bloom against a blue sky",
    "url": "/static/cherry-blossom.jpg",
    "size_kb": 245,
    "description": "A high-quality image of cherry blossoms showcasing their delicate pink petals and natural beauty."
}

class ContentService:
    """Service for managing content sections"""
    
    @staticmethod
    def get_all_sections() -> List[Dict[str, Any]]:
        """Get all content sections"""
        return content_sections
    
    @staticmethod
    def get_section_by_id(section_id: int) -> Dict[str, Any]:
        """Get a specific content section by ID"""
        for section in content_sections:
            if section["id"] == section_id:
                return section
        raise HTTPException(status_code=404, detail=f"Section with ID {section_id} not found")
    
    @staticmethod
    def get_sections_by_type(section_type: str) -> List[Dict[str, Any]]:
        """Get content sections by type"""
        filtered_sections = [section for section in content_sections 
                           if section["section_type"] == section_type]
        if not filtered_sections:
            raise HTTPException(
                status_code=404, 
                detail=f"No sections found with type '{section_type}'"
            )
        return filtered_sections
    
    @staticmethod
    def get_introduction_content() -> Dict[str, Any]:
        """Get introduction content specifically"""
        intro_sections = ContentService.get_sections_by_type("introduction")
        return {
            "section_type": "introduction",
            "sections": intro_sections,
            "count": len(intro_sections)
        }
    
    @staticmethod
    def get_facts_content() -> Dict[str, Any]:
        """Get facts content specifically"""
        facts_sections = ContentService.get_sections_by_type("facts")
        return {
            "section_type": "facts",
            "sections": facts_sections,
            "count": len(facts_sections)
        }

class ImageService:
    """Service for managing image data"""
    
    @staticmethod
    def get_image_metadata() -> Dict[str, Any]:
        """Get metadata for the cherry blossom image"""
        return image_metadata
    
    @staticmethod
    def update_image_metadata(updated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update image metadata (simulated update)"""
        global image_metadata
        
        # In a real application, this would update a database
        # For this simulation, we'll merge the updates
        for key, value in updated_data.items():
            if key in image_metadata:
                image_metadata[key] = value
        
        return image_metadata

class HealthService:
    """Service for health checks and system status"""
    
    @staticmethod
    def get_api_status() -> Dict[str, Any]:
        """Get current API status"""
        return {
            "status": "healthy",
            "message": "Cherry Blossom API is running normally",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "endpoints_available": 6,
            "content_sections": len(content_sections)
        }
    
    @staticmethod
    def check_dependencies() -> Dict[str, Any]:
        """Check system dependencies (simulated)"""
        return {
            "database": "connected" if content_sections else "disconnected",
            "file_system": "available",
            "memory_usage": "normal",
            "timestamp": datetime.now().isoformat()
        }

# Service instances for easy import
content_service = ContentService()
image_service = ImageService()
health_service = HealthService()