# ============================================================
# backend/simulador.py — Gestor de simulaciones SUMO+TraCI
# ============================================================

import os
import sys
import asyncio
import uuid
import logging
from typing import Optional, Dict, List
from simulacion.trafico_api import SimulacionTrafico
from entornos.entorno_semaforo import EntornoSemaforo
from entornos.entorno_vehiculo import EntornoVehiculo
from stable_baselines3 import PPO

logger = logging.getLogger(__name__)

class GestorSimulacion:
    """
    Capa de abstracción para manejar simulaciones con RL.
    Reutiliza: SimulacionTrafico, EntornoSemaforo, EntornoVehiculo, PPO
    """
    
    def __init__(
        self,
        config_sumo: str,
        modelo_semaforo_path: str = "modelos/semaforo_final",
        modelo_vehiculo_path: str = "modelos/vehiculo_final",
    ):
        self.config_sumo = config_sumo
        self.modelo_semaforo_path = modelo_semaforo_path
        self.modelo_vehiculo_path = modelo_vehiculo_path
        
        self.sim: Optional[SimulacionTrafico] = None
        self.env_semaforo: Optional[EntornoSemaforo] = None
        self.env_vehiculo: Optional[EntornoVehiculo] = None
        self.modelo_semaforo: Optional[PPO] = None
        self.modelo_vehiculo: Optional[PPO] = None
        
        self.activa = False
        self.paso = 0
        self.metricas_acumuladas = {}
    
    def inicializar(self):
        """Inicializa SUMO, carga modelos y entornos"""
        try:
            # Crear simulación
            self.sim = SimulacionTrafico(config_path=self.config_sumo, gui=False)
            self.sim.iniciar()
            logger.info("✓ SUMO iniciado")
            
            # Crear entornos
            self.env_semaforo = EntornoSemaforo(self.sim, modo_recompensa="completa")
            self.env_vehiculo = EntornoVehiculo(self.sim, modo_recompensa="completa")
            logger.info("✓ Entornos creados")
            
            # Cargar modelos PPO
            if os.path.exists(f"{self.modelo_semaforo_path}.zip"):
                self.modelo_semaforo = PPO.load(
                    self.modelo_semaforo_path,
                    env=self.env_semaforo
                )
                logger.info("✓ Modelo semaforo cargado")
            else:
                raise FileNotFoundError(f"Modelo semaforo no encontrado: {self.modelo_semaforo_path}")
            
            if os.path.exists(f"{self.modelo_vehiculo_path}.zip"):
                self.modelo_vehiculo = PPO.load(
                    self.modelo_vehiculo_path,
                    env=self.env_vehiculo
                )
                logger.info("✓ Modelo vehiculo cargado")
            else:
                logger.warning(f"Modelo vehiculo no encontrado: {self.modelo_vehiculo_path}")
            
            self.activa = True
            self.paso = 0
            
        except Exception as e:
            logger.error(f"Error inicializando simulación: {e}")
            self.cerrar()
            raise
    
    def paso_simulacion(self) -> Dict:
        """
        Avanza un paso: aplica acción del modelo de RL,
        retorna estado actual de la simulación
        """
        if not self.activa or not self.sim:
            raise RuntimeError("Simulación no activa")
        
        # Predicciones de los modelos
        obs_semaforo = self.env_semaforo._get_obs() if self.env_semaforo else None
        accion_semaforo, _ = self.modelo_semaforo.predict(
            obs_semaforo, deterministic=True
        ) if self.modelo_semaforo is not None else (0, None)
        
        # Step del entorno semaforo
        if self.env_semaforo:
            self.env_semaforo.step(int(accion_semaforo))
        
        # Step del entorno vehículo (si existe)
        if self.env_vehiculo and self.modelo_vehiculo:
            obs_vehiculo = self.env_vehiculo._get_obs()
            accion_vehiculo, _ = self.modelo_vehiculo.predict(
                obs_vehiculo, deterministic=True
            )
            self.env_vehiculo.step(int(accion_vehiculo))
        
        self.paso += 1
        
        # Obtener estado actual
        estado = self.sim.get_estado_interseccion()
        vehiculos = self._obtener_vehiculos_estado()
        metricas = self.sim.get_metricas_globales()
        
        return {
            "paso": self.paso,
            "fase_semaforo": estado["fase_actual"],
            "vehiculos": vehiculos,
            "autos_norte": estado["autos_norte"],
            "autos_sur": estado["autos_sur"],
            "autos_este": estado["autos_este"],
            "autos_oeste": estado["autos_oeste"],
            "espera_total": estado["espera_total"],
            "filas_total": estado["filas_total"],
            "velocidad_promedio": metricas["velocidad_promedio"],
        }
    
    def _obtener_vehiculos_estado(self) -> List[Dict]:
        """Extrae posiciones y velocidades de todos los vehículos"""
        vehiculos = []
        try:
            ids = self.sim.get_ids_vehiculos()
            for vid in ids:
                estado_v = self.sim.get_estado_vehiculo(vid)
                x, y = estado_v["posicion"]
                vehiculos.append({
                    "id": vid,
                    "x": float(x),
                    "y": float(y),
                    "velocidad": float(estado_v["velocidad"]),
                })
        except Exception as e:
            logger.error(f"Error obteniendo vehículos: {e}")
        return vehiculos
    
    def simulacion_terminada(self) -> bool:
        """Verifica si la simulación debe terminar"""
        if not self.sim:
            return True
        return self.sim.simulacion_terminada()
    
    def obtener_metricas_finales(self) -> Dict:
        """Extrae métricas finales después de completar simulación"""
        if not self.sim:
            return {}
        
        metricas = self.sim.get_metricas_globales()
        estado = self.sim.get_estado_interseccion()
        
        # Cálculos finales
        espera_promedio = estado["espera_total"] / max(1, metricas["autos_activos"])
        
        return {
            "espera_promedio": round(espera_promedio, 2),
            "fila_maxima": estado["filas_total"],
            "throughput": metricas["autos_llegaron"],
            "frenadas": 0,  # TODO: calcular desde vehículos
            "mejora_porcentual": 0.0,  # TODO: comparar con baseline
            "tiempo_simulacion": metricas["tiempo_simulacion"],
            "velocidad_promedio": metricas["velocidad_promedio"],
        }
    
    def cerrar(self):
        """Limpia recursos"""
        if self.sim:
            try:
                self.sim.cerrar()
                logger.info("✓ SUMO cerrado")
            except Exception as e:
                logger.error(f"Error cerrando SUMO: {e}")
        
        self.activa = False
        self.env_semaforo = None
        self.env_vehiculo = None
        self.modelo_semaforo = None
        self.modelo_vehiculo = None
