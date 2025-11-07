"""
Schémas Pydantic pour les événements.
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Any, Optional
from backend.app.utils.constants import EventType


class EventBase(BaseModel):
    """Schéma de base pour Event"""
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., max_length=500)
    event_type: EventType


class EventCreate(EventBase):
    """Schéma pour créer un événement"""
    effects: dict[str, Any]


class EventResponse(EventBase):
    """Schéma pour réponse événement"""
    id: int
    village_id: int
    effects: dict[str, Any]
    occurred_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class EventTrigger(BaseModel):
    """Schéma pour déclencher un événement aléatoire"""
    force_type: Optional[EventType] = None
