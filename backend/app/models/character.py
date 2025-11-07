"""
Modèle Character - PNJ joueur et IA.
"""

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, Dict, Any

from backend.app.database import Base
from backend.app.utils.constants import CharacterClass, Personality, Sex


class Character(Base):
    """Table des personnages (PNJ joueur + IA du village)"""
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    village_id: Mapped[int] = mapped_column(Integer, ForeignKey("villages.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Informations de base
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    biography: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_player_character: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Classe et personnalité
    character_class: Mapped[str] = mapped_column(String(20), nullable=False)  # CharacterClass enum
    personality: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # Personality enum (IA seulement)
    sex: Mapped[str] = mapped_column(String(20), nullable=False)  # Sex enum
    
    # Système de niveau
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    free_stat_points: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    
    # Stats de combat
    strength: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    dexterity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    endurance: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    intelligence: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    speed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    luck: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # HP et état
    current_hp: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    max_hp: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    is_on_mission: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Apparence (JSON stockant toutes les options)
    appearance: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    # Structure:
    # {
    #   "hair_color": "#000000",
    #   "hair_style": "short",
    #   "skin_tone": "#FFDBAC",
    #   "eye_color": "#8B4513",
    #   "facial_hair": "none",
    #   "accessories": ["glasses", "earrings"],
    #   "scars": ["face_scar"],
    #   "tattoos": []
    # }
    
    # Équipement (JSON stockant les slots)
    equipment: Mapped[Optional[Dict[str, int]]] = mapped_column(JSON, nullable=True)
    # Structure:
    # {
    #   "head": 123,  # equipment_id
    #   "torso": 456,
    #   "weapon_1": 789,
    #   ...
    # }
    
    # Dates
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relations
    user: Mapped["User"] = relationship("User", back_populates="characters")
    village: Mapped["Village"] = relationship("Village", back_populates="characters")
    mission_participations: Mapped[List["MissionParticipant"]] = relationship(
        "MissionParticipant",
        back_populates="character",
        cascade="all, delete-orphan",
        lazy="select"
    )
    relationships_as_source: Mapped[List["Relationship"]] = relationship(
        "Relationship",
        foreign_keys="[Relationship.character_id]",
        back_populates="character",
        cascade="all, delete-orphan",
        lazy="select"
    )
    relationships_as_target: Mapped[List["Relationship"]] = relationship(
        "Relationship",
        foreign_keys="[Relationship.target_character_id]",
        back_populates="target_character",
        cascade="all, delete-orphan",
        lazy="select"
    )
    chat_messages: Mapped[List["ChatMessage"]] = relationship(
        "ChatMessage",
        foreign_keys="[ChatMessage.character_id]",
        back_populates="character",
        cascade="all, delete-orphan",
        lazy="select"
    )
    squad_memberships: Mapped[List["SquadMember"]] = relationship(
        "SquadMember",
        back_populates="character",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self) -> str:
        char_type = "PC" if self.is_player_character else "NPC"
        return f"<Character(id={self.id}, name='{self.name}', type={char_type}, level={self.level})>"
