"""
Modèle Equipment - Équipements collectables.
"""

from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from typing import Dict, Any

from backend.app.database import Base
from backend.app.utils.constants import EquipmentRarity, EquipmentSlot


class Equipment(Base):
    """Table des équipements (objets individuels)"""
    __tablename__ = "equipment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    character_id: Mapped[int] = mapped_column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Informations de base
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    slot: Mapped[str] = mapped_column(String(20), nullable=False)  # EquipmentSlot enum
    rarity: Mapped[str] = mapped_column(String(20), nullable=False)  # EquipmentRarity enum
    
    # Stats (JSON)
    stats: Mapped[Dict[str, int]] = mapped_column(JSON, nullable=False)
    # Structure:
    # {
    #   "strength": 5,
    #   "dexterity": 3,
    #   "endurance": 2,
    #   "intelligence": 0,
    #   "speed": 1,
    #   "luck": 0,
    #   "armor": 10,
    #   "damage": 15
    # }
    
    # Sprite/icône
    sprite_key: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Dates
    obtained_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Equipment(id={self.id}, name='{self.name}', rarity='{self.rarity}', slot='{self.slot}')>"
