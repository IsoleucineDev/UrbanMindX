import numpy as np

class SimulacionMock:
    def __init__(self):
        self._fase = 0

    def iniciar(self): pass
    def avanzar_paso(self): pass
    def cerrar(self): pass

    def resetear(self):
        self._fase = 0

    def simulacion_terminada(self):
        return False

    def get_estado_interseccion(self):
        return {
            "autos_norte":  np.random.randint(0, 20),
            "autos_sur":    np.random.randint(0, 20),
            "autos_este":   np.random.randint(0, 20),
            "autos_oeste":  np.random.randint(0, 20),
            "espera_norte": np.random.random() * 50,
            "espera_sur":   np.random.random() * 50,
            "espera_este":  np.random.random() * 50,
            "espera_oeste": np.random.random() * 50,
            "filas_norte":  np.random.randint(0, 10),
            "filas_sur":    np.random.randint(0, 10),
            "filas_este":   np.random.randint(0, 10),
            "filas_oeste":  np.random.randint(0, 10),
            "fase_actual":  self._fase,
            "tiempo_fase":  np.random.randint(0, 60),
            "espera_total": np.random.random() * 200,
            "filas_total":  np.random.randint(0, 40),
        }

    def set_fase_semaforo(self, fase: int):
        self._fase = fase

    def get_ids_vehiculos(self):
        return ["veh0", "veh1", "veh2"]

    def get_estado_vehiculo(self, vehicle_id: str):
        return {
            "velocidad":          np.random.random() * 15,
            "velocidad_max":      15,
            "distancia_al_frente": np.random.random() * 50,
            "distancia_semaforo":  np.random.random() * 100,
            "semaforo_estado":     np.random.choice(["G", "R"]),
            "carril_actual":       np.random.randint(0, 2),
            "tiempo_detenido":     np.random.random() * 10,
            "aceleracion":         np.random.random() * 2,
            "posicion":            (np.random.random() * 100, np.random.random() * 100),
        }

    def set_velocidad_vehiculo(self, vehicle_id: str, velocidad: float):
        pass

    def get_metricas_globales(self):
        return {
            "tiempo_simulacion":  np.random.random() * 1000,
            "autos_activos":      3,
            "velocidad_promedio": np.random.random() * 15,
            "espera_total":       np.random.random() * 200,
            "filas_total":        np.random.randint(0, 40),
            "autos_llegaron":     np.random.randint(0, 50),
        }
