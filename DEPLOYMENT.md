# ============================================================
# INSTRUCCIONES COMPLETAS PARA DESPLEGAR
# ============================================================

## 📋 TABLA DE CONTENIDOS
1. [Requisitos Previos](#requisitos-previos)
2. [Setup Local (Desarrollo)](#setup-local)
3. [Desplegar Base de Datos (Supabase)](#desplegar-base-de-datos)
4. [Desplegar Backend (Render)](#desplegar-backend)
5. [Desplegar Frontend (Vercel)](#desplegar-frontend)
6. [Verificar Funcionamiento](#verificar-funcionamiento)

---

## 🔧 Requisitos Previos

- **Git** instalado
- **Docker** + **Docker Compose** (para local)
- Cuenta en **Supabase** (gratis)
- Cuenta en **Render** (gratis con limitaciones)
- Cuenta en **Vercel** (gratis)
- **Node.js 16+** (opcional, solo si quieres servir el frontend localmente)

---

## 🚀 SETUP LOCAL (DESARROLLO)

### 1. Clonar rama production-deployment
```bash
git clone https://github.com/IsoleucineDev/UrbanMindX.git
cd UrbanMindX
git checkout production-deployment
```

### 2. Crear archivo .env
```bash
cp .env.example .env
```

**Editar `.env` con los siguientes valores:**
```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres_dev_password@postgres:5432/urbamindx
SUMO_HOME=/usr/share/sumo
SUMO_PORT=8813
FRONTEND_URL=http://localhost:3000
VERCEL_DOMAIN=localhost:3000
DEBUG=True
```

### 3. Levantar todo con Docker Compose
```bash
docker-compose up
```

Espera hasta ver:
```
✓ SUMO iniciado
✓ Entornos creados
✓ Modelo semaforo cargado
INFO:     Application startup complete [uvicorn]
```

### 4. Verificar API
```bash
curl http://localhost:8000/health
```

Debe responder:
```json
{"status": "healthy", "service": "UrbanMind X API"}
```

### 5. Acceder al Frontend (local)
Abrir en navegador:
```
http://localhost:3000/frontend/index.html
```

---

## 📊 DESPLEGAR BASE DE DATOS (SUPABASE)

### Paso 1: Crear proyecto en Supabase
1. Ir a https://supabase.com
2. Clickear **"New Project"**
3. Nombre: `urbamindx-prod`
4. Database password: **GUARDAR EN LUGAR SEGURO**
5. Region: elegir cercana
6. Click **"Create new project"**

### Paso 2: Obtener connection string
1. Una vez creado, ir a **Settings → Database → Connection Strings**
2. Seleccionar **"Connection pooler"** (NO la directa)
3. Copiar la URL (reemplazar `[YOUR-PASSWORD]` con tu password)
4. Debería ser similar a:
```
postgresql+asyncpg://postgres:[PASSWORD]@db.supabase.co:6543/postgres
```

### Paso 3: Crear tablas
1. En Supabase, ir a **SQL Editor**
2. Click **"New Query"**
3. Copiar contenido de `database/migration.sql`
4. **RUN** (Click execute)

✅ Tablas creadas!

---

## 🐳 DESPLEGAR BACKEND (RENDER)

### Paso 1: Conectar GitHub a Render
1. Ir a https://render.com
2. Clickear **"New +"** → **"Web Service"**
3. Seleccionar **"GitHub"** (conectar tu cuenta)
4. Buscar y seleccionar `IsoleucineDev/UrbanMindX`
5. Seleccionar rama: **`production-deployment`**

### Paso 2: Configurar el servicio
- **Name**: `urbamindx-api`
- **Runtime**: Python 3
- **Build Command**: 
  ```bash
  pip install -r requirements-prod.txt
  ```
- **Start Command**: 
  ```bash
  uvicorn backend.main:app --host 0.0.0.0 --port 8000
  ```
- **Plan**: Free (suficiente para pruebas)

### Paso 3: Variables de entorno
En Render, ir a **Environment**:

```
DATABASE_URL=postgresql+asyncpg://postgres:[PASSWORD]@db.supabase.co:6543/postgres
SUMO_HOME=/usr/share/sumo
DEBUG=False
FRONTEND_URL=https://urbamindx.vercel.app
VERCEL_DOMAIN=urbamindx.vercel.app
```

(Obtener `[PASSWORD]` de Supabase)

### Paso 4: Deploy
- Click **"Create Web Service"**
- Esperar ~5-10 minutos
- Una vez desplegado, copiar la URL (algo como: `https://urbamindx-api.onrender.com`)

✅ Backend en producción!

---

## 🌐 DESPLEGAR FRONTEND (VERCEL)

### Paso 1: Actualizar URL del API en frontend
1. Editar `frontend/index.html`
2. Buscar línea:
   ```javascript
   const API_URL = window.location.hostname === 'localhost' 
       ? 'http://localhost:8000' 
       : 'https://urbamindx-api.onrender.com'; // AQUÍ
   ```
3. Cambiar `urbamindx-api.onrender.com` por la URL real de Render (del paso anterior)
4. Hacer commit:
   ```bash
   git add frontend/index.html
   git commit -m "Update API URL for production"
   git push origin production-deployment
   ```

### Paso 2: Desplegar en Vercel
1. Ir a https://vercel.com
2. Clickear **"New Project"**
3. Importar repositorio `UrbanMindX`
4. **Project Name**: `urbamindx`
5. **Branch to Deploy**: `production-deployment`
6. **Framework Preset**: Other
7. **Root Directory**: `./` (dejar default)
8. Click **"Deploy"**

### Paso 3: Configurar rutas (Vercel)
1. En dashboard de Vercel, ir a **Settings → Rewrites**
2. Agregar rewrite:
   ```
   Source: /api/*
   Destination: https://urbamindx-api.onrender.com/api/*
   ```
   (Si lo necesitas, sino es opcional)

✅ Frontend en producción!

---

## ✅ VERIFICAR FUNCIONAMIENTO

### 1. API Health Check
```bash
curl https://urbamindx-api.onrender.com/health
```

Debe responder:
```json
{"status": "healthy", "service": "UrbanMind X API"}
```

### 2. Listar Intersecciones
```bash
curl https://urbamindx-api.onrender.com/intersecciones
```

Debe responder array de intersecciones.

### 3. Abrir el Dashboard
```
https://urbamindx.vercel.app/frontend/index.html
```

Deberías ver:
- ✅ Mapa con marcadores de intersecciones
- ✅ Lista de intersecciones seleccionables
- ✅ Botón "Iniciar Simulación"
- ✅ Métricas en tiempo real

### 4. Hacer una simulación de prueba
1. Seleccionar intersección
2. Seleccionar escenario
3. Clickear "Iniciar Simulación"
4. Esperar a que complete (~30-60 segundos)
5. Ver resultados en tabla final

---

## 🐛 TROUBLESHOOTING

### Error: "Cannot connect to WebSocket"
- Verificar que la URL del API en `frontend/index.html` sea correcta
- Verificar CORS en `backend/main.py` (debe incluir dominio de Vercel)

### Error: "SUMO not found"
- Docker ya incluye SUMO. Si corres sin Docker, instala:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install sumo sumo-tools
  export SUMO_HOME=/usr/share/sumo
  
  # Mac
  brew install sumo
  export SUMO_HOME=/usr/local/opt/sumo/share/sumo
  ```

### Error: "Database connection failed"
- Verificar `DATABASE_URL` en variables de entorno
- Verificar que Supabase pooler esté accesible
- Ejecutar migration SQL en Supabase

### Simulación muy lenta
- Es normal en plan Free de Render (cold starts)
- Para producción real, usar plan Starter o superior

---

## 📈 PRÓXIMOS PASOS

1. **Monitoreo**: Usar Render logs para debug
2. **Métricas reales**: Agregar más campos a `backend/simulador.py`
3. **Cache**: Implementar Redis para WebSocket más rápidos
4. **Frontend mejorado**: Usar Vue.js o React en lugar de vanilla JS
5. **Mobile**: App nativa con React Native

---

## 📞 SOPORTE

Si algo no funciona:
1. Revisar logs en Render: **Logs** tab
2. Revisar consola del navegador (F12)
3. Hacer commit a rama dev y pedir help

¡Listo! 🚀
