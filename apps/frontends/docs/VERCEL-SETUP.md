# Vercel Setup — GitHub Secrets Required

## Secrets en GitHub

| Secret | Valor | Dónde obtenerlo |
|--------|-------|-----------------|
| `VERCEL_TOKEN` | Vercel Access Token | `https://vercel.com/account/tokens` |
| `VERCEL_ORG_ID` | Team ID | `vercel teams ls` o `https://vercel.com/settings/general` |
| `VERCEL_PROJECT_ID` | Project ID (main site) | `vercel project ls` → ID |
| `VERCEL_ABE_PROJECT_ID` | Project ID (ABE portal) | `vercel project ls` → ID |

## Setup rápido

```bash
# 1. Login en Vercel
vercel login

# 2. Link projects
cd frontends/landing && vercel link
cd frontends/abe && vercel link

# 3. Get project IDs
vercel project ls

# 4. Add secrets in GitHub
# Settings → Secrets and variables → Actions
# Add los 4 secrets arriba

# 5. Probar
git push origin main  # debe trigger vercel-deploy.yml
```

## Workflows creados

| Workflow | Trigger | Qué hace |
|----------|---------|----------|
| `vercel-deploy.yml` | Push a main (frontends/) | Deploy producción a Vercel |
| `vercel-preview.yml` | PR abierto (frontends/) | Deploy preview + comenta URL |
