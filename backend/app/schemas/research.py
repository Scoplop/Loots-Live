"""
Schémas Pydantic pour les recherches (arbre technologique).
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from backend.app.utils.constants import ResearchCategory, ResearchStatus


# ============================================================================
# SCHEMAS DE BASE
# ============================================================================

class ResearchBase(BaseModel):
    """Schéma de base pour une recherche."""
    research_key: str = Field(..., description="Clé unique de la recherche")
    category: ResearchCategory = Field(..., description="Catégorie de recherche")


class ResearchCreate(ResearchBase):
    """Schéma pour créer une recherche (usage interne)."""
    village_id: UUID


class ResearchRead(ResearchBase):
    """Schéma de lecture d'une recherche."""
    id: UUID
    village_id: UUID
    status: ResearchStatus
    progress: int = Field(..., ge=0, le=100, description="Progression en %")
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    model_config = {
        "from_attributes": True
    }


# ============================================================================
# SCHEMAS DÉTAILLÉS
# ============================================================================

class ResearchDetails(ResearchRead):
    """Schéma détaillé avec toutes les informations depuis RESEARCH_TREE."""
    name: str = Field(..., description="Nom de la recherche")
    description: str = Field(..., description="Description de la recherche")
    prerequisites: List[str] = Field(default_factory=list, description="Prérequis (research_keys)")
    costs: Dict[str, int] = Field(default_factory=dict, description="Coûts en ressources")
    duration_hours: int = Field(..., ge=1, description="Durée en heures")
    effects: Dict[str, Any] = Field(default_factory=dict, description="Effets de la recherche")


class ResearchTree(BaseModel):
    """Arbre technologique complet organisé par catégories."""
    agriculture: List[ResearchDetails] = Field(default_factory=list)
    military: List[ResearchDetails] = Field(default_factory=list)
    economy: List[ResearchDetails] = Field(default_factory=list)
    science: List[ResearchDetails] = Field(default_factory=list)


class ResearchBonuses(BaseModel):
    """Bonus actifs des recherches complétées."""
    production_multiplier: float = Field(default=1.0, description="Multiplicateur de production")
    mission_success_bonus: int = Field(default=0, description="Bonus % taux de succès missions")
    construction_speed: float = Field(default=1.0, description="Vitesse de construction")
    research_speed: float = Field(default=1.0, description="Vitesse de recherche")
    unlocked_buildings: List[str] = Field(default_factory=list, description="Bâtiments débloqués")
    unlocked_equipment: List[str] = Field(default_factory=list, description="Équipements débloqués")
    special_abilities: List[str] = Field(default_factory=list, description="Capacités spéciales")
