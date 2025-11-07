"""
Schémas Pydantic pour les ressources.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Dict
from backend.app.utils.constants import ResourceType


class ResourceBase(BaseModel):
    """Schéma de base pour Resource"""
    resource_type: ResourceType
    quantity: int = Field(default=0, ge=0)


class ResourceCreate(ResourceBase):
    """Schéma pour créer une ressource"""
    pass


class ResourceUpdate(BaseModel):
    """Schéma pour mise à jour ressource"""
    quantity: int = Field(..., ge=0)


class ResourceResponse(ResourceBase):
    """Schéma pour réponse ressource"""
    id: int
    village_id: int
    
    model_config = ConfigDict(from_attributes=True)


class ResourceAdd(BaseModel):
    """Schéma pour ajouter des ressources"""
    resource_type: ResourceType
    quantity: int = Field(..., gt=0)


class ResourceRemove(BaseModel):
    """Schéma pour retirer des ressources"""
    resource_type: ResourceType
    quantity: int = Field(..., gt=0)


class ResourceCost(BaseModel):
    """Schéma pour coût en ressources"""
    resources: Dict[ResourceType, int]


class ResourceInventory(BaseModel):
    """Schéma pour inventaire complet des ressources"""
    resources: Dict[str, int]
    warehouse_capacity: int
    warehouse_used: int
    warehouse_available: int
