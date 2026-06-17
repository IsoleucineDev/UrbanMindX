# 🚦 UrbanMind X — Sistema Inteligente de Tráfico en Producción

Sistema completo de simulación de tráfico urbano con aprendizaje por refuerzo (PPO), desplegado en la nube.

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                  Frontend (Vercel)                      │
│   HTML/JS estático + Leaflet (mapa interactivo)        │
│   https://urbamindx.vercel.app/frontend/index.html     │
└────────────────┬────────────────────────────────────────┘
                 │ WebSocket + REST
                 ▼
┌─────────────────────────────────────────────────────────┐
│            Backend FastAPI (Render)                     │
│   - Gestor de simulaciones SUMO+TraCI                  │
│   - Modelos PPO (semáforo + vehículos)                 │
│   - REST API + WebSocket                               │
│   https://urbamindx-api.onrender.com                   │
└────────────────┬────────────────────────────────────────┘
                 │ SQL
                 ▼
┌─────────────────────────────────────────────────────────┐
│         PostgreSQL (Supabase)                           │
│   - Tabla: simulaciones                                │
│   - Tabla: metricas_resultado                          │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Despliegue Rápido

### ⚡ 1 minuto: Backend local
```bash
git clone https://github.com/IsoleucineDev/UrbanMindX.git
cd UrbanMindX
git checkout production-deployment
docker-compose up
```

### ☁️ 5 minutos: Base de datos
1. Crear proyecto en https://supabase.com
2. Copiar connection string del pooler
3. Ejecutar SQL de `database/migration.sql`

### 🐳 10 minutos: Backend en Render
1. Conectar GitHub a Render
2. Crear Web Service desde `production-deployment`
3. Agregar variables de entorno (DATABASE_URL, etc.)
4. Deploy automático

### 🌐 5 minutos: Frontend en Vercel
1. Actualizar API_URL en `frontend/index.html`
2. Deploy desde Vercel

**Total: ~20 minutos ⏱️**

## 📖 Documentación Completa

Ver **[DEPLOYMENT.md](./DEPLOYMENT.md)** para instrucciones paso a paso.

## 📋 Estructura

```
UrbanMindX/
├── backend/                    # FastAPI
│   ├── main.py                # Endpoints + WebSocket
│   ├── simulador.py           # Gestor SUMO/RL
│   ├── models.py              # BD: Simulacion, MetricasResultado
│   ├── config.py              # Configuración
│   ├── intersecciones.py      # Catálogo de intersecciones
│   └── ...
├── frontend/
│   └── index.html             # Dashboard interactivo con Leaflet
├── database/
│   └── migration.sql          # Schema PostgreSQL
├── simulacion/                # (existente) Capa TraCI
├── entornos/                  # (existente) Gymnasium
├── modelos/                   # (existente) PPO entrenados
├── Dockerfile                 # Imagen Docker (SUMO + Python)
├── docker-compose.yml         # Local dev
├── render.yaml                # Configuración Render
├── requirements-prod.txt      # Dependencias
└── DEPLOYMENT.md              # Guía completa
```

## 🎯 Funcionalidades

✅ **3 intersecciones** disponibles (Toluca)  
✅ **3 escenarios** por intersección (normal, hora pico, desbalanceado)  
✅ **Mapa interactivo** con Leaflet (seleccionar intersección)  
✅ **Simulación en vivo** (WebSocket, 60 FPS)  
✅ **Modelos RL** preentrenados (PPO Semáforo + Vehículos)  
✅ **Métricas finales** guardadas en PostgreSQL  
✅ **CORS** configurado para Vercel  
✅ **Health check** para monitoreo  

## 🔌 API Reference

### REST
- `GET /health` — Health check
- `GET /intersecciones` — Listar intersecciones disponibles
- `POST /simulaciones` — Crear simulación
- `GET /simulaciones/{id}` — Obtener detalles

### WebSocket
- `WS /ws/{simulacion_id}` — Stream de estado

## 🛠️ Stack

| Componente | Tecnología | Proveedor |
|-----------|-----------|----------|
| **Simulación** | SUMO 1.19.0 + TraCI | Docker |
| **RL** | Stable-Baselines3 2.3.2 (PPO) | Backend |
| **Backend API** | FastAPI 0.104.1 | Render |
| **WebSocket** | FastAPI WebSocket | Render |
| **Base de datos** | PostgreSQL 15 | Supabase |
| **Frontend** | HTML/JS + Leaflet | Vercel |
| **Contenedor** | Docker + Docker Compose | Render |

## 🚧 Limitaciones (Plan Free)

- ⏸️ Cold start en Render (~30s primera simulación)
- 🔒 PostgreSQL gratis de Supabase limita conexiones
- 💾 Almacenamiento limitado
- ⏱️ Sin garantía de uptime 24/7

**Para producción real**: Upgrade a planes pagos.

## 📈 Métricas Almacenadas

Cada simulación guarda:
- `espera_promedio`: Segundos que esperan los vehículos
- `fila_maxima`: Máximos vehículos en cola simultáneamente
- `throughput`: Vehículos que completaron el trayecto
- `velocidad_promedio`: Velocidad promedio (m/s)
- `mejora_porcentual`: Mejora vs sistema tradicional

## 🆘 Troubleshooting

| Problema | Solución |
|----------|----------|
| SUMO no encontrado | Ver paso 1 de [DEPLOYMENT.md](./DEPLOYMENT.md) |
| WebSocket timeout | Verificar API_URL en `frontend/index.html` |
| BD no conecta | Verificar `DATABASE_URL` y migration.sql ejecutado |
| Simulación muy lenta | Normal en plan Free de Render (primera ejecución) |

## 📞 Contacto

**Autor**: IsoleucineDev  
**GitHub**: https://github.com/IsoleucineDev/UrbanMindX  
**Rama**: `production-deployment`

---

**Última actualización**: 2026-06-17  
**Estado**: ✅ Producción lista
