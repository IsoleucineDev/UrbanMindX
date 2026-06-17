# ============================================================
# backend/main.py — Aplicación FastAPI
# ============================================================

import asyncio
import uuid
import logging
from typing import Dict
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.config import settings
from backend.database import init_db, get_db
from backend.models import Simulacion, MetricasResultado, SimulacionStatus
from backend.schemas import (
    SimulacionCreate,
    SimulacionResponse,
    SimulacionSchema,
    EstadoSimulacion,
)
from backend.intersecciones import get_interseccion, listar_intersecciones
from backend.simulador import GestorSimulacion

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Diccionario global de simulaciones activas
simulaciones_activas: Dict[str, GestorSimulacion] = {}

# Lifespan para inicializar DB
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializar BD al arrancar, limpiar al detener"""
    logger.info("Iniciando UrbanMind X API...")
    await init_db()
    yield
    # Cleanup
    for sim_id, gestor in simulaciones_activas.items():
        try:
            gestor.cerrar()
        except Exception as e:
            logger.error(f"Error cerrando simulación {sim_id}: {e}")
    logger.info("API detenida")

# Crear app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

# CORS
origins = [
    settings.frontend_url,
    f"https://{settings.vercel_domain}",
    "http://localhost:3000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/health")
async def health_check():
    """Health check para Docker"""
    return {"status": "healthy", "service": "UrbanMind X API"}

@app.get("/intersecciones")
async def listar_intersecciones_endpoint():
    """Lista todas las intersecciones disponibles"""
    return listar_intersecciones()

@app.post("/simulaciones")
async def crear_simulacion(
    data: SimulacionCreate,
    db: AsyncSession = Depends(get_db),
) -> SimulacionResponse:
    """
    POST /simulaciones
    Crea una nueva simulación.
    
    Body:
    {
        "interseccion": "toluca_centro",
        "escenario": "normal"
    }
    """
    # Validar interseción
    interseccion = get_interseccion(data.interseccion)
    if not interseccion:
        raise HTTPException(status_code=400, detail="Intersección no encontrada")
    
    # Validar escenario
    if data.escenario not in interseccion["escenarios_disponibles"]:
        raise HTTPException(
            status_code=400,
            detail=f"Escenario '{data.escenario}' no disponible para esta intersección"
        )
    
    # Crear registro en BD
    sim_id = str(uuid.uuid4())
    simulacion = Simulacion(
        id=sim_id,
        interseccion=data.interseccion,
        escenario=data.escenario,
        status=SimulacionStatus.CREADA.value,
    )
    db.add(simulacion)
    await db.commit()
    await db.refresh(simulacion)
    
    logger.info(f"Simulación creada: {sim_id}")
    
    return SimulacionResponse(
        id=sim_id,
        status="creada",
        message="Simulación creada. Conecta por WebSocket para iniciar."
    )

@app.get("/simulaciones/{sim_id}")
async def obtener_simulacion(
    sim_id: str,
    db: AsyncSession = Depends(get_db),
) -> SimulacionSchema:
    """GET /simulaciones/{sim_id} - Obtiene detalles de una simulación"""
    result = await db.execute(
        select(Simulacion).where(Simulacion.id == sim_id)
    )
    simulacion = result.scalar_one_or_none()
    
    if not simulacion:
        raise HTTPException(status_code=404, detail="Simulación no encontrada")
    
    return SimulacionSchema.from_orm(simulacion)

@app.websocket("/ws/{sim_id}")
async def websocket_simulacion(websocket: WebSocket, sim_id: str):
    """
    WebSocket /ws/{sim_id}
    Transmite estado de la simulación paso a paso.
    """
    await websocket.accept()
    logger.info(f"WebSocket conectado: {sim_id}")
    
    gestor = None
    db_session = None
    
    try:
        # Obtener datos de simulación de BD
        async with AsyncSessionLocal() as db_session:
            from backend.database import AsyncSessionLocal
            
            result = await db_session.execute(
                select(Simulacion).where(Simulacion.id == sim_id)
            )
            simulacion = result.scalar_one_or_none()
            
            if not simulacion:
                await websocket.send_json({
                    "tipo": "error",
                    "data": {"mensaje": "Simulación no encontrada"}
                })
                await websocket.close(code=1008)
                return
            
            # Obtener configuración de intersección
            interseccion = get_interseccion(simulacion.interseccion)
            if not interseccion:
                await websocket.send_json({
                    "tipo": "error",
                    "data": {"mensaje": "Intersección no encontrada"}
                })
                await websocket.close(code=1008)
                return
            
            # Actualizar status en BD
            simulacion.status = SimulacionStatus.EN_EJECUCION.value
            await db_session.commit()
        
        # Crear gestor de simulación
        config_sumo = interseccion["config_sumo"]
        gestor = GestorSimulacion(
            config_sumo=config_sumo,
            modelo_semaforo_path="modelos/semaforo_final",
            modelo_vehiculo_path="modelos/vehiculo_final",
        )
        
        # Inicializar
        gestor.inicializar()
        logger.info(f"Gestor inicializado para {sim_id}")
        
        simulaciones_activas[sim_id] = gestor
        
        # Loop de simulación
        max_pasos = 21600  # 6 horas
        paso = 0
        
        while not gestor.simulacion_terminada() and paso < max_pasos:
            try:
                # Avanzar un paso
                estado = gestor.paso_simulacion()
                paso += 1
                
                # Enviar estado al cliente
                await websocket.send_json({
                    "tipo": "estado",
                    "data": estado
                })
                
                # Pequeña pausa para no saturar
                await asyncio.sleep(0.01)
                
            except Exception as e:
                logger.error(f"Error en paso {paso}: {e}")
                await websocket.send_json({
                    "tipo": "error",
                    "data": {"mensaje": f"Error en paso {paso}: {str(e)}"}
                })
                break
        
        # Obtener métricas finales
        metricas = gestor.obtener_metricas_finales()
        
        await websocket.send_json({
            "tipo": "completado",
            "data": metricas
        })
        
        # Guardar métricas en BD
        async with AsyncSessionLocal() as db_session:
            from backend.database import AsyncSessionLocal
            
            result = await db_session.execute(
                select(Simulacion).where(Simulacion.id == sim_id)
            )
            simulacion = result.scalar_one_or_none()
            
            if simulacion:
                simulacion.status = SimulacionStatus.COMPLETADA.value
                
                metrica = MetricasResultado(
                    simulacion_id=sim_id,
                    **metricas
                )
                db_session.add(metrica)
                await db_session.commit()
        
        logger.info(f"Simulación completada: {sim_id}")
        
    except Exception as e:
        logger.error(f"Error WebSocket {sim_id}: {e}")
        try:
            await websocket.send_json({
                "tipo": "error",
                "data": {"mensaje": f"Error: {str(e)}"}
            })
        except:
            pass
        
        # Actualizar status a ERROR en BD
        try:
            async with AsyncSessionLocal() as db_session:
                from backend.database import AsyncSessionLocal
                
                result = await db_session.execute(
                    select(Simulacion).where(Simulacion.id == sim_id)
                )
                simulacion = result.scalar_one_or_none()
                if simulacion:
                    simulacion.status = SimulacionStatus.ERROR.value
                    await db_session.commit()
        except:
            pass
    
    finally:
        # Limpiar
        if gestor:
            try:
                gestor.cerrar()
            except Exception as e:
                logger.error(f"Error cerrando gestor: {e}")
        
        if sim_id in simulaciones_activas:
            del simulaciones_activas[sim_id]
        
        try:
            await websocket.close()
        except:
            pass
        
        logger.info(f"WebSocket cerrado: {sim_id}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
