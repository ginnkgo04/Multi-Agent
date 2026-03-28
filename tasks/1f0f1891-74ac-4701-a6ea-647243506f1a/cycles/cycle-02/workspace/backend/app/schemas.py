from typing import List, Optional
from pydantic import BaseModel


class SnackBase(BaseModel):
    name: str
    description: str
    ingredients: List[str]
    origin: str
    popularity: int


class SnackCreate(SnackBase):
    pass


class SnackUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    ingredients: Optional[List[str]] = None
    origin: Optional[str] = None
    popularity: Optional[int] = None


class Snack(SnackBase):
    id: int

    class Config:
        from_attributes = True