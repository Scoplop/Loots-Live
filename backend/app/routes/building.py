"""
Routes API pour la gestion des bâtiments.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.user import User
from backend.app.schemas.building import (
    BuildingResponse,
    BuildingInstanceResponse,
    BuildingInstanceWithDetails,
    BuildingBuild
)
from backend.app.services.building_service import BuildingService
from backend.app.utils.dependencies import get_current_active_user


router = APIRouter(prefix="/buildings", tags=["buildings"])


@router.get("/catalog", response_model=List[BuildingResponse])
async def get_building_catalog(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère le catalogue complet des types de bâtiments disponibles.
    
    Affiche:
    - Nom, description, catégorie
    - Coût de construction
    - Production (si bâtiment de production)
    - Bonus (moral, stockage, XP, etc.)
    - Prérequis (recherches, bâtiments)
    - Nombre max d'instances
    - Niveau requis
    """
    service = BuildingService(db)
    buildings = await service.get_all_buildings()
    return buildings


@router.get("/catalog/{building_key}", response_model=BuildingResponse)
async def get_building_details(
    building_key: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère les détails d'un type de bâtiment spécifique.
    
    - **building_key**: Identifiant unique du bâtiment (ex: "warehouse", "well", "farm")
    """
    service = BuildingService(db)
    building = await service.get_building_by_key(building_key)
    
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bâtiment '{building_key}' non trouvé"
        )
    
    return building


@router.get("/", response_model=List[BuildingInstanceResponse])
async def get_my_buildings(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère toutes les instances de bâtiments de mon village.
    
    Retourne la liste des bâtiments construits avec:
    - Position (grid_x, grid_y)
    - Niveau actuel
    - État actif/inactif
    - Date de construction
    """
    service = BuildingService(db)
    instances = await service.get_village_buildings(current_user.id)
    return instances


@router.get("/{instance_id}", response_model=BuildingInstanceResponse)
async def get_building_instance(
    instance_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère les détails d'une instance de bâtiment spécifique.
    
    - **instance_id**: ID de l'instance construite
    """
    service = BuildingService(db)
    instance = await service.get_building_instance(instance_id, current_user.id)
    
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instance de bâtiment non trouvée"
        )
    
    return instance


@router.post("/build", response_model=BuildingInstanceResponse, status_code=status.HTTP_201_CREATED)
async def build_building(
    build_data: BuildingBuild,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Construit un nouveau bâtiment dans le village.
    
    - **building_key**: Type de bâtiment à construire (voir /catalog)
    - **grid_x, grid_y**: Position sur la grille (0-100)
      - Si (-1, -1): placement automatique en spirale depuis le centre
    
    Vérifie:
    - Ressources suffisantes
    - Prérequis (recherches, bâtiments)
    - Nombre max d'instances
    - Position non occupée
    
    Consomme les ressources nécessaires.
    """
    service = BuildingService(db)
    instance = await service.build_building(current_user.id, build_data)
    return instance


@router.post("/{instance_id}/upgrade", response_model=BuildingInstanceResponse)
async def upgrade_building(
    instance_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Améliore un bâtiment (niveau 1 à 5 max).
    
    - **instance_id**: ID de l'instance à améliorer
    
    Coût d'amélioration: Coût de base × Niveau actuel × 1.5
    
    Avantages:
    - Production augmentée (×niveau)
    - Stockage augmenté (×niveau)
    - Bonus renforcés
    """
    service = BuildingService(db)
    instance = await service.upgrade_building(instance_id, current_user.id)
    return instance


@router.delete("/{instance_id}", status_code=status.HTTP_200_OK)
async def destroy_building(
    instance_id: int,
    refund_percent: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Détruit un bâtiment et rembourse une partie des ressources.
    
    - **instance_id**: ID de l'instance à détruire
    - **refund_percent**: Pourcentage de remboursement (défaut: 50%)
    
    Rembourse un pourcentage du coût total (construction + améliorations).
    """
    service = BuildingService(db)
    await service.destroy_building(instance_id, current_user.id, refund_percent)
    
    return {
        "message": "Bâtiment détruit avec succès",
        "refund_percent": refund_percent
    }


@router.post("/{instance_id}/toggle", response_model=BuildingInstanceResponse)
async def toggle_building_active(
    instance_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Active/désactive un bâtiment.
    
    - **instance_id**: ID de l'instance
    
    Bâtiment désactivé:
    - Ne produit plus de ressources
    - Économise des ressources si le bâtiment en consomme
    - Reste sur la grille
    """
    service = BuildingService(db)
    instance = await service.toggle_building_active(instance_id, current_user.id)
    
    status_text = "activé" if instance.is_active else "désactivé"
    return instance


@router.get("/{instance_id}/production", response_model=dict)
async def get_building_production(
    instance_id: int,
    assigned_npcs: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calcule le taux de production actuel d'un bâtiment.
    
    - **instance_id**: ID de l'instance
    - **assigned_npcs**: Nombre de PNJ assignés (optionnel)
    
    Formule:
    Production = Base × Niveau × (1 + 0.1 × nb_PNJ)
    
    Retourne:
    - Ressource produite
    - Quantité par heure
    - Capacité de stockage
    - Multiplicateurs appliqués
    """
    service = BuildingService(db)
    
    # Vérifier que l'instance existe et appartient à l'utilisateur
    instance = await service.get_building_instance(instance_id, current_user.id)
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instance non trouvée"
        )
    
    production_data = await service.calculate_production_rate(instance_id, assigned_npcs)
    return production_data
