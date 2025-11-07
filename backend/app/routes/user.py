"""
Routes API pour la gestion des utilisateurs.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.utils.dependencies import get_current_active_user, get_current_user
from backend.app.models.user import User
from backend.app.schemas.user import UserResponse, UserUpdate
from backend.app.services.user_service import UserService


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Récupère le profil de l'utilisateur connecté
    
    Returns:
        UserResponse: Profil de l'utilisateur
    """
    return current_user


@router.put("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Met à jour le profil de l'utilisateur connecté
    
    Args:
        user_update: Données de mise à jour
        
    Returns:
        UserResponse: Profil mis à jour
        
    Raises:
        HTTPException 400: Si username ou email déjà utilisé
        HTTPException 404: Si utilisateur non trouvé
    """
    service = UserService(db)
    
    try:
        updated_user = await service.update_user_profile(
            user_id=current_user.id,
            user_update=user_update
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        return updated_user
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user_account(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Supprime le compte de l'utilisateur connecté
    
    Note: Suppression définitive (RGPD). Toutes les données associées sont perdues.
    
    Returns:
        204 No Content
    """
    service = UserService(db)
    
    deleted = await service.delete_user(current_user.id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    return None


@router.get("/{user_id}/profile", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user_public_profile(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)  # Authentification requise
):
    """
    Récupère le profil public d'un utilisateur
    
    Args:
        user_id: Identifiant de l'utilisateur
        
    Returns:
        UserResponse: Profil public (email masqué)
        
    Raises:
        HTTPException 404: Si utilisateur non trouvé
    """
    service = UserService(db)
    user = await service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    return user


@router.get("/me/stats", response_model=dict, status_code=status.HTTP_200_OK)
async def get_current_user_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère les statistiques détaillées de l'utilisateur connecté
    
    Returns:
        dict: Statistiques (compte, village, progression)
    """
    service = UserService(db)
    stats = await service.get_user_stats(current_user.id)
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Statistiques non disponibles"
        )
    
    return stats
