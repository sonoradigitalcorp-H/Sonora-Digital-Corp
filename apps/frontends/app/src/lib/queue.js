/**
 * RabbitMQ Client — Event Bus Producer
 * 
 * Conecta al event bus vía RabbitMQ para procesamiento async.
 * En desarrollo usa el event bus de archivo (events.jsonl).
 * En producción usa RabbitMQ cuando está disponible.
 */

const RABBITMQ_API = import.meta.env.VITE_RABBITMQ_API || 'http://localhost:15672'
const RABBITMQ_VHOST = import.meta.env.VITE_RABBITMQ_VHOST || '/'
const USE_RABBITMQ = import.meta.env.VITE_USE_RABBITMQ === 'true'

async function publishViaAPI(exchange, routingKey, payload) {
  try {
    const res = await fetch(`${RABBITMQ_API}/api/exchanges/${encodeURIComponent(RABBITMQ_VHOST)}/${exchange}/publish`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        properties: { delivery_mode: 2, content_type: 'application/json' },
        routing_key: routingKey,
        payload: JSON.stringify(payload),
        payload_encoding: 'string',
      }),
    })
    return res.ok
  } catch {
    return false
  }
}

async function publishViaFile(eventType, payload) {
  try {
    await fetch('/api/events', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type: eventType, payload, source: 'sdc-app' }),
    })
    return true
  } catch {
    return false
  }
}

export async function publish(eventType, payload = {}) {
  if (USE_RABBITMQ) {
    const ok = await publishViaAPI('sdc.topic', `event.${eventType}`, payload)
    if (ok) return true
  }
  return publishViaFile(eventType, payload)
}

export const QUEUES = {
  CALL_OUTBOUND: 'sdc.calls.outbound',
  CLONE_TRAINING: 'sdc.clone.training',
  EVENT_LOG: 'sdc.events.log',
  EMAIL_SEND: 'sdc.email.send',
}
