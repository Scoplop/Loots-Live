"""
Modèle RelationshipHistory - Historique des modifications de relations.
"""

from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class RelationshipHistory(Base):
    """Table d'historique des changements de relations"""
    __tablename__ = "relationship_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    relationship_id: Mapped[int] = mapped_column(Integer, ForeignKey("relationships.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Changement
    old_score: Mapped[int] = mapped_column(Integer, nullable=False)
    new_score: Mapped[int] = mapped_column(Integer, nullable=False)
    delta: Mapped[int] = mapped_column(Integer, nullable=False)  # Calculé: new_score - old_score
    
    # Raison
    reason: Mapped[str] = mapped_column(String(50), nullable=False)
    # "chat_positive", "chat_negative", "mission_success", "mission_failure", "event", "compatibility"
    
    reason_details: Mapped[str] = mapped_column(Text, nullable=False)
    # Description lisible de la raison
    
    # Date
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relations
    relationship: Mapped["Relationship"] = relationship("Relationship", back_populates="history")

    def __repr__(self) -> str:
        return f"<RelationshipHistory(relationship_id={self.relationship_id}, delta={self.delta}, reason='{self.reason}')>"
