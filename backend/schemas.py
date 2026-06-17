# ============================================================
# backend/schemas.py — Schemas Pydantic
# ============================================================

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SimulacionCreate(BaseModel):
    interseccion: str
    escenario: str = "normal"

class MetricasResultadoSchema(BaseModel):
    espera_promedio: Optional[float] = None
    fila_maxima: Optional[int] = None
    throughput: Optional[int] = None
    frenadas: Optional[int] = None
    mejora_porcentual: Optional[float] = None
    tiempo_simulacion: Optional[float] = None
    velocidad_promedio: Optional[float] = None

class SimulacionSchema(BaseModel):
    id: str
    interseccion: str
    escenario: str
    status: str
    created_at: datetime
    updated_at: datetime
    metricas: List[MetricasResultadoSchema] = []
    
    class Config:
        from_attributes = True

class SimulacionResponse(BaseModel):
    id: str
    status: str
    message: str

class EstadoSimulacion(BaseModel):
    """Mensaje WebSocket — Estado actual de la simulación"""
    paso: int
    fase_semaforo: int
    vehiculos: List[dict]  # [{id, x, y, velocidad}, ...]
    autos_norte: int
    autos_sur: int
    autos_este: int
    autos_oeste: int
    espera_total: float
    filas_total: int
    velocidad_promedio: float

class MensajeWebSocket(BaseModel):
    """Mensaje genérico WebSocket"""
    tipo: str  # 'estado', 'error', 'completado'
    data: dict
