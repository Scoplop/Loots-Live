"""
Schémas Pydantic pour le chat IA.
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from backend.app.utils.constants import ChatType


class ChatMessageBase(BaseModel):
    """Schéma de base pour ChatMessage"""
    chat_type: ChatType
    message: str = Field(..., min_length=1, max_length=2000)


class ChatMessageCreate(ChatMessageBase):
    """Schéma pour créer un message de chat"""
    building_id: Optional[int] = None
    character_id: Optional[int] = None


class ChatMessageResponse(ChatMessageBase):
    """Schéma pour réponse message de chat"""
    id: int
    user_id: int
    village_id: int
    building_id: Optional[int] = None
    character_id: Optional[int] = None
    response: str
    is_user_message: bool
    relationship_delta: int
    sent_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ChatContext(BaseModel):
    """Schéma pour contexte du chat IA"""
    chat_type: ChatType
    village_name: str
    village_moral: int
    user_name: str
    
    # Contexte spécifique
    building_name: Optional[str] = None
    building_description: Optional[str] = None
    
    character_name: Optional[str] = None
    character_personality: Optional[str] = None
    character_biography: Optional[str] = None
    relationship_score: Optional[int] = None
    
    # Ressources (pour conseils)
    resources: Optional[dict] = None


class ChatResponse(BaseModel):
    """Schéma pour réponse IA"""
    message: str
    response: str
    relationship_delta: int
    context_used: str
