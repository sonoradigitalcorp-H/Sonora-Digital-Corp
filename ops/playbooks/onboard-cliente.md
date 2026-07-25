# Playbook: Onboard Cliente

## Goal
Incorporar un nuevo cliente al ecosistema SDC con su propia galaxia
— carpetas, branding, permisos, y canales de comunicación.

## Prerequisites
- Cliente contactado y contrato firmado
- Acceso a `~/sonora-digital-corp/`
- Conocimiento del plan contratado (Conquistador / Agente IA / Imperio)

## Steps

### 1. Crear carpeta del cliente
```bash
mkdir -p clients/<id-cliente>/{branding,knowledge,memory,skills,workflows,specs}
```

### 2. Registrar en el sistema
```bash
sdc registry add --type client --id <id-cliente> --name "<Nombre Cliente>"
```

### 3. Configurar tenant (si aplica)
```bash
# Agregar a config/tenants.json
```

### 4. Configurar canales
- WhatsApp: agregar contacto en `state/whatsapp/clients/`
- Telegram: si aplica, configurar bot
- Email: si aplica

### 5. Asignar skills
```bash
# Skills específicos del cliente en clients/<id>/skills/
```

### 6. Crear primer spec
```bash
mkdir -p clients/<id>/specs
# Crear SPEC-001 con objetivos del onboarding
```

### 7. Notificar al equipo
```bash
sdc hermes message --channel telegram --text "Nuevo cliente: <Nombre>"
```

## Verification
```bash
ls clients/<id>/             # debe mostrar la estructura completa
sdc registry list --type client  # debe aparecer el nuevo cliente
```

## Rollback
```bash
rm -rf clients/<id>
sdc registry remove --id <id>
# Revertir config/tenants.json si se modificó
```
