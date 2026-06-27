#!/bin/bash
# setup-langfuse.sh — Configura LangFuse v2: seed admin user, org, project y API keys
set -e

LANGFUSE_URL="${LANGFUSE_URL:-http://localhost:3000}"
DB_CONTAINER="${DB_CONTAINER:-sdc-langfuse-db}"

echo "=== Esperando a que LangFuse esté listo ==="
for i in $(seq 1 30); do
  if curl -sf "$LANGFUSE_URL/api/public/health" >/dev/null 2>&1; then
    echo "✅ LangFuse listo (v$(curl -s $LANGFUSE_URL/api/public/health | grep -oP '\d+\.\d+\.\d+'))"
    break
  fi
  sleep 2
done

# Seed admin via DB directo (más confiable que API de NextAuth)
echo "=== Sembrando admin, org, project y API keys ==="
python3 -c "
import bcrypt, uuid, hashlib
from datetime import datetime

password = b'admin123'
hashed = bcrypt.hashpw(password, salt=bcrypt.gensalt()).decode()
user_id = str(uuid.uuid4())
org_id = str(uuid.uuid4())
project_id = str(uuid.uuid4())
now = datetime.utcnow().isoformat()

pub_key = f'pk-{uuid.uuid4().hex}'
sec_key = f'sk-{uuid.uuid4().hex}'
hashed_sec = hashlib.sha256(sec_key.encode()).hexdigest()

sql = f'''
INSERT INTO users (id, name, email, password, admin, created_at, updated_at)
VALUES (\"{user_id}\", \"SDC Admin\", \"admin@sdc.com\", \"{hashed}\", true, \"{now}\", \"{now}\")
ON CONFLICT (email) DO UPDATE SET password = \"{hashed}\", admin = true;

INSERT INTO organizations (id, name, created_at, updated_at)
VALUES (\"{org_id}\", \"Sonora Digital Corp\", \"{now}\", \"{now}\")
ON CONFLICT DO NOTHING;

INSERT INTO projects (id, name, org_id, created_at, updated_at)
VALUES (\"{project_id}\", \"SDC Main\", \"{org_id}\", \"{now}\", \"{now}\")
ON CONFLICT DO NOTHING;

INSERT INTO organization_memberships (id, org_id, user_id, role, created_at, updated_at)
VALUES (\"{str(uuid.uuid4())}\", \"{org_id}\", \"{user_id}\", \"OWNER\", \"{now}\", \"{now}\")
ON CONFLICT DO NOTHING;

INSERT INTO project_memberships (project_id, user_id, org_membership_id, role)
SELECT \"{project_id}\", \"{user_id}\", id, \"ADMIN\"
FROM organization_memberships
WHERE user_id = \"{user_id}\" LIMIT 1
ON CONFLICT DO NOTHING;

INSERT INTO api_keys (id, project_id, public_key, hashed_secret_key, display_secret_key, note, created_at)
VALUES (\"{str(uuid.uuid4())}\", \"{project_id}\", \"{pub_key}\", \"{hashed_sec}\", \"{sec_key}\", \"SDC Observability Key\", \"{now}\")
ON CONFLICT DO NOTHING;
'''

print(sql)
print(f'==API KEYS==')
print(f'LANGFUSE_PUBLIC_KEY={pub_key}')
print(f'LANGFUSE_SECRET_KEY={sec_key}')
" | tee /tmp/langfuse-seed.sql | grep -v 'LANGFUSE_' | grep -v '^\s*$' | grep -v '^==' | docker exec -i "$DB_CONTAINER" psql -U postgres -d langfuse 2>&1

echo ""
echo "✅ LangFuse configurado en $LANGFUSE_URL"
echo "   Usuario: admin@sdc.com / admin123"
grep LANGFUSE_ /tmp/langfuse-seed.sql | tee /home/mystic/sonora-digital-corp/infra/.env.langfuse
echo ""
echo "API Keys guardadas en infra/.env.langfuse"
