from typing import List, Dict, Optional
from app.schemas import (
    RedPandaInfo, RedPandaFact, RedPandaImage, 
    FunFact, ConservationOrganization, ConservationStatus
)

class RedPandaService:
    """Service for managing red panda information"""
    
    def __init__(self):
        self._initialize_data()
    
    def _initialize_data(self):
        """Initialize with sample red panda data"""
        self.red_panda_info = RedPandaInfo(
            scientific_name="Ailurus fulgens",
            common_names=["Red Panda", "Lesser Panda", "Fire Fox"],
            conservation_status=ConservationStatus.ENDANGERED,
            size="51-64 cm (20-25 in) body length, 28-49 cm (11-19 in) tail",
            weight="3-6 kg (6.6-13.2 lb)",
            lifespan="8-10 years in the wild, up to 15 years in captivity",
            habitat=["Temperate forests", "Bamboo forests", "Mixed deciduous forests"],
            geographic_range="Eastern Himalayas and southwestern China",
            diet=["Bamboo leaves and shoots", "Fruits", "Acorns", "Eggs", "Insects"],
            feeding_habits="Primarily herbivorous but occasionally omnivorous",
            behavior=["Arboreal (tree-dwelling)", "Solitary", "Territorial", "Most active at dawn and dusk"],
            activity_pattern="Crepuscular (most active at dawn and dusk)",
            threats=["Habitat loss", "Poaching", "Climate change", "Disease"],
            population_trend="Decreasing"
        )
        
        self.facts = [
            RedPandaFact(
                id="fact-1",
                title="Not Actually a Panda",
                description="Despite its name, the red panda is not closely related to the giant panda. It's actually more closely related to raccoons, weasels, and skunks.",
                category="biology",
                source="Smithsonian's National Zoo"
            ),
            RedPandaFact(
                id="fact-2",
                title="Bamboo Specialist",
                description="Red pandas have a modified wrist bone that acts like a thumb, helping them grasp bamboo stems. They spend up to 13 hours a day eating bamboo!",
                category="diet",
                source="World Wildlife Fund"
            ),
            RedPandaFact(
                id="fact-3",
                title="Temperature Regulation",
                description="Red pandas use their bushy tails as blankets to wrap around themselves for warmth in cold mountain climates.",
                category="behavior",
                source="San Diego Zoo"
            ),
            RedPandaFact(
                id="fact-4",
                title="Communication",
                description="Red pandas communicate through various sounds including twitters, whistles, and even a 'huff-quack' sound when threatened.",
                category="behavior",
                source="Red Panda Network"
            )
        ]
        
        self.fun_facts = [
            FunFact(
                id="fun-1",
                fact="Red pandas have a false thumb!",
                explanation="They have an extended wrist bone that helps them grip bamboo, similar to giant pandas."
            ),
            FunFact(
                id="fun-2",
                fact="They're excellent climbers from birth.",
                explanation="Red panda cubs can climb trees when they're just a few months old."
            ),
            FunFact(
                id="fun-3",
                fact="Their tails are almost as long as their bodies.",
                explanation="This helps with balance when climbing trees."
            ),
            FunFact(
                id="fun-4",
                fact="Red pandas are mostly solitary animals.",
                explanation="They only come together during mating season."
            )
        ]
        
        self.images = [
            RedPandaImage(
                id="img-1",
                url="/static/images/red-panda-1.jpg",
                alt_text="A red panda sitting on a tree branch with its distinctive red fur and ringed tail",
                caption="Red panda in its natural habitat",
                credit="CC BY 2.0"
            ),
            RedPandaImage(
                id="img-2",
                url="/static/images/red-panda-2.jpg",
                alt_text="Close-up of a red panda's face showing its white markings and curious expression",
                caption="Close-up of a red panda",
                credit="CC BY-SA 3.0"
            ),
            RedPandaImage(
                id="img-3",
                url="/static/images/red-panda-3.jpg",
                alt_text="Red panda climbing a tree showing its agile movements",
                caption="Red panda climbing",
                credit="CC BY 2.0"
            )
        ]
        
        self.conservation_orgs = [
            ConservationOrganization(
                name="Red Panda Network",
                website="https://redpandanetwork.org",
                description="Dedicated to the conservation of wild red pandas and their habitat",
                focus_areas=["Habitat conservation", "Community education", "Research"]
            ),
            ConservationOrganization(
                name="World Wildlife Fund",
                website="https://www.worldwildlife.org/species/red-panda",
                description="Works to conserve nature and reduce the most pressing threats to biodiversity",
                focus_areas=["Global conservation", "Policy advocacy", "Species protection"]
            ),
            ConservationOrganization(
                name="International Union for Conservation of Nature (IUCN)",
                website="https://www.iucnredlist.org/species/714/110023718",
                description="Provides information about species' conservation status",
                focus_areas=["Species assessment", "Conservation planning", "Data collection"]
            )
        ]
    
    def get_red_panda_info(self) -> RedPandaInfo:
        """Get comprehensive red panda information"""
        return self.red_panda_info
    
    def get_facts(self, category: Optional[str] = None) -> List[RedPandaFact]:
        """Get red panda facts, optionally filtered by category"""
        if category:
            return [fact for fact in self.facts if fact.category.lower() == category.lower()]
        return self.facts
    
    def get_fun_facts(self, limit: Optional[int] = None) -> List[FunFact]:
        """Get fun facts about red pandas"""
        if limit:
            return self.fun_facts[:limit]
        return self.fun_facts
    
    def get_images(self) -> List[RedPandaImage]:
        """Get red panda images"""
        return self.images
    
    def get_conservation_organizations(self) -> List[ConservationOrganization]:
        """Get conservation organizations working with red pandas"""
        return self.conservation_orgs
    
    def search_facts(self, query: str) -> List[RedPandaFact]:
        """Search facts by keyword"""
        query = query.lower()
        results = []
        for fact in self.facts:
            if (query in fact.title.lower() or 
                query in fact.description.lower() or 
                query in fact.category.lower()):
                results.append(fact)
        return results
    
    def get_statistics(self) -> Dict:
        """Get red panda statistics"""
        return {
            "total_facts": len(self.facts),
            "total_fun_facts": len(self.fun_facts),
            "total_images": len(self.images),
            "conservation_status": self.red_panda_info.conservation_status.value,
            "threat_count": len(self.red_panda_info.threats),
            "habitat_types": len(self.red_panda_info.habitat)
        }