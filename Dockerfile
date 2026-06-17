# ============================================================
# Dockerfile — Backend Production
# Python 3.10 + SUMO + TraCI + FastAPI
# ============================================================

FROM python:3.10-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    sumo \
    sumo-tools \
    sumo-doc \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Configurar SUMO_HOME
ENV SUMO_HOME=/usr/share/sumo
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app:$PYTHONPATH

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python (versión específica de SB3 2.3.2)
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    websockets==12.0 \
    sqlalchemy==2.0.23 \
    asyncpg==0.29.0 \
    python-dotenv==1.0.1 \
    pydantic==2.5.0 \
    pydantic-settings==2.1.0 \
    -r requirements.txt

# Copiar código completo
COPY . .

# Verificar que TraCI puede conectar con SUMO
RUN python -c "import traci; print('TraCI OK')"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando por defecto: correr FastAPI
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
