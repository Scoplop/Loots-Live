"""
Modèle ChatMessage - Messages de chat IA.
"""

from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from backend.app.database import Base
from backend.app.utils.constants import ChatType


class ChatMessage(Base):
    """Table des messages de chat (IA contextuelle)"""
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    village_id: Mapped[int] = mapped_column(Integer, ForeignKey("villages.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Contexte du chat
    chat_type: Mapped[str] = mapped_column(String(20), nullable=False)  # ChatType enum
    building_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("building_instances.id", ondelete="CASCADE"), nullable=True, index=True)
    character_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Message
    message: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Métadonnées
    is_user_message: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Impact sur la relation (si chat avec PNJ)
    relationship_delta: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Date
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relations
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="chat_messages"
    )
    village: Mapped["Village"] = relationship(
        "Village",
        foreign_keys=[village_id],
        back_populates="chat_messages"
    )
    building: Mapped[Optional["BuildingInstance"]] = relationship(
        "BuildingInstance",
        foreign_keys=[building_id],
        back_populates="chat_messages"
    )
    character: Mapped[Optional["Character"]] = relationship(
        "Character",
        foreign_keys=[character_id],
        back_populates="chat_messages"
    )

    def __repr__(self) -> str:
        return f"<ChatMessage(id={self.id}, type='{self.chat_type}', user_id={self.user_id})>"
