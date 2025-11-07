"""
Gestionnaire de workers background pour Loots&Live.
Utilise APScheduler pour exécuter des tâches périodiques.

Jobs automatisés:
- Auto-complétion missions (toutes les minutes)
- Production bâtiments (toutes les heures)
- Régénération HP PNJ (toutes les 10 minutes)
- Complétion recherches (toutes les minutes)
- Événements aléatoires (toutes les 30 minutes)
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import logging

from backend.app.database import AsyncSessionLocal
from backend.app.workers.mission_worker import auto_complete_missions
from backend.app.workers.building_worker import process_building_production
from backend.app.workers.character_worker import regenerate_hp
from backend.app.workers.research_worker import auto_complete_researches

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WorkerManager:
    """Gestionnaire principal des workers background."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
    
    def start(self):
        """Démarre tous les workers background."""
        if self.is_running:
            logger.warning("Workers déjà démarrés")
            return
        
        logger.info("🔧 Configuration des workers background...")
        
        # Job 1: Auto-complétion missions (toutes les minutes)
        self.scheduler.add_job(
            auto_complete_missions,
            trigger=IntervalTrigger(minutes=1),
            id="auto_complete_missions",
            name="Auto-complétion missions",
            replace_existing=True
        )
        logger.info("✅ Worker missions configuré (1 minute)")
        
        # Job 2: Production bâtiments (toutes les heures)
        self.scheduler.add_job(
            process_building_production,
            trigger=IntervalTrigger(hours=1),
            id="building_production",
            name="Production bâtiments",
            replace_existing=True
        )
        logger.info("✅ Worker production configuré (1 heure)")
        
        # Job 3: Régénération HP (toutes les 10 minutes)
        self.scheduler.add_job(
            regenerate_hp,
            trigger=IntervalTrigger(minutes=10),
            id="hp_regeneration",
            name="Régénération HP",
            replace_existing=True
        )
        logger.info("✅ Worker HP configuré (10 minutes)")
        
        # Job 4: Complétion recherches (toutes les minutes)
        self.scheduler.add_job(
            auto_complete_researches,
            trigger=IntervalTrigger(minutes=1),
            id="auto_complete_researches",
            name="Auto-complétion recherches",
            replace_existing=True
        )
        logger.info("✅ Worker recherches configuré (1 minute)")
        
        # Job 5: Événements aléatoires (toutes les 30 minutes)
        # TODO: Implémenter quand event_service sera créé
        # self.scheduler.add_job(
        #     generate_random_events,
        #     trigger=IntervalTrigger(minutes=30),
        #     id="random_events",
        #     name="Événements aléatoires",
        #     replace_existing=True
        # )
        # logger.info("✅ Worker événements configuré (30 minutes)")
        
        # Démarrage du scheduler
        self.scheduler.start()
        self.is_running = True
        
        logger.info("🚀 Tous les workers sont démarrés !")
        logger.info(f"   - Missions: check toutes les 1 minute")
        logger.info(f"   - Production: toutes les 1 heure")
        logger.info(f"   - HP: toutes les 10 minutes")
        logger.info(f"   - Recherches: toutes les 1 minute")
    
    def stop(self):
        """Arrête tous les workers background."""
        if not self.is_running:
            return
        
        logger.info("🛑 Arrêt des workers background...")
        self.scheduler.shutdown(wait=False)
        self.is_running = False
        logger.info("✅ Workers arrêtés")
    
    def get_jobs(self):
        """Récupère la liste des jobs actifs."""
        return self.scheduler.get_jobs()
    
    def get_job_status(self, job_id: str):
        """Récupère le statut d'un job spécifique."""
        job = self.scheduler.get_job(job_id)
        if not job:
            return None
        
        return {
            "id": job.id,
            "name": job.name,
            "next_run": job.next_run_time,
            "trigger": str(job.trigger)
        }


# Instance globale du gestionnaire
worker_manager = WorkerManager()
