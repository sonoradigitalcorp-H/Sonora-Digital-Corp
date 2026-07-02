# Vercel + ABE Music Group — Plan de Implementación

**Goal:** Migrar frontends estáticos y DNS a Vercel, incluyendo sitio oficial de ABE Music Group con servicios y productos.

**Arquitectura final:**
```
Vercel DNS + CDN
  sonoradigitalcorp.com
    ├── / → Landing principal (frontends/landing/)
    ├── /abe/* → ABE Music Group site
    ├── /dashboard/* → AGENTIC OS dashboards
    └── /api/* → proxy serverless → OVH backend

  abe.sonoradigitalcorp.com
    └── → Sitio oficial ABE Music Group (frontends/abe/)
          ├── Servicios: distribución, management, revenue, content, fan CRM, store
          ├── Productos: SaaS ($499/mes), Store, Content Engine
          ├── Artistas: Hector Rubio, Jesus Urquijo, Javier Arvayo
          └── Links a portales: /abe/portal, /abe/saas, /abe/store

  api.sonoradigitalcorp.com → proxy → OVH :5174 (JARVIS API)
  mystika.sonoradigitalcorp.com → OVH (sin cambios)
```

**OVH se queda con:** Neo4j, Qdrant, Ollama, Redis, PostgreSQL, n8n, Hermes MCP Gateway, JARVIS Web UI, Telegram bot.

---

## Task 1: Instalar Vercel CLI y autenticar

```bash
npm i -g vercel
vercel login
cd /home/ubuntu/sonora-digital-corp
vercel link --project sonora-digital-corp --repo git@github.com:sonoradigitalcorp-H/Sonora-Digital-Corp.git
```

**Files:**
- Create: `vercel.json`

---

## Task 2: Crear estructura de frontends

**Files to create:**
```
frontends/
├── landing/
│   └── index.html          ← Landing principal sonoradigitalcorp.com
├── abe/
│   ├── index.html          ← Sitio oficial ABE Music Group (tomar de clients/abe-music/index.html)
│   ├── services.html        ← Servicios detallados
│   ├── products.html        ← Productos (SaaS, Store, Content Engine)
│   ├── hector-rubio.html    ← Artista
│   ├── jesus-urquijo.html   ← Artista
│   ├── javier-arvayo.html   ← Artista
│   └── portal/              ← Dashboards de ABE
│       ├── index.html       ← (de mcp/gateway/abe-portal.html)
│       ├── saas.html        ← (de mcp/gateway/abe-saas.html)
│       ├── store.html       ← (de mcp/gateway/abe-store.html)
│       ├── services.html    ← (de mcp/gateway/abe-services.html)
│       ├── content.html     ← (de mcp/gateway/abe-content-queue.html)
│       └── businesses.html  ← (de mcp/gateway/abe-businesses.html)
├── dashboard/
│   ├── index.html           ← AGENTIC OS (de mcp/gateway/dashboard.html)
│   ├── adk.html             ← (de mcp/gateway/adk.html)
│   ├── workflow.html        ← (de mcp/gateway/workflow-editor.html)
│   └── cheatsheet.html      ← (de mcp/gateway/cheatsheet.html)
└── assets/
    └── css/
    └── js/
```

**Copy commands:**
```bash
mkdir -p frontends/{landing,abe/portal,dashboard,assets}
cp clients/abe-music/index.html frontends/abe/index.html
cp mcp/gateway/abe-portal.html frontends/abe/portal/index.html
cp mcp/gateway/abe-saas.html frontends/abe/portal/saas.html
cp mcp/gateway/abe-store.html frontends/abe/portal/store.html
cp mcp/gateway/abe-services.html frontends/abe/portal/services.html
cp mcp/gateway/abe-content-queue.html frontends/abe/portal/content.html
cp mcp/gateway/abe-businesses.html frontends/abe/portal/businesses.html
cp mcp/gateway/dashboard.html frontends/dashboard/index.html
cp mcp/gateway/adk.html frontends/dashboard/adk.html
cp mcp/gateway/workflow-editor.html frontends/dashboard/workflow.html
cp mcp/gateway/cheatsheet.html frontends/dashboard/cheatsheet.html
```

---

## Task 3: Crear landing principal

**Files:**
- Create: `frontends/landing/index.html`

Landing page con:
- Hero: "Sonora Digital Corp — Native Agent OS"
- Links a: ABE Music, Dashboard, API
- Estilo glassmorphism dark (consistente con el ecosistema)

---

## Task 4: Mejorar sitio ABE Music Group

**Files:**
- Modify: `frontends/abe/index.html` (expandir con servicios, productos, portal links)

Secciones a agregar (basado en datos reales de `data/abe-music.json`):

**Servicios:**
1. **Distribución Digital** — 115M+ streams gestionados, Oplaai + Colonize Media
2. **Artist Management** — 3 artistas activos, revenue tracking en vivo
3. **Revenue Intelligence** — Splits 70/20/10, tracking de regalías
4. **Content Factory** — Portadas AI (FLUX), videos (Minimax), diseño automatizado
5. **Fan CRM** — Gamificación, tokens $RESO, engagement tracking
6. **Merch Store** — Printful integrado, comisiones por artista

**Productos:**
1. **ABE Music SaaS** — $499/mes, plataforma completa para sellos independientes
2. **ABE Store** — Merch automation con revenue splits
3. **ABE Content Engine** — Generación automática de contenido por temporada

**Artistas (datos reales):**
| Artista | Streams | Revenue | Género |
|---------|---------|---------|--------|
| Héctor Rubio | 115M | $460,372 | Regional Mexicano |
| Jesús Urquijo | 4.6M | $18,540 | Regional Mexicano |
| Javier Arvayo | 50K | $200 | Regional Mexicano |

