"""
Configuration de l'application Loots&Live.
Charge les variables d'environnement et définit les constantes globales.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuration de l'application chargée depuis .env"""
    
    # Application
    APP_NAME: str = "LootsAndLive"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # Base de données
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/lootsandlive.db"
    
    # Sécurité
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    BCRYPT_ROUNDS: int = 12
    
    # Rate Limiting
    RATE_LIMIT_LOGIN_ATTEMPTS: int = 5
    RATE_LIMIT_LOGIN_WINDOW_MINUTES: int = 10
    
    # Ollama IA
    OLLAMA_ENDPOINT: str = "http://localhost:11434/api/generate"
    OLLAMA_MODEL: str = "qwen2.5:14b"
    OLLAMA_TIMEOUT: int = 30
    OLLAMA_MAX_CONCURRENT: int = 3
    OLLAMA_FALLBACK_ENABLED: bool = True
    
    # Background Workers
    WORKER_MISSION_CHECK_INTERVAL: int = 5
    WORKER_PRODUCTION_INTERVAL: int = 1
    WORKER_HEALING_INTERVAL: int = 30
    WORKER_EVENT_CHECK_INTERVAL: int = 21600  # 6 heures
    
    # Logs
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    LOG_MAX_BYTES: int = 10485760  # 10 MB
    LOG_BACKUP_COUNT: int = 5
    
    # Frontend
    CORS_ORIGINS: list[str] = ["http://localhost:8000", "http://127.0.0.1:8000"]
    
    # Optimisations
    CACHE_ENABLED: bool = False
    CACHE_TTL: int = 300
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instance globale des settings
settings = Settings()

# Chemins de base
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
FRONTEND_DIR = BASE_DIR / "frontend"

# Créer les dossiers s'ils n'existent pas
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
(DATA_DIR / "backups").mkdir(exist_ok=True)
