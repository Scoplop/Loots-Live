"""
Service pour la gestion des bâtiments et de leur construction.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
import math

from backend.app.models.building import Building
from backend.app.models.building_instance import BuildingInstance
from backend.app.models.village import Village
from backend.app.models.resource import Resource
from backend.app.models.character import Character
from backend.app.schemas.building import (
    BuildingResponse,
    BuildingInstanceCreate,
    BuildingInstanceResponse,
    BuildingInstanceWithDetails,
    BuildingBuild
)


class BuildingService:
    """Service pour gérer les bâtiments"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_buildings(self) -> List[Building]:
        """Récupère tous les types de bâtiments disponibles (référentiel)"""
        result = await self.db.execute(select(Building).order_by(Building.unlock_level, Building.name))
        return list(result.scalars().all())

    async def get_building_by_key(self, building_key: str) -> Optional[Building]:
        """Récupère un type de bâtiment par sa clé"""
        result = await self.db.execute(
            select(Building).where(Building.key == building_key)
        )
        return result.scalar_one_or_none()

    async def get_building_by_id(self, building_id: int) -> Optional[Building]:
        """Récupère un type de bâtiment par ID"""
        result = await self.db.execute(
            select(Building).where(Building.id == building_id)
        )
        return result.scalar_one_or_none()

    async def get_village_buildings(self, user_id: int) -> List[BuildingInstance]:
        """Récupère toutes les instances de bâtiments d'un village"""
        # Récupérer le village
        village_result = await self.db.execute(
            select(Village).where(Village.user_id == user_id)
        )
        village = village_result.scalar_one_or_none()
        if not village:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Village non trouvé"
            )

        # Récupérer les instances avec les détails du bâtiment
        result = await self.db.execute(
            select(BuildingInstance)
            .where(BuildingInstance.village_id == village.id)
            .order_by(BuildingInstance.built_at)
        )
        return list(result.scalars().all())

    async def get_building_instance(
        self,
        instance_id: int,
        user_id: Optional[int] = None
    ) -> Optional[BuildingInstance]:
        """Récupère une instance de bâtiment par ID (avec vérification propriétaire optionnelle)"""
        query = select(BuildingInstance).where(BuildingInstance.id == instance_id)
        
        if user_id:
            # Vérifier que l'instance appartient au village de l'utilisateur
            village_result = await self.db.execute(
                select(Village).where(Village.user_id == user_id)
            )
            village = village_result.scalar_one_or_none()
            if not village:
                return None
            
            query = query.where(BuildingInstance.village_id == village.id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def build_building(
        self,
        user_id: int,
        build_data: BuildingBuild
    ) -> BuildingInstance:
        """
        Construit un nouveau bâtiment.
        Vérifie les ressources, prérequis, placement, et nombre d'instances max.
        Placement automatique si grid_x/grid_y = -1 (spirale).
        """
        # Récupérer le village
        village_result = await self.db.execute(
            select(Village).where(Village.user_id == user_id)
        )
        village = village_result.scalar_one_or_none()
        if not village:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Village non trouvé"
            )

        # Récupérer le type de bâtiment
        building = await self.get_building_by_key(build_data.building_key)
        if not building:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Type de bâtiment '{build_data.building_key}' non trouvé"
            )

        # Vérifier le niveau requis (TODO: implémenter niveau village)
        # if village.level < building.unlock_level:
        #     raise HTTPException(...)

        # Vérifier le nombre d'instances max
        existing_count_result = await self.db.execute(
            select(BuildingInstance)
            .where(
                BuildingInstance.village_id == village.id,
                BuildingInstance.building_id == building.id
            )
        )
        existing_count = len(list(existing_count_result.scalars().all()))
        
        if existing_count >= building.max_instances:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Nombre maximum d'instances atteint ({building.max_instances})"
            )

        # Vérifier les prérequis (recherches, bâtiments)
        if building.requirements:
            await self._check_requirements(village.id, building.requirements)

        # Vérifier les ressources
        await self._check_and_consume_resources(village.id, building.build_cost)

        # Déterminer la position (auto-placement en spirale si -1, -1)
        grid_x = build_data.grid_x
        grid_y = build_data.grid_y
        
        if grid_x == -1 and grid_y == -1:
            grid_x, grid_y = await self._get_next_spiral_position(village.id)
        else:
            # Vérifier que la position n'est pas déjà occupée
            if await self._is_position_occupied(village.id, grid_x, grid_y):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Position ({grid_x}, {grid_y}) déjà occupée"
                )

        # Créer l'instance
        new_instance = BuildingInstance(
            village_id=village.id,
            building_id=building.id,
            grid_x=grid_x,
            grid_y=grid_y,
            level=1,
            is_active=True
        )

        self.db.add(new_instance)
        await self.db.commit()
        await self.db.refresh(new_instance)

        return new_instance

    async def upgrade_building(
        self,
        instance_id: int,
        user_id: int
    ) -> BuildingInstance:
        """
        Améliore un bâtiment (niveau 1 à 5 max).
        Coût : coût de base × niveau actuel × 1.5
        """
        # Récupérer l'instance
        instance = await self.get_building_instance(instance_id, user_id)
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Instance de bâtiment non trouvée"
            )

        # Vérifier niveau max
        if instance.level >= 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Niveau maximum atteint (5)"
            )

        # Récupérer le type de bâtiment
        building = await self.get_building_by_id(instance.building_id)
        if not building:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Type de bâtiment non trouvé"
            )

        # Calculer coût d'amélioration
        upgrade_cost = {}
        for resource, base_cost in building.build_cost.items():
            upgrade_cost[resource] = int(base_cost * instance.level * 1.5)

        # Vérifier et consommer ressources
        await self._check_and_consume_resources(instance.village_id, upgrade_cost)

        # Améliorer
        instance.level += 1

        await self.db.commit()
        await self.db.refresh(instance)

        return instance

    async def destroy_building(
        self,
        instance_id: int,
        user_id: int,
        refund_percent: int = 50
    ) -> bool:
        """
        Détruit un bâtiment et rembourse un pourcentage des ressources.
        Par défaut: 50% de remboursement.
        """
        # Récupérer l'instance
        instance = await self.get_building_instance(instance_id, user_id)
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Instance de bâtiment non trouvée"
            )

        # Récupérer le type de bâtiment
        building = await self.get_building_by_id(instance.building_id)
        if not building:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Type de bâtiment non trouvé"
            )

        # Calculer remboursement (coût de base + améliorations × refund_percent)
        total_cost = {}
        for resource, base_cost in building.build_cost.items():
            # Coût total = base + (base × 1.5 × 1) + (base × 1.5 × 2) + ... jusqu'au niveau actuel
            total = base_cost
            for level in range(1, instance.level):
                total += int(base_cost * level * 1.5)
            total_cost[resource] = total

        # Rembourser
        refund = {res: int(cost * (refund_percent / 100)) for res, cost in total_cost.items()}
        await self._add_resources(instance.village_id, refund)

        # Détruire
        await self.db.delete(instance)
        await self.db.commit()

        return True

    async def calculate_production_rate(
        self,
        instance_id: int,
        assigned_npcs_count: int = 0
    ) -> Dict[str, Any]:
        """
        Calcule le taux de production d'un bâtiment.
        Production = base × niveau × (1 + 0.1 × nb_npcs)
        """
        # Récupérer l'instance
        result = await self.db.execute(
            select(BuildingInstance).where(BuildingInstance.id == instance_id)
        )
        instance = result.scalar_one_or_none()
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Instance non trouvée"
            )

        # Récupérer le type de bâtiment
        building = await self.get_building_by_id(instance.building_id)
        if not building or not building.production:
            return {
                "resource": None,
                "amount_per_hour": 0,
                "storage_capacity": 0,
                "multiplier": 1.0
            }

        # Calculer multiplicateur
        level_multiplier = instance.level
        npc_multiplier = 1 + (0.1 * assigned_npcs_count)
        total_multiplier = level_multiplier * npc_multiplier

        # Calculer production
        base_production = building.production.get("amount_per_hour", 0)
        final_production = int(base_production * total_multiplier)

        # Calculer capacité de stockage
        base_storage = building.production.get("storage_capacity", 0)
        final_storage = int(base_storage * instance.level)

        return {
            "resource": building.production.get("resource"),
            "amount_per_hour": final_production,
            "storage_capacity": final_storage,
            "multiplier": total_multiplier,
            "base_production": base_production,
            "level": instance.level,
            "assigned_npcs": assigned_npcs_count
        }

    async def toggle_building_active(
        self,
        instance_id: int,
        user_id: int
    ) -> BuildingInstance:
        """Active/désactive un bâtiment (arrêt de production)"""
        instance = await self.get_building_instance(instance_id, user_id)
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Instance non trouvée"
            )

        instance.is_active = not instance.is_active
        
        await self.db.commit()
        await self.db.refresh(instance)

        return instance

    # ============================================================================
    # MÉTHODES PRIVÉES
    # ============================================================================

    async def _check_requirements(self, village_id: int, requirements: Dict[str, Any]):
        """Vérifie les prérequis (recherches, bâtiments)"""
        # TODO: Vérifier researches quand le service Research sera créé
        if "researches" in requirements:
            pass  # Placeholder

        # Vérifier bâtiments requis
        if "buildings" in requirements:
            required_buildings = requirements["buildings"]
            for req_building_key in required_buildings:
                # Vérifier qu'au moins 1 instance de ce bâtiment existe
                building = await self.get_building_by_key(req_building_key)
                if not building:
                    continue
                
                result = await self.db.execute(
                    select(BuildingInstance)
                    .where(
                        BuildingInstance.village_id == village_id,
                        BuildingInstance.building_id == building.id
                    )
                )
                existing = result.scalar_one_or_none()
                
                if not existing:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Bâtiment requis manquant: {building.name}"
                    )

    async def _check_and_consume_resources(
        self,
        village_id: int,
        cost: Dict[str, int]
    ):
        """Vérifie que le village a assez de ressources et les consomme"""
        # Récupérer toutes les ressources du village
        result = await self.db.execute(
            select(Resource).where(Resource.village_id == village_id)
        )
        resources = {r.resource_type: r for r in result.scalars().all()}

        # Vérifier disponibilité
        for resource_type, amount in cost.items():
            if resource_type not in resources or resources[resource_type].quantity < amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ressources insuffisantes: {resource_type} (besoin: {amount})"
                )

        # Consommer
        for resource_type, amount in cost.items():
            resources[resource_type].quantity -= amount

        await self.db.commit()

    async def _add_resources(self, village_id: int, resources: Dict[str, int]):
        """Ajoute des ressources au village (pour remboursement)"""
        # Récupérer ressources existantes
        result = await self.db.execute(
            select(Resource).where(Resource.village_id == village_id)
        )
        existing_resources = {r.resource_type: r for r in result.scalars().all()}

        # Ajouter
        for resource_type, amount in resources.items():
            if resource_type in existing_resources:
                existing_resources[resource_type].quantity += amount
            else:
                # Créer la ressource si elle n'existe pas
                new_resource = Resource(
                    village_id=village_id,
                    resource_type=resource_type,
                    quantity=amount
                )
                self.db.add(new_resource)

        await self.db.commit()

    async def _is_position_occupied(
        self,
        village_id: int,
        grid_x: int,
        grid_y: int
    ) -> bool:
        """Vérifie si une position est déjà occupée"""
        result = await self.db.execute(
            select(BuildingInstance)
            .where(
                BuildingInstance.village_id == village_id,
                BuildingInstance.grid_x == grid_x,
                BuildingInstance.grid_y == grid_y
            )
        )
        return result.scalar_one_or_none() is not None

    async def _get_next_spiral_position(self, village_id: int) -> tuple[int, int]:
        """
        Calcule la prochaine position disponible en spirale (centre = 50, 50).
        Spirale d'Ulam: commence au centre, tourne dans le sens horaire.
        """
        # Récupérer toutes les instances existantes
        result = await self.db.execute(
            select(BuildingInstance)
            .where(BuildingInstance.village_id == village_id)
        )
        instances = list(result.scalars().all())

        if not instances:
            # Premier bâtiment: centre de la grille
            return (50, 50)

        # Positions occupées
        occupied = {(inst.grid_x, inst.grid_y) for inst in instances}

        # Générer positions en spirale jusqu'à trouver une libre
        x, y = 50, 50
        dx, dy = 0, -1  # Direction initiale: haut
        
        for i in range(1, 10000):  # Max 10000 positions
            if (x, y) not in occupied and 0 <= x <= 100 and 0 <= y <= 100:
                return (x, y)
            
            # Spirale d'Ulam
            if x == y or (x < 0 and x == -y) or (x > 0 and x == 1 - y):
                dx, dy = -dy, dx  # Tourner à 90°
            
            x += dx
            y += dy

        # Fallback: position aléatoire si spirale saturée (ne devrait jamais arriver)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Impossible de trouver une position libre"
        )
