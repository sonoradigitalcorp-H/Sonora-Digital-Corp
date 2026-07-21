-- ABE Music Schema v1
-- Tenant: {{tenant_id}}
-- Generado por Pack Generator

-- Habilita UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Artistas (tenants)
CREATE TABLE IF NOT EXISTS artistas (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  nombre_artistico VARCHAR(255) NOT NULL,
  nombre_real VARCHAR(255),
  genero VARCHAR(100),
  email VARCHAR(255) UNIQUE,
  telefono VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Plataformas de streaming
CREATE TABLE IF NOT EXISTS plataformas (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  nombre VARCHAR(100) NOT NULL,
  icono VARCHAR(10),
  created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO plataformas (nombre, icono) VALUES
  ('Spotify', '🎵'),
  ('Apple Music', '🍎'),
  ('YouTube', '▶️'),
  ('TikTok', '📱');

-- Streams por plataforma
CREATE TABLE IF NOT EXISTS streams (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  artista_id UUID REFERENCES artistas(id),
  plataforma_id UUID REFERENCES plataformas(id),
  reproducciones INTEGER DEFAULT 0,
  oyentes_unicos INTEGER DEFAULT 0,
  periodo DATE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Lanzamientos
CREATE TABLE IF NOT EXISTS lanzamientos (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  artista_id UUID REFERENCES artistas(id),
  titulo VARCHAR(255) NOT NULL,
  tipo VARCHAR(50) DEFAULT 'single',
  fecha_lanzamiento DATE,
  estado VARCHAR(50) DEFAULT 'programada',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Campañas de promoción
CREATE TABLE IF NOT EXISTS campanias (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  artista_id UUID REFERENCES artistas(id),
  nombre VARCHAR(255) NOT NULL,
  presupuesto DECIMAL(10,2),
  plataforma_ads VARCHAR(100),
  estado VARCHAR(50) DEFAULT 'activa',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Eventos (presentaciones)
CREATE TABLE IF NOT EXISTS eventos (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  artista_id UUID REFERENCES artistas(id),
  fecha DATE NOT NULL,
  lugar VARCHAR(255),
  fee DECIMAL(10,2),
  estado VARCHAR(50) DEFAULT 'disponible',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Transacciones financieras
CREATE TABLE IF NOT EXISTS transacciones (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  artista_id UUID REFERENCES artistas(id),
  tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('ingreso', 'gasto')),
  monto DECIMAL(10,2) NOT NULL,
  concepto TEXT,
  categoria VARCHAR(100),
  conciliado BOOLEAN DEFAULT FALSE,
  fecha DATE DEFAULT CURRENT_DATE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_streams_artista ON streams(artista_id);
CREATE INDEX idx_streams_periodo ON streams(periodo);
CREATE INDEX idx_lanzamientos_artista ON lanzamientos(artista_id);
CREATE INDEX idx_eventos_artista ON eventos(artista_id);
CREATE INDEX idx_transacciones_artista ON transacciones(artista_id);
CREATE INDEX idx_transacciones_fecha ON transacciones(fecha);

-- Triggers para updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_artistas_updated_at
  BEFORE UPDATE ON artistas FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_lanzamientos_updated_at
  BEFORE UPDATE ON lanzamientos FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_campanias_updated_at
  BEFORE UPDATE ON campanias FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_eventos_updated_at
  BEFORE UPDATE ON eventos FOR EACH ROW EXECUTE FUNCTION update_updated_at();
