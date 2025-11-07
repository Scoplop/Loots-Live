"""
Worker pour l'auto-complétion des missions.
Vérifie toutes les minutes si des missions sont terminées et les complète automatiquement.
"""

import logging
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import AsyncSessionLocal
from backend.app.models.mission import Mission, MissionStatus
from backend.app.services.mission_service import MissionService

logger = logging.getLogger(__name__)


async def auto_complete_missions():
    """
    Worker qui vérifie toutes les missions IN_PROGRESS.
    Si la durée est écoulée (completed_at passé), complète automatiquement la mission.
    """
    async with AsyncSessionLocal() as db:
        try:
            # Récupérer toutes les missions en cours
            result = await db.execute(
                select(Mission).where(
                    Mission.status == MissionStatus.IN_PROGRESS,
                    Mission.completed_at <= datetime.utcnow()
                )
            )
            missions_to_complete = list(result.scalars().all())
            
            if not missions_to_complete:
                logger.debug("Aucune mission à compléter automatiquement")
                return
            
            logger.info(f"🎯 {len(missions_to_complete)} mission(s) à compléter automatiquement")
            
            # Compléter chaque mission
            mission_service = MissionService(db)
            completed_count = 0
            failed_count = 0
            
            for mission in missions_to_complete:
                try:
                    # Force completion (pas de vérification durée car déjà vérifié)
                    completed_mission, error = await mission_service.complete_mission(
                        mission_id=mission.id,
                        force=True
                    )
                    
                    if error:
                        logger.error(f"Erreur complétion mission {mission.id}: {error}")
                        failed_count += 1
                    else:
                        logger.info(f"✅ Mission '{mission.name}' complétée automatiquement")
                        completed_count += 1
                
                except Exception as e:
                    logger.error(f"Exception complétion mission {mission.id}: {e}")
                    failed_count += 1
            
            logger.info(
                f"📊 Résumé: {completed_count} complétées, {failed_count} échecs"
            )
        
        except Exception as e:
            logger.error(f"Erreur worker auto_complete_missions: {e}")
            raise
