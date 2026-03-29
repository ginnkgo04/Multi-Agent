"""
小熊猫介绍网站 - 数据模型定义
为静态网站提供简单的数据模型
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class RedPandaBasicInfo(BaseModel):
    """小熊猫基本信息"""
    scientific_name: str = Field(..., description="学名")
    common_names: List[str] = Field(..., description="常用名称")
    family: str = Field(..., description="科")
    genus: str = Field(..., description="属")
    average_weight: str = Field(..., description="平均体重")
    average_length: str = Field(..., description="平均体长")
    lifespan: str = Field(..., description="寿命")


class HabitatInfo(BaseModel):
    """栖息地信息"""
    regions: List[str] = Field(..., description="分布区域")
    countries: List[str] = Field(..., description="分布国家")
    elevation_range: str = Field(..., description="海拔范围")
    forest_types: List[str] = Field(..., description="森林类型")


class DietInfo(BaseModel):
    """饮食信息"""
    primary_food: str = Field(..., description="主要食物")
    percentage_bamboo: str = Field(..., description="竹子占比")
    other_foods: List[str] = Field(..., description="其他食物")
    feeding_habits: str = Field(..., description="进食习性")


class ConservationStatus(BaseModel):
    """保护状态"""
    iucn_status: str = Field(..., description="IUCN状态")
    population_trend: str = Field(..., description="种群趋势")
    threats: List[str] = Field(..., description="主要威胁")
    conservation_efforts: List[str] = Field(..., description="保护措施")


class FunFact(BaseModel):
    """趣味事实"""
    id: int = Field(..., description="事实ID")
    fact: str = Field(..., description="事实内容")
    category: str = Field(..., description="分类")


class RedPandaImage(BaseModel):
    """小熊猫图片信息"""
    id: int = Field(..., description="图片ID")
    filename: str = Field(..., description="文件名")
    alt_text: str = Field(..., description="替代文本")
    caption: str = Field(..., description="说明文字")
    source: Optional[str] = Field(None, description="图片来源")


class RedPandaCompleteInfo(BaseModel):
    """完整的小熊猫信息"""
    basic_info: RedPandaBasicInfo = Field(..., description="基本信息")
    habitat: HabitatInfo = Field(..., description="栖息地信息")
    diet: DietInfo = Field(..., description="饮食信息")
    conservation: ConservationStatus = Field(..., description="保护状态")
    fun_facts: List[FunFact] = Field(..., description="趣味事实")
    images: List[RedPandaImage] = Field(..., description="图片信息")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="状态")
    service: str = Field(..., description="服务名称")
    version: str = Field(..., description="版本")


class WebsiteInfo(BaseModel):
    """网站信息"""
    title: str = Field(..., description="网站标题")
    description: str = Field(..., description="网站描述")
    sections: List[str] = Field(..., description="主要章节")
    features: List[str] = Field(..., description="主要功能")