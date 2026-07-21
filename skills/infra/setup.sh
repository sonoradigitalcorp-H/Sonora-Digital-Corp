#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INFRA_DIR="$SCRIPT_DIR"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$INFRA_DIR/.env"

echo "============================================="
echo "  Sonora Digital Corp — Infra Setup"
echo "============================================="

# 1. Crear .env si no existe
if [ ! -f "$ENV_FILE" ]; then
  echo ""
  echo "📝 Creando .env desde .env.example..."
  cp "$INFRA_DIR/.env.example" "$ENV_FILE"
  echo "  ✅ .env creado"
  echo "  ⚠️  Revisa $ENV_FILE y ajusta contraseñas antes de continuar"
  echo ""
  read -p "Presiona Enter para continuar o Ctrl+C para editar..."
fi

source "$ENV_FILE"

# 2. Crear directorio de init scripts
mkdir -p "$INFRA_DIR/postgres/init"

# 3. Crear script de init DB para multi-tenant
cat > "$INFRA_DIR/postgres/init/01-init-tenants.sql" << 'SQLEOF'
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabla de tenants
CREATE TABLE IF NOT EXISTS public.tenants (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  slug VARCHAR(255) UNIQUE NOT NULL,
  pack_id VARCHAR(100),
  config JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Función para crear schema por tenant
CREATE OR REPLACE FUNCTION create_tenant_schema(tenant_slug VARCHAR)
RETURNS void AS $$
BEGIN
  EXECUTE format('CREATE SCHEMA IF NOT EXISTS %I', tenant_slug);
END;
$$ LANGUAGE plpgsql;
SQLEOF
echo "  ✅ init SQL creado"

# 4. Levantar servicios
echo ""
echo "🐳 Levantando servicios Docker..."
cd "$INFRA_DIR"
docker compose up -d

echo ""
echo "⏳ Esperando que todos los servicios estén listos..."

# Esperar PostgreSQL
echo -n "  PostgreSQL: "
until docker exec sdc-postgres pg_isready -U sdc -d sonora > /dev/null 2>&1; do
  echo -n "."
  sleep 2
done
echo " ✅"

# Esperar Hasura
echo -n "  Hasura:     "
until curl -s http://localhost:8080/healthz > /dev/null 2>&1; do
  echo -n "."
  sleep 2
done
echo " ✅"

# Esperar Qdrant
echo -n "  Qdrant:     "
until curl -s http://localhost:6333/health > /dev/null 2>&1; do
  echo -n "."
  sleep 2
done
echo " ✅"

# Esperar Redis
echo -n "  Redis:      "
until docker exec sdc-redis redis-cli ping > /dev/null 2>&1; do
  echo -n "."
  sleep 2
done
echo " ✅"

# 5. Configurar Hasura (track tables, etc.)
echo ""
echo "🔧 Configurando Hasura..."
HASURA_URL="http://localhost:8080"
HASURA_SECRET="${HASURA_ADMIN_SECRET:-sdc_hasura_secret}"

# Verificar Hasura
HASURA_VERSION=$(curl -s -H "X-Hasura-Admin-Secret: $HASURA_SECRET" "$HASURA_URL/v1/version" | python3 -c "import sys,json; print(json.load(sys.stdin).get('version','?'))" 2>/dev/null)
echo "  Hasura version: $HASURA_VERSION"

# 6. Mostrar resumen
echo ""
echo "============================================="
echo "  ✅ Infraestructura lista"
echo "============================================="
echo ""
echo "  PostgreSQL: postgres://localhost:5432/sonora"
echo "  Hasura:     http://localhost:8080"
echo "  Admin:      http://localhost:8080/console"
echo "  Qdrant:     http://localhost:6333/dashboard"
echo "  Redis:      localhost:6379"
echo ""
echo "  Hasura Admin Secret: $HASURA_SECRET"
echo ""
echo "📦 Para migrar un pack:"
echo "  ./scripts/deploy-pack.sh --pack packs/abe-music --tenant \"ABE Music\""
echo ""
echo "============================================="
