"""
Schémas Pydantic pour les relations entre PNJ.
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Any


class RelationshipBase(BaseModel):
    """Schéma de base pour Relationship"""
    character_id: int
    target_character_id: int
    score: int = Field(default=0, ge=-100, le=100)


class RelationshipCreate(RelationshipBase):
    """Schéma pour créer une relation"""
    pass


class RelationshipResponse(RelationshipBase):
    """Schéma pour réponse relation"""
    id: int
    village_id: int
    last_updated: datetime
    
    model_config = ConfigDict(from_attributes=True)


class RelationshipUpdate(BaseModel):
    """Schéma pour mise à jour relation"""
    delta: int = Field(..., ge=-100, le=100)
    reason: str = Field(..., max_length=50)
    reason_details: str = Field(..., max_length=500)


class RelationshipHistoryResponse(BaseModel):
    """Schéma pour historique de relation"""
    id: int
    relationship_id: int
    old_score: int
    new_score: int
    delta: int
    reason: str
    reason_details: str
    changed_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class RelationshipGraph(BaseModel):
    """Schéma pour graphe de relations (visualisation)"""
    character_id: int
    character_name: str
    relationships: list[dict[str, Any]]
    # Structure:
    # [
    #   {"target_id": 2, "target_name": "Bob", "score": 50, "status": "ami"},
    #   {"target_id": 3, "target_name": "Alice", "score": -30, "status": "tendu"}
    # ]
