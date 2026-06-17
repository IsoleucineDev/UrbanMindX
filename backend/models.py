# ============================================================
# backend/models.py — Modelos SQLAlchemy
# ============================================================

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base
import enum

class SimulacionStatus(str, enum.Enum):
    CREADA = "creada"
    EN_EJECUCION = "en_ejecucion"
    COMPLETADA = "completada"
    ERROR = "error"

class Interseccion(str, enum.Enum):
    TOLUCA_CENTRO = "toluca_centro"  # Venustiano Carranza y Blvr. Pino Suarez
    TOLUCA_NORTE = "toluca_norte"
    TOLUCA_SUR = "toluca_sur"

class Escenario(str, enum.Enum):
    NORMAL = "normal"
    HORA_PICO = "hora_pico"
    DESBALANCEADO = "desbalanceado"

class Simulacion(Base):
    __tablename__ = "simulaciones"
    
    id = Column(String(36), primary_key=True, index=True)
    interseccion = Column(String(50), nullable=False, index=True)
    escenario = Column(String(50), nullable=False)
    status = Column(String(20), default=SimulacionStatus.CREADA.value, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con métricas
    metricas = relationship("MetricasResultado", back_populates="simulacion", cascade="all, delete-orphan")

class MetricasResultado(Base):
    __tablename__ = "metricas_resultado"
    
    id = Column(Integer, primary_key=True, index=True)
    simulacion_id = Column(String(36), ForeignKey("simulaciones.id"), nullable=False, index=True)
    
    # Métricas finales
    espera_promedio = Column(Float, nullable=True)
    fila_maxima = Column(Integer, nullable=True)
    throughput = Column(Integer, nullable=True)
    frenadas = Column(Integer, nullable=True)
    mejora_porcentual = Column(Float, nullable=True)
    
    # Metadata
    tiempo_simulacion = Column(Float, nullable=True)
    velocidad_promedio = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relación con simulación
    simulacion = relationship("Simulacion", back_populates="metricas")
