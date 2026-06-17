# ============================================================
# backend/database.py — Conexión a PostgreSQL con SQLAlchemy
# ============================================================

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.config import settings
import logging
import os

logger = logging.getLogger(__name__)

# Base para los modelos
Base = declarative_base()

# Obtener DATABASE_URL y asegurar que tiene el driver asyncpg correcto
db_url = settings.database_url or os.getenv("DATABASE_URL", "")

# Si comienza con postgresql://, reemplazar con postgresql+asyncpg://
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif not db_url.startswith("postgresql+asyncpg://"):
    # Si no tiene ninguno, asumir que es la URL sin dialecto y agregar asyncpg
    if "://" not in db_url:
        logger.warning(f"DATABASE_URL format may be incorrect: {db_url[:50]}...")

logger.info(f"Connecting to database: {db_url.split('@')[1] if '@' in db_url else 'N/A'}")

# Motor async
engine = create_async_engine(
    db_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db():
    """Dependency para inyectar sesión en endpoints"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """Crear todas las tablas"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✓ Base de datos inicializada")
