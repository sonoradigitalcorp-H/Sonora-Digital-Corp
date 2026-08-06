#!/usr/bin/env python3
"""n8n Workflow Templates — Plantillas para automatización de ventas, soporte, seguimiento.

Estos workflows se cargan en n8n via API o se crean manualmente.
Cada workflow tiene un webhook que el bot puede llamar.
"""

WORKFLOWS = {
    "lead-hot-notify": {
        "name": "Lead Hot → Notificar César",
        "description": "Cuando un lead hot es detectado, notifica a César por Telegram y crea tarea en CRM",
        "nodes": [
            {
                "type": "webhook",
                "name": "webhook_lead_hot",
                "parameters": {"path": "lead_hot", "httpMethod": "POST"},
            },
            {
                "type": "telegram",
                "name": "notify_cesar",
                "parameters": {
                    "chatId": "5738935134",
                    "text": "🔥 NUEVO LEAD HOT\n\n👤 {{ $json.name }}\n📱 {{ $json.phone }}\n📊 Score: {{ $json.score }}/100\n💬 {{ $json.message }}",
                },
            },
            {
                "type": "httpRequest",
                "name": "log_to_crm",
                "parameters": {
                    "url": "http://localhost:8767/webhook/lead_hot",
                    "method": "POST",
                    "body": "={{ $json }}",
                },
            },
        ],
    },
    "followup-automatico": {
        "name": "Follow-up Automático",
        "description": "Envía follow-up a leads que no respondieron en 24h",
        "nodes": [
            {
                "type": "cron",
                "name": "schedule_daily",
                "parameters": {"triggerTimes": {"item": [{"mode": "everyDay", "hour": 10}]}},
            },
            {
                "type": "postgres",
                "name": "get_stale_leads",
                "parameters": {
                    "operation": "executeQuery",
                    "query": "SELECT * FROM leads WHERE lead_score > 30 AND created_at < NOW() - INTERVAL '24 hours' AND last_contact IS NULL LIMIT 10",
                },
            },
            {
                "type": "telegram",
                "name": "send_followup",
                "parameters": {
                    "chatId": "={{ $json.phone }}",
                    "text": "Hola {{ $json.name }}, soy el asistente de AstroTech. Vi que estuviste interesado/a en nuestros servicios. ¿Te gustaría que te cuente más o agendemos una llamada con César?",
                },
            },
        ],
    },
    "daily-summary": {
        "name": "Resumen Diario → César",
        "description": "Envía resumen de métricas a César todos los días a las 9am",
        "nodes": [
            {
                "type": "cron",
                "name": "schedule_9am",
                "parameters": {"triggerTimes": {"item": [{"mode": "everyDay", "hour": 9}]}},
            },
            {
                "type": "httpRequest",
                "name": "get_status",
                "parameters": {"url": "http://localhost:8767/webhook/status", "method": "GET"},
            },
            {
                "type": "telegram",
                "name": "send_summary",
                "parameters": {
                    "chatId": "5738935134",
                    "text": "📊 Resumen diario — {{ $now.format('dd/MM/yyyy') }}\n\n💬 Conversaciones: {{ $json.metrics.conversations_today }}\n👥 Leads: {{ $json.metrics.leads_today }}\n🔥 Leads hot: {{ $json.metrics.hot_leads_today }}\n🤖 TTS: {{ $json.metrics.tts_server }}\n📦 Qdrant: {{ $json.metrics.qdrant }}",
                },
            },
        ],
    },
    "soporte-automatico": {
        "name": "Soporte Automático",
        "description": "Clasifica mensajes de soporte y responde o escala",
        "nodes": [
            {
                "type": "webhook",
                "name": "webhook_support",
                "parameters": {"path": "support_ticket", "httpMethod": "POST"},
            },
            {
                "type": "openai",
                "name": "classify_issue",
                "parameters": {
                    "model": "deepseek/deepseek-v4-flash",
                    "prompt": "Clasifica este mensaje de soporte: {{ $json.message }}. Responde con: urgente, normal, o bajo.",
                },
            },
            {
                "type": "if",
                "name": "check_urgency",
                "parameters": {"conditions": {"string": [{"value": "={{ $json.response }}", "operation": "contains", "value2": "urgente"}]}},
            },
            {
                "type": "telegram",
                "name": "notify_urgent",
                "parameters": {
                    "chatId": "5738935134",
                    "text": "🚨 SOPORTE URGENTE\n\nDe: {{ $json.from }}\nMensaje: {{ $json.message }}",
                },
            },
        ],
    },
    "email-notification": {
        "name": "Email Notificación",
        "description": "Envía email cuando un lead caliente es detectado",
        "nodes": [
            {
                "type": "webhook",
                "name": "webhook_email",
                "parameters": {"path": "email_notify", "httpMethod": "POST"},
            },
            {
                "type": "emailSend",
                "name": "send_email",
                "parameters": {
                    "fromEmail": "bot@astrotech.mx",
                    "toEmail": "cesar@astrotech.mx",
                    "subject": "🔥 Lead Hot: {{ $json.name }}",
                    "text": "Nuevo lead detectado:\n\nNombre: {{ $json.name }}\nTeléfono: {{ $json.phone }}\nScore: {{ $json.score }}/100\nMensaje: {{ $json.message }}",
                },
            },
        ],
    },
}


def save_templates():
    """Save workflow templates to file."""
    import json
    from pathlib import Path
    
    out_dir = Path(__file__).parent.parent / "config" / "n8n-workflows"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    for wf_id, wf in WORKFLOWS.items():
        out_file = out_dir / f"{wf_id}.json"
        out_file.write_text(json.dumps(wf, indent=2, ensure_ascii=False))
        print(f"  ✅ {wf_id}: {wf['name']}")
    
    print(f"\n{len(WORKFLOWS)} workflow templates saved to {out_dir}")


if __name__ == "__main__":
    save_templates()