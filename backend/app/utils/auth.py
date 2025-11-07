"""
Utilitaires pour l'authentification JWT et gestion des mots de passe.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

from backend.app.config import settings


# Configuration du hashage de mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie qu'un mot de passe correspond au hash.
    
    Args:
        plain_password: Mot de passe en clair
        hashed_password: Hash du mot de passe
    
    Returns:
        True si le mot de passe correspond, False sinon
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash un mot de passe avec bcrypt.
    
    Args:
        password: Mot de passe en clair
    
    Returns:
        Hash du mot de passe
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crée un token JWT.
    
    Args:
        data: Données à encoder dans le token (user_id, username, etc.)
        expires_delta: Durée de validité du token (défaut: 30 jours)
    
    Returns:
        Token JWT signé
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Décode un token JWT.
    
    Args:
        token: Token JWT à décoder
    
    Returns:
        Données contenues dans le token, ou None si invalide
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_token(token: str) -> Optional[dict]:
    """
    Vérifie la validité d'un token JWT.
    
    Args:
        token: Token JWT à vérifier
    
    Returns:
        Données du token si valide, None sinon
    """
    payload = decode_access_token(token)
    
    if payload is None:
        return None
    
    # Vérifier la présence des données requises
    user_id: Optional[int] = payload.get("user_id")
    username: Optional[str] = payload.get("username")
    
    if user_id is None or username is None:
        return None
    
    return payload
