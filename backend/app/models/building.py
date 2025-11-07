"""
Modèle Building - Types de bâtiments (données statiques).
"""

from sqlalchemy import String, Integer, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, Dict, Any

from backend.app.database import Base
from backend.app.utils.constants import BuildingCategory


class Building(Base):
    """Table des types de bâtiments (référentiel statique)"""
    __tablename__ = "buildings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(20), nullable=False)  # BuildingCategory enum
    
    # Coûts de construction (JSON)
    build_cost: Mapped[Dict[str, int]] = mapped_column(JSON, nullable=False)
    # Structure: {"wood": 100, "stone": 50, "metal": 20}
    
    # Production (JSON, optionnel pour bâtiments de production)
    production: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    # Structure:
    # {
    #   "resource": "water",
    #   "amount_per_hour": 10,
    #   "storage_capacity": 200
    # }
    
    # Bonus (JSON, optionnel)
    bonuses: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    # Structure:
    # {
    #   "moral_bonus": 5,
    #   "xp_bonus_percent": 10,
    #   "warehouse_capacity_bonus": 500
    # }
    
    # Automation (pour bâtiments d'automation)
    automation_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    # "auto_harvest", "auto_craft", "auto_research"
    
    # Prérequis (JSON)
    requirements: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    # Structure:
    # {
    #   "researches": ["agriculture_level_2"],
    #   "buildings": ["farm"]
    # }
    
    # Métadonnées
    max_instances: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    unlock_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    # Relations
    instances: Mapped[List["BuildingInstance"]] = relationship(
        "BuildingInstance",
        back_populates="building",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Building(id={self.id}, key='{self.key}', name='{self.name}')>"
