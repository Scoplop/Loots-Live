"""
Modèle Event - Événements aléatoires du village.
"""

from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Dict, Any

from backend.app.database import Base
from backend.app.utils.constants import EventType


class Event(Base):
    """Table des événements aléatoires"""
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    village_id: Mapped[int] = mapped_column(Integer, ForeignKey("villages.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Informations de base
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    event_type: Mapped[str] = mapped_column(String(20), nullable=False)  # EventType enum
    
    # Effets (JSON)
    effects: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    # Structure:
    # {
    #   "resources_gained": {"water": 100, "food": 50},
    #   "resources_lost": {"wood": 20},
    #   "moral_change": +5,
    #   "xp_gained": 50,
    #   "relationships_affected": [
    #     {"character_id": 1, "target_id": 2, "delta": +10}
    #   ]
    # }
    
    # Date
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relations
    village: Mapped["Village"] = relationship("Village", back_populates="events")

    def __repr__(self) -> str:
        return f"<Event(id={self.id}, title='{self.title}', type='{self.event_type}', village_id={self.village_id})>"
