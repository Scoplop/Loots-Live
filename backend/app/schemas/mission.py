"""
Schémas Pydantic pour les missions.
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any, List
from backend.app.utils.constants import MissionType, MissionStatus


class MissionBase(BaseModel):
    """Schéma de base pour Mission"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., max_length=500)
    mission_type: MissionType
    difficulty: int = Field(..., ge=1, le=10)
    duration_minutes: int = Field(..., ge=5, le=1440)


class MissionCreate(MissionBase):
    """Schéma pour créer une mission"""
    rewards: Dict[str, Any]
    participant_ids: List[int] = Field(..., min_items=1, max_items=5)


class MissionResponse(MissionBase):
    """Schéma pour réponse mission"""
    id: int
    village_id: int
    status: MissionStatus
    rewards: Dict[str, Any]
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class MissionWithParticipants(MissionResponse):
    """Schéma pour mission avec participants"""
    participants: List[int]  # Liste des character_ids


class MissionStart(BaseModel):
    """Schéma pour lancer une mission"""
    mission_id: int


class MissionRecall(BaseModel):
    """Schéma pour rappeler une mission"""
    mission_id: int


class MissionComplete(BaseModel):
    """Schéma pour résultat de mission"""
    mission_id: int
    success: bool
    rewards_obtained: Dict[str, Any]
    casualties: List[int]  # character_ids blessés/morts
    xp_gained: int
