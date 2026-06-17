# ============================================================
# backend/intersecciones.py — Catálogo de intersecciones
# ============================================================

INTERSECCIONES = {
    "toluca_centro": {
        "id": "toluca_centro",
        "nombre": "Venustiano Carranza y Blvr. Pino Suarez",
        "ciudad": "Toluca, MEX",
        "latitud": 19.2878,
        "longitud": -99.6547,
        "descripcion": "Intersección real de Toluca (Quivera UAEM 2022)",
        "escenarios_disponibles": ["normal", "hora_pico", "desbalanceado"],
        "config_sumo": "sumo/config/simulacion.sumocfg",
        "rutas": {
            "normal": "sumo/rutas/normal.rou.xml",
            "hora_pico": "sumo/rutas/hora_pico.rou.xml",
            "desbalanceado": "sumo/rutas/desbalanceado.rou.xml",
        },
    },
    "toluca_norte": {
        "id": "toluca_norte",
        "nombre": "Paseo Tollocan y Avenida Universidad",
        "ciudad": "Toluca, MEX",
        "latitud": 19.3050,
        "longitud": -99.6600,
        "descripcion": "Intersección norte de Toluca (simulada)",
        "escenarios_disponibles": ["normal"],
        "config_sumo": "sumo/config/simulacion.sumocfg",
        "rutas": {
            "normal": "sumo/rutas/normal.rou.xml",
        },
    },
    "toluca_sur": {
        "id": "toluca_sur",
        "nombre": "Avenida Hidalgo y Avenida México",
        "ciudad": "Toluca, MEX",
        "latitud": 19.2700,
        "longitud": -99.6500,
        "descripcion": "Intersección sur de Toluca (simulada)",
        "escenarios_disponibles": ["normal"],
        "config_sumo": "sumo/config/simulacion.sumocfg",
        "rutas": {
            "normal": "sumo/rutas/normal.rou.xml",
        },
    },
}

def get_interseccion(id_interseccion: str):
    return INTERSECCIONES.get(id_interseccion)

def listar_intersecciones():
    return list(INTERSECCIONES.values())
