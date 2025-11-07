"""
Dépendances FastAPI pour l'authentification et les sessions.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.utils.auth import verify_token


# Schéma de sécurité Bearer Token
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dépendance FastAPI pour obtenir l'utilisateur courant depuis le token JWT.
    
    Args:
        credentials: Token d'authentification (Bearer)
        db: Session de base de données
    
    Returns:
        User: Utilisateur authentifié
    
    Raises:
        HTTPException: Si le token est invalide ou l'utilisateur n'existe pas
    """
    token = credentials.credentials
    
    # Vérifier et décoder le token
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: Optional[int] = payload.get("user_id")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Récupérer l'utilisateur depuis la base de données
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur introuvable",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dépendance pour vérifier que l'utilisateur est actif.
    Peut être étendu pour gérer des utilisateurs bannis/désactivés.
    
    Args:
        current_user: Utilisateur courant
    
    Returns:
        User: Utilisateur actif
    """
    # Pour l'instant, tous les utilisateurs sont actifs
    # On peut ajouter un champ `is_active` dans le modèle User plus tard
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Dépendance pour obtenir l'utilisateur courant si authentifié, None sinon.
    Utile pour les endpoints publics avec fonctionnalités optionnelles pour utilisateurs connectés.
    
    Args:
        credentials: Token d'authentification (optionnel)
        db: Session de base de données
    
    Returns:
        Optional[User]: Utilisateur si authentifié, None sinon
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
