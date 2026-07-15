---
name: deploy
description: Deploy apps, configure nginx, SSL, and systemd services. Use for deploying new apps, fixing DNS, or managing certificates.
version: 1.0.0
updated: 2026-07-13
---

# Deploy Skill

Deploy and configure web applications: nginx, SSL, systemd, DNS.

## Tools que usa
- `lovable_generate_page` — generar app
- `upload_file` — subir assets
- `hasura_mutate` — crear tenant
- `engram_save` — registrar deploy

## Pipeline
1. Lovable genera app
2. Configurar nginx + SSL
3. Crear systemd service
4. Verificar HTTP 200
5. Registrar en Engram

## Ejemplo
```
Deploy nueva landing page para ABE Music
```
