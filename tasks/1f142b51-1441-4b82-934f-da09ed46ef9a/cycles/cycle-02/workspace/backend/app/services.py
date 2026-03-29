"""
小熊猫介绍网站 - 业务逻辑和数据服务
为静态网站提供数据服务
"""

from typing import Dict, Any, List
from app.schemas import (
    RedPandaBasicInfo, HabitatInfo, DietInfo, ConservationStatus,
    FunFact, RedPandaImage, RedPandaCompleteInfo, WebsiteInfo
)


class RedPandaDataService:
    """小熊猫数据服务"""
    
    @staticmethod
    def get_basic_info() -> RedPandaBasicInfo:
        """获取小熊猫基本信息"""
        return RedPandaBasicInfo(
            scientific_name="Ailurus fulgens",
            common_names=["小熊猫", "红熊猫", "火狐"],
            family="Ailuridae",
            genus="Ailurus",
            average_weight="3-6 kg",
            average_length="50-64 cm",
            lifespan="8-10年（野外），12-14年（圈养）"
        )
    
    @staticmethod
    def get_habitat_info() -> HabitatInfo:
        """获取栖息地信息"""
        return HabitatInfo(
            regions=["东亚", "喜马拉雅地区"],
            countries=["中国", "尼泊尔", "印度", "不丹", "缅甸"],
            elevation_range="1500-4800米",
            forest_types=["温带森林", "亚热带森林", "竹林"]
        )
    
    @staticmethod
    def get_diet_info() -> DietInfo:
        """获取饮食信息"""
        return DietInfo(
            primary_food="竹子",
            percentage_bamboo="85-95%",
            other_foods=["水果", "橡子", "根茎", "昆虫", "小鸟蛋"],
            feeding_habits="主要在黄昏和黎明活动觅食"
        )
    
    @staticmethod
    def get_conservation_status() -> ConservationStatus:
        """获取保护状态"""
        return ConservationStatus(
            iucn_status="濒危 (Endangered)",
            population_trend="下降",
            threats=[
                "栖息地丧失和破碎化",
                "非法捕猎",
                "气候变化",
                "人类活动干扰"
            ],
            conservation_efforts=[
                "建立自然保护区",
                "人工繁殖计划",
                "社区保护教育",
                "国际保护合作"
            ]
        )
    
    @staticmethod
    def get_fun_facts() -> List[FunFact]:
        """获取趣味事实"""
        return [
            FunFact(
                id=1,
                fact="小熊猫不是熊，也不是浣熊，而是独立的Ailuridae科的唯一现存物种。",
                category="分类学"
            ),
            FunFact(
                id=2,
                fact="小熊猫的尾巴有12个红白相间的环纹，用于在树上保持平衡和在寒冷天气中保暖。",
                category="生理特征"
            ),
            FunFact(
                id=3,
                fact="小熊猫的腕骨特化为'伪拇指'，帮助它们更好地抓握竹枝。",
                category="适应性"
            ),
            FunFact(
                id=4,
                fact="小熊猫是优秀的攀爬者，但在地面上行动相对笨拙。",
                category="行为"
            ),
            FunFact(
                id=5,
                fact="小熊猫通过抬起前肢、发出嘶嘶声和喷气来展示威胁行为。",
                category="行为"
            )
        ]
    
    @staticmethod
    def get_images() -> List[RedPandaImage]:
        """获取图片信息"""
        return [
            RedPandaImage(
                id=1,
                filename="red-panda-1.jpg",
                alt_text="小熊猫在树上休息",
                caption="小熊猫在树上休息，展示其标志性的红褐色皮毛和环纹尾巴",
                source="示例图片"
            ),
            RedPandaImage(
                id=2,
                filename="red-panda-2.jpg",
                alt_text="小熊猫吃竹子",
                caption="小熊猫用前爪抓住竹枝进食",
                source="示例图片"
            ),
            RedPandaImage(
                id=3,
                filename="red-panda-3.jpg",
                alt_text="小熊猫幼崽",
                caption="可爱的小熊猫幼崽，毛色比成年个体更浅",
                source="示例图片"
            )
        ]
    
    @staticmethod
    def get_complete_info() -> RedPandaCompleteInfo:
        """获取完整的小熊猫信息"""
        return RedPandaCompleteInfo(
            basic_info=RedPandaDataService.get_basic_info(),
            habitat=RedPandaDataService.get_habitat_info(),
            diet=RedPandaDataService.get_diet_info(),
            conservation=RedPandaDataService.get_conservation_status(),
            fun_facts=RedPandaDataService.get_fun_facts(),
            images=RedPandaDataService.get_images()
        )
    
    @staticmethod
    def get_website_info() -> WebsiteInfo:
        """获取网站信息"""
        return WebsiteInfo(
            title="小熊猫介绍网站",
            description="一个介绍小熊猫（红熊猫）的响应式信息网站",
            sections=[
                "首页介绍",
                "基本信息",
                "栖息地",
                "饮食习性",
                "保护状态",
                "趣味知识"
            ],
            features=[
                "响应式设计",
                "语义化HTML结构",
                "无障碍访问支持",
                "高质量图片展示",
                "移动设备优化"
            ]
        )


class StaticContentService:
    """静态内容服务"""
    
    @staticmethod
    def get_navigation_items() -> List[Dict[str, Any]]:
        """获取导航菜单项"""
        return [
            {"id": "home", "title": "首页", "href": "#home"},
            {"id": "basic", "title": "基本信息", "href": "#basic-info"},
            {"id": "habitat", "title": "栖息地", "href": "#habitat"},
            {"id": "diet", "title": "饮食习性", "href": "#diet"},
            {"id": "conservation", "title": "保护状态", "href": "#conservation"},
            {"id": "fun-facts", "title": "趣味知识", "href": "#fun-facts"}
        ]
    
    @staticmethod
    def get_section_titles() -> Dict[str, str]:
        """获取章节标题"""
        return {
            "home": "欢迎来到小熊猫的世界",
            "basic": "小熊猫基本信息",
            "habitat": "栖息地与分布",
            "diet": "饮食习性",
            "conservation": "保护现状",
            "fun_facts": "趣味知识"
        }
    
    @staticmethod
    def get_contact_info() -> Dict[str, str]:
        """获取联系信息"""
        return {
            "email": "info@redpanda-website.example.com",
            "attribution": "本网站内容基于公开的科学资料整理",
            "disclaimer": "图片仅为示例，实际使用时请使用合适授权的高质量图片"
        }


# 创建服务实例
red_panda_service = RedPandaDataService()
static_content_service = StaticContentService()