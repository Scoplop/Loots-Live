"""
Schémas Pydantic pour les utilisateurs.
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """Schéma de base pour User"""
    username: str = Field(..., min_length=3, max_length=20, pattern="^[a-zA-Z0-9_-]+$")
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    """Schéma pour créer un utilisateur"""
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    """Schéma pour connexion"""
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=8, max_length=100)


class UserResponse(UserBase):
    """Schéma pour réponse utilisateur"""
    id: int
    created_at: datetime
    last_login: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Schéma pour mise à jour utilisateur"""
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)


class Token(BaseModel):
    """Schéma pour token JWT"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schéma pour données dans le token"""
    user_id: Optional[int] = None
    username: Optional[str] = None
