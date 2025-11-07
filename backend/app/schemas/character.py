"""
Schémas Pydantic pour les personnages (PNJ).
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any, List
from backend.app.utils.constants import CharacterClass, Personality, Sex


class CharacterBase(BaseModel):
    """Schéma de base pour Character"""
    name: str = Field(..., min_length=1, max_length=50)
    biography: Optional[str] = Field(None, max_length=500)
    character_class: CharacterClass
    sex: Sex


class CharacterCreate(CharacterBase):
    """Schéma pour créer un personnage (PNJ joueur)"""
    is_player_character: bool = True
    # Stats allouées (max 10 points libres au total + bonus de classe)
    strength: int = Field(default=0, ge=0, le=50)
    dexterity: int = Field(default=0, ge=0, le=50)
    endurance: int = Field(default=0, ge=0, le=50)
    intelligence: int = Field(default=0, ge=0, le=50)
    speed: int = Field(default=0, ge=0, le=50)
    luck: int = Field(default=0, ge=0, le=50)
    appearance: Optional[Dict[str, Any]] = None


class CharacterCreateAI(BaseModel):
    """Schéma pour créer un PNJ IA"""
    name: str = Field(..., min_length=1, max_length=50)
    biography: Optional[str] = Field(None, max_length=500)
    character_class: CharacterClass
    personality: Personality
    sex: Sex
    appearance: Optional[Dict[str, Any]] = None


class CharacterResponse(CharacterBase):
    """Schéma pour réponse personnage"""
    id: int
    user_id: int
    village_id: int
    is_player_character: bool
    personality: Optional[Personality] = None
    
    # Niveau et XP
    level: int
    xp: int
    free_stat_points: int
    
    # Stats
    strength: int
    dexterity: int
    endurance: int
    intelligence: int
    speed: int
    luck: int
    
    # HP
    current_hp: int
    max_hp: int
    is_on_mission: bool
    
    # Apparence et équipement
    appearance: Optional[Dict[str, Any]] = None
    equipment: Optional[Dict[str, int]] = None
    
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CharacterUpdate(BaseModel):
    """Schéma pour mise à jour personnage"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    biography: Optional[str] = Field(None, max_length=500)
    appearance: Optional[Dict[str, Any]] = None


class CharacterAllocateStats(BaseModel):
    """Schéma pour allouer des points de stats"""
    strength: int = Field(default=0, ge=0)
    dexterity: int = Field(default=0, ge=0)
    endurance: int = Field(default=0, ge=0)
    intelligence: int = Field(default=0, ge=0)
    speed: int = Field(default=0, ge=0)
    luck: int = Field(default=0, ge=0)


class CharacterEquip(BaseModel):
    """Schéma pour équiper un objet"""
    equipment_id: int
    slot: str  # EquipmentSlot


class CharacterStats(BaseModel):
    """Schéma pour statistiques complètes d'un personnage"""
    # Stats de base
    strength: int
    dexterity: int
    endurance: int
    intelligence: int
    speed: int
    luck: int
    
    # Stats calculées avec équipement
    total_strength: int
    total_dexterity: int
    total_endurance: int
    total_intelligence: int
    total_speed: int
    total_luck: int
    total_armor: int
    total_damage: int
    
    # HP
    current_hp: int
    max_hp: int
    
    # Niveau
    level: int
    xp: int
    xp_to_next_level: int
    
    # Bonus de classe
    class_bonus: str
