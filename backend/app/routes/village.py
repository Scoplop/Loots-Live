"""
Routes API pour la gestion des villages.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.utils.dependencies import get_current_active_user
from backend.app.models.user import User
from backend.app.schemas.village import (
    VillageCreate, 
    VillageResponse, 
    VillageUpdate, 
    VillageStats
)
from backend.app.schemas.resource import ResourceInventory, ResourceAdd, ResourceRemove
from backend.app.services.village_service import VillageService


router = APIRouter(prefix="/villages", tags=["Villages"])


@router.post("", response_model=VillageResponse, status_code=status.HTTP_201_CREATED)
async def create_village(
    village_data: VillageCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Crée un nouveau village pour l'utilisateur connecté
    
    Args:
        village_data: Données de création (nom du village)
        
    Returns:
        VillageResponse: Village créé avec ressources de départ
        
    Raises:
        HTTPException 400: Si l'utilisateur a déjà un village
    """
    service = VillageService(db)
    
    # Vérifier que l'utilisateur n'a pas déjà un village
    existing_village = await service.get_village_by_user_id(current_user.id)
    if existing_village:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous avez déjà un village"
        )
    
    village = await service.create_village(
        user_id=current_user.id,
        village_data=village_data
    )
    
    return village


@router.get("/me", response_model=VillageResponse, status_code=status.HTTP_200_OK)
async def get_my_village(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère le village de l'utilisateur connecté
    
    Returns:
        VillageResponse: Village de l'utilisateur
        
    Raises:
        HTTPException 404: Si l'utilisateur n'a pas de village
    """
    service = VillageService(db)
    village = await service.get_village_by_user_id(current_user.id)
    
    if not village:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vous n'avez pas encore créé de village"
        )
    
    return village


@router.get("/me/stats", response_model=VillageStats, status_code=status.HTTP_200_OK)
async def get_my_village_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère les statistiques du village de l'utilisateur
    
    Returns:
        VillageStats: Statistiques complètes (population, bâtiments, production)
        
    Raises:
        HTTPException 404: Si village non trouvé
    """
    service = VillageService(db)
    village = await service.get_village_by_user_id(current_user.id)
    
    if not village:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Village non trouvé"
        )
    
    stats = await service.get_village_stats(village.id)
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Statistiques non disponibles"
        )
    
    return stats


@router.put("/me", response_model=VillageResponse, status_code=status.HTTP_200_OK)
async def update_my_village(
    village_update: VillageUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Met à jour le nom du village de l'utilisateur
    
    Args:
        village_update: Nouvelles données (nom)
        
    Returns:
        VillageResponse: Village mis à jour
        
    Raises:
        HTTPException 404: Si village non trouvé
    """
    service = VillageService(db)
    village = await service.get_village_by_user_id(current_user.id)
    
    if not village:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Village non trouvé"
        )
    
    updated_village = await service.update_village_name(
        village_id=village.id,
        new_name=village_update.name
    )
    
    return updated_village


@router.get("/me/resources", response_model=ResourceInventory, status_code=status.HTTP_200_OK)
async def get_my_village_resources(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère les ressources du village de l'utilisateur
    
    Returns:
        ResourceInventory: Inventaire complet des ressources
        
    Raises:
        HTTPException 404: Si village ou ressources non trouvés
    """
    service = VillageService(db)
    village = await service.get_village_by_user_id(current_user.id)
    
    if not village:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Village non trouvé"
        )
    
    resources = await service.get_village_resources(village.id)
    
    if not resources:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ressources non trouvées"
        )
    
    return resources


@router.post("/me/resources/add", response_model=ResourceInventory, status_code=status.HTTP_200_OK)
async def add_resources_to_my_village(
    resource_add: ResourceAdd,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Ajoute des ressources au village (admin/debug)
    
    Args:
        resource_add: Ressources à ajouter {resource_name: quantity}
        
    Returns:
        ResourceInventory: Ressources mises à jour
        
    Raises:
        HTTPException 404: Si village non trouvé
    """
    service = VillageService(db)
    village = await service.get_village_by_user_id(current_user.id)
    
    if not village:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Village non trouvé"
        )
    
    resources = await service.update_resources(
        village_id=village.id,
        resource_deltas=resource_add.resources
    )
    
    return resources


@router.post("/me/resources/remove", response_model=ResourceInventory, status_code=status.HTTP_200_OK)
async def remove_resources_from_my_village(
    resource_remove: ResourceRemove,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retire des ressources du village
    
    Args:
        resource_remove: Ressources à retirer {resource_name: quantity}
        
    Returns:
        ResourceInventory: Ressources mises à jour
        
    Raises:
        HTTPException 400: Si ressources insuffisantes
        HTTPException 404: Si village non trouvé
    """
    service = VillageService(db)
    village = await service.get_village_by_user_id(current_user.id)
    
    if not village:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Village non trouvé"
        )
    
    # Inverser les quantités pour retirer
    resource_deltas = {k: -v for k, v in resource_remove.resources.items()}
    
    try:
        resources = await service.update_resources(
            village_id=village.id,
            resource_deltas=resource_deltas
        )
        return resources
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me/storage", response_model=dict, status_code=status.HTTP_200_OK)
async def check_my_village_storage(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Vérifie la capacité de stockage du village
    
    Returns:
        dict: Capacité max, ressources au max, ressources critiques
        
    Raises:
        HTTPException 404: Si village non trouvé
    """
    service = VillageService(db)
    village = await service.get_village_by_user_id(current_user.id)
    
    if not village:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Village non trouvé"
        )
    
    storage_info = await service.check_storage_capacity(village.id)
    
    return storage_info


@router.get("/{village_id}", response_model=VillageResponse, status_code=status.HTTP_200_OK)
async def get_village_by_id(
    village_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère un village par son ID (public, pour voir les autres villages)
    
    Args:
        village_id: Identifiant du village
        
    Returns:
        VillageResponse: Informations du village
        
    Raises:
        HTTPException 404: Si village non trouvé
    """
    service = VillageService(db)
    village = await service.get_village_by_id(village_id)
    
    if not village:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Village non trouvé"
        )
    
    return village