---

## Task 5: Configurar vercel.json

```json
{
  "name": "sonora-digital-corp",
  "git": {
    "deploymentEnabled": { "main": true }
  },
  "buildCommand": null,
  "outputDirectory": "frontends",
  "routes": [
    { "src": "/", "dest": "/landing/index.html" },
    { "src": "/abe/portal/(.*)", "dest": "/abe/portal/$1" },
    { "src": "/abe/(.*)", "dest": "/abe/$1" },
    { "src": "/dashboard/(.*)", "dest": "/dashboard/$1" },
    { "src": "/api/(.*)", "dest": "https://api.sonoradigitalcorp.com/$1" },
    { "src": "/(.*)", "dest": "/$1" }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-Content-Type-Options", "value": "nosniff" }
      ]
    }
  ]
}
```

---

## Task 6: Configurar dominios en Vercel

```bash
vercel domains add sonoradigitalcorp.com
vercel domains add www.sonoradigitalcorp.com
vercel domains add abe.sonoradigitalcorp.com
vercel domains add api.sonoradigitalcorp.com
```

---

## Task 7: Cambiar DNS a Vercel

```bash
# Obtener NS de Vercel
vercel dns ls sonoradigitalcorp.com

# En Hostinger: cambiar nameservers a:
# ns1.vercel-dns.com
# ns2.vercel-dns.com
```

---

## Task 8: Configurar DNS records en Vercel

```bash
# A record para root → Vercel
vercel dns add sonoradigitalcorp.com @ A 76.76.21.21

# CNAME para subdominios
vercel dns add sonoradigitalcorp.com www CNAME cname.vercel-dns.com
vercel dns add sonoradigitalcorp.com abe CNAME cname.vercel-dns.com
vercel dns add sonoradigitalcorp.com api CNAME cname.vercel-dns.com
```

---

## Task 9: Proxy serverless para /api/*

**Files:**
- Create: `api/proxy.js`

```javascript
export default async function handler(req, res) {
  const targetUrl = `http://149.56.46.173${req.url.replace('/api', '')}`;
  
  const headers = { 'Content-Type': 'application/json' };
  if (req.headers['x-tenant-id']) headers['X-Tenant-ID'] = req.headers['x-tenant-id'];

  const response = await fetch(targetUrl, {
    method: req.method,
    headers,
    body: ['GET', 'HEAD'].includes(req.method) ? undefined : JSON.stringify(req.body),
  });

  const data = response.headers.get('content-type')?.includes('json')
    ? await response.json()
    : await response.text();

  res.status(response.status).json(data);
}
```

---

## Task 10: Simplificar nginx en OVH

Después de migrar, nginx solo sirve para backends:

```nginx
server {
    server_name api.sonoradigitalcorp.com;
    location / { proxy_pass http://127.0.0.1:5174; }
    listen 443 ssl;
    ssl_certificate ...; ssl_certificate_key ...;
}

server {
    server_name mystika.sonoradigitalcorp.com;
    location / { proxy_pass http://127.0.0.1:3001; }
    listen 443 ssl;
    ssl_certificate ...; ssl_certificate_key ...;
}
```

Remover el bloque `sonoradigitalcorp.com` (ya lo maneja Vercel).

---

## Task 11: Agregar CORS headers en OVH

Para que los frontends en Vercel puedan llamar APIs en OVH:

```nginx
location /api/ {
    add_header Access-Control-Allow-Origin "https://sonoradigitalcorp.com" always;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Content-Type, X-Tenant-ID" always;
    # ...
}
```

---

## Task 12: Deploy y verificar

```bash
git add .
git commit -m "feat: migrar frontends a Vercel + sitio ABE Music Group"
git push origin main
# Vercel auto-deploys

# Verificar
curl -I https://sonoradigitalcorp.com
curl -I https://abe.sonoradigitalcorp.com
curl -I https://api.sonoradigitalcorp.com/health
```

---

## Resumen de archivos

**Nuevos:**
| Archivo | Propósito |
|---------|-----------|
| `vercel.json` | Config Vercel (rutas, headers, deploy) |
| `api/proxy.js` | Serverless function para proxy a OVH |
| `frontends/landing/index.html` | Landing principal |
| `frontends/abe/index.html` | Sitio oficial ABE Music Group (mejorado) |
| `frontends/abe/services.html` | Página de servicios ABE |
| `frontends/abe/products.html` | Página de productos ABE |
| `frontends/abe/portal/*.html` | Dashboards ABE (movidos de mcp/gateway/) |
| `frontends/dashboard/*.html` | Dashboards sistema (movidos de mcp/gateway/) |

**Modificados:**
| Archivo | Cambio |
|---------|--------|
| `/etc/nginx/sites-enabled/default` | Remover bloque sonoradigitalcorp.com, agregar CORS |
| `clients/abe-music/index.html` | Expandir con servicios/productos (o mantener copia en frontends/) |

---

## Riesgos

| Riesgo | Mitigación |
|--------|-----------|
| Propagación DNS 24-48h | Mantener OVH activo en paralelo |
| CORS entre Vercel y OVH | Agregar headers CORS en nginx |
| Serverless timeout (10s Vercel) | API calls pesadas que excedan 10s → mover a OVH directo |
| SSL en OVH para subdominios | Mantener certbot renovando api.* y mystika.* |

---

## Tiempo estimado

| Fase | Duración |
|------|----------|
| Tasks 1-5 (setup + frontends) | ~1 hora |
| Tasks 6-8 (DNS + Vercel) | ~30 min |
| Tasks 9-11 (proxy + nginx) | ~30 min |
| Task 12 (deploy) | ~15 min |
| Propagación DNS | 24-48h (automático) |
| **Total activo** | **~2.5 horas** |
