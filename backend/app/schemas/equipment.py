"""
Schémas Pydantic pour les équipements.
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Dict
from backend.app.utils.constants import EquipmentRarity, EquipmentSlot


class EquipmentBase(BaseModel):
    """Schéma de base pour Equipment"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., max_length=500)
    slot: EquipmentSlot
    rarity: EquipmentRarity


class EquipmentCreate(EquipmentBase):
    """Schéma pour créer un équipement"""
    stats: Dict[str, int]
    sprite_key: str = Field(..., max_length=50)


class EquipmentResponse(EquipmentBase):
    """Schéma pour réponse équipement"""
    id: int
    character_id: int
    stats: Dict[str, int]
    sprite_key: str
    obtained_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class EquipmentGenerate(BaseModel):
    """Schéma pour générer un équipement aléatoire"""
    slot: EquipmentSlot
    rarity: EquipmentRarity
    level: int = Field(default=1, ge=1, le=100)
