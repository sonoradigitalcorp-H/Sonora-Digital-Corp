# Spec: [Nombre del Componente]

**ID**: [XXX-nombre]
**Version**: 1.0.0
**Date**: YYYY-MM-DD
**Author**: [Nombre]

## Resumen

[Una línea que describe qué hace este componente]

## Objetivo

[Qué problema resuelve este componente]

## Contexto

### Servicios Relacionados

| Servicio | Relación |
|----------|----------|
| [Servicio] | [Cómo se relaciona] |

### Dependencias

- [Dependencia 1]
- [Dependencia 2]

## Especificación

### Inputs

```python
# Tipo de dato de entrada
class InputType:
    field: str
    field2: int
```

### Outputs

```python
# Tipo de dato de salida
class OutputType:
    field: str
    field2: bool
```

### Comportamiento

1. [Paso 1]
2. [Paso 2]
3. [Paso 3]

### Reglas de Negocio

- [Regla 1]
- [Regla 2]

### Contrato

```yaml
contract:
  input: InputType
  output: OutputType
  events_consume:
    - event.type.1
    - event.type.2
  events_publish:
    - event.type.3
  tools_allowed:
    - tool.1
    - tool.2
```

## Componentes

### [Componente 1]

- **Responsabilidad**: [Qué hace]
- **Inputs**: [Qué recibe]
- **Outputs**: [Qué produce]
- **Dependencias**: [De qué depende]

## API

### Endpoint 1

```
POST /api/v1/[recurso]
```

**Request**:
```json
{
  "field": "value"
}
```

**Response**:
```json
{
  "field": "value",
  "success": true
}
```

## Eventos

### Evento 1

```json
{
  "type": "component.event.1",
  "payload": {},
  "timestamp": "ISO-8601"
}
```

## Testing

### Casos de Prueba

| ID | Descripción | Input | Output Esperado |
|----|-------------|-------|-----------------|
| TC-001 | [Descripción] | [Input] | [Output] |
| TC-002 | [Descripción] | [Input] | [Output] |

### Casos Límite

- [Caso límite 1]
- [Caso límite 2]

## Observabilidad

### Logs

- `[Component] Evento importante: {detalles}`

### Métricas

- `[component]_requests_total`
- `[component]_duration_seconds`

## Constitution Check

### Principio I: Orquestación Única
- [ ] ¿Entra por Dispatcher?
- [ ] ¿No hay comunicación directa?

### Principio II: Separación Determinista vs LLM
- [ ] ¿La lógica es determinista?
- [ ] ¿El LLM solo se usa cuando es necesario?

### Principio III: Local-first
- [ ] ¿Los datos permanecen locales?

### Principio IV: Testing
- [ ] ¿Hay tests definidos?

### Principio V: Trazabilidad
- [ ] ¿Cada decisión se registra?

## Referencias

- [Enlace a referencia 1]
- [Enlace a referencia 2]

## Cambios

| Versión | Fecha | Autor | Cambio |
|---------|-------|-------|--------|
| 1.0.0 | YYYY-MM-DD | [Autor] | Versión inicial |
