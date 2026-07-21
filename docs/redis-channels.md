# Redis Pub/Sub Channels

## agent:content:done
- **Publisher**: content-agent
- **Subscribers**: quality-agent, monitor-agent
- **Payload**: `{artist, content_type, urls, score, duration_seconds}`
- **Cuando**: Contenido generado exitosamente

## agent:content:failed
- **Publisher**: content-agent
- **Subscribers**: quality-agent, monitor-agent
- **Payload**: `{artist, error, attempt, pipeline_name}`
- **Cuando**: Falló la generación de contenido

## agent:sales:new-order
- **Publisher**: sales-agent
- **Subscribers**: support-agent, monitor-agent
- **Payload**: `{tenant, product, amount, user_email, transaction_id}`
- **Cuando**: Nueva orden pagada

## agent:support:ticket
- **Publisher**: support-agent
- **Subscribers**: monitor-agent
- **Payload**: `{tenant, user_id, issue_category, priority}`
- **Cuando**: Nuevo ticket de soporte

## system:pipeline:start
- **Publisher**: n8n workflow
- **Subscribers**: monitor-agent
- **Payload**: `{pipeline_name, timestamp, triggered_by}`
- **Cuando**: Un pipeline inicia

## system:pipeline:end
- **Publisher**: n8n workflow
- **Subscribers**: quality-agent, monitor-agent
- **Payload**: `{pipeline_name, status, duration_seconds, error?}`
- **Cuando**: Un pipeline termina (éxito o fallo)

## system:alert
- **Publisher**: monitor-agent, cualquier agente
- **Subscribers**: monitor-agent
- **Payload**: `{service, severity, message, timestamp, incident_id}`
- **Cuando**: Alerta del sistema (severity: critical, warning, info)

## system:service:health
- **Publisher**: monitor-agent
- **Subscribers**: (log only)
- **Payload**: `{service, status, uptime_seconds, last_check}`
- **Cuando**: Health check de cada servicio

## system:service:down
- **Publisher**: monitor-agent
- **Subscribers**: monitor-agent
- **Payload**: `{service, since, last_response, attempts}`
- **Cuando**: Servicio detectado como caído
