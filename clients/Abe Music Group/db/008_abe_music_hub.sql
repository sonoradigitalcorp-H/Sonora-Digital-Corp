-- ================================================================
-- Migración 008: Abe Music Hub — tablas propias del hub físico/digital
-- Depende de: 006_music_hub.sql (artists, artist_fans, etc.)
-- ================================================================

-- ── HUB: SERVICIOS ──────────────────────────────────────────────────
-- Catálogo de servicios del hub (sala ensayo, estudio, clases, etc.)
CREATE TABLE IF NOT EXISTS hub_services (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    nombre          VARCHAR(200) NOT NULL,
    descripcion     TEXT,
    categoria       VARCHAR(50) NOT NULL
                        CHECK (categoria IN (
                            'sala_ensayo', 'estudio_grabacion', 'clase_musica',
                            'podcast_studio', 'zona_gym', 'retiro_creativo',
                            'vr_cabina', 'mini_show', 'evento_privado',
                            'creacion_contenido', 'renta_equipo', 'otro'
                        )),
    precio_mxn      DECIMAL(10, 2) NOT NULL,
    precio_reso     INTEGER DEFAULT 0,               -- costo en $RESO (si aplica)
    duracion_min    INTEGER DEFAULT 60,              -- duración en minutos
    capacidad       INTEGER DEFAULT 1,               -- personas simultáneas
    disponible      BOOLEAN NOT NULL DEFAULT true,
    foto_url        VARCHAR(500),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_hub_services_tenant    ON hub_services(tenant_id);
CREATE INDEX IF NOT EXISTS idx_hub_services_categoria ON hub_services(categoria);
CREATE INDEX IF NOT EXISTS idx_hub_services_disponible ON hub_services(disponible) WHERE disponible = true;

ALTER TABLE hub_services ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS hub_services_tenant_isolation ON hub_services;
CREATE POLICY hub_services_tenant_isolation ON hub_services
    USING (tenant_id = current_tenant_id());

CREATE TRIGGER set_hub_services_updated_at
    BEFORE UPDATE ON hub_services
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ── HUB: RESERVAS ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS hub_bookings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    service_id      UUID NOT NULL REFERENCES hub_services(id),
    fan_id          UUID REFERENCES artist_fans(fan_id),
    nombre_cliente  VARCHAR(200),
    telefono        VARCHAR(30),
    telegram_chat_id BIGINT,
    fecha_reserva   DATE NOT NULL,
    hora_inicio     TIME NOT NULL,
    hora_fin        TIME NOT NULL,
    estado          VARCHAR(20) NOT NULL DEFAULT 'pendiente'
                        CHECK (estado IN ('pendiente', 'confirmada', 'cancelada', 'completada')),
    pago_estado     VARCHAR(20) NOT NULL DEFAULT 'pendiente'
                        CHECK (pago_estado IN ('pendiente', 'pagado', 'reembolsado')),
    monto_mxn       DECIMAL(10, 2),
    reso_usado      INTEGER DEFAULT 0,
    stripe_payment_id VARCHAR(255),
    notas           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_hub_bookings_tenant  ON hub_bookings(tenant_id);
CREATE INDEX IF NOT EXISTS idx_hub_bookings_fecha   ON hub_bookings(fecha_reserva);
CREATE INDEX IF NOT EXISTS idx_hub_bookings_estado  ON hub_bookings(estado);
CREATE INDEX IF NOT EXISTS idx_hub_bookings_chat_id ON hub_bookings(telegram_chat_id);

ALTER TABLE hub_bookings ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS hub_bookings_tenant_isolation ON hub_bookings;
CREATE POLICY hub_bookings_tenant_isolation ON hub_bookings
    USING (tenant_id = current_tenant_id());

CREATE TRIGGER set_hub_bookings_updated_at
    BEFORE UPDATE ON hub_bookings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ── TOKEN LEDGER ($RESO) ─────────────────────────────────────────────
-- Registro inmutable de todas las transacciones $RESO
CREATE TABLE IF NOT EXISTS token_ledger (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    fan_id          UUID NOT NULL REFERENCES artist_fans(fan_id),
    tipo            VARCHAR(10) NOT NULL CHECK (tipo IN ('earn', 'burn')),
    cantidad        INTEGER NOT NULL CHECK (cantidad > 0),
    concepto        VARCHAR(100) NOT NULL
                        CHECK (concepto IN (
                            'meme_validado', 'dueto_reel', 'referido_suscrito',
                            'live_virtual', 'completar_curso', 'evento_flash',
                            'hora_ensayo', 'merch_exclusivo', 'acceso_vr',
                            'bienvenida', 'manual'
                        )),
    referencia_id   UUID,                           -- ID de la entidad relacionada
    notas           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_token_ledger_tenant  ON token_ledger(tenant_id);
CREATE INDEX IF NOT EXISTS idx_token_ledger_fan     ON token_ledger(fan_id);
CREATE INDEX IF NOT EXISTS idx_token_ledger_tipo    ON token_ledger(tipo);
CREATE INDEX IF NOT EXISTS idx_token_ledger_fecha   ON token_ledger(created_at DESC);

ALTER TABLE token_ledger ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS token_ledger_tenant_isolation ON token_ledger;
CREATE POLICY token_ledger_tenant_isolation ON token_ledger
    USING (tenant_id = current_tenant_id());

-- Vista: balance actual por fan (calculado desde ledger)
CREATE OR REPLACE VIEW v_token_balance AS
SELECT
    fan_id,
    tenant_id,
    SUM(CASE WHEN tipo = 'earn' THEN cantidad ELSE -cantidad END) AS balance,
    SUM(CASE WHEN tipo = 'earn' THEN cantidad ELSE 0 END) AS total_earned,
    SUM(CASE WHEN tipo = 'burn' THEN cantidad ELSE 0 END) AS total_burned,
    MAX(created_at) AS last_transaction
FROM token_ledger
GROUP BY fan_id, tenant_id;

-- ── VR: SESIONES ─────────────────────────────────────────────────────
-- Registro de sesiones en cabinas VR
CREATE TABLE IF NOT EXISTS vr_sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    fan_id          UUID REFERENCES artist_fans(fan_id),
    cabina_numero   SMALLINT NOT NULL CHECK (cabina_numero BETWEEN 1 AND 10),
    experiencia     VARCHAR(100),                   -- nombre de la experiencia VR
    fecha_sesion    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    duracion_min    INTEGER NOT NULL DEFAULT 30,
    reso_cobrado    INTEGER NOT NULL DEFAULT 0,
    mxn_cobrado     DECIMAL(10, 2),
    estado          VARCHAR(20) NOT NULL DEFAULT 'completada'
                        CHECK (estado IN ('reservada', 'en_curso', 'completada', 'cancelada')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_vr_sessions_tenant ON vr_sessions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_vr_sessions_fecha  ON vr_sessions(fecha_sesion DESC);

ALTER TABLE vr_sessions ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS vr_sessions_tenant_isolation ON vr_sessions;
CREATE POLICY vr_sessions_tenant_isolation ON vr_sessions
    USING (tenant_id = current_tenant_id());

-- ── SUSCRIPCIONES ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS hub_suscripciones (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    fan_id          UUID NOT NULL REFERENCES artist_fans(fan_id),
    plan            VARCHAR(20) NOT NULL
                        CHECK (plan IN ('basico', 'pro', 'elite')),
    precio_mxn      DECIMAL(10, 2) NOT NULL,
    reso_mensual    INTEGER NOT NULL,
    stripe_sub_id   VARCHAR(255),
    stripe_customer_id VARCHAR(255),
    estado          VARCHAR(20) NOT NULL DEFAULT 'activa'
                        CHECK (estado IN ('activa', 'pausada', 'cancelada', 'vencida')),
    fecha_inicio    DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_renovacion DATE NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, fan_id)
);

CREATE INDEX IF NOT EXISTS idx_suscripciones_tenant ON hub_suscripciones(tenant_id);
CREATE INDEX IF NOT EXISTS idx_suscripciones_fan    ON hub_suscripciones(fan_id);
CREATE INDEX IF NOT EXISTS idx_suscripciones_estado ON hub_suscripciones(estado);

ALTER TABLE hub_suscripciones ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS suscripciones_tenant_isolation ON hub_suscripciones;
CREATE POLICY suscripciones_tenant_isolation ON hub_suscripciones
    USING (tenant_id = current_tenant_id());

CREATE TRIGGER set_suscripciones_updated_at
    BEFORE UPDATE ON hub_suscripciones
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ── COMENTARIOS ──────────────────────────────────────────────────────
COMMENT ON TABLE hub_services       IS 'Catálogo de servicios del hub (salas, estudio, VR, etc.)';
COMMENT ON TABLE hub_bookings       IS 'Reservas de servicios del hub por fans';
COMMENT ON TABLE token_ledger       IS 'Registro inmutable de earn/burn $RESO';
COMMENT ON VIEW  v_token_balance    IS 'Balance actual de $RESO por fan';
COMMENT ON TABLE vr_sessions        IS 'Sesiones en cabinas VR inmersivas';
COMMENT ON TABLE hub_suscripciones  IS 'Suscripciones mensuales (Básico/Pro/Élite) con Stripe';
