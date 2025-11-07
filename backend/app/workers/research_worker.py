"""
Worker pour l'auto-complétion des recherches.
Vérifie toutes les minutes si des recherches sont terminées et les complète automatiquement.
"""

import logging
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import AsyncSessionLocal
from backend.app.models.research import Research
from backend.app.utils.constants import ResearchStatus
from backend.app.services.research_service import ResearchService

logger = logging.getLogger(__name__)


async def auto_complete_researches():
    """
    Worker qui vérifie toutes les recherches IN_PROGRESS.
    Si la durée est écoulée (completed_at passé), complète automatiquement la recherche.
    """
    async with AsyncSessionLocal() as db:
        try:
            # Récupérer toutes les recherches en cours
            result = await db.execute(
                select(Research).where(
                    Research.status == ResearchStatus.IN_PROGRESS,
                    Research.completed_at <= datetime.utcnow()
                )
            )
            researches_to_complete = list(result.scalars().all())
            
            if not researches_to_complete:
                logger.debug("Aucune recherche à compléter automatiquement")
                return
            
            logger.info(f"🔬 {len(researches_to_complete)} recherche(s) à compléter automatiquement")
            
            # Compléter chaque recherche
            research_service = ResearchService(db)
            completed_count = 0
            failed_count = 0
            
            for research in researches_to_complete:
                try:
                    # Force completion (pas de vérification durée car déjà vérifié)
                    completed_research, error = await research_service.complete_research(
                        research_id=research.id,
                        force=True
                    )
                    
                    if error:
                        logger.error(f"Erreur complétion recherche {research.id}: {error}")
                        failed_count += 1
                    else:
                        logger.info(f"✅ Recherche '{research.research_key}' complétée automatiquement")
                        completed_count += 1
                
                except Exception as e:
                    logger.error(f"Exception complétion recherche {research.id}: {e}")
                    failed_count += 1
            
            logger.info(
                f"📊 Résumé: {completed_count} complétées, {failed_count} échecs"
            )
        
        except Exception as e:
            logger.error(f"Erreur worker auto_complete_researches: {e}")
            raise
