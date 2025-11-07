"""
Schémas Pydantic pour les villages.
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class VillageBase(BaseModel):
    """Schéma de base pour Village"""
    name: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=500)


class VillageCreate(VillageBase):
    """Schéma pour créer un village"""
    pass


class VillageUpdate(BaseModel):
    """Schéma pour mise à jour village"""
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=500)


class VillageResponse(VillageBase):
    """Schéma pour réponse village"""
    id: int
    user_id: int
    warehouse_capacity: int
    moral: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class VillageStats(BaseModel):
    """Schéma pour statistiques village"""
    total_characters: int
    total_buildings: int
    total_missions: int
    total_resources: int
    moral: int
    warehouse_capacity: int
    warehouse_used: int
