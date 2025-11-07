"""
Routes API pour surveiller les workers background.
"""

from fastapi import APIRouter, Depends
from typing import List, Dict, Any

from backend.app.utils.dependencies import get_current_active_user
from backend.app.models.user import User
from backend.app.workers.worker_manager import worker_manager


router = APIRouter(prefix="/workers", tags=["workers"])


@router.get("/status")
async def get_workers_status(
    current_user: User = Depends(get_current_active_user)
):
    """
    Récupère le statut de tous les workers background.
    Affiche les jobs actifs et leur prochaine exécution.
    """
    jobs = worker_manager.get_jobs()
    
    jobs_info = []
    for job in jobs:
        jobs_info.append({
            "id": job.id,
            "name": job.name,
            "next_run": job.next_run_time,
            "trigger": str(job.trigger)
        })
    
    return {
        "is_running": worker_manager.is_running,
        "jobs_count": len(jobs),
        "jobs": jobs_info
    }


@router.get("/job/{job_id}")
async def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Récupère le statut d'un job spécifique.
    """
    status = worker_manager.get_job_status(job_id)
    
    if not status:
        return {"error": f"Job '{job_id}' introuvable"}
    
    return status
