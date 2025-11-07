"""
Service métier pour la gestion des villages.
Gère la création, les ressources, la production et les statistiques des villages.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.village import Village
from backend.app.models.resource import Resource
from backend.app.models.building_instance import BuildingInstance
from backend.app.models.character import Character
from backend.app.schemas.village import VillageCreate, VillageStats


class VillageService:
    """Service pour la gestion des villages"""
    
    def __init__(self, db: AsyncSession):
        """
        Initialise le service village
        
        Args:
            db: Session de base de données asynchrone
        """
        self.db = db
    
    async def create_village(
        self, 
        user_id: int, 
        village_data: VillageCreate
    ) -> Village:
        """
        Crée un nouveau village pour un utilisateur
        
        Args:
            user_id: ID de l'utilisateur propriétaire
            village_data: Données de création du village
            
        Returns:
            Village créé avec ressources de départ
            
        Note:
            - Création automatique des ressources de départ
            - Capacité stockage initiale : 1000 par ressource
            - Ressources de départ : 200 Eau, 150 Bois, 100 Pierre, 50 Nourriture
        """
        # Créer le village
        village = Village(
            user_id=user_id,
            name=village_data.name,
            level=1,
            prestige_cycle=0
        )
        
        self.db.add(village)
        await self.db.flush()  # Pour obtenir l'ID du village
        
        # Ressources de départ (conformément au projet)
        initial_resources = {
            "water": 200,      # Eau
            "wood": 150,       # Bois
            "stone": 100,      # Pierre
            "food": 50,        # Nourriture
            "wheat": 0,
            "meat": 0,
            "fabric": 0,
            "leather": 0,
            "herbs": 0,
            "books": 0,
            "money": 100,      # Argent de départ
            "seeds": 20,
            "tools": 5,
            "cotton": 0,
            "linen": 0,
            "paper": 0,
            "ink": 0,
            "rare_ore": 0,
            "knowledge_points": 0,
            "survival_kits": 0
        }
        
        # Créer l'entrée Resource
        resource = Resource(
            village_id=village.id,
            **initial_resources,
            max_capacity=1000  # Capacité de base sans Entrepôt
        )
        
        self.db.add(resource)
        await self.db.commit()
        await self.db.refresh(village)
        
        return village
    
    async def get_village_by_id(self, village_id: int) -> Optional[Village]:
        """
        Récupère un village par son ID
        
        Args:
            village_id: Identifiant du village
            
        Returns:
            Village si trouvé, None sinon
        """
        result = await self.db.execute(
            select(Village).where(Village.id == village_id)
        )
        return result.scalar_one_or_none()
    
    async def get_village_by_user_id(self, user_id: int) -> Optional[Village]:
        """
        Récupère le village d'un utilisateur
        
        Args:
            user_id: Identifiant de l'utilisateur
            
        Returns:
            Village si trouvé, None sinon
        """
        result = await self.db.execute(
            select(Village).where(Village.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_village_resources(self, village_id: int) -> Optional[Resource]:
        """
        Récupère les ressources d'un village
        
        Args:
            village_id: Identifiant du village
            
        Returns:
            Resource si trouvé, None sinon
        """
        result = await self.db.execute(
            select(Resource).where(Resource.village_id == village_id)
        )
        return result.scalar_one_or_none()
    
    async def update_resources(
        self, 
        village_id: int, 
        resource_deltas: Dict[str, int]
    ) -> Optional[Resource]:
        """
        Met à jour les ressources d'un village (ajout/retrait)
        
        Args:
            village_id: Identifiant du village
            resource_deltas: Dictionnaire {resource_name: delta_quantity}
                            delta positif = ajout, négatif = retrait
            
        Returns:
            Resource mis à jour, None si village non trouvé
            
        Raises:
            ValueError: Si ressource insuffisante pour un retrait
        """
        resource = await self.get_village_resources(village_id)
        if not resource:
            return None
        
        # Appliquer les deltas
        for resource_name, delta in resource_deltas.items():
            current_value = getattr(resource, resource_name, 0)
            new_value = current_value + delta
            
            # Vérifier qu'on ne descend pas en négatif
            if new_value < 0:
                raise ValueError(
                    f"Ressource insuffisante: {resource_name} "
                    f"(actuel: {current_value}, requis: {abs(delta)})"
                )
            
            # Appliquer le cap de stockage
            if new_value > resource.max_capacity:
                new_value = resource.max_capacity
            
            setattr(resource, resource_name, new_value)
        
        await self.db.commit()
        await self.db.refresh(resource)
        
        return resource
    
    async def calculate_production(self, village_id: int) -> Dict[str, int]:
        """
        Calcule la production/consommation par heure pour un village
        
        Args:
            village_id: Identifiant du village
            
        Returns:
            Dictionnaire {resource_name: net_production_per_hour}
            (positif = production, négatif = consommation)
            
        Note:
            Prend en compte:
            - Production des bâtiments actifs
            - Consommation des bâtiments
            - Consommation des PNJ (logements)
            - Bonus de recherches (à implémenter plus tard)
        """
        production_rates = {}
        
        # Récupérer tous les bâtiments actifs du village
        result = await self.db.execute(
            select(BuildingInstance)
            .where(BuildingInstance.village_id == village_id)
            .where(BuildingInstance.is_active == True)
        )
        building_instances = result.scalars().all()
        
        # TODO: Calculer production de chaque bâtiment
        # Pour l'instant, retourner vide (sera implémenté avec building_service)
        
        return production_rates
    
    async def get_village_stats(self, village_id: int) -> Optional[VillageStats]:
        """
        Récupère les statistiques complètes d'un village
        
        Args:
            village_id: Identifiant du village
            
        Returns:
            VillageStats si village trouvé, None sinon
        """
        village = await self.get_village_by_id(village_id)
        if not village:
            return None
        
        # Compter les bâtiments
        buildings_result = await self.db.execute(
            select(BuildingInstance).where(BuildingInstance.village_id == village_id)
        )
        buildings_count = len(buildings_result.scalars().all())
        
        # Compter les PNJ
        characters_result = await self.db.execute(
            select(Character).where(Character.village_id == village_id)
        )
        npcs = characters_result.scalars().all()
        npcs_count = len(npcs)
        
        # Calculer population max (2 PNJ par niveau de Maison)
        # TODO: Calculer depuis les bâtiments Maison réels
        max_population = 10  # Par défaut
        
        # Récupérer les ressources
        resources = await self.get_village_resources(village_id)
        
        # Calculer production
        production_rates = await self.calculate_production(village_id)
        
        stats = VillageStats(
            village_id=village.id,
            name=village.name,
            level=village.level,
            prestige_cycle=village.prestige_cycle,
            population=npcs_count,
            max_population=max_population,
            buildings_count=buildings_count,
            resources={
                "water": resources.water if resources else 0,
                "wood": resources.wood if resources else 0,
                "stone": resources.stone if resources else 0,
                "food": resources.food if resources else 0,
                "money": resources.money if resources else 0,
            },
            production_rates=production_rates,
            created_at=village.created_at
        )
        
        return stats
    
    async def update_village_name(
        self, 
        village_id: int, 
        new_name: str
    ) -> Optional[Village]:
        """
        Met à jour le nom d'un village
        
        Args:
            village_id: Identifiant du village
            new_name: Nouveau nom
            
        Returns:
            Village mis à jour, None si non trouvé
        """
        village = await self.get_village_by_id(village_id)
        if not village:
            return None
        
        village.name = new_name
        await self.db.commit()
        await self.db.refresh(village)
        
        return village
    
    async def check_storage_capacity(self, village_id: int) -> Dict[str, Any]:
        """
        Vérifie la capacité de stockage et retourne les ressources critiques
        
        Args:
            village_id: Identifiant du village
            
        Returns:
            Dictionnaire avec:
            - max_capacity: capacité max
            - resources_at_capacity: liste des ressources au max
            - resources_critical: liste des ressources < 20%
        """
        resources = await self.get_village_resources(village_id)
        if not resources:
            return {}
        
        at_capacity = []
        critical = []
        
        resource_fields = [
            "water", "wood", "stone", "food", "wheat", "meat",
            "fabric", "leather", "herbs", "books", "money"
        ]
        
        for field in resource_fields:
            value = getattr(resources, field, 0)
            percentage = (value / resources.max_capacity) * 100
            
            if percentage >= 100:
                at_capacity.append(field)
            elif percentage < 20:
                critical.append(field)
        
        return {
            "max_capacity": resources.max_capacity,
            "resources_at_capacity": at_capacity,
            "resources_critical": critical
        }
