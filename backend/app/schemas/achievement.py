"""
Schémas Pydantic pour les succès (achievements).
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class AchievementBase(BaseModel):
    """Schéma de base pour Achievement"""
    key: str = Field(..., max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., max_length=500)


class AchievementCreate(AchievementBase):
    """Schéma pour créer un succès"""
    reward_xp: int = Field(default=0, ge=0)


class AchievementResponse(AchievementBase):
    """Schéma pour réponse succès"""
    id: int
    village_id: int
    reward_xp: int
    unlocked_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AchievementUnlock(BaseModel):
    """Schéma pour débloquer un succès"""
    achievement_key: str
    reward_xp: int
