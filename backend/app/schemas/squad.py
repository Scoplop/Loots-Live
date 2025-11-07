"""
Schémas Pydantic pour les squads (équipes).
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List


class SquadBase(BaseModel):
    """Schéma de base pour Squad"""
    name: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., max_length=500)


class SquadCreate(SquadBase):
    """Schéma pour créer une squad"""
    member_ids: List[int] = Field(..., min_items=1, max_items=10)


class SquadResponse(SquadBase):
    """Schéma pour réponse squad"""
    id: int
    village_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class SquadMemberResponse(BaseModel):
    """Schéma pour membre de squad"""
    id: int
    squad_id: int
    character_id: int
    role: str
    
    model_config = ConfigDict(from_attributes=True)


class SquadWithMembers(SquadResponse):
    """Schéma pour squad avec membres"""
    members: List[SquadMemberResponse]


class SquadAddMember(BaseModel):
    """Schéma pour ajouter un membre"""
    character_id: int
    role: str = Field(default="member")


class SquadRemoveMember(BaseModel):
    """Schéma pour retirer un membre"""
    character_id: int
