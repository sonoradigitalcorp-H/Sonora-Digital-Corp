# Playbook: Crear Producto

## Goal
Lanzar un nuevo producto de Sonora Digital Corp con estructura estandarizada,
skills, MCP servers si aplica, y registro en el sistema.

## Prerequisites
- ADR aprobada o decisión del CEO
- Spec del producto al menos en estado draft
- Conocimiento del core: skills/, mcp/, infra/

## Steps

### 1. Crear estructura del producto
```bash
mkdir -p products/<id-producto>/{src,infra,skills,specs,tests,docs,state,scripts,prompts}
```

### 2. Registrar en el registry
```bash
sdc registry add --type product --id <id-producto> --name "<Nombre>"
```

### 3. Skills del producto
Si el producto necesita skills específicos:
```bash
# Crear skills en products/<id>/skills/
# Si son habilidades del core, agregar a skills/ con prefijo del producto
```

### 4. MCP (si aplica)
Si el producto expone herramientas MCP:
```bash
mkdir products/<id>/mcp
# Configurar server MCP y registrar en skills/mcp/gateway/
```

### 5. Infraestructura
- `infra/docker-compose.override.yml` si el producto necesita servicios extra
- `fleet.yml` actualizar con los nuevos servicios

### 6. Tests
```bash
# Tests específicos del producto en products/<id>/tests/
```

### 7. Pricing (si es producto que se vende)
- Agregar a config/pricing.yaml o similar
- Actualizar planes según corresponda

### 8. Lanzar
```bash
sdc hermes message --channel telegram --text "Nuevo producto: <Nombre>"
```

## Verification
```bash
ls products/<id>/
sdc registry list --type product
```

## Rollback
```bash
rm -rf products/<id>
sdc registry remove --id <id>
# Revertir fleet.yml, docker-compose, config si se modificaron
```
