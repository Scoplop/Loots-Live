"""
Modèle Research - Recherches technologiques.
"""

from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, Dict, Any

from backend.app.database import Base
from backend.app.utils.constants import ResearchStatus


class Research(Base):
    """Table des recherches (arbre technologique)"""
    __tablename__ = "researches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    village_id: Mapped[int] = mapped_column(Integer, ForeignKey("villages.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Informations de base
    key: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # Identifiant unique de la recherche
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=ResearchStatus.LOCKED.value, nullable=False)  # ResearchStatus enum
    
    # Coût et durée
    cost: Mapped[Dict[str, int]] = mapped_column(JSON, nullable=False)
    # Structure: {"knowledge_points": 100, "gold": 500}
    
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Bonus débloqués (JSON)
    bonuses: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    # Structure:
    # {
    #   "buildings_unlocked": ["advanced_farm"],
    #   "production_bonus_percent": 10,
    #   "warehouse_capacity_bonus": 500
    # }
    
    # Progression
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Temps écoulé en minutes
    
    # Dates
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relations
    village: Mapped["Village"] = relationship("Village", back_populates="researches")

    def __repr__(self) -> str:
        return f"<Research(id={self.id}, key='{self.key}', status='{self.status}', village_id={self.village_id})>"
