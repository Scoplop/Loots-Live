"""
Schémas Pydantic pour les recherches.
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any
from backend.app.utils.constants import ResearchStatus


class ResearchBase(BaseModel):
    """Schéma de base pour Research"""
    key: str = Field(..., max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., max_length=500)


class ResearchCreate(ResearchBase):
    """Schéma pour créer une recherche"""
    cost: Dict[str, int]
    duration_minutes: int = Field(..., ge=5)
    bonuses: Optional[Dict[str, Any]] = None


class ResearchResponse(ResearchBase):
    """Schéma pour réponse recherche"""
    id: int
    village_id: int
    status: ResearchStatus
    cost: Dict[str, int]
    duration_minutes: int
    bonuses: Optional[Dict[str, Any]] = None
    progress: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class ResearchStart(BaseModel):
    """Schéma pour lancer une recherche"""
    research_key: str


class ResearchProgress(BaseModel):
    """Schéma pour progression d'une recherche"""
    research_id: int
    progress: int
    progress_percent: float
    time_remaining_minutes: int
