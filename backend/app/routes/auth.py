"""
Routes d'authentification - Inscription et connexion.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from backend.app.services.auth_service import AuthService
from backend.app.utils.dependencies import get_current_user
from backend.app.models.user import User


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Inscription d'un nouvel utilisateur.
    
    - **username**: 3-20 caractères, alphanumériques et - _ uniquement
    - **password**: minimum 8 caractères
    - **email**: optionnel, doit être un email valide
    
    Retourne l'utilisateur créé (sans le mot de passe).
    """
    user = await AuthService.register_user(db, user_data)
    return user


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Connexion d'un utilisateur existant.
    
    - **username**: Nom d'utilisateur
    - **password**: Mot de passe
    
    Retourne un token JWT d'accès valide 30 jours.
    """
    token = await AuthService.login(db, login_data)
    return token


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Récupère les informations de l'utilisateur connecté.
    
    Nécessite un token d'authentification valide dans le header:
    `Authorization: Bearer <token>`
    """
    return current_user


@router.post("/logout")
async def logout():
    """
    Déconnexion (côté client uniquement).
    
    Le token JWT étant stateless, la déconnexion se fait côté client
    en supprimant le token du stockage local.
    
    Cette route existe pour la cohérence de l'API.
    """
    return {"message": "Déconnexion réussie. Supprimez le token côté client."}
