# Vercel DNS + Frontend Migration Plan

**Goal:** Migrar DNS y frontends estáticos a Vercel. Backend (Neo4j, Qdrant, Ollama, APIs) se queda en OVH.

**Architecture:**
```
Usuario → sonoradigitalcorp.com
              ↓ (Vercel DNS + CDN)
         Vercel Edge
           ├── / → landing page (static)
           ├── /abe/* → ABE dashboards (static)
           ├── /api/* → proxy a OVH (serverless function)
           └── api.sonoradigitalcorp.com → proxy a OVH :5174
```

**OVH se queda con:** Neo4j, Qdrant, Ollama, Redis, PostgreSQL, n8n, Hermes MCP Gateway, JARVIS Web UI, Telegram bot.

---

## Task 1: Instalar Vercel CLI y autenticar

```bash
# En el VPS o local
npm i -g vercel
vercel login
vercel link --project sonora-digital-corp --repo git@github.com:sonoradigitalcorp-H/Sonora-Digital-Corp.git
```

**Files:**
- Create: `vercel.json` (raíz del repo)

## Task 2: Estructura de frontends en Vercel

**Files:**
- Create: `frontends/landing/` — landing page principal sonoradigitalcorp.com
- Move: `mcp/gateway/*.html` → `frontends/abe/`
- Move: `clients/abe-music/*.html` → `frontends/abe/clients/`

## Task 3: Configurar vercel.json con rutas

```json
{
  "name": "sonora-digital-corp",
  "git": {
    "deploymentEnabled": {
      "main": true
    }
  },
  "buildCommand": null,
  "outputDirectory": "frontends",
  "routes": [
    { "src": "/", "dest": "/landing/index.html" },
    { "src": "/abe/(.*)", "dest": "/abe/$1" },
    { "src": "/api/(.*)", "dest": "https://149.56.46.173/$1" },
    { "src": "/(.*)", "dest": "/$1" }
  ]
}
```

## Task 4: Mover landing principal desde ref/

Seleccionar la mejor landing (`ref/landing-sdc-principal.html` o crear una nueva) como `frontends/landing/index.html`.

## Task 5: Configurar dominios en Vercel

```bash
vercel domains add sonoradigitalcorp.com
vercel domains add www.sonoradigitalcorp.com
vercel domains add api.sonoradigitalcorp.com
vercel domains add mystika.sonoradigitalcorp.com
```

## Task 6: Cambiar DNS a Vercel

1. Obtener nameservers de Vercel:
   ```
   vercel dns ls sonoradigitalcorp.com
   ```
2. Ir a Hostinger → cambiar NS a los de Vercel:
   ```
   ns1.vercel-dns.com
   ns2.vercel-dns.com
   ```

## Task 7: Configurar DNS records en Vercel

```bash
# A record para sonoradigitalcorp.com → Vercel (lo maneja automático)
vercel dns add sonoradigitalcorp.com @ A 76.76.21.21

# CNAME para api → OVH (para que proxy funcione)
vercel dns add sonoradigitalcorp.com api CNAME sonoradigitalcorp.com

# CNAME para mystika → OVH
vercel dns add sonoradigitalcorp.com mystika CNAME sonoradigitalcorp.com
```

## Task 8: Simplificar nginx en OVH

Después de la migración, nginx en OVH solo sirve para:
- `api.sonoradigitalcorp.com` → JARVIS Web UI (:5174)
- `mystika.sonoradigitalcorp.com` → Mystika (:3001)
- Backend APIs internas (no públicas)

Remover bloque `sonoradigitalcorp.com` de nginx (ya lo maneja Vercel).

## Task 9: Proxy serverless function para API calls

**Files:**
- Create: `api/proxy.js`

```javascript
export default async function handler(req, res) {
  const target = `http://149.56.46.173${req.url.replace('/api/', '/')}`;
  const response = await fetch(target, {
    method: req.method,
    headers: { 'Content-Type': 'application/json' },
    body: req.method !== 'GET' ? JSON.stringify(req.body) : undefined,
  });
  res.status(response.status).json(await response.json());
}
```

## Task 10: Deploy y verificar

```bash
git add . && git commit -m "feat: migrar frontends a Vercel"
git push origin main
# Vercel auto-deploys desde GitHub

# Verificar
curl -I https://sonoradigitalcorp.com
curl -I https://api.sonoradigitalcorp.com
```

## Task 11: Limpiar servidor OVH

- Remover servidores estáticos duplicados
- Actualizar scripts de deploy
- Documentar nueva arquitectura en docs/

---

## Riesgos

| Riesgo | Mitigación |
|--------|-----------|
| DNS propagation (hasta 48h) | Mantener OVH respondiendo durante transición |
| CORS entre Vercel y OVH | Agregar headers CORS en nginx de OVH |
| APIs necesitan IP real | Usar Vercel Edge Functions con IP fija o tunnel |
| SSL en OVH para APIs | Mantener certbot renovación para api.* y mystika.* |
