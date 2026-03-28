from typing import Dict, List, Optional
from .schemas import PigContent, PigCharacteristic, FunFact, ContentUpdate
import json
import os


class ContentService:
    """Service for managing pink pig content"""
    
    def __init__(self):
        self.content = self._load_default_content()
        self.content_file = "content_data.json"
    
    def _load_default_content(self) -> PigContent:
        """Load default content for the pink pig website"""
        return PigContent(
            name="粉粉猪",
            tagline="世界上最可爱的小猪！",
            description="粉粉猪是一只超级可爱的粉色小猪，它有着圆圆的眼睛、粉嫩的皮肤和永远开心的笑容。它喜欢在泥巴里打滚，也喜欢吃甜甜的苹果。",
            
            main_image_url="/static/images/pink-pig-main.jpg",
            secondary_images=[
                "/static/images/pig-playing.jpg",
                "/static/images/pig-sleeping.jpg",
                "/static/images/pig-eating.jpg"
            ],
            
            characteristics=[
                PigCharacteristic(
                    title="超级可爱",
                    description="粉粉猪有着圆圆的大眼睛和粉嫩的皮肤，让人一看就忍不住想抱抱！",
                    icon="heart"
                ),
                PigCharacteristic(
                    title="活泼好动",
                    description="喜欢在草地上奔跑，在泥巴里打滚，永远充满活力！",
                    icon="running"
                ),
                PigCharacteristic(
                    title="爱吃美食",
                    description="特别喜欢吃甜甜的苹果、胡萝卜和玉米，是个小吃货！",
                    icon="apple"
                ),
                PigCharacteristic(
                    title="友好善良",
                    description="对所有的朋友都很友好，喜欢和大家一起玩耍！",
                    icon="friends"
                )
            ],
            
            fun_facts=[
                FunFact(
                    fact="猪的智商相当于3岁的人类小孩，非常聪明！",
                    category="智力",
                    is_surprising=True
                ),
                FunFact(
                    fact="猪其实很爱干净，它们会在固定的地方上厕所。",
                    category="习性",
                    is_surprising=True
                ),
                FunFact(
                    fact="猪的嗅觉比狗还要灵敏，可以用来寻找松露。",
                    category="能力",
                    is_surprising=False
                ),
                FunFact(
                    fact="猪会通过不同的叫声表达不同的情绪。",
                    category="交流",
                    is_surprising=False
                ),
                FunFact(
                    fact="猪的皮肤和人一样会被晒伤，所以它们喜欢在泥巴里打滚来防晒。",
                    category="健康",
                    is_surprising=True
                )
            ],
            
            primary_color="#FFB6C1",  # Light pink
            secondary_color="#FFE4E1",  # Misty rose
            accent_color="#FF69B4",  # Hot pink
            
            social_links={
                "facebook": "https://facebook.com/pinkpig",
                "instagram": "https://instagram.com/cutepinkpig",
                "twitter": "https://twitter.com/pinkpigworld"
            }
        )
    
    def get_content(self) -> PigContent:
        """Get the current content"""
        return self.content
    
    def update_content(self, updates: ContentUpdate) -> PigContent:
        """Update content with provided values"""
        current_data = self.content.dict()
        update_data = updates.dict(exclude_unset=True)
        
        # Merge updates
        for key, value in update_data.items():
            if value is not None:
                current_data[key] = value
        
        # Create new content object
        self.content = PigContent(**current_data)
        
        # Save to file
        self._save_content()
        
        return self.content
    
    def get_characteristics(self) -> List[PigCharacteristic]:
        """Get all characteristics"""
        return self.content.characteristics
    
    def get_fun_facts(self, category: Optional[str] = None, surprising_only: bool = False) -> List[FunFact]:
        """Get fun facts, optionally filtered by category or surprising facts"""
        facts = self.content.fun_facts
        
        if category:
            facts = [f for f in facts if f.category == category]
        
        if surprising_only:
            facts = [f for f in facts if f.is_surprising]
        
        return facts
    
    def get_random_fact(self) -> Optional[FunFact]:
        """Get a random fun fact"""
        import random
        if self.content.fun_facts:
            return random.choice(self.content.fun_facts)
        return None
    
    def _save_content(self):
        """Save content to JSON file"""
        try:
            with open(self.content_file, 'w', encoding='utf-8') as f:
                json.dump(self.content.dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving content: {e}")
    
    def load_content_from_file(self) -> bool:
        """Load content from JSON file"""
        try:
            if os.path.exists(self.content_file):
                with open(self.content_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.content = PigContent(**data)
                return True
        except Exception as e:
            print(f"Error loading content: {e}")
        return False


class StaticFileService:
    """Service for managing static files"""
    
    def __init__(self, static_dir: str = "static"):
        self.static_dir = static_dir
        self.allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.css', '.js', '.html'}
    
    def get_static_file_path(self, filename: str) -> Optional[str]:
        """Get the path to a static file if it exists and is allowed"""
        # Security check: prevent directory traversal
        if '..' in filename or filename.startswith('/'):
            return None
        
        # Check extension
        _, ext = os.path.splitext(filename)
        if ext.lower() not in self.allowed_extensions:
            return None
        
        filepath = os.path.join(self.static_dir, filename)
        
        if os.path.exists(filepath) and os.path.isfile(filepath):
            return filepath
        
        return None
    
    def list_images(self) -> List[str]:
        """List all image files in static directory"""
        images = []
        if os.path.exists(self.static_dir):
            for file in os.listdir(self.static_dir):
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.svg')):
                    images.append(file)
        return images


# Create singleton instances
content_service = ContentService()
static_file_service = StaticFileService()