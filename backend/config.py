# ============================================================
# backend/config.py — Configuración de entorno
# ============================================================

import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Base de datos
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://user:password@localhost/urbamindx"
    )
    
    # SUMO
    sumo_home: str = os.getenv("SUMO_HOME", "/usr/share/sumo")
    sumo_port: int = int(os.getenv("SUMO_PORT", "8813"))
    
    # FastAPI
    app_name: str = "UrbanMind X API"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # CORS
    frontend_url: str = os.getenv(
        "FRONTEND_URL",
        "http://localhost:3000"
    )
    vercel_domain: str = os.getenv("VERCEL_DOMAIN", "urbamindx.vercel.app")
    
    # Modelos
    modelo_semaforo_path: str = "modelos/semaforo_final"
    modelo_vehiculo_path: str = "modelos/vehiculo_final"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
