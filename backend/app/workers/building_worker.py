"""
Worker pour la production automatique des bâtiments.
Calcule et distribue la production de tous les bâtiments actifs toutes les heures.
"""

import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import AsyncSessionLocal
from backend.app.models.building_instance import BuildingInstance
from backend.app.services.building_service import BuildingService
from backend.app.services.village_service import VillageService

logger = logging.getLogger(__name__)


async def process_building_production():
    """
    Worker qui traite la production de tous les bâtiments actifs.
    Exécuté toutes les heures.
    """
    async with AsyncSessionLocal() as db:
        try:
            # Récupérer tous les bâtiments actifs
            result = await db.execute(
                select(BuildingInstance).where(
                    BuildingInstance.is_active == True
                )
            )
            buildings = list(result.scalars().all())
            
            if not buildings:
                logger.debug("Aucun bâtiment actif pour production")
                return
            
            logger.info(f"🏭 Traitement production de {len(buildings)} bâtiment(s)")
            
            building_service = BuildingService(db)
            village_service = VillageService(db)
            
            # Grouper par village pour additionner les ressources
            village_productions = {}
            
            for building in buildings:
                try:
                    # Calculer la production
                    production = await building_service.calculate_production_rate(
                        building_id=building.id
                    )
                    
                    if not production or not production.get("resources"):
                        continue
                    
                    # Grouper par village
                    village_id = building.village_id
                    if village_id not in village_productions:
                        village_productions[village_id] = {}
                    
                    # Additionner les ressources
                    for resource, amount in production["resources"].items():
                        if resource not in village_productions[village_id]:
                            village_productions[village_id][resource] = 0
                        village_productions[village_id][resource] += amount
                
                except Exception as e:
                    logger.error(f"Erreur calcul production bâtiment {building.id}: {e}")
            
            # Ajouter les ressources aux villages
            total_villages = 0
            total_resources = 0
            
            for village_id, resources in village_productions.items():
                try:
                    success = await village_service.add_resources(village_id, resources)
                    
                    if success:
                        resource_count = sum(resources.values())
                        total_villages += 1
                        total_resources += resource_count
                        
                        # Log détaillé
                        resource_summary = ", ".join([
                            f"{amount} {resource}" 
                            for resource, amount in resources.items()
                        ])
                        logger.info(
                            f"✅ Village {village_id}: +{resource_summary}"
                        )
                    else:
                        logger.warning(f"Échec ajout ressources village {village_id}")
                
                except Exception as e:
                    logger.error(f"Erreur ajout ressources village {village_id}: {e}")
            
            logger.info(
                f"📊 Production terminée: {total_villages} village(s), "
                f"{total_resources} ressources produites"
            )
        
        except Exception as e:
            logger.error(f"Erreur worker process_building_production: {e}")
            raise
