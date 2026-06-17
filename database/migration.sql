-- ============================================================
-- SQL: Schema para PostgreSQL (Supabase)
-- ============================================================

CREATE TABLE IF NOT EXISTS simulaciones (
    id VARCHAR(36) PRIMARY KEY,
    interseccion VARCHAR(50) NOT NULL,
    escenario VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'creada' NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_simulaciones_status ON simulaciones(status);
CREATE INDEX idx_simulaciones_created ON simulaciones(created_at);
CREATE INDEX idx_simulaciones_interseccion ON simulaciones(interseccion);

CREATE TABLE IF NOT EXISTS metricas_resultado (
    id SERIAL PRIMARY KEY,
    simulacion_id VARCHAR(36) NOT NULL REFERENCES simulaciones(id) ON DELETE CASCADE,
    espera_promedio FLOAT,
    fila_maxima INTEGER,
    throughput INTEGER,
    frenadas INTEGER,
    mejora_porcentual FLOAT,
    tiempo_simulacion FLOAT,
    velocidad_promedio FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metricas_simulacion ON metricas_resultado(simulacion_id);
