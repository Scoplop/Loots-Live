"""
Schémas Pydantic pour les bâtiments.
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any
from backend.app.utils.constants import BuildingCategory


class BuildingBase(BaseModel):
    """Schéma de base pour Building (référence statique)"""
    key: str
    name: str
    description: str
    category: BuildingCategory


class BuildingResponse(BuildingBase):
    """Schéma pour réponse bâtiment (référence)"""
    id: int
    build_cost: Dict[str, int]
    production: Optional[Dict[str, Any]] = None
    bonuses: Optional[Dict[str, Any]] = None
    automation_type: Optional[str] = None
    requirements: Optional[Dict[str, Any]] = None
    max_instances: int
    unlock_level: int
    
    model_config = ConfigDict(from_attributes=True)


class BuildingInstanceBase(BaseModel):
    """Schéma de base pour BuildingInstance (instance placée)"""
    building_id: int
    grid_x: int = Field(..., ge=0, le=100)
    grid_y: int = Field(..., ge=0, le=100)


class BuildingInstanceCreate(BuildingInstanceBase):
    """Schéma pour créer une instance de bâtiment"""
    pass


class BuildingInstanceResponse(BuildingInstanceBase):
    """Schéma pour réponse instance de bâtiment"""
    id: int
    village_id: int
    level: int
    is_active: bool
    built_at: datetime
    last_production_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class BuildingInstanceWithDetails(BuildingInstanceResponse):
    """Schéma pour instance avec détails du bâtiment"""
    building: BuildingResponse


class BuildingBuild(BaseModel):
    """Schéma pour construire un bâtiment"""
    building_key: str
    grid_x: int = Field(..., ge=0, le=100)
    grid_y: int = Field(..., ge=0, le=100)


class BuildingDestroy(BaseModel):
    """Schéma pour détruire un bâtiment"""
    building_instance_id: int


class BuildingProduction(BaseModel):
    """Schéma pour production d'un bâtiment"""
    building_instance_id: int
    resource_produced: str
    quantity_produced: int
    production_time_hours: float
